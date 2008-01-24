#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
import urllib
import re
import sys
import time
import traceback
import os.path as path
#from urlgrabber.keepalive import HTTPHandler

SEARCH_URL = "http://www.google.com/search?hl=en&lr=&as_qdr=all&%s&btnG=Search"
#<b>1,060</b> for <b>allintext:
RE = re.compile ("<b>([0-9\,]+)</b> for <b>")

#keepalive_handler = HTTPHandler ()
#opener = urllib2.build_opener(keepalive_handler)
#urllib2.install_opener(opener)

def get_search_result (keyword):
	freq = -1
	params = urllib.urlencode ({"q": "\"%s\"" % keyword})
	url = SEARCH_URL % params
	req = urllib2.Request (url)
	req.add_header ('User-agent', 'Mozilla/5.0')
	req.add_header ('Host', 'www.google.com')
	f = urllib2.urlopen (req)
	for l in f:
		m = RE.findall (l)
		if m:
			freq = int (m[0].replace (",", ""))
			break
	return freq

def process_phrase_file (name):
	phrases = []
	phrases_dict = {}
	lines = []
	
	for l in open (name):
		phrase = l.strip ()
		try:
			freq = get_search_result (phrase)
		except KeyboardInterrupt, e:
			print >> sys.stderr, "Exit"
			sys.exit (1)
		except:
			freq = -1
		line = "%s\t%d" % (phrase, freq)
		print line
		lines.append (line)

	output = file (name + ".out", "w")
	for line in lines:
		print >>output, line
		

if __name__ == "__main__":
	#for keyword in sys.argv[1:]:
	#	print get_search_result (keyword)
	import glob
	files = glob.glob ("data/phrase.????")
	files.sort ()
	for fname in files:
		if path.exists (fname + ".out"):
			print fname + " finished"
			continue
		print "Start process " + fname
		process_phrase_file (fname)
		print fname + " finished"
		time.sleep (15)
