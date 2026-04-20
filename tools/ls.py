"""Tool definition and implementation for listing files in a directory."""
import os
import glob
from tools.utils import is_path_safe


def ls(path='.'):
    """List files in a directory, sorted asciibetically.

    # again, don't create files/folders in the test cases
    >>> import os, shutil
    >>> os.makedirs('_test_ls_dir', exist_ok=True)
    >>> ls('_test_ls_dir')
    ''
    >>> ls('/etc')
    'Error: unsafe path'
    >>> with open('_test_ls_dir/banana.txt', 'w') as f: _ = f.write('hi')
    >>> with open('_test_ls_dir/apple.txt', 'w') as f: _ = f.write('hi')
    >>> with open('_test_ls_dir/cherry.txt', 'w') as f: _ = f.write('hi')
    >>> ls('_test_ls_dir') == 'apple.txt\\nbanana.txt\\ncherry.txt'
    test cases should actually list the result
    >>> shutil.rmtree('_test_ls_dir')
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
