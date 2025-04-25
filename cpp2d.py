#!/usr/bin/env python

import sys

from cxxheaderparser.simple import *
from cxxheaderparser.types import *

tabwidth = 2
spaces = 0
# current_access = None
output_methods = False

file_ = None

def output(s):
    global file_
    file_.write(s)

def newline():
    global file_
    file_.write('\n')

def indent():
    global spaces
    assert spaces % tabwidth == 0
    spaces += tabwidth

def dedent():
    global spaces
    assert spaces >= 0 and spaces % tabwidth == 0
    spaces -= tabwidth

def output_indent():
    output(spaces * ' ')

# def reset_access():
#     global current_access
#     current_access = None

# def output_and_update_access(access):
#     global current_access
#     if current_access != access:
#         dedent()
#         print(f'{access}:')
#         indent()
#         current_access = access

def remap_param_name(name):
    # avoid collisions with D keywords
    if name == 'ref':
        return 'ref_'
    elif name == 'version':
        return 'version_'
    else:
        return name

def output_param(param):
    output_type(param.type, reset_arrays_to_ptrs=True)
    if param.name:
        output(f' {remap_param_name(param.name)}')

def remap_segment_name(name):
    if name == 'std':
        return 'std_'
    elif name == 'int8_t':
        return 'byte'
    elif name == 'int16_t':
        return 'short'
    elif name == 'int32_t':
        return 'int'
    elif name == 'int64_t':
        return 'long'
    elif name == 'unsigned char' or name == 'uint8_t':
        return 'ubyte'
    elif name == 'unsigned int' or name == 'unsigned' or name == 'uint32_t':
        return 'uint'
    elif name == 'unsigned short' or name == 'uint16_t':
        return 'ushort'
    elif name == 'unsigned long':
        return 'c_ulong'
    elif name == 'unsigned long long' or name == 'uint64_t':
        return 'ulong'
    else:
        return name

def output_template_argument(arg):
    assert not arg.param_pack
    if isinstance(arg.arg, Type) or isinstance(arg.arg, Pointer):
        output_type(arg.arg)
    elif isinstance(arg.arg, Value):
        try:
            # If a template argument is even moderately complicated,
            # this library appears to give up and just return some
            # tokens. In which case, it makes sense to just parse it
            # again, grab the type off the result, and output *that*.
            tokens = arg.arg.tokens
            type_str = ' '.join([_.value for _ in tokens])
            var_str = type_str + ' tmp;' # wee!
            parsed = parse_string(var_str)
            type_ = parsed.namespace.variables[0].type
            output_type(type_)
        except:
            import ipdb; ipdb.set_trace()
            pass
    else:
        import ipdb; ipdb.set_trace()
        pass

def output_template_arguments(args):
    assert len(args) > 0
    for arg in args[:-1]:
        output_template_argument(arg)
        output(', ')
    output_template_argument(args[-1])

def output_segment(segment):
    if isinstance(segment, NameSpecifier):
        name = remap_segment_name(segment.name)
        output(name)
        if segment.specialization is not None:
            output('!(')
            output_template_arguments(segment.specialization.args)
            output(')')
    elif isinstance(segment, FundamentalSpecifier):
        name = remap_segment_name(segment.name)
        output(name)
    elif isinstance(segment, AnonymousName):
        import ipdb; ipdb.set_trace()
        pass
    else:
        import ipdb; ipdb.set_trace()
        pass

def output_segments(segments):
    assert len(segments) > 0
    for segment in segments[:-1]:
        output_segment(segment)
        output('.')
    output_segment(segments[-1])

def output_typename(typename):
    output_segments(typename.segments)

def output_type(type_, reset_arrays_to_ptrs=False, reset_refs_to_ptrs=False):
    if isinstance(type_, Array):
        output_type(type_.array_of)
        if reset_arrays_to_ptrs:
            output('*')
        else:
            output('[')
            output_tokens(type_.size.tokens)
            output(']')
    elif isinstance(type_, Pointer) and isinstance(type_.ptr_to, FunctionType):
        type_ = type_.ptr_to
        output_type(type_.return_type)
        output(' function(')
        if type_.parameters:
            output_param(type_.parameters[0])
            for i in range(1, len(type_.parameters)):
                output(', ')
                output_param(type_.parameters[i])
        output(')')
    elif isinstance(type_, Pointer):
        output_type(type_.ptr_to)
        output('*')
    elif isinstance(type_, Reference):
        if not reset_refs_to_ptrs:
            output('ref ')
        output_type(type_.ref_to)
        if reset_refs_to_ptrs:
            output('*')
    elif isinstance(type_, Type):
        # NOTE: no volatile in D
        # assert not type_.volatile
        typename = type_.typename
        classkey = typename.classkey
        if classkey is not None and classkey not in {'class', 'struct', 'union', 'enum class'}:
            import ipdb; ipdb.set_trace()
            pass
        if type_.const:
            output('const(')
        output_typename(typename)
        if type_.const:
            output(')')
    else:
        import ipdb; ipdb.set_trace()
        pass

def output_tokens(tokens):
    for token in tokens:
        assert isinstance(token.value, str)
        s = token.value
        if s == '::':
            s = '.'
        output(s)

def is_anonymous(_):
    if isinstance(_, ClassScope):
        return is_anonymous(_.class_decl)
    elif isinstance(_, ClassDecl) or isinstance(_, EnumDecl) or isinstance(_, Type):
        return len(_.typename.segments) == 1 \
            and isinstance(_.typename.segments[0], AnonymousName)
    elif isinstance(_, Field):
        return is_anonymous(_.type)
    else:
        import ipdb; ipdb.set_trace()
        pass

def is_union(_):
    if isinstance(_, Array) or isinstance(_, Pointer) or isinstance(_, Reference):
        return False
    elif isinstance(_, Field):
        return is_union(_.type)
    elif isinstance(_, Type):
        return _.typename.classkey == 'union'
    else:
        try:
            return _.class_decl.typename.classkey == 'union'
        except:
            import ipdb; ipdb.set_trace()
            pass

def is_enum(_):
    if isinstance(_, EnumDecl):
        classkey = _.typename.classkey
        return classkey == 'enum' or classkey == 'enum class'
    else:
        import ipdb; ipdb.set_trace()
        pass
        # return cls.class_decl.typename.classkey == 'enum'

def is_anonymous_union(_):
    return is_union(_) and is_anonymous(_)

def is_anonymous_enum(_):
    return is_enum(_) and is_anonymous(_)

def get_anonymous_union_key(_):
    if isinstance(_, ClassScope):
        return get_anonymous_union_key(_.class_decl)
    elif isinstance(_, ClassDecl) or isinstance(_, Type):
        segments = _.typename.segments
        assert len(segments) == 1
        return segments[0].id
    elif isinstance(_, Field):
        return get_anonymous_union_key(_.type)
    else:
        import ipdb; ipdb.set_trace()
        pass

def output_union(union):
    output('union')
    if not is_anonymous(union):
        import ipdb; ipdb.set_trace()
        pass
    output(' {')
    newline()
    indent()
    for field in union.fields:
        output_indent()
        output_type(field.type, reset_refs_to_ptrs=True)
        output(f' {field.name};')
        newline()
    dedent()
    output_indent()
    output('}')

def output_enum(_):
    assert is_enum(_)
    assert len(_.values) > 0
    output_indent()
    output(f'enum')
    try:
        if not is_anonymous_enum(_):
            output(f' ')
            output_typename(_.typename)
    except:
        import ipdb; ipdb.set_trace()
        pass
    if _.base:
        output(' : ')
        output_typename(_.base)
    output(' {')
    newline()
    indent()
    for i, value in enumerate(_.values):
        output_indent()
        output(f'{value.name}')
        if value.value:
            output(' = ')
            output_tokens(value.value.tokens)
        output(',' if i + 1 < len(_.values) else '')
        newline()
    dedent()
    output_indent()
    output('}')
    newline()

def output_template_parameter(param):
    assert not param.param_pack
    assert param.default is None
    assert param.template is None
    if param.typekey == 'class':
        output(param.name)
    else:
        assert False

def output_template_parameters(params):
    assert len(params) > 0
    output('(')
    for param in params[:-1]:
        output_template_parameter(param)
        output(', ')
    output_template_parameter(params[-1])
    output(')')

def output_class_method(method):
    # skip ctors and dtors for now
    if method.constructor or method.destructor:
        return

    # skip overloaded operators for now
    if method.operator:
        return

    # only wrap public API
    if method.access == 'private' or method.access == 'protected':
        return

    # unhandled stuff:
    assert not method.extern
    assert not method.has_trailing_return
    assert not method.default
    assert not method.final
    assert method.ref_qualifier is None
    assert method.template is None
    assert not method.constexpr
    assert not method.deleted
    assert not method.explicit
    assert method.msvc_convention is None
    assert method.operator is None
    assert method.throw is None
    assert not method.volatile

    output_indent()
    if method.pure_virtual:
        output('abstract ')
    elif method.override:
        output('override ')
    elif method.static:
        output('static ')
    elif method.virtual:
        pass
    else:
        output('final ')
    if method.return_type is None:
        assert method.constructor or method.destructor
    else:
        output_type(method.return_type)
    if method.constructor:
        output('this')
    elif method.destructor:
        output('~this')
    else:
        output(f' ')
        output_segments(method.name.segments)
    output('(')
    if method.parameters:
        output_param(method.parameters[0])
        for i in range(1, len(method.parameters)):
            output(', ')
            output_param(method.parameters[i])
    if method.vararg:
        output(', ...')
    output(')')
    if method.const:
        output(' const')
    if method.noexcept:
        output(' nothrow')
    output(';')
    newline()

def output_class_methods(cls):
    for method in cls.methods:
        output_class_method(method)

def output_class(cls):
    decl = cls.class_decl
    assert not decl.explicit

    # TODO: No multiple inheritance unless pure virtual...
    assert len(decl.bases) <= 1

    if decl.final:
        output('final ')

    name = decl.typename.segments[0].name
    if output_methods:
        output(f'class {name}')
    else:
        output(f'struct {name}')

    if decl.template:
        output_template_parameters(decl.template.params)

    if output_methods and decl.bases:
        base = decl.bases[0]
        assert not base.virtual # no virtual inheritance
        output(f': ')
        output_typename(base.typename)

    output(' {')
    newline()

    indent()

    for enum in cls.enums:
        # output_and_update_access(enum.access)
        output_enum(enum)

    anonymous_union_fields = dict()

    for cls_ in cls.classes:
        if is_anonymous_union(cls_):
            key = get_anonymous_union_key(cls_)
            assert key not in anonymous_union_fields
            anonymous_union_fields[key] = cls_
        elif isinstance(cls_, ClassScope):
            output_indent()
            output_class(cls_)
        else:
            import ipdb; ipdb.set_trace()
            pass

    for field in cls.fields:
        # output_and_update_access(field.access)
        output_indent()
        if is_anonymous_union(field):
            key = get_anonymous_union_key(field)
            output_union(anonymous_union_fields[key])
        else:
            if field.static:
                output('__gshared ')
            output_type(field.type, reset_refs_to_ptrs=True)
            output(f' {field.name}')
        output(';')
        newline()

    if output_methods:
        output_class_methods(cls)

    dedent()
    output_indent()
    output('}')
    newline()

if __name__ == '__main__':
    file_ = sys.stdout

    parsed = parse_file('filtered.cpp')

    output('extern(C++):')
    newline()

    for using in parsed.namespace.using_alias:
        newline()
        assert using.access is None
        assert using.template is None
        output(f'alias {using.alias} = ')
        output_type(using.type)
        output(';')

    for typedef in parsed.namespace.typedefs:
        newline()
        assert typedef.access is None
        output(f'alias {typedef.name} = ')
        output_type(typedef.type)
        output(';')

    for enum in parsed.namespace.enums:
        newline()
        output_enum(enum)

    for cls in parsed.namespace.classes:
        newline()
        output_class(cls)
