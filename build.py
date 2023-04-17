import platform
import shutil
import subprocess
import sys
from pathlib import Path

from constants import VERSION

OS_NAME, MACHINE, ARCH = sys.platform, platform.machine().lower(), platform.architecture()[0][:2]
if MACHINE in ('x86', 'x86_64', 'amd64', 'i386', 'i686'):
    MACHINE = 'x86' if ARCH == '32' else ''


def main() -> None:
    'Build full command list and run build process.'
    opts = sys.argv[1:]

    standalone = '--standalone' in opts
    name, path = get_dist_path(standalone)

    if not standalone and '--onefile' not in opts:
        opts.extend(('--onefile', f'--output-filename={name}'))

    powershell_hook = get_powershell_alias() if OS_NAME == 'win32' else ''

    print(f"Building lj-dl-img v{VERSION} for {OS_NAME}{'_'.join((MACHINE,))} with options:\n{opts}\n")
    print(f'Build destination:\n{path}\n')

    cmd = [
        *powershell_hook,
        get_python_alias(),
        '-m',
        'nuitka',
        f'--onefile-tempdir-spec={get_cache_dir()}',
        f'--windows-icon-from-ico={Path("assets/logo.ico")}',
        '--company-name=https://github.com/mezhgano/lj-dl-img',
        f'--product-version={VERSION}',
        '--file-description="Download Livejournal photo albums"',
        '--copyright="dmitrymeshkoff@gmail.com | UNLICENSE"',
        f'--output-dir={path}',
        *opts,
        'lj_dl_img.py'
    ]

    print(f'Running Nuitka with options:\n{cmd}\n')
    run_nuitka(cmd)


def get_cache_dir() -> str:
    '''
    Return Path object with cache path populated with single version number.\n
    Using this instead nuitka %VERSION% token wich is combination of --file-version & --product-version.
    '''
    path = Path(f'%CACHE_DIR%/dmitrymeshkoff/lj-dl-img/{VERSION}')

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
            # Uncomment to pass a null input if Nuitka will asking to download something.
            # return (alias, '-NoProfile', '-Command', '"$null" |')
            return (alias, '-NoProfile', '-Command')
    else:
        # if not found pass empty string, this will lead to
        # subprocess run executable directly
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


if __name__ == '__main__':
    main()