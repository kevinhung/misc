#!/bin/bash


PrintTitle()
{
    echo -e "\n\033[32m======== $1 ========\033[0m"
}

Run()
{
    echo "Run against '$1/libfoobar.so.6' ..."
    LD_LIBRARY_PATH="$1" pkg/a.out
}


PrintTitle "At Build Time"
make clean
make -j 4

PrintTitle "At Runtime"
Run dsm6.0
Run dsm6.1

# vim:ft=sh ts=4 sts=4 sw=4 et
