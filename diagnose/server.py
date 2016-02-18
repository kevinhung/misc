#!/usr/bin/python2

from simpleldap import Host, ldapsearch


def from_nslcd_conf():

    def read_bindpw(dummy):
        with open('/usr/syno/etc/private/ldap.secret', 'r') as f:
            return f.read().strip()

    keymap = {
        'uri': 'ldapuri',
        'base': 'basedn',
        'binddn': 'binddn',
        'bindpw': {
            'name': 'bindpw',
            'fn': read_bindpw
        },
        'ssl': {
            'name': 'starttls',
            'fn': lambda x: x == 'start_tls'
        }
    }

    res = {}
    with open('/usr/syno/etc/nslcd.conf', 'r') as f:
        for line in f.read().expandtabs(1).splitlines():
            idx = line.find(' ')
            if idx == -1:
                continue
            key, val = line[:idx], line[idx:].strip()
            try:
                res[keymap[key]] = val
            except TypeError:
                res[keymap[key]['name']] = keymap[key]['fn'](val)
            except KeyError:
                pass  # Ignore other keys.

    return res


def is_synology(host):
    if not isinstance(host, Host):
        raise TypeError('bad parameter')

    res, err = ldapsearch(host, '', 'dn', basedn='cn=synoconf,' + host.basedn, scope='base')
    return True if err == 0 and len(res) else False


def is_open_directory(host):
    if not isinstance(host, Host):
        raise TypeError('bad parameter')

    res, err = ldapsearch(host, '(&(objectClass=organizationalUnit)(ou=macosxodconfig))', 'dn')
    return True if err == 0 and len(res) else False


def is_openldap(host):
    if not isinstance(host, Host):
        raise TypeError('bad parameter')

    res, err = ldapsearch(host, '', 'dn', 'objectClass', basedn='', scope='base')
    return True if err == 0 and len(res) and 'OpenLDAProotDSE' in res[0]['objectClass'] else False


def is_ibm_domino(host):
    if not isinstance(host, Host):
        raise TypeError('bad parameter')

    res, err = ldapsearch(host, '(objectClass=dominoOrganization)', 'dn', basedn='')
    return True if err == 0 and len(res) else False


def __server_test():
    # host = Host('ldap://kevin414j', basedn='dc=kevin414j,dc=com')
    host = Host('ldap://10.13.21.172', basedn='dc=server,dc=local')
    # host = Host(
    #     'ldap://10.11.242.205',
    #     bindn='cn=admin,o=synology',
    #     bindpw='synology',
    #     basedn='o=synology')

    print 'Synology Directory Server: ' + str(is_synology(host))
    print 'Apple Open Directory:      ' + str(is_open_directory(host))
    print 'OpenLDAP:                  ' + str(is_openldap(host))
    print 'IBM Lotus Domino:          ' + str(is_ibm_domino(host))

    # print from_nslcd_conf()


if __name__ == '__main__':
    __server_test()

# vim:ts=4 sts=4 sw=4 et
