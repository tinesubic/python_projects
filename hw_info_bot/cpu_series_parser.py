__author__ = 'MikroMan'

import requests
from bs4 import BeautifulSoup

attributes = []
root_url = "http://ark.intel.com"


def get_html(response):
    return BeautifulSoup(response.text)


def make_url(url):
    return root_url + url


def get_cpu_table(webpage_html, url):
    tab = "tabs-" + get_tag(url)
    a = [webpage_html.find(id=tab)]

    if a[0] is None:
        a = (webpage_html.select("div[class=main-inner]"))

    return a


def get_attr_names(inner_html_block):
    names = []
    attrs = inner_html_block[0].select('thead')[0].select('th')
    attrs.pop(0)

    for attr in attrs:
        name = str(attr.string)
        names.append(name.strip(" \n\r"))

    return names


# TODO implement getting product codes for unique ids and fast search in DB

def get_cpu_body(inner_html_block):
    file = inner_html_block[0].select('tbody')[0].select('tr')

    return file


def get_tag(url):
    return url.split('@')[1]


def get_cpu_name(string):
    return string[0]


def get_cpus(cpu_list):
    cpus = {}

    for cpu in cpu_list:
        data = cpu.select('td')
        # product_code = cpu.select('a')[0]['data-product-id']

        link = make_url(cpu.select('a')[1]['href'])
        name = get_cpu_name(cpu.select('a')[1].contents)
        data.pop(0)
        data.pop(0)
        values = [name, link]

        for value in data:
            if str(value.string) != 'NoneType':

                values.append(str(value.string).strip(" \r\n"))
            else:
                values.append("")

        cpus[name] = values

    return cpus


def get_links(array):
    file = []
    for key in array:
        print(key)

        for series_key in array[key]:
            ser = array[key][series_key]
            # print(ser)

            data = requests.get(ser)

            html = get_html(data)

            cpu_table = get_cpu_table(html, ser)

            #attributes = get_attr_names(cpu_table)
            #attributes[len(attributes)-1]= "Processor Graphics"
            ##print(attributes)

            cpu_list = get_cpu_body(cpu_table)
            cpus = get_cpus(cpu_list)
            file.append(cpus)
            print("In " + series_key + " : " + str(len(cpus)))

    return file












