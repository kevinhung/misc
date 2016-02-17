-include /env.mak

SUBDIR = dsm6.0 dsm6.1 pkg

.PHONY: all clean $(SUBDIR)

all clean: $(SUBDIR)

$(SUBDIR):
	make -C $@ $(MAKECMDGOALS)

pkg: dsm6.0 dsm6.1

# vim:ft=make ts=4 sts=4 sw=4
