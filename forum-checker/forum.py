from email.mime.text import MIMEText
import time
from bs4 import BeautifulSoup
import urllib.request
from email.mime.multipart import MIMEMultipart

import smtplib
import sys

__author__ = 'MikroMan'

root_url = "http://www.pd-ljmatica.si/forum/phpBB2/"
sections = [
    ("Novice", "viewforum.php?f=2"),
    ("Diskusije", "viewforum.php?f=5"),
    ("Objave šol", "viewforum.php?f=3"),
    ("Fotke & Video", "viewforum.php?f=8"),
    ("Alpinistični vzponi", "viewforum.php?f=10"),
    ("Športnoplezalni vzponi", "viewforum.php?f=14"),
    ("Hej, pojdimo!", "viewforum.php?f=11"),
    ("Kupim, prodam, iščem", "viewforum.php?f=6"),
    ("ne-Uporabno", "viewforum.php?f=3"),
]

months = {"Jan": "01",
          "Feb": "02",
          "Mar": "03",
          "Apr": "04",
          "Maj": "05",
          "Jun": "06",
          "Jul": "07",
          "Avg": "08",
          "Sep": "09",
          "Okt": "10",
          "Nov": "11",
          "Dec": "12"}

#add list of emails to send mail to
emails = ["subic.tine@gmail.com"]

ONE_DAY = 60 * 60 * 24
CUR_TIME = time.localtime()


def get_month(month):
    for name, value in months.items():
        if value == month:
            return name


def struct_to_str(time_obj):
    time_str = time.strftime('%Y-%m-%dT%H:%M:%SZ', time_obj).strip("Z").split("T")

    date_str = time_str[0].split("-")
    month = get_month(date_str[1])
    time_str = time_str[1][:-3:]

    return "{0} {1}, {2} @ {3}".format(month, date_str[2], date_str[0], time_str)


def construct_html(post_data):
    html_content = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
                    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
                <html xmlns="http://www.w3.org/1999/xhtml">
                <head>
                    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
                    <title>AO Matica Forum - Novo</title>
                    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
                </head>
                <body style="margin: 0; padding: 0;">"""

    # print(to_send)
    for section_tuple in sections:
        key = section_tuple[0]
        if len(post_data[key]) > 0:
            html_content += "<h3>" + key + "</h3><ul>"
            for post in post_data[key]:
                html_content += '<li><a href="{0}"><b>{1}</b></a> - zadnji komentar <b>{2}</b> ({3})'.format(
                    post["last_comment_link"], post["title"], post["last_author"], struct_to_str(post["time_obj"]))
                if post["new"]:
                    html_content += "<font color=red><b> [Novo] </b></font>"

                html_content += "<br></li>"

            html_content += "</ul><hr>"

    return html_content + "</body></html>"


def get_24_time(post_time, is_am):
    if is_am == "am" or post_time.startswith("12"):
        return post_time.zfill(5)
    else:
        s = post_time.split(":")
        hours = int(s[0]) + 12
        return "{0}:{1}".format(hours, s[1])


def get_time_string(html_time_string):
    time_array = html_time_string.split(" ")
    month = months[time_array[0]]
    day = time_array[1].strip(",")
    year = time_array[2]
    time_string = get_24_time(time_array[3], time_array[4])

    return "{0}-{1}-{2}T{3}:00".format(year, month, day, time_string)


def active(post):
    return (time.mktime(CUR_TIME) - time.mktime(post["time_obj"])) < ONE_DAY


def get_last_activity(item_html):
    activity = item_html.findAll("span", {"class": "postdetails"})[2]

    last_author = activity.findAll("a")[0].text

    last_time = activity.text[4:-len(last_author) - 1]

    return last_time, last_author


def is_new_topic(post_html):
    return post_html.findAll("span", {"class": "postdetails"})[0].text == "0"


def get_post_data(post_html):
    post = {}

    post["title"] = post_html.findAll("span", {"class": "topictitle"})[0].text
    last_active_date, post["last_author"] = get_last_activity(post_html)

    post["last_comment_link"] = root_url + post_html.findAll("span", {"class": "postdetails"})[2].findAll("a")[1][
        "href"]

    time_string = get_time_string(last_active_date)
    time_obj = time.strptime(time_string, "%Y-%m-%dT%H:%M:%S")

    post["time_obj"] = time.gmtime(time.mktime(time_obj))

    post["new"] = is_new_topic(post_html)

    return post


def parse_html_data(html_data):
    posts = []
    content = html_data.findAll("table", {"class": "forumline"})[0].findAll("tr")
    content = content[1:-1:]
    for post in content:
        posts.append(get_post_data(post))

    return posts


def send_mail(email_content, target_email):
    #must enable smtp in gmail settings (https://support.google.com/accounts/answer/6010255?hl=en)
    #or set up alternate SMTP
    #https://docs.python.org/3/library/email-examples.html

    #add your own mail and password
    #ex for gmail: source_email = subic.tine@gmail.com, user_passwd: SecretPassword111
    source_email = <SMTP MAIL> 
    user_passwd = <PWD>

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(source_email, user_passwd)

    msg = MIMEMultipart('alternative')
    msg["From"] = source_email
    msg["To"] = target_email
    msg["Subject"] = "AO Matica Forum - novo"


    msg.attach(MIMEText(email_content, "html"))

    server.sendmail(source_email, target_email, msg.as_string())
    server.quit()

def fetch_html(url):
    f = urllib.request.urlopen(root_url + url)
    data = f.read()
    return BeautifulSoup(data, "html.parser")

#runs forever.
#Remove loop and sleep function to run with scheduler
while True:
    CUR_TIME = time.localtime()
    print(time.strftime('%Y-%m-%dT%H:%M:%SZ', CUR_TIME))

    to_send = {}
    items = 0

    for item in sections:
        to_send[item[0]] = []
        print("Fetching: " + item[0])
        sys.stdout.flush()

        content = fetch_html(item[1])

        data = parse_html_data(content)

        for i in range(0, len(data)):
            if active(data[i]):
                to_send[item[0]].append(data[i])
                items += 1

    if items > 0:
        html = construct_html(to_send)

        for email in emails:
            print("Sending mail: " + email)
            sys.stdout.flush()

            send_mail(html, email)
            print("Mail sent")
    else:
        print("No news")

    data = []
    sys.stdout.flush()
    time.sleep(ONE_DAY)