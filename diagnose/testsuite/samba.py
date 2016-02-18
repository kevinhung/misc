#!/usr/bin/python2

from simpleldap import ldapsearch
from report import report, Report


@report('Support Samba authentication')
def check_samba_support(host, filt):
    '''
    Check whether host supports Samba's NTLM authentication.
    '''

    ok, msg = Report.PASS, []

    if not host.object_class['sambaSamAccount']:
        msg.append('no object class \'sambaSamAccount\'')
        return False, {'messages': msg}

    # sambaDomain seems not necessary, but LDAP Account Manager (LAM) requires it.
    if host.object_class['sambaDomain']:
        res, err = ldapsearch(host, '(objectClass=sambaDomain)', 'sambaDomainName')
        if err or not len(res):
            msg.append('no \'sambaDomain\' found')
    else:
        msg.append('no object class \'sambaDomain\'')

    unix_users, err = ldapsearch(host, filt, 'dn')
    if err == 0x00:
        pass
    elif err == 0x04:
        ok = Report.FAIL
        msg.append('size limit exceeded, ' + str(len(unix_users)) + ' LDAP user(s) recognized')
    else:
        msg.append('failed to recognize LDAP user(s)')
        return False, {'messages': msg}

    samba_filt = filt
    if samba_filt[0] != '(':
        samba_filt = '(' + samba_filt + ')'
    samba_users, err = ldapsearch(host, '(&' + samba_filt + '(objectClass=sambaSamAccount))', 'dn', 'sambaNTPassword')
    if err == 0x00:
        pass
    elif err == 0x04:
        ok = Report.FAIL
        msg.append('size limit exceeded, ' + str(len(samba_users)) + ' Samba account(s) recognized')
    else:
        msg.append('failed to recognize Samba account(s)')
        return False, {'messages': msg}

    if len(unix_users) != len(samba_users):
        ok = Report.FAIL
        msg.append(str(len(unix_users)) + ' LDAP user(s) recognized but only ' + str(len(samba_users)) + ' Samba account(s)')

    flags = map(lambda x: 'sambaNTPassword' in x, samba_users)
    if (all(flags)):
        msg.append(str(len(samba_users)) + ' Samba account(s) recognized')
        return ok, {'messages': msg}

    msg.extend([
        str(len(samba_users)) + ' Samba account(s) recognized but ' + str(flags.count(False)) +
        ' without \'sambaNTPassword\', maybe bind DN \'' + host.binddn + '\' does NOT have sufficient privilege'
    ])
    return Report.FAIL, {'messages': msg}

# vim:ts=4 sts=4 sw=4 et
