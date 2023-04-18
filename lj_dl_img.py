import argparse
import asyncio
import json
import os
import re
import sys
from math import floor
from pathlib import Path
from typing import List, Optional, Sequence
from urllib.parse import urlparse

import aiofiles
import aiohttp
from bs4 import BeautifulSoup
from rich.console import Console
from rich.progress import (BarColumn, MofNCompleteColumn, Progress, TaskID,
                           TaskProgressColumn, TextColumn, TimeRemainingColumn)

from constants import (RESPONSE_NOT_200, UAS_BACKUP, URL_API, URL_AUTH,
                       VERSION, TermColors, headers_default)
from user_agents import Ua

parser = argparse.ArgumentParser(
    description='LJDL - Download image albums from livejournal.com.\n\n'
                'Usage: lj-dl-img [OPTIONS] [URL]',
    formatter_class=argparse.RawTextHelpFormatter,
    add_help=False
    )

parser.add_argument(
    'URL',
    type=str,
    help='URL of Livejournal user or certain album to download. For example, specify: \n'
         'https://username.livejournal.com - to download all avaliable albums.\n'
         'https://username.livejournal.com/photo/album/1337 - to download just one certain album.\n\n'
    )

parser.add_argument(
    '-h',
    '--help',
    action='help',
    default=argparse.SUPPRESS,
    help='Show this help message and exit.\n\n'
    )

parser.add_argument(
    '-v',
    '--version',
    action='version',
    version=VERSION,
    help='Show script version and exit.\n\n'
    )

parser.add_argument(
    '-d',
    '--directory',
    type=str,
    metavar='',
    help='Path where images should be downloaded.\n'
         'Note that script will create a subfolder for each downloaded album.\n'
         'Default: current working directory.\n\n'
    )

args = parser.parse_args()

progress = Progress(
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TaskProgressColumn(),
    "•",
    MofNCompleteColumn(),
    "•",
    TextColumn("({task.fields[filename]})"),
    "•",
    TimeRemainingColumn(elapsed_when_finished=True),
)


class Ljdl():
    '''Class for downloading photo albums from livejournal.com'''

    def __init__(self, url: str, path: Optional[str] = None) -> None:
        self.console = Console()
        self.colors = TermColors
        self.error_mark = f'{self.colors.FAIL}●{self.colors.ENDC}'
        self.url = url
        self.url_parse = self._validate_url(url)
        self.goal_is_multiple = self._goal_is_multiple()
        self.download_path = self._set_download_path(path)
        self.user_agent = Ua.random()
        self.username = self._get_username()
        self.cookies = None
        self.auth_token = None


    def _exit(self, message: str, status: int = 0):
        'Gracefully exit with status code and message to stderr.'
        if status != 0:
            sys.stderr.write(f'{self.error_mark} {message}')
        raise SystemExit(status)


    def _validate_url(self, url:str) -> object:
        'Check if given string is valid url. Return `urlparse` ParseResult object.'
        message = ('Not a valid URL.\n'
                   'Please enter URL like this to download specific album:\n'
                   'https://username.livejournal.com/photo/album/1337\n'
                   'Or like this to download all albums:\n'
                   'https://username.livejournal.com')
        try:
            url_parse = urlparse(url)
        except ValueError:
            self._exit(message, 1)

        if not all((url_parse.scheme, url_parse.netloc)):
            self._exit(message, 1)
        if 'livejournal.com' not in url_parse.netloc:
            self._exit('Only downloading from https://www.livejournal.com is supported.', 1)

        pattern = re.compile(r'^https:\/\/([a-z0-9_\-])+\.livejournal\.com')
        if not pattern.search(url):
            self._exit('Not a valid username, please check URL spelling.', 1)

        return url_parse


    def _goal_is_multiple(self) -> bool:
        'Return `True` if download goal is multiple albums, otherwise `False`.'
        if not self.url_parse.path:
            return True
        else:
            pattern = re.compile(r'/album/\d+$')
            if pattern.search(self.url_parse.path):
                return False
            else:
                print('URL doesn\'t contain specific album id, '
                      'downloading all available albums...')
                return True


    def _get_username(self) -> str:
        'Return username string from `urlparse` ParseResult object.'
        return (self.url_parse.netloc).split('.')[0]


    def _get_album_id(self):
        'Return `album_id` int from `urlparse` ParseResult object.'
        return int((self.url_parse.path).split('/')[-1])


    def _set_download_path(self, path: Optional[str] = None) -> Path:
        if not path:
            download_path = Path.cwd().resolve()

        else:
            download_path = Path(path)
            message = ('Given path is not {reason}'
                       'Please specify different path or not specify path at all '
                       'to download to current directory.')

            if not download_path.exists():
                try:
                    download_path.mkdir(parents=True)
                except Exception as e:
                    self._exit(message.format(reason = f'created.\nException: {e}\n\n'), 1)

            if not download_path.is_dir():
                self._exit(message.format(reason = 'a folder.\n'), 1)
            if not os.access(download_path, os.W_OK):
                self._exit(message.format(reason = 'writable.\n'), 1)

        return download_path


    async def _get_cookies(self, session: aiohttp.ClientSession) -> dict:
        'Make request by given `URL_AUTH` url and return `RequestsCookieJar` object from response.'
        async with session.get(url=URL_AUTH) as response:
            assert response.status == 200, f'{self.error_mark} {RESPONSE_NOT_200}'
            json_text = json.loads(await response.text())

        assert 'ljuniq' in json_text, f"{self.error_mark} Can\'t get 'ljuniq' cookie, exiting."

        cookie_jar = str(session.cookie_jar.filter_cookies(f"{URL_AUTH.rsplit('/', 3 )[0]}"))
        assert len(cookie_jar) > 0, f"{self.error_mark} Can\'t get 'luid' cookie, exiting."

        cookie_dict = {
            'luid':
                f"{cookie_jar.split('=', 1)[1]}",
            'ljuniq':
                f"{json_text['ljuniq']}"
        }

        return cookie_dict


    async def _get_auth_token(self, session: aiohttp.ClientSession) -> str:
        '''
        Extract all inline JS scripts from `_get_html` response text
        and search for `auth_token` string. Return `auth_token` string.
        '''
        async with session.get(url=self.url) as response:
            assert response.status == 200, f'{self.error_mark} {RESPONSE_NOT_200}'
            html = await response.text()

        soup = BeautifulSoup(html, features='html.parser')
        scripts = list(soup.find_all('script', attrs={'src':None}))

        for element in scripts:
            if 'auth_token' in str(element):
                script = str(element)

        assert script != None, f"{self.error_mark} Can\'t find any 'auth_token' string\
        in page scripts, exiting."

        pattern = re.compile(r'{.+\"auth_token\":.+}')
        match = pattern.search(script).group()
        auth_token = json.loads(match)['auth_token']

        return auth_token


    async def _auth(self) -> None:
        headers = dict(headers_default)
        del headers['Origin'], headers['Referer']
        headers['User-Agent'] = self.user_agent

        async with aiohttp.ClientSession(headers=headers) as session:
            self.cookies = await self._get_cookies(session)

        async with aiohttp.ClientSession(headers=headers, cookies=self.cookies) as session:
            self.auth_token = await self._get_auth_token(session)


    async def _get_albums(self) -> list[dict]:
        '''
        Make jsonrpc request to API to get albums info.
        Return list of dict with albums info.
        '''
        headers = dict(headers_default)
        del headers['Upgrade-Insecure-Requests']

        headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
        origin = ''.join((self.url_parse.scheme, '://', self.url_parse.netloc))
        headers['Origin'] = origin
        headers['Referer'] = ''.join((origin, '/photo'))
        headers['User-Agent'] = self.user_agent

        payload = [{
            "id": 1,
            "jsonrpc": "2.0",
            "method": "photo.get_albums",
            "params":{
                "auth_token": f"{self.auth_token}",
                "user": f"{self.username}"
            }}]

        payload_dump = json.dumps(payload)

        async with aiohttp.ClientSession(headers=headers, cookies=self.cookies) as session:
            async with session.post(url=URL_API, data=payload_dump) as response:
                assert response.status == 200, f'{self.error_mark} {RESPONSE_NOT_200}'
                response_json = json.loads(await response.text())

        for _dict in response_json:
            try:
                albums = _dict['result']['albums']
            except KeyError:
                continue

        assert albums != None, f"{self.error_mark} Can\'t find 'albums' \
        key in JSON response, exiting."

        if self.goal_is_multiple:
            return albums
        else:
            for album in albums:
                if album['id'] == self._get_album_id():
                    return [album]


    async def _get_records(
        self,
        session: aiohttp.ClientSession,
        album_id: int,
        limit: int) -> list[dict]:
        '''
        Make jsonrpc request to API to get specific album records.
        Return dict with image file names as keys and urls as values.
        '''
        headers = dict(headers_default)
        del headers['Upgrade-Insecure-Requests']

        headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
        origin = ''.join((self.url_parse.scheme, '://', self.url_parse.netloc))
        headers['Origin'] = origin
        headers['Referer'] = ''.join((origin, '/photo', f'/album/{str(album_id)}'))
        headers['User-Agent'] = self.user_agent
        payload = [{
            "jsonrpc":"2.0",
            "method":"photo.get_records",
            "params":{
                "albumid":album_id,
                "user":f"{self.username}",
                "offset":0,
                "limit":limit,
                "sort":"timecreate",
                "order":"desc",
                "migrated_info":1,
                "auth_token":f"{self.auth_token}"
                },
            "id":7
            }]

        payload_dump = json.dumps(payload)

        async with session.post(url=URL_API, data=payload_dump) as response:
            assert response.status == 200, f'{self.error_mark} {RESPONSE_NOT_200}'
            response_json = json.loads(await response.text())

        for _dict in response_json:
            try:
                records_json = response_json[0]['result']['records']
            except KeyError:
                continue

        assert records_json != None, f"{self.error_mark} Can\'t find 'records' \
        key in JSON response, exiting"

        records = {}
        records[album_id] = {}
        possible_exts = ('.jpg', '.jpeg', '.gif', '.png')

        for record in records_json:
            url_ext = Path(record['url']).suffix
            record_ext = Path(record['name']).suffix

            if record_ext.isupper():
                record['name'] = record_ext.lower().join(record['name'].rsplit(record_ext, 1))

            if not record['name'].endswith(possible_exts):
                record['name'] = ''.join((record['name'], url_ext))

            if record['name'].endswith('.jpeg'):
                record['name'] = '.jpg'.join(record['name'].rsplit('.jpeg', 1))

            # add 'index' field to result file name to avoid overwriting files with same original file name
            # plus: it will be possible to sort them in a folder
            image_name = f"{record['index']}__{record['name'].replace(' ', '_')}"
            image_url = f"{record['url']}"
            records[album_id][image_name] = image_url

        return records


    async def _generate_job_list(self) -> List[dict[dict]]:
        '''
        Return combined results of `_get_albums` and `_get_records` as a list of dicts.
        '''
        with self.console.status('Generating Job List...', spinner='dots'):
            await self._auth()
            albums = await self._get_albums()

            job_list = {'albums': []}
            keys_to_keep = ('count', 'timecreate', 'name', 'id')
            for album in albums:
                # create a shallow copy to avoid
                # "RuntimeError: dictionary changed size during iteration"
                for _key in album.copy():
                    if _key not in keys_to_keep:
                        del album[f'{_key}']
                job_list['albums'].append(album)


            async with aiohttp.ClientSession(cookies=self.cookies) as session:
                tasks = []
                results = {}
                for album in job_list['albums']:
                    tasks.append(asyncio.create_task(self._get_records(
                        session=session,
                        album_id=album['id'],
                        limit=album['count']
                        )))
                done, _ = await asyncio.wait(tasks)
                for task in done:
                    results.update(task.result())


            albums_total = len(job_list['albums'])
            records_total = 0
            for album in job_list['albums']:
                album['records'] = results[album['id']]
                records_total += album['count']

        print(f"Found total {self.colors.OK_GREEN}{records_total}{self.colors.ENDC} "
              f"images in {self.colors.OK_GREEN}{albums_total}{self.colors.ENDC} "
              f"album{'s' if albums_total > 1 else ''}.")

        return job_list


    async def _fetch_image(
        self,
        session: aiohttp.ClientSession,
        url: str,
        path: Path,
        task_id: TaskID,
        filename: str) -> None:
        '''
        Download image from given url to specified path,
        updates progress task id with image filename.
        '''
        async with session.get(url) as response:
            assert response.status == 200, f'{self.error_mark} {RESPONSE_NOT_200}'
            data = await response.read()

        async with aiofiles.open(path, 'wb') as file:
            await file.write(data)

        progress.update(task_id, filename=filename)
        progress.update(task_id, advance=1)


    def _get_task_filename(self, record: str, width: int = 20) -> str:
        'Return normalized filename of the record for task progress display.'
        assert width % 2 == 0, "'width' parameter must be even number, \
            otherwise right display bracket will shaking."

        record = record.split('__', 1)[1][:width]

        if len(record) == width:
            record = record[:-3] + '...'

        indent = floor(abs(len(record) - width)/2)

        if len(record) % 2 != 0:
            cf = 1
        else:
            cf = 0

        filename = f" {' ' * indent}{record}{' ' * (indent + cf)} "
        return filename


    async def _json_dump(self, fp: Path, data: Sequence):
        'Dump any sequence `data` to json file at given path.'
        with open(fp, 'w', encoding='UTF-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)


    async def download_images(self) -> None:
        '''
        Gather list of async download tasks and start download process.
        '''
        semaphore = asyncio.BoundedSemaphore(5)
        job_list = await self._generate_job_list()

        job_list_path = Path.joinpath(
            Path(self.download_path),
            Path(f"lj_{self.username}_job_list.json")
            )
        await self._json_dump(job_list_path, job_list)

        with progress:
            task_id = progress.add_task('Downloading...', filename=' ... ')

            async with semaphore, aiohttp.ClientSession() as session:
                tasks = []

                for album in job_list['albums']:
                    album_dir = f"lj_{self.username}_{album['id']}__{album['name'].replace(' ', '_')}"
                    album['download_path'] = Path.joinpath(Path(self.download_path), Path(album_dir))
                    album_path = album['download_path']
                    if not Path.exists(album_path):
                        Path.mkdir(album_path, parents=True, exist_ok=True)

                    for record in album['records']:
                        url = album['records'][record]
                        path = Path.joinpath(
                            Path(album['download_path']),
                            Path(record.replace(' ', '_'))
                            )
                        filename = self._get_task_filename(record)
                        tasks.append(
                            asyncio.create_task(
                                self._fetch_image(session, url, path, task_id, filename)
                                ))

                progress.update(task_id, total=len(tasks))
                await asyncio.wait(tasks)

                progress.update(task_id, description='Completed')
                progress.update(task_id, filename='')



def main():
    ljdl = Ljdl(url=args.URL, path=args.directory)
    asyncio.run(ljdl.download_images())


if __name__ == '__main__':
    main()
