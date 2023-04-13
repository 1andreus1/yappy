import asyncio
from traceback import format_exc

import aiohttp
from codetiming import Timer


class Parser:
    def __init__(self, uids):
        self.uids = uids
        self.iterations = 500
        self.workers = 100

        self.ids = set()

    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.parse())

    async def parse(self):
        tasks = []

        for uid in self.uids:
            tasks.append(self.get_video_info(uid))
            if len(tasks) > self.workers:
                await asyncio.gather(*tasks)
                tasks.clear()
        await asyncio.gather(*tasks)

    async def get_video_info(self, uid):
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'uid': uid,
                }
                url = f'https://yappy.media/_next/data/ybEMEK-pGeZPNGV4iLrOn/ru-RU/video/{params["uid"]}.json'
                async with session.get(url, params=params, timeout=20) as response:
                    if response.status != 200:
                        # print(response.status)
                        raise TimeoutError('Превышено кол-во запросов')

                    res = await response.json()

                    a = res['pageProps']['data']['likesCount']
                    print(a)
        except (TimeoutError, asyncio.TimeoutError):
            self.uids.append(uid)
        except (Exception,):
            print('Ошибка получения:', '\n', format_exc())


if __name__ == '__main__':
    with Timer(text="\n Всего времени: {:.1f}"):
        uids = ['ece87f478cbf45a9a2e94ce6805b1db5', '8aefbcf4a75345b7a0e15d018b53fdae'] * 200
        parser = Parser(uids)
        parser.run()
