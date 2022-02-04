import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import requests
from bs4 import BeautifulSoup
import pickle
import time
import hashlib
import os

# Cache posts for 3 days. If item is listed > 3 days, it will appear in email again after this period.
THREE_DAYS = 3 * 30 * 24 * 60 * 60

# Cache file so script knows which ads we sent notifications for already
CACHE_FILE = "./nepremicnine_cache.pickle"

# Base url of webpage
ROOT_URL = "https://www.nepremicnine.net"

# Ad listing URL. Configure your own filtered search, then copy URL here. I'm filtering prices between 90k and 140k. Be careful to use s=16 order param, to ensure script works correctly.
# IMPORTANT! `?s=16` parameter sortira od najnovejsih postov proti najstarejsim!
REQ_URL = ROOT_URL + "/oglasi-prodaja/ljubljana-mesto/stanovanje/cena-od-90000-do-140000-eur/?s=16"

# Configure your own APP PASSWORD: https://support.google.com/mail/answer/185833?hl=en
EMAIL_ADDR = "subic.tine@gmail.com"
EMAIL_PASS = "dadabada"


# Mail sender
class GmailAdapter:
    def __init__(self, email, password):
        '''
        Password needs to be app password! (https://support.google.com/mail/answer/185833?hl=en)
        :param email:
        :param password:
        '''
        self.email = email
        self.password = password
        self.server = 'smtp.gmail.com'
        self.port = 587
        session = smtplib.SMTP(self.server, self.port)
        session.ehlo()

        # upggrade to secure
        session.starttls()
        session.ehlo()
        session.login(self.email, self.password)
        self.session = session

    def send(self, recipient: str, subject: str, body: str):
        ''' Format and send email to smtp.gmail.com relay. '''

        # create header
        msg = MIMEMultipart()

        msg['From'] = self.email
        msg['To'] = self.email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        # send
        self.session.send_message(msg)

# Stores Ad data
class PlaceAd:
    def __init__(self, location, year, floor, price, area, description, url, agency, date, notified, type, img):
        self.location = location 
        self.year = year # year of building
        self.floor = floor # which floor
        self.area = area # area in m2
        self.price = price # price in eur
        self.description = description #provided description
        self.url = url
        self.agency = agency # posredniska hisa 
        self.hash = self._make_hash() # ID hash
        self.date = date # date of post
        self.notified = notified # has user been notified
        self.type = type # type of property (garsonjera, enosobno, itd.)
        self.imglink = img # url to first image

    def _make_hash(self):
        '''Encode url to unique hash'''
        return hashlib.md5(self.url.encode()).digest()


# parse one ad for data
# fugly code, but it works. If your script doesn't work, it's probably problem with updated HTML in webpage.
def parse_ad_html(ad):
    adname_html = ad.find("h2", {"itemprop": "name"})
    if adname_html is None:
        return None

    url = ROOT_URL + adname_html["data-href"]
    location = adname_html.find("span", {"class": "title"}).text
    floor = ""
    year = ""
    for atr in ad.find_all("span", {"class": "atribut"}):
        if 'leto' in atr['class']:
            year = atr.text
        else:
            floor = atr.text.replace("Nadstropje:", "").strip()
    description_html = ad.find("div", {"itemprop": "description"})
    description = description_html.text if description_html is not None else ""

    area_html = ad.find("span", {"class": "velikost"})
    area = area_html.text if area_html is not None else ""

    type_html = ad.find("span", {"class": "vrsta"})
    type = type_html.text if type_html is not None else ""
    type_html = ad.find("span", {"class": "tipi"})
    type += ": " + type_html.text if type_html is not None else ""

    price_html = ad.find("span", {"class": "cena"})
    if price_html is not None and price_html.find("span", {"class": "cena-old"}) is not None:
        price_html.find("span", {"class": "cena-old"}).replace_with('')

    price = price_html.text if price_html is not None else ""

    agency_html = ad.find("span", {"class": "agencija"})
    agency = agency_html.text if agency_html is not None else ""
    seen_timestamp = int(time.time())
    img = ad.find("img")
    if img is not None:
        img = img["data-src"].replace("sIonep", "slonep")

    return PlaceAd(location, year, floor, price, area, description, url, agency, seen_timestamp, False,
                   type, img)


# fetches newest page from url
def fetch_latest_posts() -> [PlaceAd]:
    response = requests.get(REQ_URL)

    html = BeautifulSoup(response.text, "html.parser")

    ad_list_container = html.find("div", {"class": "seznam"})
    ad_list = ad_list_container.find_all("div", {"class": "oglas_container"})

    ads = []

    for ad in ad_list:
        try:
            ad_content = parse_ad_html(ad)
            if ad_content is None:
                continue

            ads.append(ad_content)
        except Exception as e:
            print(ad, e)
    return ads


def load_from_file_cache() -> [PlaceAd]:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "rb") as f:
            return pickle.load(f)
    else:
        return []


def store_to_file_cache(items: [PlaceAd]):
    with open(CACHE_FILE, "wb") as f:
        return pickle.dump(items, f)

# format HTML for email
def build_mail_html(items):
    timestamp = datetime.datetime.now().strftime("%d.%m.%Y ob %H:%M")
    content = "Našel {} novih ponudb. (Skripta pognana ob {})<br><br>".format(len(items), timestamp)
    idx = 0
    for item in items:
        item.notified = True
        idx += 1
        content += """<a href= {}>[{}] {} </a> <br>\t- Lokacija: {} ({}) <br>
            \t- Cena: {}<br> \t- Kvadratura: {}, nadstropje: {}<br> <img src={} height=300 width=300><br><br>""".format(
            item.url,
            idx, item.type, item.location, item.year, item.price, item.area, item.floor, item.imglink)

    return content


if __name__ == "__main__":
    existing: [PlaceAd] = load_from_file_cache()

    website_latest: [PlaceAd] = fetch_latest_posts()

    mail = GmailAdapter(EMAIL_ADDR, EMAIL_PASS)
    for item in website_latest:
        found_item = None
        for e in existing:
            if e.hash == item.hash:
                found_item = e
                break
        if found_item is not None:
            pass
        else:
            existing.append(item)

    # remove older than 3 days
    filtered = [x for x in existing if x.date > int(time.time() - THREE_DAYS)]
    not_notified = [x for x in filtered if x.notified is False]

    print(len(not_notified), 'Ads to notify...')

    if len(not_notified) > 0:
        content = build_mail_html(not_notified)
        mail.send("subic.tine@gmail.com", "Nepremicnine - {} novih ponudb".format(len(not_notified)), content)

    with open("./nepremicnine.log", "a+") as log:
        log.write(
            "[{}] - Found {} new. Total {} in cache.\n".format(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                                                               len(not_notified), len(filtered)))

    store_to_file_cache(filtered)