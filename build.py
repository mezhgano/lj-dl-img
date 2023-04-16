import platform
import shutil
import subprocess
import sys
from pathlib import Path

from constants import VERSION

OS_NAME, MACHINE, ARCH = sys.platform, platform.machine().lower(), platform.architecture()[0][:2]
if MACHINE in ('x86', 'x86_64', 'amd64', 'i386', 'i686'):
    MACHINE = 'x86' if ARCH == '32' else ''

icon_option = {
    'win32': '--windows-icon-from-ico',
    'darwin': '--macos-app-icon',
    'linux': '--linux-icon'
}

icon_option = {
    'win32': {
        'cmd': '--windows-icon-from-ico',
        'path': 'assets/lj_icon_test.ico'
        },
    'darwin': {
        'cmd': '--macos-app-icon',
        'path': 'assets/lj_icon_test.ico'
        },
    'linux': {
        'cmd': '--linux-icon',
        'path': 'assets/Artboard 1.png'
        }
}


def main() -> None:
    'Build full command list and run build process.'
    opts = sys.argv[1:]

    standalone = '--standalone' in opts
    name, path = get_dist_path(standalone)

    if not standalone and '--onefile' not in opts:
        opts.extend(('--onefile', f'--output-filename={name}'))

    powershell_hook = get_powershell_alias() if OS_NAME == 'win32' else ''

    cache_dir = get_cache_dir()

    print(f"Building lj-dl-img v{VERSION} for {OS_NAME}{'_'.join((MACHINE,))} with options:\n{opts}\n")
    print(f'Build destination:\n{path}\n')

    cmd = [
        *powershell_hook,
        f'{get_python_alias()}',
        '-m',
        'nuitka',
        f'--onefile-tempdir-spec={cache_dir}',
        f'{icon_option[OS_NAME]}={Path("assets/icon_final.svg")}',
        f'--company-name=https://github.com/mezhgano/lj-dl-img',
        f'--product-version={VERSION}',
        '--file-description=Download Livejournal photo albums',
        '--copyright="dmitrymeshkoff@gmail.com | UNLICENSE"',
        #Automatically download external code, otherwise it will not possible to complete subprocess run
        '--assume-yes-for-downloads',
        f'--output-dir={path}',
        *opts,
        'lj_dl_img.py'
        #Redirect input from null to disable prompt asking to download anything
        # '<NUL:'
    ]

    print(f'Running Nuitka with options:\n{cmd}\n')
    # run_nuitka(cmd)


def get_cache_dir() -> Path:
    'Change default cache directory on Windows, return cache Path object.'
    if OS_NAME == 'win32':
        top_dir = '%localappdata%/Temp'
    else:
        top_dir = '%CACHE_DIR%'
    path = Path(f'{top_dir}/dmitrymeshkoff/lj-dl-img/{VERSION}')

    return path


def get_dist_path(standalone: bool) -> tuple:
    'Return tuple with executable name and relative path.'
    name = '_'.join(filter(None, ('lj-dl-img', {'win32': '', 'darwin': 'macos'}.get(OS_NAME, OS_NAME), MACHINE)))
    path = Path(f'dist/{name}')
    name = ''.join(filter(None, (name, OS_NAME == 'win32' and '.exe')))

    return name, path


def get_powershell_alias() -> tuple | str:
    'Return Powershell alias if found in system path.'
    for alias in ('pwsh', 'powershell'):
        path = shutil.which(alias)
        if path:
            return (alias, '-NoProfile', '-Command')
    else:
        # if powershell not found in path pass empty string
        # and let subprocess run cmd.exe
        return ''

def get_python_alias() -> str:
    'Return python alias if found in system path.'
    for alias in ('py', 'python'):
        path = shutil.which(alias)
        if path:
            return alias
    else:
        raise FileNotFoundError('Can\'t find python path, exiting.')


def run_nuitka(cmd: list) -> None:
    'Run nuitka build in subprocess and print output.'
    process = subprocess.Popen(cmd,
                               stdout=subprocess.PIPE,
                               bufsize=1,
                               text=True)
    while True:
        line = process.stdout.readline()
        if not line:
            break
        print(line.strip())




# process = subprocess.Popen(['py', 'test.py'],
#                            stdout=subprocess.PIPE,
#                            universal_newlines=True)

# cmd_list = ['powershell', '-NoProfile', 'py', 'sandbox.py']

# process = subprocess.Popen(cmd_list,
#                            stdout=subprocess.PIPE,
#                            bufsize=1,
#                            text=True
#                            )

# process = subprocess.Popen(['dir'],
#                            executable='cmd.exe',
#                            stdout=subprocess.PIPE,
#                            universal_newlines=True)


# print(shutil.which('powershell'))
# print(shutil.which('cmd'))
# print(shutil.which('pwsh'))



# while True:
#     line = process.stdout.readline()
#     if not line:
#         break
#     print(line.strip())

# while line:= process.stdout.readline():
#     print(line.strip())


# while True:
#     output = process.stdout.readline()
#     print(output.strip())
#     # Do something else
#     return_code = process.poll()
#     if return_code is not None:
#         print('RETURN CODE', return_code)
#         # Process has finished, read rest of the output
#         for output in process.stdout.readlines():
#             print(output.strip())
#         break


if __name__ == '__main__':
    main()