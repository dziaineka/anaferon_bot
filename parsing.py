import requests
from bs4 import BeautifulSoup


def get_html(url):
    response = requests.get(url)
    return response.text


def get_all_drugs(html):
    return_list = []

    soup = BeautifulSoup(html, 'lxml')
    div = soup.find('div', id='mw-content-text')
    uls = div.find_all('ul', class_=None)

    for ul in uls:
        lis = ul.find_all('li', class_=None)

        if lis:
            for drug in lis:
                description = str(drug)
                description = description.replace('<li>', '')
                description = description.replace('</li>', '')
                # TODO: заменить тэги со ссылками на ссылки

                return_list.append(description)

    return return_list


def main():
    html = get_html(
        'http://encyclopatia.ru/wiki/Расстрельный_список_препаратов')

    medicines = get_all_drugs(html)

    for medicine in medicines:
        print(medicine)


if __name__ == '__main__':
    main()
