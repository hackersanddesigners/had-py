import os
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.utils import redirect
import requests
from requests_futures.sessions import FuturesSession
import pprint
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
      Rule('/p/<page_title>', endpoint='article'),
      Rule('/s/<section_title>', endpoint='section'),
      Rule('/s/<section_title>/p/<page_title>', endpoint='article')
    ])

  # ===========
  # navigation

  def nav_main():
    base_url = "http://wikidev.hackersanddesigners.nl/"
    folder_url = "mediawiki/"
    api_call =  "api.php?"
    
    filters_nav_main = "|?MainNavigation|order=descending"
    nav_main_options = {'action': 'ask', 'query': '[[Concept:MainNavigation]]' + filters_nav_main, 'format': 'json', 'formatversion': '2'}
    response_nav_main = requests.get(base_url + folder_url + api_call , params=nav_main_options)
    wk_nav_main = response_nav_main.json()
    return wk_nav_main

  def nav_sections():
    base_url = "http://wikidev.hackersanddesigners.nl/"
    folder_url = "mediawiki/"
    api_call =  "api.php?"
    
    nav_sections_options = {'action': 'ask', 'query': '[[Concept:+]]', 'format': 'json', 'formatversion': '2'}
    response_nav_sections = requests.get(base_url + folder_url + api_call , params=nav_sections_options)
    wk_nav_sections = response_nav_sections.json()
    
    # delete MainNavigation concept from the dict
    del wk_nav_sections['query']['results']['Concept:MainNavigation']
    
    return wk_nav_sections

  # ==========
  # home	
  def on_home(self, request, wk_nav_main=nav_main(), wk_nav_sections=nav_sections()):
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

    # delete wiki infobox
    infobox = soup_wk_intro.find('table')
    if infobox:
      infobox.decompose()

    # get rid of <a>s wrapping <img>s
      a_img = img.find_parent("a")
      a_img.unwrap()

    wk_intro = soup_wk_intro
    
    # ======
    # events
    
    def query(request):
      request['action'] = 'query'
      request['format'] = 'json'
      request['formatversion'] = '2'
      lastContinue = {'continue': ''}
      while True:
        # clone original request
        req = request.copy()
        # modify it with the values returned in the 'continue' section of the last result
        req.update(lastContinue)
        # call API
        result = requests.get(base_url + folder_url + api_call, params=req).json()
        if 'error' in result:
          raise Error(result['error'])
        if 'warnings' in result:
          print(result['warnings'])
        if 'query' in result:
          yield result['query']
        if 'continue' not in result:
          break
        lastContinue = result['continue']
    
    event_title_list = []
    for result in query({'generator': 'categorymembers', 'gcmtitle': 'Category:Event'}):
      for item in result['pages']:
        event_title_list.append(item['title'])
    
    # print(event_title_list)

    # def query(request):
    #   request['action'] = 'askargs'
    #   request['format'] = 'json'
    #   request['formatversion'] = '2'
    #   lastContinue = {'query-continue-offset': ''}
    #   while True:
    #     # clone original request
    #     req = request.copy()
    #     # modify it with the values returned in the 'continue' section of the last result
    #     req.update(lastContinue)
    #     # call API
    #     result = requests.get(base_url + folder_url + api_call, params=req).json()
    #     if 'error' in result:
    #       raise Error(result['error'])
    #     if 'warnings' in result:
    #       print(result['warnings'])
    #     if 'query' in result:
    #       yield result['query']
    #     if 'continue' not in result:
    #       break
    #     lastContinue = result['continue']
    
    # category_events = "[[Category:Event]]"
    # filters_events = "|?NameOfEvent|?OnDate|?Venue|?Time|sort=OnDate|order=descending"
    # today = datetime.date.today()
    # today = today.strftime('%Y/%m/%d')

    # event_title_list = []
    # for result in query({'conditions': 'Category:Event', 'printouts': 'NameOfEvent|OnDate|Venue|Time', 'parameters': 'sort=OnDate|order=desc'}):
    #   print(result)
    #   for item in result['results']:
    #     event_title_list.append(item)
    
    # print(event_title_list)

    # fetch event's metadata
    event_list = []
   
    for event_title in event_title_list:
      category_events = "[[Category:Event]]"
      page_meta_options = {'action': 'browsebysubject', 'subject': event_title, 'format': 'json', 'formatversion': '2'}
      response_meta = requests.get(base_url + folder_url + api_call, params=page_meta_options)
      wkdata_meta = response_meta.json()
      
      event_item = []
      # print('===')
      for item in wkdata_meta['query']['data']:
        if 'NameOfEvent' in item['property']:
          # event_tl = {'Title': item['dataitem'][0]['item']}
          tt = item['dataitem'][0]['item']
          tt = re.sub(r'#\d#', '', tt)
          event_item.append(tt)
        if 'OnDate' in item['property']:
          # event_dt = {'OnDate': item['dataitem'][0]['item']}
          dt = item['dataitem'][0]['item']
          dt = re.sub(r'#\d#', '', dt)
          event_item.append(dt)
    
      event_list.append(event_item)
      print(event_list)

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

    # ===========
    # past events
    date_pastevents = "[[OnDate::<" + today + "]]"
    options_pastevents = {'action': 'ask', 'query': category_events + date_pastevents + filters_events, 'format': 'json', 'formatversion': '2', 'disableeditsection': 'true'}
    response_pastevents = requests.get(base_url + folder_url + api_call , params=options_pastevents)
    wkdata_pastevents = response_pastevents.json()

    # build template
    return self.render_template('intro.html',
                                nav_main=wk_nav_main,
                                nav_sections=wk_nav_sections,
                                title=wk_title,
                                intro=wk_intro,
                                up_event_list=wkdata_upevents,
                                past_event_list=wkdata_pastevents
                                )

  def on_section(self, request, section_title=None, page_title=None, wk_nav_main=nav_main(), wk_nav_sections=nav_sections()):
    base_url = "http://wikidev.hackersanddesigners.nl/"
    folder_url = "mediawiki/"
    api_call =  "api.php?"

    # fetch page-content
    page_head_options = {'action': 'parse', 'page': 'Concept:' + section_title, 'format': 'json', 'formatversion': '2'}
    response_head = requests.get(base_url + folder_url + api_call, params=page_head_options)
    wkdata_head = response_head.json()
    wk_title = wkdata_head['parse']['title']

    def query(request):
      request['action'] = 'askargs'
      request['format'] = 'json'
      request['formatversion'] = '2'
      lastContinue = {'query-continue-offset': ''}
      while True:
        # clone original request
        req = request.copy()
        # modify it with the values returned in the 'continue' section of the last result
        req.update(lastContinue)
        # call API
        result = requests.get(base_url + folder_url + api_call, params=req).json()
        if 'error' in result:
          raise Error(result['error'])
        if 'warnings' in result:
          print(result['warnings'])
        if 'query' in result:
          yield result['query']
        if 'continue' not in result:
          break
        lastContinue = result['continue']
    
    # make section_items list by fetching item's title and img (if any)
    for result in query({'conditions': 'Concept:' + section_title, 'printouts': 'Modification date'}):
     
      wk_section_items = []
      for item in result['results'].items():
        section_item_title = item[1]['fulltext']
        wk_section_items.append(section_item_title)

        # fetch section item's content
        item_introtext_options = {'action': 'parse', 'page': section_item_title, 'format': 'json', 'formatversion': '2', 'disableeditsection': 'true'}
        response_introtext_item = requests.get(base_url + folder_url + api_call , params=item_introtext_options)
        wkdata_introtext_item = response_introtext_item.json()

        wkdata_text_item = wkdata_introtext_item['parse']['text']
        
        # get section item's img
        soup_wk_introtext = BeautifulSoup(wkdata_text_item, 'html.parser')
        if soup_wk_introtext.img:
          cover_img = soup_wk_introtext.img

          src_rel_link = cover_img.get('src')
          srcset_rel_link = cover_img.get('srcset')
          if src_rel_link:
            out_link = urljoin(base_url, src_rel_link)
            cover_img['src'] = out_link
          if srcset_rel_link:
            srcset_list = re.split(r'[,]\s*', srcset_rel_link)
            srcset_lu = srcset_list
            srcset_list[:] = [urljoin(base_url, srcset_i) for srcset_i in srcset_list]
            srcset_s = ', '.join(srcset_lu)
            cover_img['srcset'] = srcset_s
        else:
          cover_img = ''

        # add `cover_img` to `wk_section_items`
        wk_section_items.append(cover_img)

    # turn list into tuple w/ zip-zip
    wk_section_items = list(zip(*[iter(wk_section_items)]*2))


    # build template
    return self.render_template('section.html',
                                nav_main=wk_nav_main,
                                nav_sections=wk_nav_sections,
                                title=wk_title,
                                section_items=wk_section_items
                                )

  # ===========
  # article
  def on_article(self, request, page_title=None, section_title=None, wk_nav_main=nav_main(), wk_nav_sections=nav_sections()):
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

    # fetch page-metadata for Event
    if wk_data['parse']['categories'][0]['category'] == 'Event':
      category_events = "[[Category:Event]]"
      page_meta_filter = "|?PeopleOrganisations"
      page_meta_options = {'action': 'browsebysubject', 'subject': page_title, 'format': 'json', 'formatversion': '2'}
      response_meta = requests.get(base_url + folder_url + api_call, params=page_meta_options)
      wkdata_meta = response_meta.json()

      def extract_metadata(query):
        list = []
        for item in query:
          str = item['item']
          # strip out weird hash at the end (see why https://www.semantic-mediawiki.org/wiki/Ask_API#BrowseBySubject)
          item = re.sub(r'#\d#', '', str).replace('_', ' ')
          list.append(item)
        return list

      wk_date = wkdata_meta['query']['data'][1]['dataitem']
      wk_date = extract_metadata(wk_date)

      wk_peopleorgs = wkdata_meta['query']['data'][2]['dataitem']
      wk_peopleorgs = extract_metadata(wk_peopleorgs)

      wk_time = wkdata_meta['query']['data'][4]['dataitem']
      wk_time = extract_metadata(wk_time)

      wk_place = wkdata_meta['query']['data'][6]['dataitem']
      wk_place = extract_metadata(wk_place)
    
    else:
      wk_date = None
      wk_peopleorgs = None
      wk_time = None
      wk_place = None

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

    # build template
    return self.render_template('article.html',
                                nav_main=wk_nav_main,
                                nav_sections=wk_nav_sections,
                                title=wk_title,
                                date=wk_date,
                                time=wk_time,
                                peopleorgs=wk_peopleorgs,
                                place=wk_place,
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
