import json
import random
import asyncio
import requests
from bs4 import BeautifulSoup
import re
import os

DOMAIN = "https://www.truckscout24.de"


def create_folder():
    if os.path.exists("data"):
        print("Folder exists")
    else:
        os.mkdir("data")


def create_json_file(json_data):
    with open("data/data.json", "w+", encoding="utf-8") as outfile:
        outfile.write(json_data)


def get_pages(html):
    soup = BeautifulSoup(html.text, 'html.parser')
    try:
        # pages = soup.find('div', {'class': 'sc-padding-bottom-m'}).find('ul', {'class': 'sc-pagination'}) --- ??????
        # <ul class="sc-pagination" data-next-text="Weiter" data-previous-text="Zurück"></ul>
        # https://www.truckscout24.de/transporter/gebraucht/kuehl-iso-frischdienst/renault?currentpage=1
        # https://www.truckscout24.de/transporter/gebraucht/kuehl-iso-frischdienst/renault?currentpage=2
        # https://www.truckscout24.de/transporter/gebraucht/kuehl-iso-frischdienst/renault?currentpage=3
        # https://www.truckscout24.de/transporter/gebraucht/kuehl-iso-frischdienst/renault?currentpage=4
        pages = 4
    except:
        pages = 1
    print('Количество найденных страниц: ', pages)
    return pages


def get_html(url):
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0)"
    }
    html = requests.get(url, headers=headers)
    return html


def get_href_car(html) -> str:
    soup = BeautifulSoup(html.text, 'html.parser')
    return DOMAIN + soup.find('div', class_="ls-elem ls-elem-gap").find('div', "ls-titles").find('a').get('href')


def get_img(href, index):
    if os.path.exists(f"./data/{index}"):
        soup = BeautifulSoup(get_html(href).text, 'html.parser')
        img = soup.find_all('img', class_="gallery-picture__image sc-lazy-image lazyload")[:3]
        for i in img:
            img_data = requests.get(i['data-src']).content
            with open(f'./data/{index}/{img.index(i)}.jpg', 'wb') as handler:
                handler.write(img_data)
    else:
        os.mkdir(f"./data/{index}")


# Could make a class
def get_title(html):
    try:
        soup = BeautifulSoup(get_html(html).text, 'html.parser')
        title = soup.find('h1', class_="sc-ellipsis sc-font-xl")
        return title.text
    except:
        return ''


def get_price(html):
    try:
        soup = BeautifulSoup(get_html(html).text, 'html.parser')
        price = soup.find('h2', class_="sc-highlighter-4 sc-highlighter-xl sc-font-bold")
        return int(re.sub(r'[^\d]+', '', price.text))
    except:
        return 0


def get_mileage(html):
    try:
        soup = BeautifulSoup(get_html(html).text, 'html.parser')
        mileage = soup.find('div', class_='itemval', text=re.compile('km'))
        return int(re.sub(r'[^\d]+', '', mileage.text))
    except:
        return 0


def get_color(html):
    try:
        soup = BeautifulSoup(get_html(html).text, 'html.parser')
        color = soup.find("div", attrs={"class": "sc-expandable-box"}).find('ul', attrs={'class': "columns"}).find(
            'div', class_='sc-font-bold', text='Farbe').find_next('div')
        return color.text
    except:
        return ''


def get_power(html):
    try:
        soup = BeautifulSoup(get_html(html).text, 'html.parser')
        power = soup.find("div", attrs={"class": "sc-expandable-box"}).find('ul', attrs={'class': "columns"}).find(
            'div', class_='sc-font-bold', text='Leistung').find_next('div')
        return int(re.sub(r'[^\d\(\)]+|\([^)]*\)', '', power.text))
    except:
        return ''


def get_description(html):
    try:
        soup = BeautifulSoup(get_html(html).text, 'html.parser')
        description = soup.find("div", attrs={"class": "sec-wrap", "data-item-name": "description"}).find('div',
                                                                                                          attrs={
                                                                                                              'class': 'sc-expandable-box__content'}).find(
            "div", attrs={"class": "short-description", "data-type": "description"})
        return description.text
    except:
        return ''


def get_content(list_href):
    data = []
    for href in list_href:
        soup = BeautifulSoup(get_html(href).text, 'html.parser')
        # price = int(
        #     re.sub(r'[^\d]+', '', soup.find('h2', class_="sc-highlighter-4 sc-highlighter-xl sc-font-bold").text))
        # mileage = int(re.sub(r'[^\d]+', '', soup.find('div', class_='itemval', text=re.compile('km')).text))
        # color = soup.find("div", attrs={"class": "sc-expandable-box"}).find('ul',
        #                                                                     attrs={'class': "columns"}).find(
        #     'div', class_='sc-font-bold', text='Farbe').find_next('div').get_text()
        # power = int(re.sub(r'[^\d\(\)]+|\([^)]*\)', '',
        #                    soup.find("div", attrs={"class": "sc-expandable-box"}).find('ul',
        #                                                                                attrs={
        #                                                                                    'class': "columns"}).find(
        #                        'div', class_='sc-font-bold', text='Leistung').find_next('div').get_text()))
        # description = soup.find("div", attrs={"class": "sec-wrap", "data-item-name": "description"}).find('div',
        #                                                                                                   attrs={
        #                                                                                                       'class': 'sc-expandable-box__content'}).find(
        #     "div", attrs={"class": "short-description", "data-type": "description"}).text
        data.append(
            dict(id=list_href.index(href), href=href, title=get_title(href),
                 price=get_price(href),
                 mileage=get_mileage(href),
                 color=get_color(href),
                 power=get_power(href),
                 description=get_description(href),
                 ))
        get_img(href, list_href.index(href))
    return json.dumps({'ads': data}, ensure_ascii=False)


def main():
    create_folder()
    html = get_html("https://www.truckscout24.de/transporter/gebraucht/kuehl-iso-frischdienst/renault")
    pages = get_pages(html)
    list_href = []
    for i in range(1, pages + 1):
        list_href.append(get_href_car(get_html(
            f"https://www.truckscout24.de/transporter/gebraucht/kuehl-iso-frischdienst/renault?currentpage={i}")))
    json_data = get_content(list_href)
    print(json_data)
    create_json_file(json_data)


main()
