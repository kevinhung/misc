/**
 * New function introduced in DSM 6.1
 */

#include <cstdio>
#include <cstdlib>
#include "../foobar.h"


void FooBar::bar(int value)
{
	fprintf(stdout, "I'm %s in DSM %d.%d\n", __FUNCTION__, MAJOR, MINOR);
}

// vim:ts=4 sts=4 sw=4
