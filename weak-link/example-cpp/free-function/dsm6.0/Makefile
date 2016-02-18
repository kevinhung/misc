# The same as ../dsm6.1/Makefile excepts value of $(MINOR)

-include /env.mak

LIBNAME = foobar
MAJOR = 6
MINOR = 0

CFLAGS += -DMAJOR=$(MAJOR) -DMINOR=$(MINOR)
CFLAGS += -fPIC -DPIC
CFLAGS += -Werror -Wall -Wextra -Wno-unused-parameter
CXXFLAGS += $(CFLAGS)
LDFLAGS += -Wl,--as-needed

SRCS = $(wildcard *.cpp)
OBJS = $(SRCS:%.cpp=%.o)

.PHONY: all clean

all: lib$(LIBNAME).so.$(MAJOR)

lib$(LIBNAME).so.$(MAJOR): $(OBJS)
	$(CXX) -shared -o $@ $^ -Wl,-soname,$@ $(LDFLAGS)
	ln -sf $@ lib$(LIBNAME).so

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $<

clean:
	rm -f *.o *.so* *.a a.out

# vim:ft=make ts=4 sts=4 sw=4
