#!/bin/bash


PROG=diagnose.py
INSTALLDIR=$(mktemp -d /tmp/XXXXXX)
DESTDIR=$INSTALLDIR/diagnose


OnExit()
{
    [ -n "$INSTALLDIR" ] && rm -rf $INSTALLDIR
}


trap OnExit EXIT


for f in $(find -name \*.py -o -name \*.map); do
    install -Dm644 $f $DESTDIR/$f
done
chmod +x $DESTDIR/$PROG
tar cJpvf diagnose.txz -C $INSTALLDIR diagnose

# vim:ts=4 sts=4 sw=4 et
