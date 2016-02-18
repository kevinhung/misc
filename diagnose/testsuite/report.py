#!/usr/bin/python2

'''
Decorators for each test case.

Parameters:
    title - title of this test case.
    kwargs - extensions which denote output format.

Return of fn:
    ok - True or False.
    data - detailed info (as dictionary) about test result. It contains:
        'messages': [<string>, ...],
'''


class Report:
    PASS, FAIL, WARN = range(3)


def __console_output(title, **kwargs):
    def outter(fn):
        from functools import wraps

        @wraps(fn)
        def inner(*args, **kwargs):
            tmap = {
                Report.PASS: {'color': 32, 'text': 'PASS'},
                Report.FAIL: {'color': 31, 'text': 'FAIL'},
                Report.WARN: {'color': 33, 'text': 'WARN'},
            }

            def get_color(v):
                return str(tmap[v]['color'])

            def get_text(v):
                return tmap[v]['text']

            print '{:46s} ......'.format(title),
            ok, info = fn(*args, **kwargs)
            try:
                print '[\033[' + get_color(ok) + 'm' + get_text(ok) + '\033[0m]'
            except KeyError:
                print '[UND]'
            try:
                for msg in info['messages']:
                    if isinstance(msg, str):
                        print '    >>> ' + msg
                    else:
                        raise TypeError('bad parameter')
            except KeyError:
                pass
            return ok, info
        return inner
    return outter


report = __console_output

# vim:ts=4 sts=4 sw=4 et
