/* testprog.c - uses the testdata to make sure it doesn't get optimised away
 *
 * (c) David Haworth
 *
 * This file is part of Certhas.
 *
 * Certhas is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Certhas is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
  * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Certhas.  If not, see <http://www.gnu.org/licenses/>.
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
