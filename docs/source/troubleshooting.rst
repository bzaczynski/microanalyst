Troubleshooting
===============

1. When invoking a script on Linux there is a "``:No such file or directory``" error.

.. tip::
    This indicates that some Python source files contain non-Unix newline characters such as ``\r\n`` (Windows) or ``\r`` (Mac OS) instead of simply ``\n``. To identify the culprits use the included ``check_newline.py`` script and correct the issue with a text editor.

2. Error "``IOError: [Errno 9] Bad file descriptor``" or similar.

.. tip::
    Are you using a shell wrapper on Windows? Use the standard ``cmd.exe``.

3. Error "``The process tried to write to a nonexistent pipe``".

.. tip::
    This is a bug on some versions of Windows. You can safely ignore it.

