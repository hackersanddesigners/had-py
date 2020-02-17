import os
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule, NotFound, RequestRedirect
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.utils import redirect
from werkzeug.wsgi import get_current_url
import requests
import datetime
import re
from bs4 import BeautifulSoup, Comment
from urllib.parse import urljoin, quote
from jinja2 import Environment, FileSystemLoader

class had(object):

  def __init__(self):
    template_path = os.path.join(os.path.dirname(__file__), 'templates')
    self.jinja_env = Environment(loader=FileSystemLoader(template_path), autoescape=True)
    # --------------------
    # jinja custom filters
    def dateformat(value, format='%d.%m.%Y'):
      item = re.search(r'(\d{4}[/]\d{2}[/]\d{2})-(\d{4}[/]\d{2}[/]\d{2})', value)
      if item:
        date_start = item.group(1)
        date_start = datetime.datetime.strptime(date_start, '%Y/%m/%d')
        date_start = date_start.strftime(format)

        date_end = item.group(2)
        date_end = datetime.datetime.strptime(date_end, '%Y/%m/%d')
        date_end = date_end.strftime(format)

        multi_date = date_start, date_end
        multi_date = '——'.join(multi_date)
        return multi_date
      else:
        single_date = datetime.datetime.strptime(value, '%Y/%m/%d')
        single_date = single_date.strftime(format)
        return single_date
    self.jinja_env.filters['dateformat'] = dateformat

    # -------
    # routing
    self.url_map = Map([
      Rule('/', endpoint='home'),
      Rule('/<file>', redirect_to='/assets/files/<file>'),
      Rule('/browserconfig.xml', redirect_to='/assets/files/favicon/browserconfig.xml'),
      Rule('/p/<page_title>', endpoint='article'),
      Rule('/s/<section_title>', endpoint='section'),
      Rule('/s/<section_title>/p/<page_title>', endpoint='article')
    ])

  # ----------
  # navigation
  def nav_main():
    base_url = 'https://wiki.hackersanddesigners.nl/'
    api_call = 'api.php?'

    filters_nav_main = '|?MainNavigation|order=asc'
    nav_main_options = {'action': 'ask', 'query': '[[Concept:MainNavigation]]' + filters_nav_main, 'format': 'json', 'formatversion': '2'}
    response_nav_main = requests.get(base_url + api_call , params=nav_main_options)
    wk_nav_main = response_nav_main.json()
    print('MN', wk_nav_main)
    print(wk_nav_main['query']['results'])
    try:
      del wk_nav_main['query']['results']['Summer Academy 2019']
      del wk_nav_main['query']['results']['Concept:Summer Academy 2019']
    except Exception as e:
      print(e)

    return wk_nav_main

  def nav_sections():
    base_url = 'https://wiki.hackersanddesigners.nl/'
    api_call =  'api.php?'

    nav_sections_options = {'action': 'ask', 'query': '[[Concept:+]]', 'format': 'json', 'formatversion': '2'}
    response_nav_sections = requests.get(base_url + api_call , params=nav_sections_options)
    wk_nav_sections = response_nav_sections.json()

    # delete MainNavigation concept from the dict
    try:
      del wk_nav_sections['query']['results']['Concept:MainNavigation']
      del wk_nav_sections['query']['results']['Concept:01Publications']
      del wk_nav_sections['query']['results']['Concept:ActiveSA']
      del wk_nav_sections['query']['results']['Concept:HDSA']
      del wk_nav_sections['query']['results']['Concept:Activities# QUERYd64f49fa6b3fd3a2d4c7eda437e49e88']
    except Exception as error:
      print(error)

    nav_ban = ['Concept:MainNavigation', 'Concept:01Publications', 'Concept:ActiveSA', 'Concept:HDSA', 'Concept:Activities# QUERYd64f49fa6b3fd3a2d4c7eda437e49e88']

    nav_sections = []
    for item in wk_nav_sections['query']['results'].items():
      if '# QUERY' not in item[0] and item[0] not in nav_ban:
        if '1' in item[1]['exists']:
          nav_item = item[1]['fulltext']
          nav_sections.append(nav_item)

    return nav_sections

    # nav_sections = []
    # for item in wk_nav_sections['query']['results']:
    #   print(item)
    #   if not 'QUERY' in item:
    #     nav_sections.append(item)

    # print(nav_sections)

    # return nav_sections

  # --- fix rel-links to be abs-ones (a)
  def fix_extlinks_a(text, url):
    base_url = 'https://wiki.hackersanddesigners.nl/'

    for a in text.find_all('a', href=re.compile(r'/index.php/.*')):
      rel_link = a.get('href')
      rel_link = rel_link.replace(':', '%3A')
      rel_link = rel_link.rsplit('/', 1)
      a['href'] = urljoin(url, rel_link[1])
    return text

  # --- fix rel-links to be abs ones (img)
  def fix_extlink_imgs(text):
    base_url = 'https://wiki.hackersanddesigners.nl/'

    for img in text.find_all('img', src=re.compile(r'/.*')):
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
    return text

  # --- typography
  def typography(text):
    
    # delete wiki infobox
    infobox = text.find('table')
    if infobox:
      infobox.decompose()

    for heading in text.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
      heading['class'] = 'ft-sans ft-1 ft-1__m ft-bold mg-v--2 w--copy'

    for p in text.find_all('p'):
      p['class'] = 'w--copy mg-b--2'

    for bq in text.find_all('blockquote'):
      bq['class'] = 'ft-2 ft-2__m w--copy'

    for code in text.find_all(['pre']):
      code['class'] = 'w--copy d-b ft-mono blue ft-05 ft-05__m mg-b--2 pd-l--2 bd-l--1 bd-r--1 o-x__scroll'

    for code in text.find_all(['code']):
      code['class'] = 'ft-mono blue bd-a--1 ft-05 ft-05__m'

    for img in text.find_all('img'):
      img['class'] = 'mg-v--1 shadow'
      del img['width']
      del img['height']

      # check if img has caption/is wrapped inside a div
      img_thumb = img.find_parent('div', class_='thumbinner')
      img_p = img.find_parent('p')
      figure = img.find_parent('figure')
      if img_thumb:
        img_thumb.unwrap()
        figure = img.find_parent('div', class_='thumb')
        figure.name = 'figure'
        figure['class'] = 'w--copy mg-b--2 mg-l--3__m'

        # set img caption
        img_caption = figure.find('div', class_='thumbcaption')
        if img_caption.content:
          img_caption.name = 'figcaption'
          img_caption['class'] = 'mg-auto w--four-fifths ft-sans t-a--c'
        else:
          img_caption.decompose()

        magnify = img_caption.find('div', class_='magnify')
        if magnify:
          magnify.decompose()

        figure.unwrap()

      a_img = img.find_parent('a')
      if a_img:
        a_img.name = 'figure'
        del a_img['href']
        a_img['class'] = 'w--copy mg-b--2 mg-l--3__m'

    # --- set up soundcloud
    try:
      for sc in text.find_all('iframe', src=re.compile(r'soundcloud')):
        sc['class'] = 'w--full'
        sc.parent.unwrap()

    except:
      print('no soundcloud embed')

    # --- set up embedded videos (yt)
    try:
      for embedvid in text.find_all('div', class_='embedvideo'):
        del embedvid['style']
        embedvid['class'] = 'w--copy mg-t--1 mg-b--3 mg-l--3__m'

        embedvid_c = embedvid.find('div', class_='thumbinner');
        del embedvid_c['style']
        embedvid_c['class'] = 'embed-container'

        embedvid_iframe = embedvid_c.find('iframe')
        del embedvid_iframe['width']
        del embedvid_iframe['height']
        embedvid_iframe['frameborder'] = '0'

        # video caption
        embedvid_caption = embedvid_c.find('div', class_='thumbcaption')
        embedvid_caption['class'] = 'pd-t--2 mg-auto w--four-fifths ft-sans t-a--c'
        # move video caption outside the `iframe`'s wrapper
        embedvid_caption.extract()
        embedvid.append(embedvid_caption)
    except TypeError:
      print('No embed video')

    # --- etherpad embed
    for ep in text.find_all('iframe', class_=re.compile(r'eplite')):
      del ep['style']
      ep['frameborder'] = '0'
      ep.wrap(text.new_tag('div'))
      ep.parent['class'] = 'w--copy mhvh--half bd-a--1 mg-b--2'
      ep['class'] = 'w--full mhvh--half bd-a--0'

    for ul in text.find_all('ul'):
      ul['class'] = 'd-tb pd-b--1 w--copy'
      for li in ul.find_all('li'):
        li['class'] = 'd-tbr li-em'

    for ol in text.find_all('ol'):
      ol['class'] = 'pd-l--2 pd-b-0 w--copy'

    # delete mediawiki autogenerated comments
    for comment in text.find_all(text=lambda text:isinstance(text, Comment)):
      comment.extract()
    
    return text
  
  # --- Views
  
  # home	
  def on_home(self, request, typography=typography, fix_extlinks_a=fix_extlinks_a, fix_extlink_imgs=fix_extlink_imgs, wk_nav_main=nav_main(), wk_nav_sections=nav_sections()):
    base_url = 'https://wiki.hackersanddesigners.nl/'
    api_call =  'api.php?'

    # fetch intro
    intro_options = {'action': 'parse', 'pageid': '29', 'format': 'json', 'formatversion': '2', 'disableeditsection': 'true'}
    intro_response = requests.get(base_url + api_call , params=intro_options)
    wkdata_intro = intro_response.json()

    wk_title = wkdata_intro['parse']['title']
    wk_intro = wkdata_intro['parse']['text']
    
    soup_wk_intro = BeautifulSoup(wk_intro, 'html.parser')
    # ---
    fix_extlinks_a(soup_wk_intro, url='s/Events/p/')
    fix_extlink_imgs(soup_wk_intro)
    typography(soup_wk_intro)
    # ---
    wk_intro = soup_wk_intro

    # --- events list
    # recursively fetch all pages using `askargs`
    def query(request):
      request['action'] = 'askargs'
      request['format'] = 'json'
      request['formatversion'] = '2'
      lastContinue = ''
      while True:
        # clone original request
        req = request.copy()
        # modify it with the values returned in the 'query-continue-offset' section of the last result
        parameters = req['parameters']
        continue_offset = [parameters, '|offset=', str(lastContinue)]
        continue_offset = ''.join(continue_offset)

        parameters = {'parameters': continue_offset}
        req.update(parameters)
        
        # call API
        result = requests.get(base_url + api_call, params=req).json()
        if 'error' in result:
          raise Error(result['error'])
        if 'warnings' in result:
          print(result['warnings'])
        if 'query' in result:
          yield result['query']
        if 'query-continue-offset' not in result:
          break
        lastContinue = result['query-continue-offset']
    
    # ---------------------------
    today = datetime.date.today()
    today = today.strftime('%Y/%m/%d')

    # --- upcoming events
    wkdata_upevents = []
    for result in query({'conditions': 'Category:Event|OnDate::>' + today, 'printouts': 'NameOfEvent|OnDate|Venue|Time', 'parameters': 'sort=OnDate|order=asc'}):
      try:
        for item in result['results'].items():
          title = item[1]['printouts']['NameOfEvent'][0]['fulltext']
          wkdata_upevents.append(title)

          date = item[1]['printouts']['OnDate'][0]['fulltext']
          wkdata_upevents.append(date)

          upevents_introtext_options = {'action': 'parse', 'page': title, 'format': 'json', 'formatversion': '2', 'disableeditsection': 'true'}
          response_introtext_upevents = requests.get(base_url + api_call , params=upevents_introtext_options)
          wkdata_introtext_upevents = response_introtext_upevents.json()

          text = wkdata_introtext_upevents['parse']['text']
          soup_wk_introtext = BeautifulSoup(text, 'html.parser')
          # ---
          typography(soup_wk_introtext)
          p_intro = soup_wk_introtext.p
          fix_extlinks_a(p_intro, '/s/Events/p/')
          fix_extlink_imgs(soup_wk_introtext)
          # ---
          soup_intro = p_intro
          wkdata_upevents.append(p_intro)

      except AttributeError:
        print('No upcoming events')

    wkdata_upevents = list(zip(*[iter(wkdata_upevents)]*3))
    wkdata_upevents = sorted(wkdata_upevents, key=lambda x: x[1])
    
    # --- past events
    wkdata_pastevents = []
    for result in query({'conditions': 'Category:Event|OnDate::<' + today, 'printouts': 'NameOfEvent|OnDate|Venue|Time', 'parameters': 'sort=OnDate|order=desc'}):
      for item in result['results'].items():
        title = item[0]
        wkdata_pastevents.append(title)
        date = item[1]['printouts']['OnDate'][0]['fulltext']
        wkdata_pastevents.append(date)

    wkdata_pastevents = list(zip(*[iter(wkdata_pastevents)]*2))
    wkdata_pastevents = sorted(wkdata_pastevents, key=lambda x: x[1], reverse=True)
    
    # build template
    return self.render_template('event_list.html',
                                nav_main=wk_nav_main,
                                nav_sections=wk_nav_sections,
                                title=wk_title,
                                intro=wk_intro,
                                up_event_list=wkdata_upevents,
                                past_event_list=wkdata_pastevents
                                )

  def on_section(self, request, fix_extlinks_a=fix_extlinks_a, typography=typography, section_title=None, page_title=None, wk_nav_main=nav_main(), wk_nav_sections=nav_sections()):
    base_url = 'https://wiki.hackersanddesigners.nl/'
    api_call =  'api.php?'

    # fetch page-content
    page_head_options = {'action': 'parse', 'page': 'Concept:' + section_title, 'format': 'json', 'formatversion': '2'}
    response_head = requests.get(base_url + api_call, params=page_head_options)
    wkdata_head = response_head.json()

    wk_title = wkdata_head['parse']['title']
   
    if wkdata_head['parse']['text']:
      wk_intro = wkdata_head['parse']['text']
      soup_wk_intro = BeautifulSoup(wk_intro, 'html.parser')
      typography(soup_wk_intro)
      
      # fix rel-links to be abs-ones
      envy = request.environ
      p_url = get_current_url(envy)
      fix_extlinks_a(soup_wk_intro, url=p_url + '/p/')

      p_intro = soup_wk_intro.find('p')
      if p_intro.string:
        wk_intro = p_intro
      else:
        wk_intro = None

    # --------------------------
    today = datetime.date.today()
    today = today.strftime('%Y/%m/%d')
    
    # recursively fetch all pages using `askargs`
    def query(request):
      request['action'] = 'askargs'
      request['format'] = 'json'
      request['formatversion'] = '2'
      lastContinue = ''
      while True:
        # clone original request
        req = request.copy()
        # modify it with the values returned in the 'query-continue-offset' section of the last result
        parameters = req['parameters']
        continue_offset = [parameters, '|offset=', str(lastContinue)]
        continue_offset = ''.join(continue_offset)

        parameters = {'parameters': continue_offset}
        req.update(parameters)
        
        # call API
        result = requests.get(base_url + api_call, params=req).json()
        if 'error' in result:
          raise Error(result['error'])
        if 'warnings' in result:
          print(result['warnings'])
        if 'query' in result:
          yield result['query']
        if 'query-continue-offset' not in result:
          break
        lastContinue = result['query-continue-offset']

    # make section_items list by fetching item's title and img (if any)
    # ---- Activities
    if 'Activities' in section_title:
      wk_section_items = None

      # --- upcoming items
      wk_section_upitems = []
      for result in query({'conditions': 'Concept:' + section_title + '|OnDate::>' + today, 'printouts': 'NameOfEvent|OnDate|Venue|Time', 'parameters': 'sort=OnDate|order=asc'}):
        try:
          for item in result['results'].items():
            title = item[1]['fulltext']
            wk_section_upitems.append(title)
            date = item[1]['printouts']['OnDate'][0]['fulltext']
            wk_section_upitems.append(date)

            # fetch section item's content
            item_introtext_options = {'action': 'parse', 'page': title, 'format': 'json', 'formatversion': '2', 'disableeditsection': 'true'}
            response_introtext_item = requests.get(base_url + api_call , params=item_introtext_options)
            wkdata_introtext_item = response_introtext_item.json()

            wkdata_text_item = wkdata_introtext_item['parse']['text']

            # get section item's img
            soup_wk_introtext = BeautifulSoup(wkdata_text_item, 'html.parser')
            if soup_wk_introtext.img:
              cover_img = soup_wk_introtext.img
              cover_img['class'] = 'mg-t--1 shadow'

              # setup <noscript> tag for original images
              # in case of no js browser-enabled
              noscript = soup_wk_introtext.new_tag('noscript')
              noscript.append(cover_img)
              ns_cover_img = noscript

              src_rel_link = cover_img.get('src')
              if src_rel_link:
                src_c = re.split(r'[/]\s*', src_rel_link)
                src_c = '/'.join(src_c)
                out_link = urljoin(base_url, src_rel_link)
                cover_img['src'] = out_link

              srcset_rel_link = cover_img.get('srcset')
              if srcset_rel_link:
                del cover_img['srcset']

              # duplicate img tag and 
              # replace `src` w/ `data-src`
              import copy
              dcover_img = copy.copy(cover_img)
              dcover_img['data-src'] = dcover_img['src']
              dcover_img['class'] += ' cover-img d-n'
              del dcover_img['src']

              dsrc_rel_link = dcover_img.get('data-src')
              if dsrc_rel_link:
                src_c = re.split(r'[/]\s*', dsrc_rel_link)
                src_c = '/'.join(src_c)
                out_link = urljoin(base_url, dsrc_rel_link)
                dcover_img['data-src'] = out_link

              dsrcset_rel_link = dcover_img.get('srcset')
              if dsrcset_rel_link:
                del dcover_img['srcset']

            else:
              cover_img = None
              ns_cover_img = None
              dcover_img = None

            # add `cover_img` & `dcover_img` to `wk_section_items`
            wk_section_upitems.append(ns_cover_img)
            wk_section_upitems.append(dcover_img)

        except AttributeError:
          print('No upcoming event')

      # ---- * * *
      wk_section_upitems = list(zip(*[iter(wk_section_upitems)]*4))
      wk_section_upitems = sorted(wk_section_upitems, key=lambda x: x[1])
     
      # ---- past items
      wk_section_pastitems = []

      for result in query({'conditions': 'Concept:' + section_title + '|OnDate::<' + today, 'printouts': 'NameOfEvent|OnDate|Venue|Time', 'parameters': 'sort=OnDate|order=desc'}):
        
        for item in result['results'].items():
          title = item[1]['fulltext']
          wk_section_pastitems.append(title)
          date = item[1]['printouts']['OnDate'][0]['fulltext']
          wk_section_pastitems.append(date)

          # fetch section item's content
          item_introtext_options = {'action': 'parse', 'page': title, 'format': 'json', 'formatversion': '2', 'disableeditsection': 'true'}
          response_introtext_item = requests.get(base_url + api_call , params=item_introtext_options)
          wkdata_introtext_item = response_introtext_item.json()

          wkdata_text_item = wkdata_introtext_item['parse']['text']

          # get section item's img
          soup_wk_introtext = BeautifulSoup(wkdata_text_item, 'html.parser')
          if soup_wk_introtext.img:
            cover_img = soup_wk_introtext.img
            cover_img['class'] = 'mg-t--1 shadow'

            # setup <noscript> tag for original images
            # in case of no js browser-enabled
            noscript = soup_wk_introtext.new_tag('noscript')
            noscript.append(cover_img)
            ns_cover_img = noscript

            src_rel_link = cover_img.get('src')
            if src_rel_link:
              src_c = re.split(r'[/]\s*', src_rel_link)
              src_c = '/'.join(src_c)
              out_link = urljoin(base_url, src_rel_link)
              cover_img['src'] = out_link

            srcset_rel_link = cover_img.get('srcset')
            if srcset_rel_link:
              del cover_img['srcset']

            # duplicate img tag and 
            # replace `src` w/ `data-src`
            import copy
            dcover_img = copy.copy(cover_img)
            dcover_img['data-src'] = dcover_img['src']
            dcover_img['class'] += ' cover-img d-n'
            del dcover_img['src']

            dsrc_rel_link = dcover_img.get('data-src')
            if dsrc_rel_link:
              src_c = re.split(r'[/]\s*', dsrc_rel_link)
              src_c = '/'.join(src_c)
              out_link = urljoin(base_url, dsrc_rel_link)
              dcover_img['data-src'] = out_link

            dsrcset_rel_link = dcover_img.get('srcset')
            if dsrcset_rel_link:
              del dcover_img['srcset']

          else:
            cover_img = None
            ns_cover_img = None
            dcover_img = None

          # add `cover_img` & `dcover_img` to `wk_section_items`
          wk_section_pastitems.append(ns_cover_img)
          wk_section_pastitems.append(dcover_img)
    
      # ---- * * *
      wk_section_pastitems = list(zip(*[iter(wk_section_pastitems)]*4))
      wk_section_pastitems = sorted(wk_section_pastitems, key=lambda x: x[1], reverse=True)

    # --------------
    # other sections
    else:
      wk_section_upitems = None
      wk_section_pastitems = None
      wk_section_items = []
      for result in query({'conditions': 'Concept:' + section_title, 'printouts': 'Modification date|NameOfEvent|OnDate|Venue|Time', 'parameters': 'sort=Modification date|OnDate|order=desc'}):
        try:
          for item in result['results'].items():
            title = item[1]['fulltext']
            wk_section_items.append(title)
            if len(item) > 1 and len(item[1]['printouts']['OnDate']) > 0:
              date = item[1]['printouts']['OnDate'][0]['fulltext']
              wk_section_items.append(date)
            else:
              date = None
              wk_section_items.append(date)

            # fetch section item's content
            item_introtext_options = {'action': 'parse', 'page': title, 'format': 'json', 'formatversion': '2', 'disableeditsection': 'true'}
            response_introtext_item = requests.get(base_url + api_call , params=item_introtext_options)
            wkdata_introtext_item = response_introtext_item.json()

            wkdata_text_item = wkdata_introtext_item['parse']['text']
            # get section item's img
            soup_wk_introtext = BeautifulSoup(wkdata_text_item, 'html.parser')
            if soup_wk_introtext.img:
              cover_img = soup_wk_introtext.img
              cover_img['class'] = 'mg-t--1 shadow'

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
              cover_img = None

            # add `cover_img` to `wk_section_items`
            wk_section_items.append(cover_img)
        except AttributeError:
          wk_intro = "Could not load items"
          
      # ---- * * *
      wk_section_items = list(zip(*[iter(wk_section_items)]*3))
      try:
        wk_section_items = sorted(wk_section_items, key=lambda x: x[1])
      except TypeError:
        wk_section_items = sorted(wk_section_items, key=lambda x: x[0])
    
    # build template
    return self.render_template('section_list.html',
                                nav_main=wk_nav_main,
                                nav_sections=wk_nav_sections,
                                title=wk_title,
                                intro=wk_intro,
                                section_upitems=wk_section_upitems,
                                section_pastitems=wk_section_pastitems, 
                                section_items=wk_section_items
                                )

  # -------
  # article
  def on_article(self, request, typography=typography, fix_extlinks_a=fix_extlinks_a, page_title=None, section_title=None, wk_nav_main=nav_main(), wk_nav_sections=nav_sections()):
    base_url = 'https://wiki.hackersanddesigners.nl/'
    api_call =  'api.php?'

    # fetch page-content
    page_options = {'action': 'parse', 'page': page_title, 'format': 'json', 'formatversion': '2', 'disableeditsection': 'true'}
    response_content = requests.get(base_url + api_call, params=page_options)
    wk_data = response_content.json()

    wk_title = wk_data['parse']['title']
    wk_bodytext = wk_data['parse']['text']

    try:
      # --- if it has [Category:Event]
      # fetch page-metadata for Event
      page_meta_options = {'action': 'browsebysubject', 'subject': page_title, 'format': 'json', 'formatversion': '2'}
      response_meta = requests.get(base_url + api_call, params=page_meta_options)
      wkdata_meta = response_meta.json()

      def extract_metadata(query):
        item_list = []
        for item in query:
          print(item)
          str = item['item']
          # strip out weird hash at the end 
          # (see why https://www.semantic-mediawiki.org/wiki/Ask_API#BrowseBySubject)
          item = re.sub(r'#\d##', '', str).replace('_', ' ')
          item_list.append(item)
        return item_list

      wk_date = None
      wk_time = None
      wk_venue = None
      wk_peopleorgs = None

      for item in wkdata_meta['query']['data']:
        # --- Date
        if 'OnDate' in item['property']:
          wk_date = extract_metadata(item['dataitem'])
        # --- Time
        if 'Time' in item['property']:
          wk_time = extract_metadata(item['dataitem'])
        # --- Venue
        if 'Venue' in item['property']:
          wk_venue = extract_metadata(item['dataitem'])
        # --- PeopleOrgs
        if 'PeopleOrganisations' in item['property']:
          wk_peopleorgs = extract_metadata(item['dataitem'])
    
    # --- if it has not, set Event's metadata to `None`
    except KeyError:
      print('No Event metadata')
    
    # fix rel-links to be abs-ones
    soup_bodytext = BeautifulSoup(wk_bodytext, 'html.parser')
   
    envy = request.environ
    p_url = get_current_url(envy)
    p_url = p_url.rsplit('/', 1)

    fix_extlinks_a(soup_bodytext, url=p_url[0] + '/')

    # --- images
    for img in soup_bodytext.find_all('img', src=re.compile(r'/images/.*')):
      src_rel_link = img.get('src')
      srcset_rel_link = img.get('srcset')
      if src_rel_link:
        split = re.split(r'[/]\s*', src_rel_link)
        if 'thumb' in split:
          del split[2]
          del split[-1]
          split = '/'.join(split)
          out_link = urljoin(base_url, split)
          img['src'] = out_link
        else:
          out_link = urljoin(base_url, src_rel_link)
          img['src'] = out_link
      if (srcset_rel_link):
        split = re.split(r'[/]\s*', src_rel_link)
        if 'thumb' in split:
          del img['srcset']
        else:
          srcset_list = re.split(r'[,]\s*', srcset_rel_link)
          srcset_lu = srcset_list
          srcset_list[:] = [urljoin(base_url, srcset_i) for srcset_i in srcset_list]
          srcset_s = ', '.join(srcset_lu)
          img['srcset'] = srcset_s

    # --- flickity slideshow
    for gallery_item in soup_bodytext.find_all('li', class_='gallerybox'):
      # img div wrapper (from <li> to <div>)
      gallery_item.name = 'div'
      del gallery_item['style']
      gallery_item['class'] = 'gallery-item'

      # delete extra <div>s before and after img div wrapper
      gallery_item_div = gallery_item.find('div', class_='thumb')
      gallery_pp = gallery_item_div.parent
      gallery_pp.unwrap()
      child = gallery_item_div.div
      child.unwrap()
      gallery_item_div.unwrap()

      # set img caption
      gallery_item_caption = gallery_item.find('div', class_='gallerytext')
      if gallery_item_caption.content:
        gallery_item_caption.name = 'figcaption'
        gallery_item_caption['class'] = 'pd-t--1 mg-auto w--copy ft-sans t-a--c'
      else:
        gallery_item_caption.unwrap()

      # get parent <ul>
      gallerybox = gallery_item.find_parent('ul')
      gallerybox['class'] = 'gallery'

    # --- set class to flickity.js
    for gallery in soup_bodytext.find_all('ul', class_='gallery'):
      gallery.name = 'div'
      gallery['class'] = 'gallery flex-c w--copy mg-v--3'

    # --- typography
    typography(soup_bodytext)

    wk_bodytext = soup_bodytext

    # build template
    return self.render_template('article.html',
                                nav_main=wk_nav_main,
                                nav_sections=wk_nav_sections,
                                title=wk_title,
                                date=wk_date,
                                time=wk_time,
                                venue=wk_venue,
                                peopleorgs=wk_peopleorgs,
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
	run_simple('127.0.0.1', 5000, app, use_debugger=False, use_reloader=True)
