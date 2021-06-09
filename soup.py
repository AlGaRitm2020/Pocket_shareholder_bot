from bs4 import BeautifulSoup
from pprint import pprint
from get_html import get_html


def get_data():
    URL = 'https://smart-lab.ru/q/shares/'

    src = get_html(URL)
    soup = BeautifulSoup(src, 'lxml')
    tr_list = soup.find(class_='simple-little-table trades-table').find_all('tr')
    black_list_of_indexes = [1, 2, 4, 12, 11, 20, 21]
    black_list_of_indexes = []
    data = []
    for i, tr in enumerate(tr_list):
        if 1 < i < 260:
            data.append([elem for i, elem in enumerate(tr.text.split('\n')) if
                         i not in black_list_of_indexes and elem and elem != '+' and '\t' not in elem])
    for i, td in enumerate(data):
        for j, elem in enumerate(td):
            to_float_list = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
            if j in to_float_list:
                try:

                    data[i][j] = float(elem[:-1].replace(' ', ''))
                except:

                    data[i][j] = int(elem)

    return data


# pprint(get_data())
