#!/bin/sh
#
# Run the Cirth test suite. In the base directory, type 'testsuite/runtest.sh'
#
# Prerequisites: same as Cirth, plus gcc

(cd testsuite; gcc -g -o testprog testprog.c testdata.c)
./explore.py testsuite/testprog uc1
