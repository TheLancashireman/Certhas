/* testdata.c - a load of test data
 *
 * (c) David Haworth
*/
#include "testdata.h"

const unsigned char c2[] = "Goodbye world";
unsigned char c3[] = "Variable string";

/* Some scalars
*/
const unsigned char uc1 = 'A';
const unsigned short us1 = 0x1234;
const unsigned int ui1 = 0x12345678;
const unsigned long long ul1 = 0x123456789abcdef0;

const signed char sc1 = 'a';
const signed short ss1 = 0x4321;
const signed int si1 = 0x87654321;
const signed long long sl1 = 0xfedcba9876543210;

/* Some pointers
*/
const unsigned char * const p1 = &uc1;
const unsigned short * const p2 = &us1;
const unsigned int * const p3 = &ui1;
const unsigned long long * const p4 = &ul1;

const enum1_t e1a = enum1a;
const enum1_t e1h = enum1h;
const enum enum1_e e1d = enum1d;
const enum1_t e142 = (enum1_t)42;

const unsigned char * const p5 = "Hello, world";
const unsigned char * const p6 = c2;
unsigned char * const p7 = c3;

typedef struct struct1_s struct1_t;

const struct1_t struct1a =			{ 'B', 99, &uc1, &us1, &ui1, &ul1 };
const struct struct1_s struct1b =	{ 'C', 66, &c2[1], 0, (const unsigned int *)&si1, (const unsigned long long *)666 };
const struct1_t * const p8 =		&struct1a;

const union1_t union1a =			{ .uu_p = &c3[3] };
const union union1_u union1b =		{ .uu_p = &c3[4] };
const union1_t * const p9 =			&union1b;

const fp_t fp1 = function1;


int function1(const void *param)
{
	return (int)*(char *)param;
}
