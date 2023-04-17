
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from time import sleep

from rich.progress import track

OS_NAME = 'win32'
ARCH = platform.architecture()[0][:2]
# test_list = ['a', 'b', 'c']
# powershell = ['powershell', '-NoProfile'] if OS_NAME == 'win32' else ''
# new_list = [*powershell, *test_list]

# print(new_list)


def get_win_shell() -> tuple | str:
    for alias in ('pwsh', 'powershell'):
        path = shutil.which(alias)
        if path:
            # return (alias, '-NoProfile', '-Command')
            return (alias, '-NoProfile', '-Command', '"$null" |')
    else:
        return ''

# shells = ('pwsh', 'powershell', 'cmd')
# path = get_win_shell()

# if any(shell in path for shell in shells[0:2]):
#     print('Got it')
# def get_win_shell() -> str:
#     shells = ('pwsh', 'powershell', 'cmd')
#     count = 0
#     for shell in shells:
#         path = shutil.which(shell)
#         count += 1
#         if path in any(shells[0:2]):
#             return [path, '-NoProfile']
#         else:
#             return [path]

# def get_win_shell() -> str:
#     shells = ('pwshz', 'powershell', 'cmd')
#     for shell in shells:
#         path = shutil.which(shell)
#         if any(shell in path for shell in shells[0:2]):
#         # if any(path in shell for shell in shells[0:2]):
#             return [path, '-NoProfile']
#         else:
#             return [path]

win_shell_hook = get_win_shell() if OS_NAME == 'win32' else ''
# print(win_shell_hook)
# exit()
# assert win_shell_hook != None

# cmd_list = [
#     *win_shell_hook,
#     'py',
#     '-m',
#     'nuitka',
# ]
# print(get_win_shell())

# print(cmd_list)


def get_python_alias():
    for alias in ('py', 'python'):
        path = shutil.which(alias)
        if path:
            return alias
    else:
        raise FileNotFoundError('Can\'t find python path, exiting.')

# print(get_python_path())

# test_list = ['a', 'b', 'c']


# test_list.extend(('d', 'e'))

# print(test_list)


# print(test_func())

# test_parse()

# test_tuple = ('a', 'b', 'c')

# print(test_tuple[0:2])




# n = 0
# for n in range(20):
#     n += 1
#     sleep(0.5)
#     print(n)


# user_input = input('Enter anything:\n')

# if not user_input:
#     print('You have entered nothing')
# else:
#     print('You have entered:', user_input)

# for i in track(range(20)):
#     sleep(0.2)

cmd = [
    f'{get_python_alias()}',
    '-m',
    'nuitka'
]

cmd = [
    'py',
]

cmd = [
    'pwsh',
    '-NoProfile',
    '-Command',
    'py'
    # '&',
    # f'.{get_python_path()}',
    # '-m',
    # 'nuitka'
]

cmd = [
    'cmd'
    'py'
]

cmd = [
    *win_shell_hook,
    # 'py',
    f'{get_python_alias()}',
    '-m',
    # 'pip',
    # 'list'
    'nuitka'
]

cmd = [
    *win_shell_hook,
    # 'py',
    f'{get_python_alias()}',
    'test.py'
]

# check = subprocess.check_output(cmd, encoding='utf-8', timeout=3)
# print(check)


def run_nuitka(cmd: list) -> None:
    'Run nuitka build in subprocess and print output.'
    process = subprocess.Popen(cmd,
                            #    executable='pwsh',
                            #    executable='C:\\Program Files\\PowerShell\\7\\pwsh.EXE',
                               stdout=subprocess.PIPE,
                               bufsize=1,
                            #    shell=True,
                               text=True)
    while True:
        line = process.stdout.readline()
        if not line:
            break
        print(line.strip())

# print(get_win_shell())
# print(get_python_path())
run_nuitka(cmd)

# print(shutil.which('cmd'))

# Path.mkdir(Path('%localappdata%/Temp/dmitrymeshkoff/lj-dl-img/2023.03.27'))

# path = r'%localappdata%/Temp/dmitrymeshkoff/lj-dl-img/2023.03.27'

# print(path)

# path.mkdir(parents=True)