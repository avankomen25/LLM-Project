import git
from tools.utils import is_path_safe
from tools.cat import cat  # noqa: F401


def write_files(files, commit_message):
    '''
    Write multiple files and commit them to git.

    >>> write_files({'path': 'test_files/test_write.txt', 'contents': 'hello'}, 'test')
    'Files written and committed: test_files/test_write.txt'
    >>> write_files([{'path': 'test_files/test_write.txt', 'contents': 'hello'}], 'test')
    'Files written and committed: test_files/test_write.txt'
    >>> write_files([{'path': '/etc/passwd', 'contents': 'bad'}], 'hack')
    'Error: unsafe path: /etc/passwd'
    >>> write_files([{'path': '../secret', 'contents': 'bad'}], 'hack')
    'Error: unsafe path: ../secret'
    '''
    if not isinstance(files, list):
        files = [files]
    written = []
    for f in files:
        path = f['path']
        contents = f['contents']
        if not is_path_safe(path):
            return f'Error: unsafe path: {path}'
        with open(path, 'w', encoding='utf-8') as fp:
            fp.write(contents)
        written.append(path)
    repo = git.Repo('.')
    repo.index.add(written)
    repo.index.commit(f'[docchat] {commit_message}')
    return f'Files written and committed: {", ".join(written)}'


tool_definition = {
    "type": "function",
    "function": {
        "name": "write_files",
        "description": "Write multiple files and commit them to git.",
        "parameters": {
            "type": "object",
            "properties": {
                "files": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "contents": {"type": "string"},
                        },
                        "required": ["path", "contents"],
                    },
                    "description": "List of files to write, each with a path and contents.",
                },
                "commit_message": {
                    "type": "string",
                    "description": "The git commit message.",
                },
            },
            "required": ["files", "commit_message"],
        },
    },
}
