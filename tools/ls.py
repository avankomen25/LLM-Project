"""Tool definition and implementation for listing files in a directory."""
import os
import glob
from tools.utils import is_path_safe


def ls(path='.'):
    """List files in a directory, sorted asciibetically.

    >>> ls('/etc')
    'Error: unsafe path'
    >>> ls('.github')
    'workflows'
    >>> print(ls('tools'))
    __init__.py
    __pycache__
    calculate.py
    cat.py
    doctests.py
    grep.py
    ls.py
    rm.py
    utils.py
    write_file.py
    write_files.py
    """
    if not is_path_safe(path):
        return 'Error: unsafe path'
    files = sorted(glob.glob(f'{path}/*'))
    return '\n'.join(os.path.basename(f) for f in files)


tool_definition = {
    "type": "function",
    "function": {
        "name": "ls",
        "description": "List files in a directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The directory to list. Defaults to current directory.",
                }
            },
            "required": [],
        },
    },
}
