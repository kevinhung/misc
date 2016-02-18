-include /env.mak

CFLAGS += -Werror -Wall -Wextra -Wno-unused-parameter
CXXFLAGS += $(CFLAGS)
LDFLAGS += -Wl,--as-needed

# Without -fPIC, segfault when running with DSM 6.0
CFLAGS += -fPIC -DPIC

# Link against newest toolkit at build time
LDFLAGS += -L../dsm6.1

ifeq ($(HAVE_FOO),yes)
CFLAGS += -DHAVE_FOO
LIBS += -lfoobar
else
LIBS += -Wl,--no-as-needed -lfoobar -Wl,--as-needed
endif

.PHONY: all clean

all: main.cpp
	$(CXX) $(CXXFLAGS) $< $(LDFLAGS) $(LIBS)

clean:
	rm -f *.o *.so* *.a a.out

# vim:ft=make ts=4 sts=4 sw=4
