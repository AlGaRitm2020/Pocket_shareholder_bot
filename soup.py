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
            data[company_name.upper()] = [elem for i, elem in enumerate(tr.text.split('\n'))]

    for i, company_name in enumerate(data):
        if len(data[company_name]) == 28:
            for _ in range(4):
                del data[company_name][5]
        for j, elem in enumerate(data[company_name]):
            to_float_list = [8, 12, 13, 14, 15, 16, 17, 18, 19, 20]
            if j in to_float_list:
                if elem and '\t' not in elem:
                    try:
                        data[company_name][j] = float(elem[:-1].replace(' ', ''))
                    except:

                        data[company_name][j] = int(elem)
                else:
                    data[company_name][j] = 0.001
    for i, company_name in enumerate(data):
        data[company_name] = {
            'upload_time': data[company_name][2],
            'name': company_name,
            'cost': data[company_name][8],
            'volume': data[company_name][12],
            'weekly_growth': data[company_name][13],
            'monthly_growth': data[company_name][14],
            'yearly_growth': data[company_name][15],
            '12_monthly_growth': data[company_name][16],
            'delta_volume': data[company_name][19],

        }
    return data


pprint(get_data())
