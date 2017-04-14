import os
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.utils import redirect
import requests
import datetime
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
from jinja2 import Environment, FileSystemLoader


class had(object):

	def __init__(self):
		template_path = os.path.join(os.path.dirname(__file__), 'templates')
		self.jinja_env = Environment(loader=FileSystemLoader(template_path),
																 autoescape=True)
		self.url_map = Map([
			Rule('/', endpoint='home'),
			Rule('/<pageid>', endpoint='article')
		])
		
	def on_home(self, request):
		
		#fetch intro
		base_url = "http://wikidev.hackersanddesigners.nl/"
		folder_url = "mediawiki/"
		options = {'action': 'parse', 'page': 'Hackers_&_Designers' , 'format': 'json', 'formatversion': '2'}
		intro_url = requests.get(base_url + folder_url + 'api.php?', params=options)
		wkdata_intro = intro_url.json()
		print(wkdata_intro)

		wktitle = wkdata_intro['parse']['title']
		wkintro = wkdata_intro['parse']['text']

		#fetch upcoming events
		today = datetime.date.today()
		today = today.strftime('%Y/%m/%d')
		query = "api.php?action=ask&query=[[Category:Events]]"
		date = "[[OnDate::>" + today + "]]"
		options = "|?NameOfEvent|?OnDate|?Venue|?Time|sort=OnDate|order=descending"
		url_format = "&format=json&formatversion=2"
		url_up_events = base_url + query + date + options + url_format
		print(url_up_events)

		response_up_event_list = requests.get(url_up_events)
		wkdata_up_event_list = response_up_event_list.json()

		#fetch upcoming events
		date = "[[OnDate::<" + today + "]]"
		keep_fetching = "&continue="
		url_past_events = base_url + query + date + options + url_format + keep_fetching
		print(url_past_events)

		response_past_event_list = requests.get(url_past_events)
		wkdata_past_event_list = response_past_event_list.json()

		# fix rel-links to be abs-ones
		soup = BeautifulSoup(wkintro, 'html.parser')

		for a in soup.find_all('a', href=re.compile(r'^(?!(?:[a-zA-Z][a-zA-Z0-9+.-]*:|//))')):
			rel_link = a.get('href')
			out_link = urljoin(base_url, rel_link)
			a['href'] = out_link

		for img in soup.find_all('img', src=re.compile(r'^(?!(?:[a-zA-Z][a-zA-Z0-9+.-]*:|//))')):
			rel_link = img.get('src')
			out_link = urljoin(base_url, rel_link)
			img['src'] = out_link

		wkintro = soup

		#build template
		return self.render_template('index.html', 
			title=wktitle,
			intro=wkintro,
			up_event_list=wkdata_up_event_list,
			past_event_list=wkdata_past_event_list
		)

	def on_article(self, request, pageid):
		
		#fetch content
		base_url = "http://wikidev.hackersanddesigners.nl/"
		folder_url = "mediawiki/"
		url_action = "api.php?action=parse&page="
		url_query_pageid = quote(pageid)
		url_query_format = "&format=json&formatversion=2&disableeditsection=true"

		url_fetch_page_content = base_url + folder_url + url_action + url_query_pageid + url_query_format
		print(url_fetch_page_content)
		response_content = requests.get(url_fetch_page_content)
		wikidata = response_content.json()

		wikititle = wikidata['parse']['title']
		wikibodytext = wikidata['parse']['text']
		
		wikimeta = wikidata['parse']['links']
		wikidate = wikimeta[4]['title']

		# fix rel-links to be abs-ones
		soup = BeautifulSoup(wikibodytext, 'html.parser')

		for a in soup.find_all('a', href=re.compile(r'(\/mediawiki\/.+)')):
			rel_link = a.get('href')
			print (rel_link)
			#out_link = urljoin(base_url, rel_link)
			#a['href'] = out_link

		for img in soup.find_all('img', src=re.compile(r'^(?!(?:[a-zA-Z][a-zA-Z0-9+.-]*:|//))')):
			src_rel_link = img.get('src')
			srcset_rel_link = img.get('srcset')
			if (src_rel_link):
				out_link = urljoin(base_url, src_rel_link)
				img['src'] = out_link
			if (srcset_rel_link):
				srcset_list = re.split(r'[,]\s*', srcset_rel_link)
				srcset_lu = srcset_list
				srcset_list[:] = [urljoin(base_url, srcset_i) for srcset_i in srcset_list]
				srcset_s = ', '.join(srcset_lu)
				img['srcset'] = srcset_s
			
			# get rid of <a>s wrapping <img>s
			a_img = img.find_parent("a")
			a_img.unwrap()

		# delete wiki infobox
		infobox = soup.find('table')
		infobox.decompose()

		wikibodytext = soup

		#build template
		return self.render_template('article.html',
			title=wikititle,
			date=wikidate,
			bodytext=wikibodytext
		)

	def error_404(self):
		response = self.render_template('404.html')
		response.status_code = 404
		return response

	def render_template(self, template_name, **context):
		t = self.jinja_env.get_template(template_name)
		return Response(t.render(context), mimetype='text/html')

	def dispatch_request(self, request):
		adapter = self.url_map.bind_to_environ(request.environ)
		try:
			endpoint, values = adapter.match()
			return getattr(self, 'on_' + endpoint)(request, **values)
		except NotFound as e:
			return self.error_404()
		except HTTPException as e:
			return e

	def wsgi_app(self, environ, start_response):
		request = Request(environ)
		response = self.dispatch_request(request)
		return response(environ, start_response)

	def __call__(self, environ, start_response):
		return self.wsgi_app(environ, start_response)

	
def create_app(with_assets=True):
	app = had()
	if with_assets:
		app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
			'/assets': os.path.join(os.path.dirname(__file__), 'assets')
		})
	return app
	
if __name__ == '__main__':
	from werkzeug.serving import run_simple
	app = create_app()
	run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)

