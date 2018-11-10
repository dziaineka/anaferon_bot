import re

import aiohttp
from bs4 import BeautifulSoup

import regexps


class Medicines:
    def __init__(self):
        self.a_tag_regexp = re.compile(regexps.A_TAGS, re.IGNORECASE)
        self.href_regexp = re.compile(regexps.HREF, re.IGNORECASE)
        self.wiki_regexp = re.compile(regexps.WIKI, re.IGNORECASE)
        self.MAIN_URL = 'http://encyclopatia.ru'
        self.medicines = []

    async def fetch(self, session, url):
        async with session.get(url) as response:
            return await response.text()

    async def get_html(self, url):
        async with aiohttp.ClientSession() as session:
            html = await self.fetch(session, url)
            return html

    def extract_urls_from_a_tags(self, description):
        a_tags = self.a_tag_regexp.findall(description)

        for a in a_tags:
            title = a[2]
            params = a[1]
            a_string = a[0]

            try:
                urls = self.href_regexp.findall(params)

                for url in urls:
                    if self.wiki_regexp.match(url):
                        url = self.MAIN_URL + url

                    replacement = title + ' (' + url + ')'
                    description = description.replace(a_string, replacement)

                if not urls:
                    description = description.replace(a_string, title)

            except IndexError:
                description = description.replace(a_string, title)

        return description

    def delete_tags(self, text, *tags):
        for tag in tags:
            text = text.replace(tag, '')

        return text

    def get_all_drugs(self, html):
        return_list = []

        soup = BeautifulSoup(html, 'lxml')
        div = soup.find('div', id='mw-content-text')
        uls = div.find_all('ul', class_=None)
        alphabet = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
        prev_first_letter = 'А'

        for ul in uls:
            lis = ul.find_all('li', class_=None)

            if lis:
                for drug in lis:
                    description = self.delete_tags(
                        str(drug),
                        '<li>', '</li>', '<b>', '</b>')

                    first_letter = description[0].upper()

                    try:
                        if (alphabet.index(first_letter) <
                                alphabet.index(prev_first_letter)):
                            continue

                        prev_first_letter = first_letter
                    except ValueError:  # название не на русском и пошло оно
                        continue

                    description = self.extract_urls_from_a_tags(description)
                    return_list.append(description)

        return return_list

    async def load_medicine_list(self):
        url = self.MAIN_URL + '/wiki/Расстрельный_список_препаратов'
        html = await self.get_html(url)
        self.medicines = self.get_all_drugs(html)

    def get_descriptions(self, medicine):
        descriptions = []

        for description in self.medicines:
            if medicine.lower() in description.lower():
                descriptions.append(description)

        if not descriptions:
            descriptions.append('Упоминаний этого лекарства нет в списке.')

        return descriptions
