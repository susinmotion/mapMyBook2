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
import time
from psycopg2 import extras

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
	returnbooks=[]
	title=request.args.get('title')
	author=request.args.get("author")
	includeCheckedOut=request.args.get("includeCheckedOut")
	query= title+"_"+author
	try:
		dict_cur.execute("SELECT * FROM books WHERE query = '{0}';".format( query ))
		returnbooks=dict_cur.fetchall()
	except Exception as e:
		print e

	if returnbooks == []:
		books=search(title=title, author=author)
		index= 0
		for book in books[0:min(5, len(books))]:
			if book.link_to_copies:
				print book.link_to_copies
				index = index +1
				bookID = book.link_to_copies[53:book.link_to_copies.find("?")]
				try:
					dict_cur.execute("INSERT INTO books (id, index,query,title, author, link_to_copies) VALUES (%s,%s,%s, %s,%s, %s)",(bookID, index, query, book.title, book.author, book.link_to_copies))
				except Exception as e:
					#print "Fail! %s %s %s %s %s %s" %(bookID, index, query, book.title, book.author, e)
					index = index - 1

		dict_cur.execute("SELECT * FROM books WHERE query = '{0}';".format( query ))
		returnbooks = dict_cur.fetchall()


	if returnbooks == []:
		return render_template("noBooks.html", title=title, author=author)
	else:
		return render_template("pickabook.html",books=returnbooks, query=query, includeCheckedOut = includeCheckedOut )

@app.route('/map')
@app.route('/map/<bookID>/<title>', methods=['GET','POST'])
def map(bookID, title):
	try:
		dict_cur.execute("SELECT * FROM books WHERE id = '{0}';".format(bookID) )
		book=dict_cur.fetchone()
		print book,"BOOK"
	except Exception as e:
		print "fail select by id %s" %e
		print "nobook"
		query = request.form.get("query").encode('ascii')
		(throwaway, author)= query.split("_")
		search(title, author)
		#this is not done

	thebook = api.Book(title=book['title'], author=book['author'], link_to_copies=book["link_to_copies"])
	print thebook.link_to_copies,"LINK"
	print thebook.copies
	new = False
	try:
		dict_cur.execute("""
			SELECT c.*
			FROM 
						copies  c
			INNER JOIN	books_copies 	bc
				ON c.id = bc.copyid
			INNER JOIN books 	b
				ON b.id = bc.bookID
			WHERE b.id = '{0}')
		""".format(bookID))
		copies = []
		for result in dict_cur.fetchall():
			location = result['location']
			collection = result['collection']
			callno = result['callno']
			status = result['status']
			copy = Copy(name,collection, callno,status)
			copies.append(copy)

	except Exception as e:
		print e
		copies = thebook.copies
		print copies
		new = True
	

	with open('dictionary.p', 'rb') as fp:
		possible_libraries = pickle.load(fp)
	
	libraries=[]
	for copy in copies:
		if new:
				dict_cur.execute("INSERT INTO copies (id, location, collection, callno, status) VALUES (%f, %s,%s, %s,%s)" (copyid, copy.location,copy.collection, copy.callno,copy.status))
				dict_cur.execute("INSERT INTO map (bookID, copyID) VALUES (%i, %s)" (bookid, copyid))

		copy.location = re.sub(r"\(\d\)", "",copy.location).strip().replace("\'","")
		if copy.location in possible_libraries.keys():
			possible_libraries[copy.location].name=possible_libraries[copy.location].name.strip()
			possible_libraries[copy.location].address=possible_libraries[copy.location].address.strip()
			possible_libraries[copy.location].number=possible_libraries[copy.location].number.strip()
			possible_libraries[copy.location].status = copy.status
			libraries.append(possible_libraries[copy.location])
			copyid=time.mktime(time.localtime())
			
	includeCheckedOut = request.args.get("includeCheckedOut")
	if includeCheckedOut != 'yes':
		temp = []
		for library in libraries:
			if library.status == "Available":
				temp.append(library)
		libraries = temp

	print libraries
	print type(libraries[0])
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
