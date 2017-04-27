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
      Rule('/<page_title>', endpoint='section'),
      Rule('/<section_title>/<page_title>', endpoint='article')
    ])

  # ===========
  # nav
  def nav():
    base_url = "http://wikidev.hackersanddesigners.nl/"
    folder_url = "mediawiki/"
    api_call =  "api.php?"

    nav_options = {'action': 'ask', 'query': '[[Concept:+]]', 'format': 'json', 'formatversion': '2', 'disableeditsection': 'true'}
    response_nav = requests.get(base_url + folder_url + api_call , params=nav_options)
    wk_nav = response_nav.json()

    return wk_nav

  # ==========
  # home	
  def on_home(self, request, wk_nav=nav()):
    base_url = "http://wikidev.hackersanddesigners.nl/"
    folder_url = "mediawiki/"
    api_call =  "api.php?"

    # fetch intro
    intro_options = {'action': 'parse', 'pageid': '29', 'format': 'json', 'formatversion': '2', 'disableeditsection': 'true'}
    intro_response = requests.get(base_url + folder_url + api_call , params=intro_options)
    wkdata_intro = intro_response.json()

    wk_title = wkdata_intro['parse']['title']
    wk_intro = wkdata_intro['parse']['text']

    # fix rel-links to be abs-ones
    soup_wk_intro = BeautifulSoup(wk_intro, 'html.parser')

    for a in soup_wk_intro.find_all('a', href=re.compile(r'^(?!(?:[a-zA-Z][a-zA-Z0-9+.-]*:|//))')):
      rel_link = a.get('href')
      out_link = urljoin(base_url, rel_link)
      a['href'] = out_link

    for img in soup_wk_intro.find_all('img', src=re.compile(r'^(?!(?:[a-zA-Z][a-zA-Z0-9+.-]*:|//))')):
      rel_link = img.get('src')
      out_link = urljoin(base_url, rel_link)
      img['src'] = out_link

    wk_intro = soup_wk_intro

    # events
    category_events = "[[Category:Event]]"
    filters_events = "|?NameOfEvent|?OnDate|?Venue|?Time|sort=OnDate|order=descending"
    today = datetime.date.today()
    today = today.strftime('%Y/%m/%d')

    # attempt to get all event pages recursively (failing atm)
    options_allevents = {'action': 'query', 'generator': 'categorymembers', 'gcmtitle': 'Category:Event', 'format': 'json', 'formatversion': '2', 'disableeditsection': 'true'}
    response_allevents = requests.get(base_url + folder_url + api_call, params=options_allevents)
    wkdata_allevents = response_allevents.json()

    # get `pageid` and put it in a list
    ev_pages = wkdata_allevents['query']['pages']
    ev_pageid_list = []
    for dict in ev_pages:
      ev_list = list(dict.items())
      ev_list = ev_list[0][1]
      ev_pageid_list.append(ev_list)

    # ===============
    # upcoming events
    date_upevents = "[[OnDate::>" + today + "]]"
    upevents_options = {'action': 'ask', 'query': category_events + date_upevents + filters_events, 'format': 'json', 'formatversion': '2', 'disableeditsection': 'true'}
    response_upevents = requests.get(base_url + folder_url + api_call , params=upevents_options)
    wkdata_upevents = response_upevents.json()

    for item in wkdata_upevents['query']['results'].items(): 
      upevents_title = item[1]['printouts']['NameOfEvent'][0]['fulltext']
      
      upevents_introtext_options = {'action': 'parse', 'page': upevents_title, 'format': 'json', 'formatversion': '2', 'disableeditsection': 'true'}
      response_introtext_upevents = requests.get(base_url + folder_url + api_call , params=upevents_introtext_options)
      wkdata_introtext_upevents = response_introtext_upevents.json()

      wkdata_text_upevents = wkdata_introtext_upevents['parse']['text']

      soup_wk_introtext = BeautifulSoup(wkdata_text_upevents, 'html.parser')
      p_intro = soup_wk_introtext.p

      # add custom `intro_text` dict to `wkdata_upevents`
      item[1]['printouts']['intro_text'] = p_intro

    # past events
    date_pastevents = "[[OnDate::<" + today + "]]"
    options_pastevents = {'action': 'ask', 'query': category_events + date_pastevents + filters_events, 'format': 'json', 'formatversion': '2', 'disableeditsection': 'true'}
    response_pastevents = requests.get(base_url + folder_url + api_call , params=options_pastevents)
    wkdata_pastevents = response_pastevents.json()

    # for item in wkdata_pastevents['query']['results'].items(): 
      # pastevents_title = item[1]['printouts']['NameOfEvent'][0]['fulltext']

      # pastevents_introtext_options = {'action': 'parse', 'page': pastevents_title, 'format': 'json', 'formatversion': '2'}
      # response_introtext_pastevents = requests.get(base_url + folder_url + api_call , params=pastevents_introtext_options)
      # wkdata_introtext_pastevents = response_introtext_pastevents.json()
      # print(response_introtext_pastevents.url)

      # wkdata_text_pastevents = wkdata_introtext_pastevents['parse']['text']
      # soup_wk_introtext = BeautifulSoup(wkdata_text_pastevents, 'html.parser')
      # p_intro = soup_wk_introtext.p

      # # add custom `intro_text` dict to `wkdata_upevents`
      # item[1]['printouts']['intro_text'] = p_intro

    # ==========================
    # build template
    return self.render_template('index.html',
                                nav=wk_nav,
                                title=wk_title,
                                intro=wk_intro,
                                up_event_list=wkdata_upevents,
                                past_event_list=wkdata_pastevents
                                )

  def on_section(self, request, page_title, wk_nav=nav()):
    base_url = "http://wikidev.hackersanddesigners.nl/"
    folder_url = "mediawiki/"
    api_call =  "api.php?"

    # fetch page-content
    page_head_options = {'action': 'parse', 'page': 'Concept:' + page_title, 'format': 'json', 'formatversion': '2', 'disableeditsection': 'true'}
    response_head = requests.get(base_url + folder_url + api_call, params=page_head_options)
    wkdata_head = response_head.json()
    wk_title = wkdata_head['parse']['title']
    
    # fetch page-metadata
    category_events = "[[Category:Event]]"
    page_meta_filter = "|?PeopleOrganisations"
    page_meta_options = {'action': 'browsebysubject', 'subject': page_title, 'format': 'json', 'formatversion': '2', 'disableeditsection': 'true'}
    response_meta = requests.get(base_url + folder_url + api_call, params=page_meta_options)
    wkdata_meta = response_meta.json()

    # fetch page-content
    page_content_options = {'action': 'ask', 'query': '[[Concept:' + page_title + ']]', 'format': 'json', 'formatversion': '2', 'disableeditsection': 'true'}
    response_content = requests.get(base_url + folder_url + api_call, params=page_content_options)
    wkdata_content = response_content.json()

    #build template
    return self.render_template('section.html',
                                nav=wk_nav,
                                title=wk_title,
                                wkdata=wkdata_content
                                )

  # ===========
  # article
  def on_article(self, request, page_title, section_title, wk_nav=nav()):
    base_url = "http://wikidev.hackersanddesigners.nl/"
    folder_url = "mediawiki/"
    api_call =  "api.php?"

    # fetch page-content
    page_options = {'action': 'parse', 'page': page_title, 'format': 'json', 'formatversion': '2', 'disableeditsection': 'true'}
    response_content = requests.get(base_url + folder_url + api_call, params=page_options)
    wk_data = response_content.json()
    print(response_content.url)
    
    wk_title = wk_data['parse']['title']
    wk_bodytext = wk_data['parse']['text']

    wk_meta = wk_data['parse']['links']
    if wk_meta:
      wk_date = wk_meta[1]['title']

    # fix rel-links to be abs-ones
    soup_bodytext = BeautifulSoup(wk_bodytext, 'html.parser')

    for a in soup_bodytext.find_all('a', href=re.compile(r'^(?!(?:[a-zA-Z][a-zA-Z0-9+.-]*:|//))')):
      rel_link = a.get('href')
      rel_link = rel_link.rsplit('/', 1)
      a['href'] = rel_link[1]

    for img in soup_bodytext.find_all('img', src=re.compile(r'^(?!(?:[a-zA-Z][a-zA-Z0-9+.-]*:|//))')):
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
    infobox = soup_bodytext.find('table')
    if infobox:
      infobox.decompose()
    
    wk_bodytext = soup_bodytext

    #build template
    return self.render_template('article.html',
                                nav=wk_nav,
                                title=wk_title,
                                date=wk_date,
                                bodytext=wk_bodytext
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
