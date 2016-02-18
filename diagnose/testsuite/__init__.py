#!/usr/bin/python2

'''
This module contains different test cases we can think of to exam compatibility
of Synology Disk Station against target LDAP server.

Each test case should be a function which is decorated by @report and exported
via __all__.

Simple cases are put in this __init__.py, complicated cases should be put in
separated .py files.
'''

from report import report, Report
from basic import recognize_users, recognize_groups, check_user_completeness
from samba import check_samba_support
from conflict import check_uid_conflicts, check_gid_conflicts


__all__ = [
    'print_settings',
    'required_object_classes',
    'recognize_users',
    'recognize_groups',
    'check_user_completeness',
    'check_samba_support',
    'check_uid_conflicts',
    'check_gid_conflicts',
]


@report('Check required object class(es)')
def required_object_classes(host, requires):
    flags = map(lambda x: host.object_class[x], requires)
    if all(flags):
        return Report.PASS, {}

    msg = []
    for cls in filter(lambda x: not x[1], zip(requires, flags)):
        msg.append('no object class \'' + cls[0] + '\'')
    return Report.FAIL, {'messages': msg}


@report('Diagnose settings')
def print_settings(host, mapping):
    return Report.PASS, {
        'messages': [
            'Server URI:    ' + host.uri,
            'Base DN:       ' + host.basedn,
            'Bind DN:       ' + (host.binddn or '(nil)'),
            'LDAP mapping:  ' + str(mapping),
        ]
    }

# vim:ts=4 sts=4 sw=4 et
