/**
 * Use of weak link for C++ non-static member function.
 */

#include <cstdio>
#include <cstdlib>
#include "../foobar.h"


static void bar_alternative(int value)
{
	fprintf(stdout, "I'm %s\n", __FUNCTION__);
}


int main(int argc, char **argv)
{
	int value = 5;
	FooBar obj;

#ifdef HAVE_FOO
	obj.foo(value);
#endif

	/**
	 * If HAVE_FOO is undefined => no "strong" symbol of libfoobar.so is
	 * referenced. Then libfoobar.so will NOT be NEEDED due to the effect
	 * of -Wl,--as-needed. As the result, always enter else-part...
	 * See ./Makefile for the solution.
	 */
	if (&FooBar::bar) {  // "&" is required or build fail.
		obj.bar(value);
	} else {
		bar_alternative(value);
	}

	return EXIT_SUCCESS;
}

// vim:ts=4 sts=4 sw=4
