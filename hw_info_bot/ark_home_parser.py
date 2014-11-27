__author__ = 'MikroMan'

from bs4 import BeautifulSoup

root_url = "http://ark.intel.com"


def get_html(response):
    return BeautifulSoup(response.text)


def get_series_table(webpage_html):
    return webpage_html.find(id='Processors-pane')


def make_url(url):
    return root_url + url


def get_cpu_platforms(cpu_html_table):
    series = cpu_html_table.select('div[class=innerNavPanel]')

    return series


def get_cpu_series_urls(platforms):
    models = {}
    for platform in platforms:
        platform_key = platform.select('h3')[0].string
        models[platform_key] = {}
        cpus = platform.select('a')
        for cpu in cpus:
            link = cpu['href']
            series = cpu.string
            models[platform_key][series] = make_url(link)
    return models

