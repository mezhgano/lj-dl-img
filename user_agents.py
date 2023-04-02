import asyncio
import itertools
import json
import random
from typing import Sequence
from urllib.parse import urlparse

import aiohttp
from bs4 import BeautifulSoup

from constants import (BROWSER_FIELD_INCLUDE_PATTERNS,
                       OS_FIELD_EXCLUDE_PATTERNS, RESPONSE_NOT_200, UAS_BACKUP,
                       URL_UAS, TermColors, headers_default)


class Ua:
    'Class for getting latest user-agent strings from the web.'

    @classmethod
    async def _get_uas(cls, session: object, browser: str) -> list:
        '''
        Fetch user-agent strings for specific `browser`.
        Return list of strings.
        '''
        url = ''.join((URL_UAS, browser))

        async with session.get(url) as response:
            assert response.status == 200, RESPONSE_NOT_200
            html = await response.text()
            soup = BeautifulSoup(html, features='html.parser')
            rows = soup.select('td li span.code')

            if not rows:
                return []

            uas = []
            for row in rows:
                ua = row.text.strip()
                if any(os in ua.lower() for os in OS_FIELD_EXCLUDE_PATTERNS):
                    continue
                uas.append(ua)

            return uas


    @classmethod
    async def _gather_uas(cls) -> tuple:
        '''
        Gather results from `_get_uas` function.
        Return list with latest user-agent strings.
        '''
        headers = dict(headers_default)
        del headers['Origin'], headers['Referer'], headers['Host'], headers['Connection']
        headers['Host'] = urlparse(URL_UAS).netloc
        headers['User-Agent'] = random.choice(UAS_BACKUP)

        async with aiohttp.ClientSession(headers=headers) as session:
            tasks = []
            for browser in BROWSER_FIELD_INCLUDE_PATTERNS:
                tasks.append(asyncio.create_task(cls._get_uas(session, browser)))

            results = await asyncio.gather(*tasks)
            uas = tuple(itertools.chain.from_iterable(results))

            return uas


    @classmethod
    def _json_dumps(cls, data: Sequence) -> str:
        'Return JSON formatted string with ident and `strip()` applied.'
        return json.dumps(data, indent=4).strip()


    @classmethod
    def _actualize_uas(cls) -> tuple:
        '''
        Run the whole process of getting latest user-agent strings.\n
        Return list of latest strings. If process fails for some reason,
        return list of backup strings.
        '''
        colors = TermColors
        error_mark = f'{colors.FAIL}●{colors.ENDC}'
        message = ('Failed to collect latest user-agent strings from external source.\n'
                   '{error_mark} Exception: {ex}\n\n'
                   'Using internal user-agents strings backup...')
        uas_backup_json = cls._json_dumps(UAS_BACKUP)

        try:
            uas_new = asyncio.run(cls._gather_uas())
            if not uas_new:
                print(message.replace('{error_mark} Exception: {ex}\n\n', ''))
                return UAS_BACKUP
        except Exception as ex:
            print(message.format(error_mark=error_mark, ex=ex))
            return UAS_BACKUP

        uas_new_json = cls._json_dumps(uas_new)

        if uas_backup_json != uas_new_json:
            return uas_new
        else:
            return UAS_BACKUP


    @classmethod
    def random(cls) -> str:
        'Return random chosen user-agent string.'
        uas = cls._actualize_uas()
        return random.choice(uas)

if __name__ == '__main__':
    print(Ua.random())