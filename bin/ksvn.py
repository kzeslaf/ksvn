#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
ksvn.py

Decorator for svn tools allowing for simultaneous operations on many working
copies.

Additional commands when inside working copy:
    - clear: remove all unversioned files

Commands outside working copy:
    - info
    - update
    - freeze
"""


import os
import re
import shutil
import sys

import pysvn
import termcolor


#######################
# Constats
#######################


RES_OK = 0
RES_ERROR = 1
RES_INVARG = 2


#######################
# Utils Functions
#######################


def get_relative_url(info):
    """..."""
    assert isinstance(info, pysvn.PysvnEntry)

    url = info.url
    url = '^' + url[len(info.repos):]

    return url


def get_unversioned_files(status):
    """Return list of unversioned and ignored files."""
    assert isinstance(status, list)
    if status:
        assert isinstance(status[0], pysvn.PysvnStatus)

    result = []
    sk = pysvn.wc_status_kind

    for i in status:
        if i.text_status in [sk.unversioned, sk.ignored]:
            result.append(os.path.abspath(i.path))

    return result


def list_working_copies(path):
    """..."""
    result = []

    exists = os.path.exists
    join = os.path.join

    for i in os.listdir(path):
        if exists(join(join(path, i), '.svn')):
            result.append(i)

    return result


def is_dirty(status):
    """..."""
    assert isinstance(status, list)
    if status:
        assert isinstance(status[0], pysvn.PysvnStatus)

    sk = pysvn.wc_status_kind
    ok_states = [sk.unversioned, sk.normal, sk.ignored]

    for i in status:
        if i.text_status not in ok_states:
            return True

    return False


def is_working_copy(path):
    """..."""
    abspath = os.path.abspath
    exists = os.path.exists
    join = os.path.join

    while path != '' and path != '/' and path[1:] != ":\\":
        if exists(join(path, '.svn')):
            return True
        path = abspath(join(path, '..'))
    return False


def remove(files):
    """..."""
    for i in files:
        if os.path.isdir(i):
            shutil.rmtree(i)
        else:
            os.remove(i)


########################
# Command Functions
########################


def svn_clear(paths, params):
    """Remove unversioned/ignored items in working copy.

    Function does not remove following files:
        - .idea
        - *.user

    Additional params:
        --all - remove all files (for example: *.user)
        --force - don't require user confirmation
    """
    param_all = '--all'
    param_force = '--force'

    client = pysvn.Client()

    for i in paths:
        files = get_unversioned_files(client.status(i))

        if param_all not in params:
            files = [v for v in files if not v.endswith('.user')]
            files = [v for v in files if not v.endswith('.idea')]

        if not files:
            continue

        for j in files:
            print j

        proceed = 'y' if param_force in params else raw_input(
            '--> Proceed [y/N]: ')

        if proceed in ['y', 'Y', 'yes']:
            remove(files)


def svn_freeze(paths, params):
    """..."""
    client = pysvn.Client()
    result = []

    for i in paths:
        info = client.info(i)
        result.append([i, info.url, info.revision])

    for i in sorted(result):
        print i


def svn_info(paths, params):
    """..."""
    colors = [
        ('branches', 'red'),
        ('trunk', 'cyan'),
        ('STABLE', 'green'),
    ]

    client = pysvn.Client()

    for i in paths:
        url = get_relative_url(client.info(i))
        for j in colors:
            url = url.replace(j[0], termcolor.colored(j[0], j[1]))
        print '[{}] {}'.format(i, url)

    return 0


def svn_status(paths, params):
    """..."""
    client = pysvn.Client()

    for i in paths:
        dirty = is_dirty(client.status(i))
        print '{} {}'.format(
            i, termcolor.colored('Dirty', 'red') if dirty else 'Clean'
        )

    return 0


def svn_switch(paths, params):
    """..."""
    try:
        from_ = params[0]
        to = params[1]
    except IndexError:
        print 'Invalid params for svn switch command: {}'.format(params)
        return RES_INVARG

    client = pysvn.Client()
    error = False

    for i in paths:
        url = get_relative_url(client.info(i))

        if url.startswith(from_):
            if is_dirty(client.status(i)):
                print '{} is Dirty, omitting ...'.format(i)

            res = os.system(
                '( echo Directory: [{0}]; cd {0}; svn switch {1} )'.format(
                    i, url.replace(from_, to)
                )
            )

            if res != 0:
                error = True

    if error:
        return RES_ERROR
    return RES_OK


def svn_switch_wc(paths, params):
    """..."""
    for key, val in enumerate(params):
        if re.match(r'\d+', val):
            params[key] = '^/branches/' + val
    return os.system('svn switch ' + ' '.join(params))


def svn_update(paths, params):
    """..."""
    for i in paths:
        res = os.system(
            '( echo Directory: [{0}]; cd {0}; svn update )'.format(i)
        )
        if res != 0:
            return res
    return 0


##########################
#
##########################


def main():
    """..."""
    cwd = os.getcwd()

    wc_functions = [
        (['clear'], svn_clear),
        (['switch'], svn_switch_wc),
    ]

    functions = [
        (['clear'], svn_clear),
        (['freeze'], svn_freeze),
        (['info'], svn_info),
        (['stat', 'status'], svn_status),
        (['up', 'update'], svn_update),
        (['switch'], svn_switch),
    ]

    if is_working_copy(cwd):
        for i in wc_functions:
            if sys.argv[1] in i[0]:
                return i[1]('.', sys.argv[2:])
        return os.system('svn ' + ' '.join(sys.argv[1:]))
    else:
        for i in functions:
            if sys.argv[1] in i[0]:
                return i[1](sorted(list_working_copies(cwd)), sys.argv[2:])

    print 'Unknown command: {}'.format(sys.argv[1:])
    return RES_INVARG


#######################
# Main
#######################


if __name__ == '__main__':
    sys.exit(main())
