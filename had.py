#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# this is sample code from @jbg

# import urllib2

# response = urllib2.urlopen("https://wiki.hackersanddesigners.nl/mediawiki/api.php?action=parse&page=Hackers_%26_Designers&format=json&disableeditsection=true") 
# print response.read() 

# response = urllib2.urlopen("https://wiki.hackersanddesigners.nl/mediawiki/api.php?action=ask&query=[[Category:Events]][[Type::Meetup]]%7C?NameOfEvent%7C?OnDate%7C?Venue%7C?Time%7Csort=OnDate%7Corder=descending&format=json") 
# print response.read() 

#response = urllib2.urlopen("https://wiki.hackersanddesigners.nl/mediawiki/api.php?action=ask&query=[[Category:Events]][[Type::Summer Academy]]|?NameOfEvent|?OnDate|?Venue|?Time|sort=OnDate|order=descending&format=json") 
# print response.read() import json import urllib2 

import urllib2
import json

from jinja2 import Environment, FileSystemLoader
import os

url = "https://wiki.hackersanddesigners.nl/mediawiki/api.php?action=parse&page=Hackers_%26_Designers&format=json&formatversion=2&utf8=&disableeditsection=true"
response = urllib2.urlopen(url)
wikidata = json.load(response)

wikititle = wikidata['parse']['title']
wikibodytext = wikidata['parse']['text'].encode('utf-8').strip()

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

def print_html_doc():
	j2_env = Environment(loader=FileSystemLoader(THIS_DIR),
											 trim_blocks=True)
	output = j2_env.get_template('index.html').render(
			title 	 = wikititle,
			bodytext = wikibodytext)
        print output.encode('utf-8').strip()

def print_headers():
	print "Content-type: text/html"
	print "\n\r"

if __name__ == '__main__':

	print_headers()
        print wikibodytext
	#print_html_doc()


