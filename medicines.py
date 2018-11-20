import re

import aiohttp
from bs4 import BeautifulSoup

import regexps


class Medicines:
    def __init__(self):
        self.a_tag_regexp = re.compile(regexps.A_TAGS, re.IGNORECASE)
        self.href_regexp = re.compile(regexps.HREF, re.IGNORECASE)
        self.wiki_regexp = re.compile(regexps.WIKI, re.IGNORECASE)
        self.ul_regexp = re.compile(regexps.UL, re.MULTILINE | re.IGNORECASE)
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

    def tags_processing(self, text):
        description = self.delete_tags(
            text,
            '<li>', '</li>', '<b>', '</b>', '<i>', '</i>',
            '</sup>')

        description = description.replace('<del>', '(')
        description = description.replace('</del>', ')')

        description = description.replace('<sup>', '^')

        return description

    def process_http_description(self, text):
        description = self.tags_processing(text)
        description = self.extract_urls_from_a_tags(description)

        return description

    def split_ul(self, text):
        uls = self.ul_regexp.findall(text)
        return_list = []

        for ul in uls:
            text = text.replace(ul, '')
            ul = self.delete_tags(ul, '<ul>', '</ul>')
            return_list.append(ul)

        return_list.append(text)

        return return_list

    def get_all_drugs(self, html):
        return_list = []

        soup = BeautifulSoup(html, 'lxml')
        div = soup.find('div', id='mw-content-text')
        uls = div.find_all('ul', class_=None)

        for ul in uls:
            lis = ul.find_all('li', class_=None)

            if lis:
                for drug in lis:
                    description = self.process_http_description(str(drug))
                    return_list.append(description)

        # по какой-то мне неведомой причине попадаются склеенные позиции
        # попробую их расклеить
        temp_list = []
        return_list.sort()

        for description in return_list:
            descrs = self.split_ul(description)

            while return_list.remove(description):
                pass

            for desc in descrs:
                temp_list.append(desc)

        return_list.extend(temp_list)
        return_list = list(set(return_list))

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
