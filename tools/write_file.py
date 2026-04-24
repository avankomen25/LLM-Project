"""Tool definition and implementation for writing a single file and committing it to git."""

from tools.write_files import write_files
from tools.cat import cat  # noqa: F401


def write_file(path, contents, commit_message):
    '''
    Write a single file and commit it to git.

    >>> write_file('test_files/test_write.txt', 'hello again', 'test single write')
    'Files written and committed: test_files/test_write.txt'
    >>> from tools.cat import cat
    >>> cat('test_files/test_write.txt')
    'hello again'
    >>> write_file('test_files/test_write.txt', 'goodbye world', 'update test file')
    'Files written and committed: test_files/test_write.txt'
    >>> cat('test_files/test_write.txt')
    'goodbye world'
    >>> write_file('/etc/passwd', 'bad', 'hack')
    'Error: unsafe path: /etc/passwd'
    '''
    return write_files([{'path': path, 'contents': contents}], commit_message)


tool_definition = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Write contents to a single file and commit it to git.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The file path to write to.",
                },
                "contents": {
                    "type": "string",
                    "description": "The contents to write to the file.",
                },
                "commit_message": {
                    "type": "string",
                    "description": "The git commit message.",
                },
            },
            "required": ["path", "contents", "commit_message"],
        },
    },
}
