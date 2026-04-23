"""Tool definition and implementation for reading file contents."""
import os
from tools.utils import is_path_safe


def cat(path):
    """
    Return the contents of a file as a string.

    >>> print(cat('requirements.txt'))
    groq
    python-dotenv
    gitpython
    <BLANKLINE>
    >>> cat('_nonexistent_file.txt')
    'Error: file not found'
    >>> cat('/etc/passwd')
    'Error: unsafe path'
    >>> import os
    >>> os.makedirs('_test_dir', exist_ok=True)
    >>> cat('_test_dir')
    'Error: path is a directory, not a file'
    >>> os.rmdir('_test_dir')
    >>> cat('llmdemo.gif')
    'Error: cannot decode file'
    """
    if not is_path_safe(path):
        return 'Error: unsafe path'
    if os.path.isdir(path):
        return 'Error: path is a directory, not a file'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return 'Error: file not found'
    except UnicodeDecodeError:
        try:
            with open(path, 'r', encoding='utf-16') as f:
                return f.read()
        except Exception:
            return 'Error: cannot decode file'


tool_definition = {
    "type": "function",
    "function": {
        "name": "cat",
        "description": "Read and return the contents of a file.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The file to read.",
                }
            },
            "required": ["path"],
        },
    },
}
