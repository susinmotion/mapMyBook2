# from CONTAINING FOLDER OF RUN.PY import MODULE NAMED BELOW
from app import app
from flask import render_template, url_for, request, redirect, jsonify
import requests
import googlemaps
from NYPL import search, api
from libraries import Library
import cPickle as pickle
import re

import os
import psycopg2
import urlparse

urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["DATABASE_URL"])

conn = psycopg2.connect(
    database="d6ki3e1ckkv6f3",
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)

cache={}
 
"""
+class SqlBook(Base):
+       __tablename__="Books"
+       id = Column(Integer, primary_key=True)
+       title = Column(String(255), nullable=False)
+       author = Column(String(100), nullable =True)
+       link_to_copies = Column(String(100), nullable=True)
+
+class SqlCopy(Base):
+       __tablename__="Copies"
+       id = Column(Integer, primary_key=True)
+       location = Column(String(50), nullable=False)
+       call_number = Column(String(50), nullable=False)
+       status = Column(String(50), nullable=False)
+
+"""

@app.route('/', methods=['GET'])

def index():
	return render_template ("start.html")

@app.route('/input', methods=['GET'])
#@app.route('/input/<title>', methods =['GET'])
def input(title=None, author = None):
	try:
		title=request.args.get('title')
		author=request.args.get("author")
		includeCheckedOut=request.args.get("includeCheckedOut")
		key=(title+"_"+author)
	except:
		title = re.sub(r"\([^)]*\)", "", request.args["title"])
		print title
		key = title+"_"

	global cache
	if key in cache:
		returnbooks=cache[key]
	else:
		returnbooks=[]
		books=search(title=title, author=author)
		for book in books[0:min(5, len(books))]:
			if book.link_to_copies:
				returnbooks.append(book)
		cache[key]=returnbooks
	if returnbooks == []:
		return render_template("noBooks.html", title=title, author=author)
	else:
		return render_template("pickabook.html",books=returnbooks, key=key, includeCheckedOut = includeCheckedOut)


@app.route('/map/<title>', methods=['GET','POST'])
def map(title):
	if request.method=="POST":
		index = int(request.form.get("value"))
		key = request.form.get("key").encode('ascii')
		global cache
		thebook= cache[key][index]
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
		cache[thebook.title]= [libraries,includeCheckedOut]

	if request.method == "GET":
		if title in cache:
			[libraries,includeCheckedOut]=cache[title]
		else:
			print "not in cache"
			return redirect(url_for('input', title=title))
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
