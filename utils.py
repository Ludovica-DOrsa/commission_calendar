import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import numpy as np


def get_info_divs(divs: list, total_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts key info from divs
    :param divs:
    :param total_df:
    :return:
    """
    for div in divs:
        dicti = {}
        days = div.find("span", {"class": 'ecl-date-block__day'})
        if len(days) > 0:
            dicti['Day'] = days.text
        else:
            dicti['Day'] = np.NaN
        months = div.find("abbr", {"class": 'ecl-date-block__month'})
        if len(months) > 0:
            dicti['Month'] = months.attrs['title']
        else:
            dicti['Month'] = np.NaN

        years = div.find("span", {"class": 'ecl-date-block__year'})
        if len(years) > 0:
            dicti['Year'] = years.text
        else:
            dicti['Year'] = np.NaN
        texts = div.find("h1", {"class": 'ecl-content-block__title'})
        if len(texts) > 0:
            dicti['Text'] = texts.text
        else:
            dicti['Text'] = np.NaN

        secondary = div.find_all("span", {"class": 'ecl-content-block__secondary-meta-label'})
        if len(secondary) > 0:
            if "," in secondary[0].text:
                dicti['Location'] = secondary[0].text
            else:
                dicti['Commissioner'] = secondary[0].text
        if len(secondary) > 1:
            if "," in secondary[1].text:
                dicti['Location'] = secondary[1].text
            else:
                dicti['Commissioner'] = secondary[1].text
        else:
            dicti['Location'] = 'None'
            dicti['Commissioner'] = 'None'

        dicti = pd.DataFrame([dicti])
        total_df = pd.concat([total_df, dicti], ignore_index=True)
    return total_df


def get_link(link: str):
    """
    Given a webpage link, returns the webpage
    :param link:
    :return:
    """
    try:
        webpage = requests.get(link, verify=False)
    except ConnectionError:
        time.sleep(5)
        webpage = requests.get(link, verify=False)
    return webpage


def get_info(link: str) -> pd.DataFrame:
    """
    Obtains information from webpage
    :param link:
    :return:
    """
    webpage = get_link(link)
    html = webpage.text
    soup = BeautifulSoup(html, features="html.parser")
    divs = soup.find_all("div", {"class": 'ecl-content-item-block__item ecl-u-mb-l ecl-col-12'})
    divs = divs + soup.find_all("div", {"class": 'ecl-content-item-block__item ecl-u-mb-l ecl-col-12 '
                                                 'last-item-column last-item'})
    total_df = pd.DataFrame()
    total_df = get_info_divs(divs, total_df)
    page_n = 0
    while page_n < 15:
        page_n = page_n + 1
        link_page = link + f'&page={page_n}'
        page_n = page_n + 1
        webpage = get_link(link_page)
        html = webpage.text
        soup = BeautifulSoup(html, features="html.parser")
        divs = soup.find_all("div", {"class": 'ecl-content-item-block__item ecl-u-mb-l ecl-col-12'})
        divs = divs + soup.find_all("div", {"class": 'ecl-content-item-block__item ecl-u-mb-l ecl-col-12 '
                                                     'last-item-column last-item'})
        total_df = get_info_divs(divs, total_df)
    return total_df
