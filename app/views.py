# from CONTAINING FOLDER OF RUN.PY import MODULE NAMED BELOW
from app import app
from flask import render_template, url_for, request, redirect, jsonify
import requests
import googlemaps

from libraries import Library
import cPickle as pickle
import re
from NYPL import search,api
import os
import psycopg2
import urlparse
import time
from psycopg2 import extras
import random

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#conn = psycopg2.connect(os.environ["DATABASE_URL"])

urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse("postgres://pmehzpfkeotntn:u4OXp20HhAef8TD8L9Hqk1LciC@ec2-174-129-21-42.compute-1.amazonaws.com:5432/d6ki3e1ckkv6f3")

conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)
conn.set_session(autocommit=True)
dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

@app.route('/', methods=['GET'])
def index():
	return render_template ("start.html")

@app.route('/input', methods=['GET'])
#@app.route('/input/<title>', methods =['GET'])
def input(title=None, author = None):
	title=request.args.get('title')
	author=request.args.get("author")
	includeCheckedOut=request.args.get("includeCheckedOut")
	query= title.upper()+"_"+author.upper()
	
	dict_cur.execute("SELECT * FROM books WHERE query = '{0}';".format( query ))
	returnbooks=dict_cur.fetchall()

	if returnbooks == []:
		books=search(title=title, author=author)
		index= 0
		for book in books[0:min(6, len(books))]:
			if book.link_to_copies:
				index = index +1
				libHash = book.link_to_copies[53:book.link_to_copies.find("?")]
					dict_cur.execute("INSERT INTO books (index,query,title, author, link_to_copies, libHash) VALUES (%s,%s, %s,%s, %s, %s)",(index, query, book.title, book.author, book.link_to_copies, libHash))
					index = index - 1

		dict_cur.execute("SELECT * FROM books WHERE query = '{0}';".format( query ))
		returnbooks = dict_cur.fetchall()


	if returnbooks == []:
		return redirect(url_for("noBooks", title=title, author=author))
	else:
		return render_template("pickabook.html",books=returnbooks, query=query, includeCheckedOut = includeCheckedOut )

@app.route('/map')
@app.route('/map/<libHash>/<title>', methods=['GET','POST'])

def map(libHash, title):
	dict_cur.execute("SELECT * FROM books WHERE libHash = '{0}';".format(libHash) )
	book=dict_cur.fetchone()
	if book == None:
		return redirect(url_for('index'))

	thebook = api.Book(title=book['title'], author=book['author'], link_to_copies=book["link_to_copies"])
	noCopiesInDatabase = True

	dict_cur.execute("""
		SELECT c.*
		FROM 
					copies  c
		INNER JOIN books 	b
			ON b.libHash = c.libHash
		WHERE b.libHash = '{0}'
	""".format(libHash))

	copies = []
	for result in dict_cur.fetchall():
		location = result['location']
		collection = result['collection']
		callNo = result['callno']
		status = result['status']
		copy = api.Copy(location, collection, callNo, status)
		copies.append(copy)

	if copies ==[]:
		foundCopiesInDatabase = False
		copies = thebook.copies
		
	
	with open('dictionary.p', 'rb') as fp:
		possible_libraries = pickle.load(fp)
	
	libraries=[]
	for copy in copies:
		copy.location = re.sub(r"\(\d\)", "",copy.location).strip().replace("\'","")
		thetime = 0
		if copy.location in possible_libraries.keys():
			possible_libraries[copy.location].name=possible_libraries[copy.location].name.strip()
			possible_libraries[copy.location].address=possible_libraries[copy.location].address.strip()
			possible_libraries[copy.location].number=possible_libraries[copy.location].number.strip()
			possible_libraries[copy.location].status = copy.status
			libraries.append(possible_libraries[copy.location])
			del possible_libraries[copy.location]
			thetime=time.mktime(time.localtime())
		if foundCopiesInDatabase == False:
			try:
				dict_cur.execute("INSERT INTO copies (time, location, collection, callno, status, libHash) VALUES (%s, %s,%s, %s,%s, %s)", (thetime, copy.location,copy.collection, copy.callNo,copy.status, libHash))
				dict_cur.execute("SELECT id FROM copies WHERE time = '{0}';".format(thetime))
				copyid=dict_cur.fetchone()
				dict_cur.execute("SELECT id FROM books WHERE libHash ='{0}';".format(libHash))
				bookID = dict_cur.fetchone()
				dict_cur.execute("INSERT INTO books_copies (bookID, copyID) VALUES (%s, %s)", (bookID, copyid))
			except Exception as e:
				print e
	includeCheckedOut = request.args.get("includeCheckedOut")
	if includeCheckedOut != 'yes':
		temp = []
		for library in libraries:
			if library.status == "Available":
				temp.append(library)
		libraries = temp	

		
	if libraries == []:
		return render_template ("nobooks_av.html", title=title, libHash=libHash, includeCheckedOut=includeCheckedOut)
	
	api_key=open('api_key').read()
	url="https://maps.googleapis.com/maps/api/js?key=%s"%api_key
	return render_template("libMap.html", libraries=libraries, url=url, title=title, includeCheckedOut= includeCheckedOut)

@app.route('/didyoumean/<alt>')
def alt(alt):
	return render_template ("didyoumean.html",alt=alt)


@app.route('/noBooks/<title>/<author>')
def noBooks(title, author):
	return render_template("nobooks.html", title=title, author=author)
