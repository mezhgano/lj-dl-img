import json
import os
import sys
import time
from math import floor
from pathlib import Path
from typing import Optional

from constants import TermColors


def test_cycle():
  with open('..\\LJ_Parser\\json\\job_list_test_records_v2.json', encoding='UTF-8') as file:
    job_list_json = json.load(file)
  #n must be even number, otherwise right bracket will shaking.
  width = 22
  cf = 0
  for album in job_list_json['albums']:
    for record in album['records']:

      # record = record[:width]
      record = record.split('__', 1)[1][:width]
      if len(record) == width:
        record = record[:-3] + '...'

      indent = floor(abs(len(record) - width)/2)
      # indent = round(abs(len(record) - width)/2)

      if len(record) % 2 != 0:
        cf = 1
      else:
        cf = 0
      # cf = 0
      filename = f"( {' ' * indent}{record}{' ' * (indent + cf)} )"
      print(filename, end='\r')
      time.sleep(0.2)
      sys.stdout.write("\033[K")

# test_cycle()


colors = TermColors

error_mark = f'{colors.FAIL}●{colors.ENDC}'

def _exit(message: str, status: int = 0):
    'Gracefully exit with status code and message to stderr.'
    if status != 0:
        sys.stderr.write(f'{error_mark} {message}')
    raise SystemExit(status)


def _set_download_path(path: Optional[str] = None) -> Path:
    if not path:
        download_path = Path.cwd().resolve()
    else:
        _path = Path(path)
        message = ('Given path is not {reason}.\n'
                    'Please specify different path or not specify path at all '
                    'to download to current directory.')
        if not Path.exists(_path):
            _exit(message.format(reason = 'exist'), 1)
        elif not Path.is_dir(_path):
            _exit(message.format(reason = 'a folder'), 1)
        elif not os.access(_path, os.W_OK):
            _exit(message.format(reason = 'writable'), 1)
        else:
            download_path = _path

    return download_path



def _set_download_path_v2(path: Optional[str] = None) -> Path:
  if not path:
    download_path = Path.cwd().resolve()

  else:
    download_path = Path(download_path)
    message = ('Given path is not {reason}'
               'Please specify different path or not specify path at all '
               'to download to current directory.')

    if not download_path.exists():
      try:
        download_path.mkdir(parents=True)
      except Exception as e:
        _exit(message.format(reason = f'created. Exception: {e}\n\n'), 1)

    if not download_path.is_dir():
      _exit(message.format(reason = 'a folder.\n'), 1)
    if not os.access(download_path, os.W_OK):
      _exit(message.format(reason = 'writable.\n'), 1)

  return download_path


given_path = 'C:\\Users\\dmitry\\OMG'
# given_path = 'C:\\Users\\dmitry\\zzz\\rrrr.txt'
# given_path = 'C:\\Users\\mejga\\AppData'
# given_path = 'C:\\Windows\\System32'

# print(_set_download_path(given_path))
print(_set_download_path_v2(given_path))