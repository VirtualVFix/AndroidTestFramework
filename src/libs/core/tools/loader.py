# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "17/10/17 20:46"

import os
import sys
from config import CONFIG
from libs.core.logger import getSysLogger


def load_module(loader_name, path):
    """
    Module loader. Load module by path and try load module via Framework encrypt importer.
    Load module with *importlib.machinery.SourceFileLoader* if Framework encrypt importer is not available.

    Args:
        loader_name (str): Name of loader
        path (str): Full path to module

    Returns:
        module
    """
    syslogger = getSysLogger()

    # check path and replace file extension if required
    if not os.path.exists(path):
        extensions = CONFIG.PROJECT_FILE_EXTENSIONS
        for x in extensions:
            if path.endswith(x):
                continue
            path = path[:path.rfind('.')] + x
            if os.path.exists(path):
                break

    # find encrypt loader
    loader = None
    for x in sys.meta_path:
        if hasattr(x, '__name__') and x.__name__ == CONFIG.PROJECT_ENCRYPT_IMPORTER:
            loader = x
            break

    # load module with encrypt loader
    if loader is not None:
        mod = loader.load_module(None, path=path)
        mod.__name__ = loader_name
        return mod

    syslogger.error('"%s" loader not found. Will be used "importlib.machinery" loader !'
                    % CONFIG.PROJECT_ENCRYPT_IMPORTER)

    # load module with importlib.machinery.SourceFileLoader
    import importlib.machinery
    loader = importlib.machinery.SourceFileLoader(loader_name, path)
    return loader.load_module()
