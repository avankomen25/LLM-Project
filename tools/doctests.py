"""Tool definition and implementation for running doctests on a file."""

import subprocess
from tools.utils import is_path_safe


def doctests(path):
    '''
    Run doctests on a file and return the output.

    >>> result = doctests('tools/utils.py')
    >>> 'ok' in result or 'passed' in result or 'items' in result
    True

    Does not support absolute paths or directory traversal.
    >>> doctests('/etc/passwd')
    'Error: unsafe path'
    >>> doctests('../secret')
    'Error: unsafe path'
    '''
    if not is_path_safe(path):
        return 'Error: unsafe path'
    result = subprocess.run(
        ['python3', '-m', 'pytest', '--doctest-modules', '-v', path],
        capture_output=True,
        text=True,
    )
    return result.stdout + result.stderr


tool_definition = {
    "type": "function",
    "function": {
        "name": "doctests",
        "description": "Run doctests on a file and return the output.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the Python file to run doctests on.",
                }
            },
            "required": ["path"],
        },
    },
}
