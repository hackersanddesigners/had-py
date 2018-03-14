# hackersanddesigners.nl

Website for H&D, Amsterdam.

## Side A

The wiki and the backend are running on [MediaWiki](https://www.mediawiki.org/wiki/MediaWiki), acting as open-door cms, workshop space, archive for projects and knowledge.

A wiki comes with no predetermined hierarchy, which lets you create your own logic for a navigation. On the the H&D wiki we work with [Forms](https://www.mediawiki.org/wiki/Extension:Page_Forms) and [Templates](https://www.mediawiki.org/wiki/Help:Templates) for a better editing experience; [Semantic MediaWiki](https://www.semantic-mediawiki.org/wiki/Semantic_MediaWiki) for organising all bits of data and metadata on each page and [Concepts](https://www.semantic-mediawiki.org/wiki/Help:Concepts) to create sections and the navigation for the frontend website.

## Side B

The front-end is built in Python 3.6 with:

- [Werkzeug](https://github.com/pallets/werkzeug) to wrap the website inside an app and put it on the internet through the `WSGI` interface
- [Requests](https://github.com/kennethreitz/requests) to fetch all `json` from the MediaWiki backend
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) to parse and clean up wiki’s extra markup, and to add atomic, functional `css` classes to `html` tags
- [Jinja](https://github.com/pallets/jinja) to build the templates (works hand in hand w/ Werkzeug)

## To run the frontend website

Requirements

- terminal basics ([introduction](https://hackersanddesigners.nl/s/Projects/p/Terminal_introduction_workshop))
- Python ([introduction](https://hackersanddesigners.nl/s/Projects/p/Python_Introduction_Workshop))
- `pip` Python package manager ([instructions](https://en.wikipedia.org/wiki/Pip_(package_manager)))
- venv to setup a Python environment ([check this](http://www.marinamele.com/2014/07/install-python3-on-mac-os-x-and-use-virtualenv-and-virtualenvwrapper.html) for instructions)
- git!

Then

- open terminal
- clone the repository: `git clone git@github.com:hackersanddesigners/had-py.git`
- setup a new Python 3.6 environment inside the repo folder: `python3.6 -m venv env`. To activate it, type: `source env/bin/activate`
- type: `python had.py`
- you will be asked to install a bunch of dependencies using Python’s `pip` package manager. Do `pip install name-of-package` and keep running `python had.py` until everything is installed
- type: `python had.py` again, the Python app should start and print something like `http://127.0.0.1:5000`, copy that in your browser to see the H&D’s frontend website ☺︎

## Some thoughts on the process

Improving and organising the MediaWiki demanded a good reading of the extensive (at times confusing) [documentation](https://www.mediawiki.org/wiki/Manual:Contents), installing some plugins (in particular [PageForms](https://www.mediawiki.org/wiki/Extension:Page_Forms) on top of [Semantic MediaWiki](https://www.mediawiki.org/wiki/Extension:Semantic_MediaWiki)) and manage the data through the MediaWiki interface. The most challenging part was to understand how Mediawiki actually treated data, and to decide how much complexity adding to the existing wiki. Overall, the aim was to be able to create new articles and to edit them in a pleasant manner but not limited the editing activities too much.

The wiki is fully able to parse different syntaxes whenever you need to embed an image, a video, an audio clip, an etherpad, etc, and it supports your writing and mark-up. One instance is the token autocompletion: for example some fields suggest you already used words (tokens) while you are typing.

Check [Page Forms:Input types](https://www.mediawiki.org/wiki/Extension:Page_Forms/Input_types) for an overview of what’s available.

Currently, the Event page receives data with this template

```
{{{for template|Event}}}

{| class="formtable"

! Name

| {{{field|Name}}}

|-

! Location

| {{{field|Location|input type=combobox}}}

|-

! Date

| {{{field|Date}}}

|-

! Time

| {{{field|Time}}}

|-

! PeopleOrganisations

| {{{field|PeopleOrganisations}}}

|-

! Type

| {{{field|Type|input type=combobox}}}

|-

! Web

| {{{field|Web|input type=checkbox}}}

|-

! Print

| {{{field|Print|input type=checkbox}}}

|}

{{{end template}}}

'''Text'''

{{{standard input|free text|rows=15|editor=wikieditor}}}
```

The `combobox input type` ([see](https://www.mediawiki.org/wiki/Extension:Page_Forms/Input_types#combobox)) looks up what has been already saved in that particular field from all the previous pages, and suggests possible completion.

± ± ±

Working with the frontend instead, requires to have / get some knowledge of:

- restful APIs ([ref](http://www.vinaysahni.com/best-practices-for-a-pragmatic-restful-api))
- how to handle page request, setup page routing, serve the app to the web, etc. — in this case with Python
- how to use a templating library

As we decided not to use a framework, the second point in particular gives you the chance to manually fiddle with stuff than if you mostly use a (`php`-based) cms, usually you can avoid or don’t have to touch at all.

Working with a restful API introduces you to the powerful world of `json` ([intro](https://en.wikipedia.org/wiki/JSON)), a very flexible data format able to convert anything into anything else—and back.

When working with Python, there are two very useful commands that let you inspect a `json` dataset:

- `type(data)`, eg `print(type(data))` — to check if the current object is a dict, or a lists, a string and so forth
- `data.keys()`, eg `print(data.keys())` — to check the object’s keys (which is how `json` structures data)

Alternatively, you can access to a pretty-printed version of the `json` request you made to MediaWiki, by visiting that url, eg

```
https://en.wikipedia.org/w/api.php?action=query&titles=Main%20Page&prop=revisions&rvprop=content&format=json
```

and adding `fm` after `format=json`, like `format=jsonfm` ([see docs](https://www.mediawiki.org/wiki/API:Main_page#The_format)) to have an indented, more readable version

```
https://en.wikipedia.org/w/api.php?action=query&titles=Main%20Page&prop=revisions&rvprop=content&format=jsonfm
```

This double approach lets you inspect better what’s going on in case you are unsure which data you are working with.

± ± ±

Once you get acquainted with MediaWiki’s design language (Forms, Templates, etc), `json` data structures and some basic Python, you can play around with the website.

± ± ±

## custom mediawiki styles

- `/mediawiki/resources/src/mediawiki.action/mediawiki.action.history.styles.css`

this add more padding and take out list styles to the revision list

```
#pagehistory {
    margin-left: 0;
    padding-top: 0.25rem;
}
#pagehistory li {
	list-style: none;
	padding: 0.5rem;
	margin-bottom: 0.25rem;
}
#pagehistory li:hover {
	background-color: #f8f9fa;
	border: 1px dashed #a2a9b1;
}
```

- `/mediawiki/resources/src/mediawiki.action/mediawiki.action.history.css`

this set the ‘compare selected revisions’ to the bottom-right, always at reach and more prominent (before there were two buttons at the top and bottom of the revision list, very much buried amongst the rest of the text)

```
.historysubmit {
    position: fixed;
    bottom: 0.5rem;
    right: 1rem;
    padding: 0.5rem;
    font-size: 100%;
}

.historysubmit:hover, .historysubmit:active {
    background-color: yellow;
    cursor: pointer;
}
```