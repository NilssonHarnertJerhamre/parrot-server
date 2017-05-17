import httplib, subprocess

c = httplib.HTTPConnection('localhost', 45678)
c.request('POST', '/chirp', '{}')
doc = c.getresponse().read()
print doc
