#!/usr/bin/python2

from report import report, Report
from simpleldap import ldapsearch


def __load_id(fpath):
    ids = set()

    with open(fpath, 'r') as f:
        for line in f.read().splitlines():
            if line[0] == '#':
                continue
            tokens = line.split(':')
            try:
                ids.add(int(tokens[2]))
            except IndexError:
                pass  # Ignore format error.
            except ValueError:
                pass  # Ignore invalid uid/gid.

    return ids


def __check_id_conflicts(host, ugfilter, ugid, local_ids, unit):
    ok, msg = Report.FAIL, []

    res, err = ldapsearch(host, ugfilter, 'dn', ugid)

    if err != 0x00 and err != 0x04:
        msg.append('failed to recognize ' + unit)
        return ok, {'messages': msg}

    ok = Report.PASS

    ids = set(map(lambda x: int(x[ugid][0]),
              filter(lambda x: ugid in x and x[ugid][0].isdigit(), res)))
    if len(ids) != len(res):
        msg.append('some ' + unit + ' have no numeric ID(s)')

    if len(ids.intersection(local_ids)):
        ok = Report.FAIL
        msg.append('some ' + unit + ' have numeric ID conflict with local one(s)')

    return ok, {'messages': msg}


@report('No numeric uid conflict with local user(s)')
def check_uid_conflicts(host, ufilter, uid):
    uids = __load_id('/etc/passwd')
    return __check_id_conflicts(host, ufilter, uid, uids, 'LDAP user(s)')


@report('No numeric gid conflict with local group(s)')
def check_gid_conflicts(host, gfilter, gid):
    gids = __load_id('/etc/group')
    return __check_id_conflicts(host, gfilter, gid, gids, 'LDAP group(s)')

# vim:ts=4 sts=4 sw=4 et
