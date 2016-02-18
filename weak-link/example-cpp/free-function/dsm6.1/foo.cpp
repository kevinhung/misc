/**
 * The same as ../dsm6.0/foo.c
 */

#include <cstdio>
#include <cstdlib>


void foo(int value)
{
	fprintf(stdout, "I'm %s in DSM %d.%d\n", __FUNCTION__, MAJOR, MINOR);
}

// vim:ts=4 sts=4 sw=4
