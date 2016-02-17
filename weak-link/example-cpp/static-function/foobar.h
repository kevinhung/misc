/**
 * Exported header of libfoobar.
 */

#ifndef __FOOBAR_H__
#define __FOOBAR_H__

/**
 * Fake availability.h for ease of demo.
 */
#define AVAILABLE_INT_REGULAR
#define AVAILABLE_INT_WEAK          __attribute__((weak))
#define AVAILABLE_INT_SDK_VER_6_0   AVAILABLE_INT_REGULAR
#define AVAILABLE_INT_SDK_VER_6_1   AVAILABLE_INT_WEAK
#define SDK_STARTING_FROM(version)  AVAILABLE_INT_##version


class FooBar {
public:
	SDK_STARTING_FROM(SDK_VER_6_0) static void foo(int value);
	SDK_STARTING_FROM(SDK_VER_6_1) static void bar(int value);
};

#endif  // __FOOBAR_H__
// vim:ts=4 sts=4 sw=4
