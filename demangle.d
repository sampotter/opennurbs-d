void main(string[] args) {
  import core.demangle : demangle;
  import std.stdio;
  assert(args.length == 2);
  writeln(demangle(args[1]));
}
