"""Tool definition and implementation for deleting files and committing the deletion to git."""

import os
import glob
import git
from tools.utils import is_path_safe


def rm(path):
    '''
    Delete files matching a glob pattern and commit the deletion to git.

    >>> from tools.write_file import write_file
    >>> _ = write_file('test_files/to_delete.txt', 'bye', 'add delete test file')
    >>> rm('test_files/to_delete.txt')
    'Deleted and committed: test_files/to_delete.txt'
    >>> import os
    >>> os.path.exists('test_files/to_delete.txt')
    False
    >>> rm('/etc/passwd')
    'Error: unsafe path'
    >>> rm('../secret')
    'Error: unsafe path'
    >>> rm('test_files/nonexistent_file.txt')
    'Error: no files found matching test_files/nonexistent_file.txt'
    '''
    if not is_path_safe(path):
        return 'Error: unsafe path'
    files = glob.glob(path)
    if not files:
        return f'Error: no files found matching {path}'
    deleted = []
    for f in files:
        os.remove(f)
        deleted.append(f)
    repo = git.Repo('.')
    repo.index.remove(deleted)
    repo.index.commit(f'[docchat] rm {path}')
    return f'Deleted and committed: {", ".join(deleted)}'


tool_definition = {
    "type": "function",
    "function": {
        "name": "rm",
        "description": "Delete files matching a glob pattern and commit the deletion to git.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The file path or glob pattern to delete.",
                }
            },
            "required": ["path"],
        },
    },
}
