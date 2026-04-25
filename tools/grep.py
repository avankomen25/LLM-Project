"""Tool definition and implementation for searching file contents with a regex."""

import re
import glob
from tools.utils import is_path_safe
import os


def grep(pattern, path):
    """
    Search for lines matching a regex pattern across files matching a glob path.

    >>> grep('groq', 'requirements.txt')
    'groq'
    >>> grep('zzz', 'requirements.txt')
    ''
    >>> grep('hello', '/etc/passwd')
    'Error: unsafe path'
    >>> grep('hello', 'llmdemo.gif')
    ''
    >>> grep('hello', '../secret')
    'Error: unsafe path'
    """
    if not is_path_safe(path):
        return 'Error: unsafe path'
    matches = []
    for filepath in glob.glob(path):
        if os.path.isdir(filepath):
            continue
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    if re.search(pattern, line):
                        matches.append(line.rstrip('\n'))
        except (UnicodeDecodeError, FileNotFoundError):
            continue
    return '\n'.join(matches)


tool_definition = {
    "type": "function",
    "function": {
        "name": "grep",
        "description": "Search for lines matching a regex in files matching a glob pattern.",
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "The regex pattern to search for.",
                },
                "path": {
                    "type": "string",
                    "description": "The file path or glob pattern to search in.",
                },
            },
            "required": ["pattern", "path"],
        },
    },
}
