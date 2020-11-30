#!/bin/sh
#
# Run the Certhas test suite. In the base directory, type 'testsuite/runtest.sh'
#
# Prerequisites: same as Certhas, plus gcc
#
# This file is part of Certhas.
#
# Certhas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Certhas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Certhas.  If not, see <http://www.gnu.org/licenses/>.

(cd testsuite; gcc -g -o testprog testprog.c testdata.c)
./explore.py testsuite/testprog \
	uc1 us1 ui1 ul1 \
	sc1 ss1 si1 sl1 \
	p1 p2 p3 p4 p5 p6 p7 p8 p9 \
	struct1a struct1b \
	union1a union1b \
	fp1 \
	> results.txt
diff -q results.txt testsuite/expected.txt
if [ $? = 0 ]; then
	echo "TEST PASSED"
else
	echo "TEST FAILED"
fi
