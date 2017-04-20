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
		api_call =  "api.php?"
		intro_options = {'action': 'parse', 'page': 'Hackers_&_Designers', 'format': 'json', 'formatversion': '2'}
		intro_response = requests.get(base_url + folder_url + api_call , params=intro_options)
		wkdata_intro = intro_response.json()

		wkpage_title = wkdata_intro['parse']['title']
		wkintro = wkdata_intro['parse']['text']
		
		# ========================
		#fetch events
		
		category_events = "[[Category:Event]]"
		filters_events = "|?NameOfEvent|?OnDate|?Venue|?Time|sort=OnDate|order=descending"
		today = datetime.date.today()
		today = today.strftime('%Y/%m/%d')

		# upcoming events
	
		date_upevents = "[[OnDate::>" + today + "]]"
		upevents_options = {'action': 'ask', 'query': category_events + date_upevents + filters_events, 'format': 'json', 'formatversion': '2'}

		response_upevents = requests.get(base_url + folder_url + api_call , params=upevents_options)
		wkdata_upevents = response_upevents.json()
		#print(response_upevents.url)
		# past events

		options_pasteve = {'action': 'query', 'generator': 'categorymembers', 'gcmtitle': 'Category:Event', 'format': 'json', 'formatversion': '2'}
		response_pasteve = requests.get(base_url + folder_url + api_call, params=options_pasteve)
		wkdata_pasteve = response_pasteve.json()

		# ========

		def query(request):
			request['action'] = 'query'
			request['format'] = 'json'
			last_continue = {'continue': ''}
			while True:
				req = request.copy()
				req.update(last_continue)
				
				result = requests.get(base_url + folder_url + api_call, params=req).json()
				if 'error' in result:
					raise Error(result['error'])
				if 'warnings' in result:
					print(result['warnings'])
				if 'query' in result:
					yield result['query']
				if 'continue' not in result:
					break
				last_continue = result['continue']

		#ohhh = query(request = response_pasteve.url)
		#print(ohhh.json())
		# ========

		date_pastevents = "[[OnDate::<" + today + "]]"
		options_pastevents = {'action': 'ask', 'query': category_events + date_pastevents + filters_events, 'format': 'json', 'formatversion': '2'}

		response_pastevents = requests.get(base_url + folder_url + api_call , params=options_pastevents)
		wkdata_pastevents = response_pastevents.json()
#		print(response_pastevents.url)

		# =========================
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
		
		# ==========================
		# build template
		return self.render_template('index.html', 
			title=wkpage_title,
			intro=wkintro,
			up_event_list=wkdata_upevents,
			past_event_list=wkdata_pastevents
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
		wikidate = wikimeta[1]['title']

		# fix rel-links to be abs-ones
		soup = BeautifulSoup(wikibodytext, 'html.parser')

#		for a in soup.find_all('a', href=re.compile(r'(\/mediawiki\/.+)')):
#			rel_link = a.get('href')
#			print (rel_link)
			#out_link = urljoin(base_url, rel_link)
			#a['href'] = out_link

		for a in soup.find_all('a', href=re.compile(r'^(?!(?:[a-zA-Z][a-zA-Z0-9+.-]*:|//))')):
			rel_link = a.get('href')
			print(rel_link)
			print('===')
			#out_link = urljoin(base_url, rel_link)
			#print(out_link)
			#print('***')
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

