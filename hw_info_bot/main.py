__author__ = 'MikroMan'

import requests

from ark_home_parser import get_html, get_series_table, get_cpu_platforms, get_cpu_series_urls
from cpu_series_parser import get_links
from cpu_parser import get_cpu


webpage_url = "http://ark.intel.com/#@Processors"
server = "irc.freenode.net"


def parse_cpu_specs_to_db(specs):
    pass


def initialize():
    data = requests.get(webpage_url)

    html = get_html(data)

    data = get_series_table(html)

    cpu_platforms = get_cpu_platforms(data)
    cpu_series_list = get_cpu_series_urls(cpu_platforms)

    cpu_urls = get_links(cpu_series_list)

    for array in cpu_urls:
        for key in array:
            link = array[key][1]

            parse_cpu_specs_to_db(get_cpu(link))


if __name__ == "__main__":
    initialize()



