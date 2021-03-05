# import library
import requests
from bs4 import BeautifulSoup
import telegram
from apscheduler.schedulers.blocking import BlockingScheduler


# 기타 설정
token = '텔레그램 봇 토큰값'
bot = telegram.Bot(token=token)
sched = BlockingScheduler()

headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/87.0.4280.77 Mobile/15E148 Safari/604.1"}

# 텔레그램 ID
chat_id_list = ['00000','00001'] 

# 갤러리 및 검색 설정 + 저장소
old_links = []
search_type = 'subject_m' #subject: 제목만, subject_m: 제목/내용
gallery_list = ['pridepc_new4'] #갤러리 주소 ex) 컴퓨터 본체 갤러리: pridepc_new4
keyword_list = ['할인', '특가']


def extract_links(old_links=[]):
    links = []
    for gallery in gallery_list:
        for search_word in keyword_list:
            url = f'https://m.dcinside.com/board/{gallery}?s_type={search_type}&serval={search_word}'
            headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/87.0.4280.77 Mobile/15E148 Safari/604.1"}
            req = requests.get(url, headers=headers)
            html = req.text
            soup = BeautifulSoup(html, 'html.parser')
            search_result = soup.select_one('body > div > div > div > section:nth-child(4) > ul')
            airdrop_list = search_result.select('li:nth-child(1) > div > a.lt')
            for airdrop in airdrop_list[:200]:
                link = airdrop['href']
                links.append(link)

    new_links=[]
    for link in links:
        if link not in old_links:
            new_links.append(link)
    
    return new_links

def send_links():
    global old_links
    new_links = extract_links(old_links)
    if new_links:
        for link in new_links:
            for chatid in chat_id_list:
                bot.sendMessage(chat_id=chatid, text=link)
    old_links += new_links.copy()
    old_links = list(set(old_links))

send_links()
sched.add_job(send_links, 'interval', seconds=6)
sched.start()
