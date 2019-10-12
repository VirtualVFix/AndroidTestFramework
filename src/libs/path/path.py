# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "03/22/18 15:33"

import re
import os
import platform
from config import CONFIG


def get_script_name(file):
    """ return script name of __file__ """
    return os.path.basename(file)


def get_name(file):
    """ return script name of __file__ without .py """
    return os.path.splitext(get_script_name(file))[0]


def get_real_path(file):
    """ return real path of file """
    return os.path.dirname(os.path.realpath(file)) + os.sep


def get_parent_dir(file):
    """ get parent dir of file """
    return os.path.split(os.path.dirname(os.path.realpath(file)))[0] + os.sep


def find_path_by_regexp(default_dir, search_regexp, allow_environment_path=True) -> list:
    """
    Search regexp or path in default directory and directory by environment path.

    Args:
        default_dir (str): Default directory to search application
        search_regexp (str): Regex t search application by name
        allow_environment_path (bool): Allow to search application by system environment configured
            in **CONFIG.SYSTEM.ENVIRONMENT_VARIABLE**

    Returns:
        [list of find path] or [None]
    """
    path_list = []
    try:
        _search_regexp = search_regexp.rstrip(os.sep)
        match = re.compile(_search_regexp, re.I)
        # search in default folder
        if os.path.exists(default_dir):
            # add path if search_regexp is path
            if os.path.exists(os.path.join(default_dir, _search_regexp)):
                path_list.append(os.path.join(default_dir, _search_regexp))
            for x in os.listdir(default_dir):
                if re.search(match, x):
                    path_list.append(os.path.join(default_dir, x))
        # search by environment path
        if allow_environment_path and CONFIG.SYSTEM.ENVIRONMENT_VARIABLE in os.environ:
            for p in os.environ[CONFIG.SYSTEM.ENVIRONMENT_VARIABLE].split(
                    ';' if 'window' in platform.system().lower() else ':'):
                # expand path with "~"
                if p.startswith('~'):
                    _path = os.path.expanduser(p)
                else:
                    _path = p
                # add path if search_regexp is path
                if os.path.exists(os.path.join(_path, _search_regexp)):
                    path_list.append(os.path.join(_path, _search_regexp))
                if os.path.exists(_path):
                    for x in os.listdir(_path):
                        if re.search(match, x):
                            path_list.append(os.path.join(_path, x))
    except Exception:
        raise
    return path_list or [None]
