import core.stdc.config : c_ulong;
import core.stdc.stddef : wchar_t;
import core.stdc.stdio : FILE;
import core.stdc.time : time_t, tm;

import std_;

// see https://forum.dlang.org/post/zmzzissfeqoqxojgprxy@forum.dlang.org
string fixMangle(alias sym, string name)() {
  import std.string;
  import std.conv : text;
  version(Windows)
    return sym.mangleof.replace(__traits(identifier, sym), "f");
  else version(Posix)
    return sym.mangleof.replace(
      __traits(identifier, sym).length.text ~ __traits(identifier, sym),
      name.length.text ~ name);
  else
    static assert (0, "unsupported system");
}

extern(C) {
  struct Block;
  struct CImpl;
  struct CImplDSP;
  struct CImplSL;
  struct Impl;
  struct Private;
  struct memchunk;

  struct ONX_ModelComponentReferenceLink;
  struct ONX_ModelPrivate;
  struct ON_3dmAnnotationSettingsPrivate;
  struct ON_3dmObjectAttributesPrivate;
  struct ON_3dmRenderSettingsPrivate;
  struct ON_3dmTableStatusLink;
  struct ON_ArithmeticCalculatorImplementation;
  struct ON_BUFFER_SEGMENT;
  struct ON_ComponentManifestImpl;
  struct ON_CompressorImplementation;
  struct ON_DecalCollection;
  struct ON_DirectoryIteratorImpl;
  struct ON_FontGlyphCache;
  struct ON_FontListImpl;
  struct ON_FreeTypeFace;
  struct ON_LayerPrivate;
  struct ON_LinetypePrivate;
  struct ON_ManifestMapImpl;
  struct ON_MeshCacheItem;
  struct ON_OBSOLETE_V2_Annotation;
  struct ON_OBSOLETE_V2_TextDot;
  struct ON_OBSOLETE_V5_Annotation;
  struct ON_RTreeListNode;
  struct ON_ReferencedComponentSettingsImpl;
  struct ON_SN_BLOCK;
  struct ON_SectionStylePrivate;
  struct ON_SerialNumberMapPrivate;
  struct ON_SubDEdgeSurfaceCurve;
  struct ON_SubDLevel;
  struct ON_SubDMeshImpl;
  struct ON_SubD_FixedSizeHeap_ComponentPairHashElement;
  struct ON_SubDimple;
  struct ON_UnicodeTextFilePrivate;
  struct ON_UuidIndexList2_Private;
  struct ON_UuidPairList2_Private;
  struct ON_UuidPtrList2_Private;
  struct ON_V4V5_MeshNgonList;
  struct ON_V5x_DimStyle;
  struct ON_Value;
  struct ON_XMLNodeChildIteratorPrivate;
  struct ON_XMLNodePrivate;
  struct ON_XMLNodePropertyIteratorPrivate;
  struct ON_XMLParametersIteratorPrivate;
  struct ON_XMLParametersPrivate;
  struct ON_XMLPropertyPrivate;
  struct ON_XMLRootNodePrivate;
  struct ON_XMLSegmentedStreamPrivate;
  struct ON_XMLUserDataPrivate;
  struct ON_XMLVariantPrivate;
  struct ON__3dmV1LayerIndex;
  struct ON__3dmV1_XDATA;
}

alias ReadCallback = void *;
alias TransformCallback = void *;
alias WriteCallback = void *;

alias ON_GetFontMetricsFuncType = void *;
alias ON_GetGlyphMetricsFuncType = void *;
alias ON_GetGlyphOutlineFuncType = void *;

immutable(double) ON_UNSET_POSITIVE_VALUE = 1.23432101234321e+308;
immutable(double) ON_UNSET_VALUE = -ON_UNSET_POSITIVE_VALUE;
