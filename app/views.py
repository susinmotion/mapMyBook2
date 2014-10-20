# from CONTAINING FOLDER OF RUN.PY import MODULE NAMED BELOW
from app import app
from flask import render_template, url_for, request, redirect, jsonify
import requests
import googlemaps
from NYPL import search, api
from libraries import Library
import cPickle as pickle
import re
import json


@app.route('/', methods=['GET','POST'])

def index():

	if request.method=="GET":
		return render_template ("start.html")

@app.route('/input', methods=['GET'])
def input(title="", author="",number=None):
	title=request.args.get('title')
	author=request.args.get("author")
	if request.args.get("includeCheckedOut"):
		includeCheckedOut = True
	else:
		includeCheckedOut = False
	books=search(title=title, author=author)
	returnbooks=[]
	for book in books[0:min(5, len(books))]:
		if book.link_to_copies:
			returnbooks.append(book)
	return render_template("pickabook.html",books=returnbooks, jsonBooks=[json.dumps(book.__dict__) for book in returnbooks], includeCheckedOut = includeCheckedOut)


@app.route('/map/<title>', methods=['GET','POST'])
@app.route('/map')
def map(title):
	bookAsDict=(json.loads(str(request.form.get("value"))))
	print bookAsDict
	title = bookAsDict['title']
	link_to_copies = bookAsDict['link_to_copies']
	try:
		author=bookAsDict['author']
	except KeyError:
		author=None
	thebook=api.Book(title=title, author=author, link_to_copies=link_to_copies)

	with open('dictionary.p', 'rb') as fp:
		possible_libraries = pickle.load(fp)
	
	libraries=[]
	includeCheckedOut = request.form.get("includeCheckedOut")
	if includeCheckedOut:
		copies= thebook.copies
	else:
		copies=thebook.available_copies

	for copy in copies:
		copy.location = re.sub(r"\(\d\)", "",copy.location).strip().replace("\'","")
		if copy.location in possible_libraries.keys():
			possible_libraries[copy.location].name=possible_libraries[copy.location].name.strip()
			possible_libraries[copy.location].address=possible_libraries[copy.location].address.strip()
			possible_libraries[copy.location].number=possible_libraries[copy.location].number.strip()
			possible_libraries[copy.location].status = copy.status
			libraries.append(possible_libraries[copy.location])
	
	api_key=open('api_key').read()
	url="https://maps.googleapis.com/maps/api/js?key=%s"%api_key
	return render_template("libMap.html", libraries=libraries, url=url, title=title, includeCheckedOut= includeCheckedOut)

@app.route('/didyoumean/<alt>')

def alt(alt):
	return render_template ("didyoumean.html",alt=alt)

@app.route('/checkedOut/<title>')
def checkedOut(title):
	return render_template("noneFound.html", title=title)

@app.route('/noBooks/<title>')
def noBooks(title):
	return render_template("nobooks.html", title=title)



#these include the data itself that could be part of the view. The html page controls how it looks and what gets shown
#def THE NAME OF THE THING AFTER THE SLASH--different page views
