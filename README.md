# opennurbs-d

Quick and dirty C++ -> D header conversion tool using the cxxheaderparse Python library.
Focused entirely on stamping out `extern(C++)` wrappers in D for McNeel's open source OpenNURBS library.

To build the wrapper, run:
```sh
$ ./run.sh
```
To build a simple test program, run:
```sh
$ dmd test.d
```
