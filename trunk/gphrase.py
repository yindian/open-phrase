#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
import urllib
import re
import sys, os
import time
import traceback
import os.path as path
import random

random.seed (time.time ())
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
	result = False
	
	for l in open (name):
		phrase = l.strip ()
		try:
			freq = get_search_result (phrase)
			if freq != -1:
				result = True
		except KeyboardInterrupt, e:
			print >> sys.stderr, "Exit"
			sys.exit (1)
		except:
			freq = -1
		line = "%s\t%d" % (phrase, freq)
		print line
		lines.append (line)

	if result == False: # Did not get any usefull data from google.
		print >> sys.stderr, "This time you did not get any usefull data from google. we should stop and try later."
		sys.exit (-1)

	output = file (name + ".out", "w")
	for line in lines:
		print >>output, line
		
def pick_a_file (files):
	os.system ("svn update data")
	remove_out = lambda x : x[:-4]
	done_files = map (remove_out, glob.glob ("data/phrase.????.out"))

	files_new = list (set (files) - set (done_files))
	if files_new:
		return files_new [random.randint (0, len (files_new) - 1)]
	else:
		return None

def save_a_file_to_svn (file_name):
	os.system ("svn add %s" % file_name)
	os.system ("svn ci %s -m \"add %s\"" % (file_name, file_name))

if __name__ == "__main__":
	#for keyword in sys.argv[1:]:
	#	print get_search_result (keyword)
	import glob
	files = glob.glob ("data/phrase.????")
	files.sort ()
	while True:
		fname = pick_a_file (files)
		if fname == None:
			print "All were done!"
			break
		if path.exists (fname + ".out"):
			print fname + " finished"
			continue
		print "Start process " + fname
		process_phrase_file (fname)
		save_a_file_to_svn (fname + ".out")
		print fname + " finished"
		time.sleep (30)
