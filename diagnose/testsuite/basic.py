#!/usr/bin/python2

from report import report, Report
from simpleldap import ldapsearch


def __is_name_valid(name):
    if not name:
        return False
    if '@' in name:
        return False
    return True


def __recognize_entries(host, ugfilter, name, ugid, unit):
    ok, msg = Report.FAIL, []

    res, err = ldapsearch(host, ugfilter, 'dn', name, ugid)

    if err == 0x00:
        ok = Report.PASS if len(res) else Report.WARN
        msg.append(str(len(res)) + ' ' + unit + ' recognized')
    elif err == 0x04:
        msg.append('size limit exceeded, ' + str(len(res)) + ' ' + unit + ' recognized')
    else:
        msg.append('failed to recognize ' + unit)
        return ok, {'messages': msg}

    try:
        if any(map(lambda x: not __is_name_valid(x[name][0]), res)):
            ok = Report.FAIL
            msg.append('name(s) of some ' + unit + ' are invalid')
    except KeyError:
        ok = Report.FAIL
        msg.append('some ' + unit + ' have no name(s)')

    try:
        if any(map(lambda x: not x[ugid][0].isdigit(), res)):
            ok = Report.FAIL
            msg.append('ID(s) of some ' + unit + ' are not numeric')
    except KeyError:
        ok = Report.FAIL
        msg.append('some ' + unit + ' have no numeric ID(s)')

    try:
        if len(res) != len(set([x[name][0] for x in res])):
            ok = Report.FAIL
            msg.append('name(s) of ' + unit + ' are not unique')
        if len(res) != len(set([x[ugid][0] for x in res])):
            ok = Report.FAIL
            msg.append('ID(s) of ' + unit + ' are not unique')
    except KeyError:
        pass  # Missing attributes are handled in privious checks.

    return ok, {'messages': msg}


@report('Recognize LDAP user(s)')
def recognize_users(host, ufilter, name, uid):
    return __recognize_entries(host, ufilter, name, uid, 'LDAP user(s)')


@report('Recognize LDAP group(s)')
def recognize_groups(host, gfilter, name, gid):
    return __recognize_entries(host, gfilter, name, gid, 'LDAP group(s)')


@report('Completeness of LDAP user(s)')
def check_user_completeness(host, pfilter, sfilter):
    ok, is_sizelimit, msg = Report.FAIL, False, []

    passwd, err = ldapsearch(host, pfilter, 'dn')
    if err == 0x00:
        pass
    elif err == 0x04:
        is_sizelimit = True
    else:
        msg.append('failed to recognize LDAP user(s)')
        return ok, {'messages': msg}
    passwd = set(x['dn'] for x in passwd)

    shadow, err = ldapsearch(host, sfilter, 'dn')
    if err == 0x00:
        pass
    elif err == 0x04:
        is_sizelimit = True
    else:
        msg.append('failed to recognize LDAP user(s)')
        return ok, {'messages': msg}
    shadow = set(x['dn'] for x in shadow)

    if is_sizelimit:
        msg.append('size limit exceeded')
    else:
        ok = Report.PASS

    if len(passwd - shadow):
        ok = Report.FAIL
        msg.append(str(len(passwd - shadow)) + ' potential LDAP user(s) do not match \'' + sfilter + '\'')
    if len(shadow - passwd):
        ok = Report.FAIL
        msg.append(str(len(shadow - passwd)) + ' potential LDAP user(s) do not match \'' + pfilter + '\'')

    return ok, {'messages': msg}

# vim:ts=4 sts=4 sw=4 et
