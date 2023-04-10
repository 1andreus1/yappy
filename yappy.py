import asyncio
from traceback import format_exc

import aiohttp
from codetiming import Timer
from fake_useragent import UserAgent

URL = f'https://yappy.media/api/feed'
headers = {
    'Accept': 'application/json',
    'Connection': 'keep-alive',
    'Referer': 'https://yappy.media/feed',
    'accept-language': 'ru-RU',
    'user-agent': UserAgent().random,
}


class Parser:
    def __init__(self):
        self.iterations = 1000
        self.pages = list(range(self.iterations))
        self.workers = 100

        self.ids = set()

    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.parse())

    async def parse(self):
        try:
            await self.get_url()
            print('Получено ')
        except (Exception,):
            print('Ошибка получения:', '\n', format_exc())

    async def get_url(self):
        connector = aiohttp.TCPConnector(limit=50, force_close=True)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []

            for i in self.pages:
                tasks.append(asyncio.create_task(self.get_video_info(i, session)))
                if len(tasks) > self.workers:
                    await asyncio.gather(*tasks)
                    tasks.clear()
            await asyncio.gather(*tasks)

    async def get_video_info(self, idx, session):
        try:
            headers['user-agent'] = UserAgent().random
            params = {
                'page': idx,
            }

            response = await session.get(URL,
                                         params=params,
                                         headers=headers,
                                         timeout=30)

            if response.status != 200:
                raise TimeoutError('Превышено кол-во запросов')

            res = await response.json()
            print(res)
        except TimeoutError:
            self.pages.append(idx)
        except (Exception,):
            print('Ошибка получения:', '\n', format_exc())


if __name__ == '__main__':
    with Timer(text="\n Всего времени: {:.1f}"):
        parser = Parser()
        parser.run()
