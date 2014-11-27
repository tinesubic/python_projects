__author__ = 'MikroMan'

import requests
from bs4 import BeautifulSoup

webpage_urls = ["http://ark.intel.com/products/27451/Intel-Pentium-4-Processor-506-1M-Cache-2_66-GHz-533-MHz-FSB",
                "http://ark.intel.com/products/75123/Intel-Core-i7-4770K-Processor-8M-Cache-up-to-3_90-GHz"]
http = "http://"


def get_html(response):
    return BeautifulSoup(response.text)


def get_cpu_specs_html(webpage_html):
    return webpage_html.find(id="specifications-pane")


def cut_url(url):
    url_array = url[7:].split('/')
    url_array.pop(len(url_array) - 1)
    return http + "/".join(url_array) + "/"


def parse_cpu_html_to_dict(html_block):
    specs = {}
    spec_table = html_block.select('tr[id]')
    if len(spec_table) > 0:
        spec_table.pop(0)

    for f in spec_table:
        key = f['id']

        selection_text = f.select('span')
        value = f.select('td[class=rc]')[0].string
        text = ""
        if len(selection_text) > 0:
            text = selection_text[0].string
        values = [text, value]
        specs[key] = values

    return specs


def get_cpu(url):
    data = requests.get(url)

    html = get_html(data)

    specs_html = get_cpu_specs_html(html)

    data = parse_cpu_html_to_dict(specs_html)

    return data





