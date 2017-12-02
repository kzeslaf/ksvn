#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
ksvn.py - decorator for svn tools allowing for simultaneous
operations on many working copies.

Additional commands when inside working copy:
    - clear: remove all unversioned files

Commands outside working copy:
    - info
    - update
    - freeze

TODO:
    - make the script work for python3
    - better output
    - 'clear' asks user for confirmation
    - dodać polecenie 'stat'
"""

import os
import re
import shutil
import sys
import traceback

# TODO: ...
import pysvn

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../third-party/termcolor"))
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
    if status: assert isinstance(status[0], pysvn.PysvnStatus)

    result = []
    sk = pysvn.wc_status_kind

    for i in status:
        if i.text_status in [sk.unversioned, sk.ignored]:
            result.append(os.path.abspath(i.path))

    return result


def list_working_copies(path):
    """..."""
    result = []

    for i in os.listdir(path):
        p = os.path.join(path, i)
        p = os.path.join(p, '.svn')

        if os.path.exists(p):
            result.append(i)

    return result


def is_dirty(status):
    """..."""
    assert isinstance(status, list)
    if status: assert isinstance(status[0], pysvn.PysvnStatus)

    sk = pysvn.wc_status_kind
    ok_states = [sk.unversioned, sk.normal, sk.ignored]

    for i in status:
        if i.text_status not in ok_states:
            return True

    return False


def is_working_copy(path):
    """..."""
    while path != '' and path != '/' and path[1:] != ":\\":
        if os.path.exists(os.path.join(path, '.svn')):
            return True
        path = os.path.abspath(os.path.join(path, '..'))
    return False


def remove(files):
    """..."""
    for f in files:
        if os.path.isdir(f):
            shutil.rmtree(f)
        else:
            os.remove(f)


########################
# Command Functions
########################


def svn_clear(path_list, params):
    """Remove unversioned/ignored items in working copy.

    Function does not remove following files:
        - .idea
        - *.user

    Additional params:
        --all - remove all files (for example: *.user)
        --force - don't require user confirmation
    """
    PARAM_ALL = '--all'
    PARAM_FORCE = '--force'

    client = pysvn.Client()

    for i in path_list:
        files = get_unversioned_files(client.status(i))

        if PARAM_ALL not in params:
            files = [v for v in files if not v.endswith('.user')]
            files = [v for v in files if not v.endswith('.idea')]

        if not files:
            continue

        for f in files:
            print(f)

        proceed = 'y' if PARAM_FORCE in params else raw_input('--> Proceed [y/N]: ')

        if proceed in ['y', 'Y', 'yes']:
            remove(files)


def svn_freeze(path_list, params):
    """..."""
    client = pysvn.Client()
    result = []

    for i in path_list:
        info = client.info(i)
        result.append([i, info.url, info.revision])

    for i in sorted(result):
        print(i)


def svn_info(path_list, params):
    """..."""
    client = pysvn.Client()

    for i in path_list:
        url = get_relative_url(client.info(i))

        url = url.replace('branches', termcolor.colored('branches', 'red'))
        url = url.replace('trunk', termcolor.colored('trunk', 'cyan'))
        url = url.replace('STABLE', termcolor.colored('STABLE', 'green'))

        print('[{}] {}'.format(i, url))

    return 0


def svn_status(path_list, params):
    """..."""
    client = pysvn.Client()

    for i in path_list:
        dirty = False
        status = client.status(i)

        for j in status:
            if is_dirty(status):
                dirty = True
                break

        print('{} {}'.format(i, termcolor.colored('Dirty', 'red') if dirty else 'Clean'))

    return 0


def svn_switch(path_list, params):
    """..."""
    try:
        from_ = params[0]
        to = params[1]
    except:
        return RES_INVARG

    client = pysvn.Client()
    error = False

    for i in path_list:
        url = get_relative_url(client.info(i))
        if url.startswith(from_):
            if is_dirty(client.status(i)):
                print('{} is Dirty, omitting ...'.format(i))

            res = os.system('( echo Directory: [{0}]; cd {0}; svn switch {1} )'.format(i, url.replace(from_, to)))
            if res != 0:
                error = True

    if error:
        return RES_ERROR
    return RES_OK


def svn_switch_wc(path_list, params):
    """..."""
    for i, v in enumerate(params):
        if re.match(r'\d+', v):
            params[i] = '^/branches/feature/' + v

    return os.system('svn switch ' + ' '.join(params))


def svn_update(path_list, params):
    """..."""
    for i in path_list:
        res = os.system('( echo Directory: [{0}]; cd {0}; svn update )'.format(i))
        if res != 0:
            return res
    return 0


##########################
#
##########################


def main():
    """..."""
    cwd = os.getcwd()

    #
    #
    #
    wc_functions = [
        (['clear'], svn_clear),
        (['switch'], svn_switch_wc),
    ]

    #
    #
    #
    functions = [
        (['clear'], svn_clear),
        (['freeze'], svn_freeze),
        (['info'], svn_info),
        (['stat', 'status'], svn_status),
        (['up', 'update'], svn_update),
        (['switch'], svn_switch),
    ]

    #
    #
    #
    if is_working_copy(cwd):

        for i in wc_functions:
            if sys.argv[1] in i[0]:
                return i[1]('.', sys.argv[2:])

        return os.system('svn ' + ' '.join(sys.argv[1:]))

    #
    #
    #
    wc_list = sorted(list_working_copies(cwd))

    for i in functions:
        if sys.argv[1] in i[0]:
            return i[1](wc_list, sys.argv[2:])

    raise Exception('Unknown command: {}'.format(sys.argv[1:]))


#######################
# Main
#######################


if __name__ == '__main__':
    try:
        res = main()
    except Exception as e:
        print(e)
        traceback.print_exc()
        sys.exit(RES_ERROR)

    if res != RES_OK:
        sys.exit(res)
