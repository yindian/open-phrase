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

# counter for the search time
total_nu=0

#from urlgrabber.keepalive import HTTPHandler

#SEARCH_URL = "http://www.google.com/search?hl=en&lr=&as_qdr=all&%s&btnG=Search"
#<b>1,060</b> for <b>allintext:
RE = re.compile (r"<b>([0-9\,]+)</b>项符合<b>")
re_non = re.compile(r"<br>找不到和您的查询.*相符的网页。")

#keepalive_handler = HTTPHandler ()
#opener = urllib2.build_opener(keepalive_handler)
#urllib2.install_opener(opener)
# in key:(host,url)

g_list=[\
		#("www.google.cn","http://www.google.cn/search?hl=zh_CN&c2coff=1&lr=&as_qdr=all&%s&btnG=Google+%s&meta="),\
		("www.google.cn","http://www.google.cn/search?hl=zh-CN&c2coff=1&%s&btnG=Google+%s&meta=&aq=f"),\
		("www.google.com.sg","http://www.google.com.sg/search?hl=zh_CN&c2coff=1&lr=&as_qdr=all&%s&btnG=Google+%s&meta=&aq=f"),\
		("www.google.com","http://www.google.com/search?hl=zh_CN&c2coff=1&lr=&as_qdr=all&%s&btnG=Google+%s&meta=&aq=f")]

def get_search_result (keyword, g_tuple):
	freq = -1
	params0 = urllib.urlencode ({"as_epq": "\"%s\"" % keyword})
	params1 = urllib.pathname2url ("搜索")
	url = g_tuple[1] % (params0,params1)
	req = urllib2.Request (url)
	req.add_header ('User-agent', 'Mozilla/5.0')
	req.add_header ('Host', g_tuple[0])
	f = urllib2.urlopen (req)
	fetch=f.readlines()
	for l in fetch:	
		m = RE.findall (l)
		if m:
			freq = int (m[0].replace (",", ""))
			break
	if freq == -1:
		m = re_non.findall(l)
		if m:
			freq = 0
	return freq

def process_phrase_file (name, total):
#def process_phrase_file (name):

#	phrases = []
#	phrases_dict = {}
	lines = []
	result = False
	
	for l in open (name):
		# we take a rest of 15s for every 1000 times:)
		if total % 1000 ==0 and total != 0:
			print 'It time to pause a bit :)'
		time.sleep(15)
		phrase = l.strip ()
		try:
			# change search engine every 100 words
			freq = get_search_result (phrase,g_list[ total/100%3 ])
			if freq != -1:
				result = True
			else:
				print >> sys.stderr, "During searching for \"%s\", we are banned from google. we should stop and try later." % phrase
				sys.exit (-1)


		except KeyboardInterrupt, e:
			print >> sys.stderr, "Exit"
			sys.exit (1)
		line = "%s\t%d" % (phrase, freq)
		print line
		lines.append (line)
		total += 1
	if result == False: # Did not get any usefull data from google.
		print >> sys.stderr, "This time you did not get any usefull data from google. we should stop and try later."
		sys.exit (-1)

	output = file (name + ".out", "w")
	for line in lines:
		print >>output, line
	return total
		
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
		total_nu = process_phrase_file (fname, total_nu)
		#process_phrase_file (fname)#, total_nu)
		save_a_file_to_svn (fname + ".out")
		print fname + " finished"
