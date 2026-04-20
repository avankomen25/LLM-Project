"""Tool definition and implementation for searching file contents with a regex."""

import re
import glob
from tools.utils import is_path_safe


def grep(pattern, path):
    """
    Search for lines matching a regex pattern across files matching a glob path.

    # don't create files
    >>> import os
    >>> with open('_test_grep.txt', 'w') as f:
    ...     _ = f.write('hello world\\nfoo bar\\nhello again')
    >>> grep('hello', '_test_grep.txt')
    'hello world\\nhello again'
    >>> grep('zzz', '_test_grep.txt')
    ''
    >>> grep('hello', '/etc/passwd')
    'Error: unsafe path'
    >>> os.remove('_test_grep.txt')
    >>> import os
    >>> with open('_test_binary.bin', 'wb') as f:
    ...     _ = f.write(bytes([0xff, 0xfe]))
    >>> grep('hello', '_test_binary.bin')
    ''
    >>> os.remove('_test_binary.bin')
    """
    if not is_path_safe(path):
        return 'Error: unsafe path'
    matches = []
    for filepath in glob.glob(path):
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
