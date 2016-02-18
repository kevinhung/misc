#!/usr/bin/python2

import sys
import argparse
import traceback
import mapping
import server
from simpleldap import Host, ldapsearch, ldaperror, DEBUG_LOG_FILE


class ExitCode:
    SUCCESS, FAILURE, IO_ERROR, INVALID_BASE_DN = range(4)


def select_basedn(candidates):
    idx = 0

    while idx <= 0 or idx > candidates:
        print
        for i in range(0, len(candidates)):
            print str(i + 1) + ') ' + candidates[i]
        try:
            idx = int(raw_input('Please select a base DN you want: '))
        except ValueError:
            pass  # Re-try.

    return candidates[idx - 1]


def validate_basedn(host):
    res, err = ldapsearch(host, '', 'namingContexts', basedn='', scope='base')

    if err:
        print >> sys.stderr, 'Error: ' + ldaperror(err) + '\n'
        return False

    candidates = []
    if len(res) and 'namingContexts' in res[0]:
        candidates = res[0]['namingContexts']

    if host.basedn:
        if host.basedn not in candidates:
            print >> sys.stderr, 'Warning: Given base DN \'' + host.basedn + '\' does not match any candidates.'
    else:
        if len(candidates) == 0:
            print >> sys.stderr, 'Error: No available base DN detected, please specify it via \'-b\' option.\n'
            return False
        if len(candidates) == 1:
            host.basedn = candidates[0]
        else:
            if not sys.stdin.isatty():
                return False  # Not in interactive mode.
            host.basedn = select_basedn(candidates)

    return True


def run_testsuites(host, mapfile):
    import testsuite as ts

    if isinstance(mapfile, mapping.Mapping):
        m = mapfile
    elif mapfile:
        m = mapping.load_mapping_file(mapfile)
    else:
        # TODO Select mapping by detected server type.
        m = mapping.rfc_2307()

    passwd = m.backends['passwd']
    # shadow = m.backends['shadow']
    group = m.backends['group']

    ts.print_settings(host, m)

    ts.required_object_classes(host, m.required_object_class)
    ts.recognize_users(host, m.user_filter, passwd['uid'], passwd['uidNumber'])
    ts.check_user_completeness(host, m.passwd_filter, m.shadow_filter)
    ts.recognize_groups(host, m.group_filter, group['cn'], group['gidNumber'])
    ts.check_samba_support(host, m.user_filter)
    ts.check_uid_conflicts(host, m.user_filter, passwd['uidNumber'])
    ts.check_gid_conflicts(host, m.group_filter, group['gidNumber'])
    # TODO Append more tests.


def main(argv):
    parser = argparse.ArgumentParser()
    req = parser.add_mutually_exclusive_group(required=True)
    req.add_argument(
        '-H', dest='ldapuri', metavar='ldapuri',
        help='LDAP servr URI, e.g. \'ldap://ldap.synology.io\'')
    req.add_argument(
        '-C', dest='config', default=False, action='store_true',
        help='DS only, read LDAP server info from nslcd.conf which can be overridden by -b, -D -w, -Z and -m options')
    parser.add_argument(
        '-b', dest='basedn', metavar='searchbase',
        help='search base (base DN)')
    parser.add_argument(
        '-D', dest='binddn', metavar='binddn',
        help='bind DN')
    parser.add_argument(
        '-w', dest='bindpw', metavar='passwd',
        help='bind password')
    parser.add_argument(
        '-Z', dest='starttls', default=False, action='store_true',
        help='issue StartTLS')
    parser.add_argument(
        '-m', dest='mapfile', metavar='mapfile',
        help='custom LDAP mapping file, e.g. \'mapping/rfc-2307.map\'')
    parser.add_argument(
        '-o', dest='outfile', metavar='outfile',
        help='output file, default stdout')
    # TODO Select output format, only console_output now (see @report in testsuite/report.py).
    args = parser.parse_args(argv[1:])

    if args.outfile:
        try:
            sys.stdout = open(args.outfile, 'w')
        except IOError:
            print >> sys.stderr, 'Failed to open \'' + args.outfile + '\'\n'
            return ExitCode.IO_ERROR

    if args.config:
        info = server.from_nslcd_conf()
        args.ldapuri = info['ldapuri']
        if args.basedn is None:
            args.basedn = info['basedn']
        if args.binddn is None:
            args.binddn = info['binddn']
        if args.bindpw is None:
            args.bindpw = info['bindpw']
        if info['starttls']:
            args.starttls = True
        if args.mapfile is None:
            args.mapfile = mapping.from_nslcd_conf()

    host = Host(args.ldapuri,
                basedn=args.basedn or '',
                binddn=args.binddn or '',
                bindpw=args.bindpw or '',
                starttls=args.starttls)

    try:
        if validate_basedn(host):
            run_testsuites(host, args.mapfile)
            code = ExitCode.SUCCESS
        else:
            code = ExitCode.INVALID_BASE_DN
    except:
        sys.stdout.flush()
        traceback.print_exc()
        code = ExitCode.FAILURE
    finally:
        print >> sys.stderr, '\nRefer \'' + DEBUG_LOG_FILE + '\' for more info.'
        if args.outfile:
            print >> sys.stderr, 'Result is stored as \'' + args.outfile + '\'.'

    return code


if __name__ == '__main__':
    sys.exit(main(sys.argv))

# vim:ts=4 sts=4 sw=4 et
