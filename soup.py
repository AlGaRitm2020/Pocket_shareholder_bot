from bs4 import BeautifulSoup
from pprint import pprint
from get_html import get_html


def get_data():
    URL = 'https://smart-lab.ru/q/shares/'

    src = get_html(URL)
    soup = BeautifulSoup(src, 'lxml')
    tr_list = soup.find(class_='simple-little-table trades-table').find_all('tr')
    data = {}
    for i, tr in enumerate(tr_list):
        if 1 < i < 260:
            company_name = tr.text.split('\n')[3]
            data[company_name] = [elem for i, elem in enumerate(tr.text.split('\n'))]

    for i, company_name in enumerate(data):
        if len(data[company_name]) == 28:
            for _ in range(4):
                del data[company_name][5]
        for j, elem in enumerate(data[company_name]):
            to_float_list = [8, 13, 14, 15, 16, 17, 18, 19, 20]
            if j in to_float_list:
                if elem and '\t' not in elem:
                    try:
                        data[company_name][j] = float(elem[:-1].replace(' ', ''))
                    except:

                        data[company_name][j] = int(elem)
                else:
                    data[company_name][j] = 0.001

    return data


pprint(get_data())
