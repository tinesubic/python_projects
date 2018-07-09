from fanfictor.scraper import Scraper
import sqlite3
import fanficfare
import time
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

url = 'https://m.fanfiction.net/book/Harry-Potter/?&srt=1&lan=1&r=10&p='
conn = sqlite3.connect('ffn.db')

c = conn.cursor()

scraper = Scraper()


def db_insert(metadataArr):
    tuples = []
    times = []
    for i in metadataArr:
        tuples.append((i['id'], i['author'], i['author_id'], i['title'], i['updated'], i['published'], i['status'],
                     ", ".join(i['genres']), i['num_chapters'], i['num_words'], 0))
    sql = '''INSERT OR REPLACE INTO ffn VALUES (?,?,?,?,?,?,?,?,?,?,?)'''

    c.executemany(sql, tuples)
    conn.commit()


for i in range(1, 10):
    req = requests.get(url + str(i))
    html = BeautifulSoup(req.content, "html5lib")

    html = html.find_all("div", {"id": "content"})[0].find_all("div", {"class": "bs"})
    arr = []
    for item in tqdm(html):
        time.sleep(0.5)
        props = item.find_all('a')
        id = None
        author = ""
        hasTitle = False
        for tag in props:
            if tag.has_attr('href'):
                if tag['href'].startswith('/s/') and not hasTitle:
                    id = tag['href'].split('/')[2]
                    hasTitle = True
                elif tag['href'].startswith('/u/'):
                    author = tag.text

        try:
            metadata = scraper.scrape_story_metadata(id)
            metadata['author'] = author
            if 'num_chapters' not in metadata:
                metadata['num_chapters'] = 1
            arr.append(metadata)
            # print(metadata)
        except Exception as err:
            print('Error retrieving metadata, ID: ', id, err)
    db_insert(arr)
    print('Finished ', i, 'page')
