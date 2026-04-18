"""Utility functions shared across tools to block access to all files."""


def is_path_safe(path):
    """
    Return True if the path is safe to read (no absolute paths or directory traversal).

    >>> is_path_safe('README.md')
    True
    >>> is_path_safe('/etc/passwd')
    False
    >>> is_path_safe('../secret.txt')
    False
    >>> is_path_safe('subdir/../file.txt')
    False
    """
    if path.startswith('/'):
        return False
    if '..' in path.split('/'):
        return False
    return True
