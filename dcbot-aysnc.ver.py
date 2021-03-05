# import library
import requests
from bs4 import BeautifulSoup
import telegram
from apscheduler.schedulers.blocking import BlockingScheduler
import asyncio
from pathlib import Path
import aiohttp



# 기타 설정값
ALREADY_SENT_FILE = 'already_sent.log'

token = '텔레그램 봇 토큰값'
bot = telegram.Bot(token=token)
sched = BlockingScheduler()

CONCURRENCY = 100000
HEADER = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/87.0.4280.77 Mobile/15E148 Safari/604.1"}

# 텔레그램 ID
chat_id_list = ['00000','00001'] 

# 갤러리 및 검색 설정 + 저장소
old_links = []
search_type = 'subject_m' #subject: 제목만, subject_m: 제목/내용
gallery_list = ['pridepc_new4'] #갤러리 주소 ex) 컴퓨터 본체 갤러리: pridepc_new4
keyword_list = ['할인', '특가']


def _get_set_event_loop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as e:
        if e.args[0].startswith('There is no current event loop'):
            asyncio.set_event_loop(asyncio.new_event_loop())
            return asyncio.get_event_loop()
        raise e


async def _fetch(url, session, sem):
    async with sem:
        async with session.get(url, headers=HEADER) as res:
            return await res.text()


async def _dispatch(urls):
    sem = asyncio.Semaphore(CONCURRENCY)
    async with aiohttp.ClientSession() as session:
        coros = (_fetch(url, session, sem) for url in urls)
        return await asyncio.gather(*coros)


def async_get(urls):
    return _get_set_event_loop().run_until_complete(_dispatch(urls))


def _extract_links_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    search_result = soup.select_one('body > div > div > div > section:nth-child(4) > ul')
    airdrop_list = search_result.select('li:nth-child(1) > div > a.lt')
    return [x['href'] for x in airdrop_list]


def extract_links(old_links=[]):
    links = []
    target_urls = []
    for g in gallery_list:
        for k in keyword_list:
            target_urls.append(f'https://m.dcinside.com/board/{g}?s_type={search_type}&serval={k}')
    htmls = async_get(target_urls)
    for html in htmls:
        links.extend(_extract_links_from_html(html))
        print('working')
    return [x for x in links if x not in old_links]


def send_links():
    try:
        old_links = Path(ALREADY_SENT_FILE).read_text().split('\n')
    except:
        old_links = []
    new_links = extract_links(old_links)
    if new_links:
        for link in new_links:
            for chatid in chat_id_list:
                bot.sendMessage(chat_id=chatid, text=link)
    old_links += new_links.copy()
    Path(ALREADY_SENT_FILE).write_text('\n'.join(set(old_links)))


if __name__ == '__main__':
    send_links()
    sched.add_job(send_links, 'interval', seconds=2.5
    sched.start()
