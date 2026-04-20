"""Tool definition and implementation for reading file contents."""
import os
from tools.utils import is_path_safe


def cat(path):
    """
    Return the contents of a file as a string.

    # these are very ugly test cases;
    # you should actually just have a file somewhere that already exists in the repo
    # and cat that file;
    # in general, test cases should be "side effect free" which means
    # they shouldn't be creating new files on the filesystem
    >>> import os
    >>> with open('_test_cat.txt', 'w') as f:
    ...     _ = f.write('hello world')
    >>> cat('_test_cat.txt')
    'hello world'
    >>> cat('_nonexistent_file.txt')
    'Error: file not found'
    >>> cat('/etc/passwd')
    'Error: unsafe path'
    >>> os.remove('_test_cat.txt')
    >>> import os
    >>> with open('_test_binary.bin', 'wb') as f:
    ...     _ = f.write(bytes([0xff, 0xfe, 0x68, 0x00, 0x69, 0x00]))
    >>> cat('_test_binary.bin')
    'hi'
    >>> os.remove('_test_binary.bin')
    >>> with open('_test_bad.bin', 'wb') as f:
    ...     _ = f.write(bytes([0x80, 0x81, 0x82]))
    >>> cat('_test_bad.bin')
    'Error: cannot decode file'
    >>> os.remove('_test_bad.bin')
    >>> import os
    >>> os.makedirs('_test_dir', exist_ok=True)
    >>> cat('_test_dir')
    'Error: path is a directory, not a file'
    >>> os.rmdir('_test_dir')
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
