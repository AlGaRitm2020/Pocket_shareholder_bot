import requests

def get_html(URL):
    response = requests.get(URL).content
    with open('index.html', mode='wb') as html:
        html.write(response)


get_html('https://smart-lab.ru/q/shares/')