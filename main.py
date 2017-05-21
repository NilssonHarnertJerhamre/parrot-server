#!/usr/bin/python -p

import MySQLdb, base64, json, datetime
from bottle import run, post, request, response, get, route

KEY = "P3NT4G0N"

db = MySQLdb.connect("localhost","root","parrot","parrot" )
cursor = db.cursor()

def encode(key, string):
	encoded_chars = []
	for i in xrange(len(string)):
		key_c = key[i % len(key)]
		encoded_c = chr(ord(string[i]) + ord(key_c) % 256)
		encoded_chars.append(encoded_c)
	encoded_string = "".join(encoded_chars)
	return base64.urlsafe_b64encode(encoded_string)

@route('/chirp',method='POST')
def chirp_post():
	print request.body.read()
	parrot = request.forms.get('parrot')
	chirp = request.forms.get('chirp')
	if(parrot != None and chirp != None):
		sql = "INSERT INTO chirps (parrot, chirp) VALUES (%s, %s);"
		print sql
		try:
			cursor.execute(sql, (parrot, chirp))
			db.commit()
			sql = "SELECT LAST_INSERT_ID();"
			print sql
			cursor.execute(sql)
			results = cursor.fetchall()
			for result in results:
				return str(result[0])
		except:
			db.rollback()
			return '-6'
	return '-1'

@route('/chirp',method='GET')
def chirp_get():
	print request.body.read()
	id = request.query['id']
	if(id != None):
		sql = "SELECT chirp FROM chirps WHERE id=%s;" % id
		try:
			cursor.execute(sql)
			results = cursor.fetchall()
			for result in results:
				print result[0]
				return result[0]
		except:
			return '-8'
	return '-7'

@route('/chirps',method='GET')
def active():
	sql = "SELECT id, parrot, sent FROM chirps WHERE 1 ORDER BY sent DESC;"
	try:
		cursor.execute(sql)
		results = cursor.fetchall()
		data = []
		for result in results:

			sql = "SELECT uname FROM parrots WHERE id='%s'" % result[1]
			cursor.execute(sql)
			uname_results = cursor.fetchall()
			for uname_result in uname_results:
				uname = uname_result[0]

			data.append({'id':result[0], 'parrot':uname, 'sent':str(result[2])})
		return json.dumps(data)
	except:
		return '-9'

@route('/birth',method='POST')
def birth():
	print request.body.read()
	uname = request.forms.get('uname')
	pw = request.forms.get('pw')
	if(uname != None and pw != None):
		if(len(uname)>48 or len(pw)>48):
			return '-5'
		pw = encode(KEY, pw)
		sql = "INSERT INTO parrots (uname, pw) VALUES ('%s', '%s');" % (uname, pw)
		print sql
		try:
			cursor.execute(sql)
			db.commit()
			sql = "SELECT id FROM parrots WHERE uname='%s';" % uname
			cursor.execute(sql)
			results = cursor.fetchall()
			for result in results:
				return "%s" % result[0]
		except:
			db.rollback()
			return '-2'
	return '-1'

@route('/wake',method='POST')
def wake():
	print request.body.read()
	uname = request.forms.get('uname')
	pw = request.forms.get('pw')
	if(uname != None and pw != None):
		pw = encode(KEY, pw)
		sql = "SELECT id FROM parrots WHERE uname='%s' AND pw='%s';" % (uname, pw)
		print sql
		try:
			cursor.execute(sql)
			results = cursor.fetchall()
			for result in results:
				return "%s" % result[0]
			return '-4'
		except:
			return '-3'
	return '-1'

run(host='0.0.0.0', port=45678, debug=True, reloader=True)

# ERRORS
# -1	request data error
# -2	parrot exsists
# -3	sql crash during signin
# -4	wrong parrot info
# -5	too long signin info
# -6 	crash inserting chirp
# -7 	bad get chirp info
# -8 	crash getting chirp
# -9	crash getting list of chirps
