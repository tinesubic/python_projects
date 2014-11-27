__author__ = 'mikroman'

# downloads all strips from www.commitstrip.com
#to use, create a folder named "scripts" in folder you're running python file from
#run file with python 3 and script will autodownload all strips on site

import requests
from bs4 import BeautifulSoup


root_url = "http://www.commitstrip.com/en/page/"


def parse_html(html_data):
    try:
        img_div = html_data.select("div[class=entry-content]")[0]
        url = ""
        arr = img_div.select("img")

        for img in arr:
            if "src=\"http://www.commitstrip.com/wp-content/uploads" in str(img) and ".png" not in str(img):
                url = img['src']

        return url

    except:
        img_div = html_data.select("div[class=entry-content]")[0]
        print(img_div)
        return ""


def get_file_path(url):
    array = url.split('/')
    name = array[len(array) - 1]

    return name


if __name__ == "__main__":
    fail_array = []
    for i in range(1, 574):
        response = requests.get(root_url + str(i))

        html = BeautifulSoup(response.text)
        link = parse_html(html)

        file_name = get_file_path(link)
        file_path = "./strips/#" + str(i) + " " + file_name
        print("Downloading strip #%s: %s" % (str(i), file_name))
        if link == "":
            fail_array.append(i)
        try:
            r = requests.get(link)
            with open(file_path, "wb") as code:
                code.write(r.content)
        except:
            pass

    print("Failed: " + str(fail_array))