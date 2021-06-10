import requests


def get_html(URL):
    response = requests.get(URL).content
    return response

