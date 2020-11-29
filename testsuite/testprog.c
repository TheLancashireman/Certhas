/* testprog.c - uses the testdata to make sure it doesn't get optimised away
 *
 * (c) David Haworth
*/

#include <stdio.h>
#include "testdata.h"

int main(int argc, char **argv)
{
	function1(&uc1);
	function1(&us1);
	function1(&ui1);
	function1(&ul1);

	function1(&sc1);
	function1(&ss1);
	function1(&si1);
	function1(&sl1);

	function1(p1);
	function1(p2);
	function1(p3);
	function1(p4);
	function1(p5);
	function1(p6);
	function1(p7);
	function1(p8);
	function1(p9);

	function1(&struct1a);
	function1(&struct1b);
	function1(&union1a);
	function1(&union1b);

	return (*fp1)(NULL);
}
