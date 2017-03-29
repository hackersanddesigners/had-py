#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests
from mako.template import Template

url = "https://wiki.hackersanddesigners.nl/mediawiki/api.php?action=parse&page=Hackers_%26_Designers&format=json&disableeditsection=true"
response = requests.get(url)
wikidata = response.json()

wikititle = wikidata['parse']['title']
wikibodytext = wikidata['parse']['text']['*']

def print_headers():
	print ("Content-type: text/html")
	print ("\n\r")

t_home = Template(filename='index.html')

if __name__ == '__main__':

	print_headers()
	print(t_home.render(title=wikititle, bodytext=wikibodytext))
