from bs4 import BeautifulSoup
from pprint import pprint
with open('index.html', mode='rb') as html:
    src = html.read()
soup = BeautifulSoup(src, 'lxml')
tr_list = soup.find(class_='simple-little-table trades-table').find_all('tr')
black_list_of_indexes = [1, 3, 4, 5, 6, 8, 9, 10, 19, 20, 21]
data = []
for i, tr in enumerate(tr_list):
    if i > 1 and i < 260:
        data.append([elem for i, elem in enumerate(tr.text.strip().split('\n')) if i not in black_list_of_indexes ])
    print('end')
pprint(data)