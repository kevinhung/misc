/**
 * Exported header of libfoobar.
 */

#ifndef __FOOBAR_H__
#define __FOOBAR_H__

/**
 * Fake availability.h for ease of demo.
 */
#define AVAILABLE_INT_REGULAR
#ifdef BUILD_LIBFOOBAR
#define AVAILABLE_INT_WEAK          AVAILABLE_INT_REGULAR
#else
#define AVAILABLE_INT_WEAK          __attribute__((weak))
#endif
#define AVAILABLE_INT_SDK_VER_6_0   AVAILABLE_INT_REGULAR
#define AVAILABLE_INT_SDK_VER_6_1   AVAILABLE_INT_WEAK
#define SDK_STARTING_FROM(version)  AVAILABLE_INT_##version


class FooBar {
public:
	SDK_STARTING_FROM(SDK_VER_6_0) void foo(int value);
	SDK_STARTING_FROM(SDK_VER_6_1) void bar(int value);
};

#endif  // __FOOBAR_H__
// vim:ts=4 sts=4 sw=4
