import json
import requests
from bs4 import BeautifulSoup

url = 'https://andromeda.eu.org/xbmc/'
ext = 'zip'

def listFD(url, ext=''):
    page = requests.get(url).text
    print page
    soup = BeautifulSoup(page, 'html.parser')
    return [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]


androAddons = listFD(url, ext)


for file in androAddons:
    print file

print ""

addons = json.load(open('addons.json'))

print addons

