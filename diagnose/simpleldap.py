#!/usr/bin/python2

'''
Wrap ldapsearch command for ease of programming.
See __simpleldap_test for example, log.simpleldap for executed commands.
'''


import logging
from cidict import CIDict


# ldapserach command, specify absolute path to denote what to use.
__ldapsearch = 'ldapsearch'

if __ldapsearch[0] != '/':
    from subprocess import Popen, PIPE

    with open('/dev/null', 'w') as null_f:
        pipe = Popen('which ldapsearch', stdout=PIPE, stderr=null_f, shell=True)
        res = pipe.communicate()[0].splitlines()
        if pipe.returncode or len(res) == 0:
            raise RuntimeError('failed to locate ldapsearch command')
        __ldapsearch = res[0]

DEBUG_LOG_FILE = '/tmp/log.' + __name__
logging.basicConfig(
    level=logging.DEBUG,
    format='%(message)s',
    filename=DEBUG_LOG_FILE,
    filemode='w')
__logger = logging.getLogger(__name__)


def debug_logger(fn):
    from functools import wraps

    @wraps(fn)
    def inner(*args, **kwargs):
        import re
        ret = fn(*args, **kwargs)
        if isinstance(ret, str):  # Is ldapsearch command.
            __logger.debug(re.sub(r' -w \'.*\' ', ' -w \'****\' ', ret))
        else:
            __logger.debug(ret)
        return ret
    return inner


def ldaperror(code):
    tbl = {
        0x01: 'Operations error',
        0x02: 'Protocol error',
        0x03: 'Time limit exceeded',
        0x04: 'Size limit exceeded',
        0x07: 'Authentication method not supported',
        0x08: 'Strong(er) authentication required',
        0x0D: 'Confidentiality required (not using SSL/TLS or STARTTLS?)',
        0x10: 'No such attribute',
        0x11: 'Undefined attribute type',
        0x20: 'No such object',
        0x30: 'Inappropriate authentication (anonymous bind is disallowed?)',
        0x31: 'Invalid credentials',
        0x32: 'Insufficient access',
        0x33: 'Server is busy',
        0x34: 'Server is unavailable',
        0x35: 'Server is unwilling to perform (bind password is given?)',
        0xFE: 'Connect error (254)',
        0xFF: 'Connect error (255)',
    }

    if not isinstance(code, int):
        raise TypeError('bad parameter')

    try:
        return tbl[code]
    except KeyError:
        return 'Unknown error (' + str(code) + ')'


def interpret_as(v, t):
    '''
    Interpret v as type t and raise TypeError when failure.
    '''

    if isinstance(v, t):
        return v
    raise TypeError('bad parameter')


class Host(object):
    ''''
    LDAP host.
    '''

    def __init__(self, uri, **kwargs):
        from urlparse import urlparse

        self.__object_class = CIDict()

        portmap = {'ldap': 389, 'ldaps': 636}
        self.__uri = interpret_as(uri, str)
        r = urlparse(self.__uri)
        if r.netloc[0] == '[':  # IPv6.
            idx = r.netloc.rfind(']')
            idx = r.netloc.find(':', idx)
        else:
            idx = r.netloc.rfind(':')
        if idx != -1:
            if idx + 1 == len(r.netloc):
                raise ValueError('invalid LDAP uri \'' + self.__uri + '\'')
            if int(r.netloc[idx + 1:]) != portmap[r.scheme]:
                raise ValueError('not standard port of ' + r.scheme + '://, it should be ' + str(portmap[r.scheme]))

        self.__starttls = interpret_as(kwargs['starttls'], bool) if 'starttls' in kwargs else False
        self.__binddn = interpret_as(kwargs['binddn'], str).lower() if 'binddn' in kwargs else ''
        self.__bindpw = interpret_as(kwargs['bindpw'], str) if 'bindpw' in kwargs else ''

        self.basedn = kwargs['basedn'] if 'basedn' in kwargs else ''

    @property
    def uri(self):
        return self.__uri

    @property
    def starttls(self):
        return self.__starttls

    @property
    def binddn(self):
        return self.__binddn

    @property
    def bindpw(self):
        return self.__bindpw

    @property
    def basedn(self):
        return self.__basedn

    @basedn.setter
    def basedn(self, val):
        self.__basedn = interpret_as(val, str).lower()

    @property
    def object_class(self):
        if not self.__object_class:
            self.__object_class = detect_object_class(self)
        return self.__object_class


@debug_logger
def __build_search_command(host, filt, *args, **kwargs):
    '''
    Build ldapsearch command.
    '''

    def decorate_arg(val):
        return '\'' + val + '\''

    def build_option(opt, val):
        return ' ' + opt + ' ' + decorate_arg(val)

    if not isinstance(filt, str):
        raise TypeError('bad parameter')
    if not all(map(lambda x: isinstance(x, str), args)):
        raise TypeError('bad parameter')

    cmd = __ldapsearch
    cmd += ' -o ldif-wrap=no'
    cmd += ' -Z -LLLx' if host.starttls else ' -LLLx'
    cmd += build_option('-H', host.uri)

    basedn = interpret_as(kwargs['basedn'], str) if 'basedn' in kwargs else host.basedn
    cmd += build_option('-b', basedn)

    if host.binddn:
        cmd += build_option('-D', host.binddn)
        cmd += build_option('-w', host.bindpw)

    scope = interpret_as(kwargs['scope'], str) if 'scope' in kwargs else 'sub'
    if scope in ['base', 'one', 'sub', 'children']:
        cmd += build_option('-s', scope)
    else:
        raise ValueError('invalid scope \'' + scope + '\'')

    cmd += ' ' + decorate_arg(filt)
    return cmd + ' ' + ' '.join(map(lambda x: decorate_arg(x), args))


def __parse_search_result(lines):
    '''
    Parse ldapsearch response lines then return result CIDict.
    '''

    key, val, obj, res = '', '', CIDict(), []

    if not lines:
        return res

    for line in lines:
        if line:
            idx = line.find(':')
            key = line[0:idx]
            try:
                if line[idx + 1] == ':':
                    val = line[idx + 2:].strip().decode('base64')
                else:
                    val = line[idx + 1:].strip()
            except IndexError:  # DN of RootDSE is empty.
                val = ''
            if key in obj:
                if key.lower() == 'dn':
                    raise RuntimeError('multiple DN for an entry')
                obj[key].append(val)
            else:
                obj[key] = val if key.lower() == 'dn' else [val]
        else:
            res.append(obj)
            obj = {}

    return res


@debug_logger
def ldapsearch(host, filt, *args, **kwargs):
    '''
    Run ldapsearch command and get result as list of LDAP entries (each is a CIDict).
    For example (only 'dn' is string, others are list of string),

        [{
            'dn': 'uid=johnsmith,cn=users,dc=synology.dc=io',
            'objectClass': ['posixAccount', 'shadowAccount', 'sambaSamAccount'],
            '...': ['...', ...]
        }, ...]

    Parameters:
        host - host handle.
        filt - LDAP filter, default ''.
        args - LDAP attribute list.
        kwargs - accept 'basedn' (overrides host.basedn) and 'scope' (default 'sub').

    Return:
        result - result list, each element is an LDAP entry.
        err_code - LDAP error code.
    '''

    from subprocess import Popen, PIPE

    if not isinstance(host, Host):
        raise TypeError('bad parameter')

    cmd = __build_search_command(host, filt, *args, **kwargs)

    with open('/dev/null', 'w') as null_f:
        pipe = Popen(cmd, stdout=PIPE, stderr=null_f, shell=True)
        result = __parse_search_result(pipe.communicate()[0].splitlines())
        return result, pipe.returncode

    return [], -1  # Should not reach here.


def detect_object_class(host):
    targets = [
        'posixAccount',
        'shadowAccount',
        'posixGroup',
        'sambaDomain',
        'sambaSamAccount',
        'sambaGroupMapping',
        'apple-user',
        'apple-group',
        'groupOfNames',
        'groupOfUniqueNames',
        'dominoPerson',
        'dominoGroup',
        'dominoOrganization',
    ]
    cls = CIDict.fromkeys(targets, False)

    try:
        res, _ = ldapsearch(host, '', 'subschemaSubentry', scope='base')
        res, _ = ldapsearch(host, '', 'objectClasses', basedn=res[0]['subschemasubentry'][0], scope='base')
    except:
        raise RuntimeError('failed to get schema from server')

    for name in targets:
        for line in res[0]['objectClasses']:
            if line.find('\'' + name + '\'') > 0:
                cls[name] = True
                break
    return cls


def __simpleldap_test():
    host = Host(
        'ldap://kevin414j',
        basedn='dc=kevin414j,dc=com',
        binddn='uid=root,cn=users,dc=kevin414j,dc=com',
        bindpw='q',
        starttls=False)

    print 'uri:       ' + host.uri
    print 'basedn:    ' + host.basedn
    print 'binddn:    ' + host.binddn
    print 'bindpw:    ' + host.bindpw
    print 'starttls:  ' + str(host.starttls)

    res, err = ldapsearch(host, '(objectClass=posixAccount)', 'dn', 'uid')

    print 'exit code: ' + str(err)
    print 'response:  ' + str(res)


if __name__ == '__main__':
    __simpleldap_test()

# vim:ts=4 sts=4 sw=4 et
