#!/usr/bin/python2

'''
LDAP mappings.

Known mappgins are record as .map files in this folder.
'''

import os
import sys
import json


__all__ = [
    'load_mapping_file',
    'from_nslcd_conf',
    'rfc_2307',
    'ibm_domino',
]


class Mapping(object):

    def __init__(self, **kwargs):
        passwd_attr = ['uid', 'uidNumber', 'gidNumber']
        shadow_attr = ['uid']
        group_attr = ['cn', 'gidNumber', 'memberUid', 'member']

        def interpret_as_s(v):
            if isinstance(v, str):
                return v
            raise TypeError('bad parameter')

        try:
            self.__object_class = kwargs['requires']
            if any(map(lambda x: not isinstance(x, str), self.__object_class)):
                raise TypeError('bad parameter')

            self.__name = interpret_as_s(kwargs['name'])

            self.__passwd_filter = interpret_as_s(kwargs['filters']['passwd'])
            self.__shadow_filter = interpret_as_s(kwargs['filters']['shadow'])
            self.__group_filter = interpret_as_s(kwargs['filters']['group'])
            if self.__passwd_filter == self.__shadow_filter:
                self.__user_filter = self.__passwd_filter
            else:
                self.__user_filter = '(&' + self.__passwd_filter + self.__shadow_filter + ')'

            self.__backends = kwargs['backends']
            if not all(map(lambda x: isinstance(self.__backends['passwd'][x], str), passwd_attr)):
                raise TypeError('bad parameter')
            if not all(map(lambda x: isinstance(self.__backends['shadow'][x], str), shadow_attr)):
                raise TypeError('bad parameter')
            if not all(map(lambda x: isinstance(self.__backends['group'][x], str), group_attr)):
                raise TypeError('bad parameter')

        except KeyError as e:
            raise TypeError('missing ' + str(e))

    @property
    def required_object_class(self):
        return self.__object_class

    @property
    def passwd_filter(self):
        return self.__passwd_filter

    @property
    def shadow_filter(self):
        return self.__shadow_filter

    @property
    def group_filter(self):
        return self.__group_filter

    @property
    def user_filter(self):
        return self.__user_filter

    @property
    def backends(self):
        return self.__backends

    def __str__(self):
        return self.__name


def __unicode2str(sth):
    if isinstance(sth, dict):
        return {__unicode2str(k): __unicode2str(v) for k, v in sth.iteritems()}
    if isinstance(sth, list):
        return [__unicode2str(x) for x in sth]
    if isinstance(sth, unicode):
        return sth.encode('utf-8')
    return sth


def from_nslcd_conf():

    def parse_filter(tokens):
        try:
            if tokens[1][0] == '(':
                return tokens[0], tokens[1]
            else:
                return tokens[0], '(' + tokens[1] + ')'
        except IndexError:
            raise ValueError('invalid filter')

    def parse_map(tokens):
        try:
            if tokens[2].startswith('HASH('):
                return tokens[0], tokens[1], tokens[2][5:-1]
            else:
                return tokens[0], tokens[1], tokens[2]
        except IndexError:
            raise ValueError('invalid map')

    is_custom = False
    fpath = (os.path.dirname(__file__) or '.') + '/rfc-2307.map'
    with open(fpath, 'r') as f:
        try:
            res = __unicode2str(json.load(f))
        except Exception as e:
            print >> sys.stderr, 'Error: Failed to parse \'' + fpath + '\', ' + str(e)
            raise

    with open('/usr/syno/etc/nslcd.conf', 'r') as f:
        for line in f.read().expandtabs(1).splitlines():
            idx = line.find(' ')
            if idx == -1:
                continue
            key, val = line[:idx], line[idx:].strip()
            if key == 'filter':
                k, v = parse_filter(val.split())
                res['filters'][k] = v
                is_custom = True
            elif key == 'map':
                b, k, v = parse_map(val.split())
                res['backends'][b][k] = v
                is_custom = True
            else:
                pass  # Ignore other lines.

    if is_custom:
        res['name'] = 'Custom'

    return Mapping(**res)


def load_mapping_file(fpath):

    if not isinstance(fpath, str):
        raise TypeError('bad parameter')

    with open(fpath, 'r') as f:
        try:
            return Mapping(**__unicode2str(json.load(f)))
        except Exception as e:
            print >> sys.stderr, 'Error: Failed to parse \'' + fpath + '\', ' + str(e)
            raise

    return None  # Should not reach here.


def __load_mapping(name):

    if not isinstance(name, str):
        raise TypeError('bad parameter')

    folder = os.path.dirname(__file__) or '.'
    return load_mapping_file(folder + '/' + name + '.map')


def rfc_2307():
    return __load_mapping('rfc-2307')


def ibm_domino():
    return __load_mapping('ibm-domino')


def __mapping_test():
    m = rfc_2307()
    print m
    print m.required_object_class
    print m.user_filter
    print m.group_filter
    print m.backends


if __name__ == '__main__':
    __mapping_test()

# vim:ts=4 sts=4 sw=4 et
