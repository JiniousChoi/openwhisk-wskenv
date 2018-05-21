#!/usr/local/bin/python3

import re
import os
import argparse
from pathlib import Path
from shutil import copyfile, rmtree

HOME_DIR = os.path.expanduser('~')
MAIN_WSKPROP = os.path.join(HOME_DIR, '.wskprops')
WSKENVS_DIR = os.path.join(HOME_DIR, '.wskenvs')
SELECTED_WSKENV = os.path.join(HOME_DIR, '.wskenvs', '.selected')


def main():
    args = parseArgs()
    if not args.cmd:
        print("usage: wskenvs.py -h")
        return 1

    return {
        'create': cmd_create,
        'remove': cmd_remove,
        'activate': cmd_activate,
        'list': cmd_list,
        'show': cmd_show,
        'cd': cmd_cd
    }[args.cmd](args)


###### parsers ######


def parseArgs():
    usage = "usage: %prog [options] arg1 arg2"
    parser = argparse.ArgumentParser(\
             description='a CLI-based tool for managing multiple `.wskprops` of wsk command')
    subparsers = parser.add_subparsers(title='available commands', dest='cmd')
    addCreateParser(subparsers)
    addRemoveParser(subparsers)
    addActivateParser(subparsers)
    addListParser(subparsers)
    addShowParser(subparsers)
    addCdParser(subparsers)
    return parser.parse_args()


def addCreateParser(subparsers):
    cmd = subparsers.add_parser('create', help='create an wsk-environment')
    cmd.add_argument('wskenv', help='alias for the environment')
    cmd.add_argument('api_host', help='url or ip address')
    cmd.add_argument('auth', help='in form of `uuid:key`')


def addRemoveParser(subparsers):
    cmd = subparsers.add_parser('remove', help='remove an wsk-environment')
    cmd.add_argument('wskenv', help='.wskprop name to activate')


def addActivateParser(subparsers):
    cmd = subparsers.add_parser('activate', help='activate an wsk-environment')
    cmd.add_argument('wskenv', help='.wskprop name to activate')


def addListParser(subparsers):
    cmd = subparsers.add_parser('list', help='list all the wsk-environment\'s')


def addShowParser(subparsers):
    cmd = subparsers.add_parser(
        'show', help='show current wsk environment properties')


def addCdParser(subparsers):
    cmd = subparsers.add_parser(
        'cd', help='when you wish to get into wskenvs directory')


###### commands ######


def cmd_create(args):
    wskenv, api_host, auth = args.wskenv, args.api_host, args.auth
    wskenv_path = get_wskenv_path(wskenv)
    if Path(wskenv_path).exists():
        print('[ERR]', 'Exists Already')
        return 1
    if not is_valid_url(api_host):
        print('[ERR]', 'api_host `{}` is invalid'.format(api_host))
        return 1
    if not is_valid_auth(auth):
        print('[ERR]', 'auth `{}` is invalid'.format(auth))
        return 1

    mkdir_if_not_exist(WSKENVS_DIR)
    mkdir_if_not_exist(wskenv_path)
    create_wskprops(wskenv_path, api_host, auth)
    update_selected_wskenv(wskenv)
    print('[OK]', '{} is created'.format(wskenv))

    cmd_activate(args)
    return 0


def cmd_remove(args):
    wskenv = args.wskenv
    wskenv_path = get_wskenv_path(wskenv)
    if not Path(wskenv_path).exists():
        print('[ERR]', '{} does NOT exists'.format(wskenv))
        return 1
    rmtree(wskenv_path)
    print('[OK]', '{} is removed'.format(wskenv))
    return 0


def cmd_activate(args):
    wskenv = args.wskenv
    wskenv_path = get_wskenv_path(wskenv)
    wskenv_prop_path = get_wskenv_prop_path(wskenv)

    if not Path(wskenv_path).exists():
        print('[ERR]', '{} does NOT exists'.format(wskenv))
        return 1
    if not Path(wskenv_prop_path).exists():
        print('[ERR]', '{} does NOT exists'.format(wskenv_prop_path))
        return 1
    copyfile(wskenv_prop_path, MAIN_WSKPROP)
    update_selected_wskenv(wskenv)
    print('[OK]', '{} is activated'.format(wskenv))
    return 0


def cmd_list(args):
    wskenvs = Path(WSKENVS_DIR)
    if not wskenvs.is_dir():
        print('[ERR]', 'It is empty')
        return 1
    selected = get_selected_wskenv()
    for prop in Path(WSKENVS_DIR).iterdir():
        if '.selected' in prop.as_posix():
            continue
        env = prop.as_posix().rsplit('/')[-1]
        if env == selected:
            print('\033[92m{} (selected)\033[0m'.format(env))
        else:
            print(env)
    return 0


def cmd_show(args):
    selected = get_selected_wskenv()
    if selected != '':
        print('# {} #'.format(selected))
    wskprop = Path(MAIN_WSKPROP)
    if not wskprop.is_file():
        print('[ERR]', '`~/.wskprops` does NOT exist')
        return 1
    with open(wskprop) as fp:
        auth, api_host = fp.read().split()
        print('[API_HOST]', api_host.lstrip('APIHOST='))
        print('[AUTH]', auth.lstrip('AUTH='))
    return 0


def cmd_cd(args):
    wskenvs = Path(WSKENVS_DIR)
    if not wskenvs.is_dir():
        print('[ERR]', '`~/.wskenvs` directory does NOT exist')
        return 1
    print('cd', WSKENVS_DIR)
    return 0


###### helper methods ######


def is_valid_url(url):
    ''' @reference https://stackoverflow.com/a/7160778 '''
    regex = re.compile(
        r'^((?:http|ftp)s?://)?'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  #domain...
        r'localhost|'  #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$',
        re.IGNORECASE)
    return re.match(regex, url)


def is_valid_auth(auth):
    ''' reference https://bukkit.org/threads/best-way-to-check-if-a-string-is-a-uuid.258625/ '''
    if auth.count(':') != 1:
        return False
    uuid, key = auth.split(':')
    uuid_regex = re.compile(r'[0-9a-f]{8}-'
                            r'[0-9a-f]{4}-'
                            r'[1-5][0-9a-f]{3}-'
                            r'[89ab][0-9a-f]{3}-'
                            r'[0-9a-f]{12}')
    return re.match(uuid_regex, uuid) and len(key) == 64


def create_wskprops(wskenv, api_host, auth):
    wskprop_path = get_wskenv_prop_path(wskenv)
    with open(wskprop_path, 'w') as fp:
        fp.write('AUTH={}'.format(auth))
        fp.write(os.linesep)
        fp.write('APIHOST={}'.format(api_host))
        fp.write(os.linesep)


def mkdir_if_not_exist(dirname):
    if Path(dirname).exists():
        return
    os.mkdir(dirname)


def get_wskenv_path(wskenv):
    return os.path.join(WSKENVS_DIR, wskenv)


def get_wskenv_prop_path(wskenv):
    return os.path.join(WSKENVS_DIR, wskenv, '.wskprops')


def update_selected_wskenv(wskenv):
    with open(SELECTED_WSKENV, 'w') as out:
        out.write(wskenv + '\n')


def get_selected_wskenv():
    selected = Path(SELECTED_WSKENV)
    if selected.is_file():
        with open(selected) as fp:
            return fp.read().strip()
    else:
        return ''


if __name__ == "__main__":
    main()
