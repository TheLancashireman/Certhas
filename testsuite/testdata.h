/* testdata.h - a load of test data
 *
 * (c) David Haworth
*/
#ifndef TESTDATA_H
#define TESTDATA_H	1

/* Some scalars
*/
extern const unsigned char uc1;
extern const unsigned short us1;
extern const unsigned int ui1;
extern const unsigned long long ul1;

extern const signed char sc1;
extern const signed short ss1;
extern const signed int si1;
extern const signed long long sl1;

/* Some pointers
*/
extern const unsigned char * const p1;
extern const unsigned short * const p2;
extern const unsigned int * const p3;
extern const unsigned long long * const p4;

enum enum1_e { enum1a, enum1b, enum1c, enum1d, enum1e, enum1f, enum1g, enum1h };
typedef enum enum1_e enum1_t;

extern const enum1_t e1a;
extern const enum1_t e1h;
extern const enum enum1_e e1d;
extern const enum1_t e142;

extern const unsigned char * const p5;
extern const unsigned char * const p6;
extern unsigned char * const p7;

struct struct1_s
{
	char ss_c;
	int ss_i;
	const char *ss_pc;
	const unsigned short *ss_ps;
	const unsigned int *ss_pi;
	const unsigned long long *ss_pl;
};

typedef struct struct1_s struct1_t;

extern const struct1_t struct1a;
extern const struct struct1_s struct1b;
extern const struct1_t * const p8;

union union1_u
{
	unsigned long long uu_ul;
	unsigned int uu_ui;
	unsigned short uu_us;
	unsigned char uu_uc;
	void *uu_p;
};

typedef union union1_u union1_t;

extern const union1_t union1a;
extern const union union1_u union1b;
extern const union1_t * const p9;

typedef int (*fp_t)(const void *param);

extern const fp_t fp1;
extern int function1(const void *param);

#endif
