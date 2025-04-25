#!/usr/bin/env bash

HEADER_CPP=header.cpp
HEADER_D=header.d
DRIVER=driver.cpp
INPUT=filtered.cpp
OUTPUT=opennurbs.d
OPENNURBS_PATH=../opennurbs

clang++ -DD_WRAP -I$OPENNURBS_PATH -E -P -CC $DRIVER > $INPUT

sed --in-place -n -f - $INPUT <<'EOF'
/__BEGIN_TARGET__/,/__END_TARGET__/{
    /__BEGIN_TARGET__/b
    /__END_TARGET__/b
    p
}
EOF

clang-format -i $INPUT

TMP=$(mktemp)
cat $HEADER_CPP $INPUT > $TMP
mv $TMP $INPUT

./test.py > $OUTPUT

TMP=$(mktemp)
cat $HEADER_D $OUTPUT > $TMP
mv $TMP $OUTPUT
