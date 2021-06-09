from bs4 import BeautifulSoup

with open('index.html', mode='rb') as html:
    src = html.read()
soup = BeautifulSoup(src, 'lxml')
print(soup.find('tr').text)
