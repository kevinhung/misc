# The same as ../dsm6.0/Makefile excepts value of $(MINOR)

-include /env.mak

LIBNAME = foobar
MAJOR = 6
MINOR = 1

CFLAGS += -DMAJOR=$(MAJOR) -DMINOR=$(MINOR)
CFLAGS += -fPIC -DPIC
CFLAGS += -Werror -Wall -Wextra -Wno-unused-parameter
LDFLAGS += -Wl,--as-needed

SRCS = $(wildcard *.c)
OBJS = $(SRCS:%.c=%.o)

.PHONY: all clean

all: lib$(LIBNAME).so.$(MAJOR)

lib$(LIBNAME).so.$(MAJOR): $(OBJS)
	$(CC) -shared -o $@ $^ -Wl,-soname,$@ $(LDFLAGS)
	ln -sf $@ lib$(LIBNAME).so

%.o: %.c
	$(CC) $(CFLAGS) -c $<

clean:
	rm -f *.o *.so* *.a a.out

# vim:ft=make ts=4 sts=4 sw=4
