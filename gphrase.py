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
import socket

random.seed (time.time ())

# counter for the search time
total_nu=0

#from urlgrabber.keepalive import HTTPHandler

#SEARCH_URL = "http://www.google.com/search?hl=en&lr=&as_qdr=all&%s&btnG=Search"
#RE = re.compile(r"<b>1,060</b> for <b>")
#RE = re.compile (r"<b>([0-9\,]+)</b> for <b>")
RE = re.compile (r"<b>([0-9\,]+)</b> *项符合<b>")
#re_non = re.compile (r"<br>Your search - .* - did not match any documents.")
re_non = re.compile(r"<br>找不到和您的查询.*相符的网页。")

#keepalive_handler = HTTPHandler ()
#opener = urllib2.build_opener(keepalive_handler)
#urllib2.install_opener(opener)
# in key:(host,url)
g_url = "http://%s/search?%s&hl=zh_CN&newwindow=1&c2coff=1&lr="
g_list=[\
	"203.208.37.104",
	"203.208.37.99",
	"216.239.51.100",
	"216.239.59.103",
	"216.239.59.104",
	"216.239.59.147",
	"216.239.59.99",
	"64.233.161.104",
	"64.233.161.99",
	"64.233.163.104",
	"64.233.163.99",
	"64.233.169.147",
	"64.233.183.91",
	"64.233.183.99",
	"64.233.187.104",
	"64.233.187.107",
	"64.233.187.99",
	"66.102.11.104",
	"66.102.11.99",
	"66.102.9.104",
	"66.102.9.107",
	"66.102.9.147",
	"66.102.9.99",
	"66.249.89.147",
	"72.14.203.104",
	"72.14.235.147",
	]

def get_search_result (keyword, ip):
	freq = -1
	params0 = urllib.urlencode ({"as_epq": "\"%s\"" % keyword})
	#params1 = urllib.pathname2url ("搜索")
	url = g_url % (ip, params0)#,params1)
	print url
	req = urllib2.Request (url)
	req.add_header ('Host', ip)
	req.add_header ('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; zh-CN; rv:1.8.1.11) Gecko/20080112 Firefox/2.0.0.11')
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
	# write for debug:
	ef=file('err.html','w')
	ef.writelines(fetch)
	ef.close()
	return freq

def process_phrase_file (name, total):
	lines = []
	rd_n = _rd_n=0
	for l in open (name):
		result = False
		phrase = l.strip ()
		while not result:
			try:
		#		print phrase
				while rd_n == _rd_n: 
					rd_n = random.randint(0,len(g_list)-1)
				_rd_n =rd_n
				print rd_n
				freq = get_search_result (phrase,g_list[ rd_n ])
				if freq != -1:
					result = True
				else:
					print >> sys.stderr, "During searching for \"%s\", we are banned from google. we should stop and try later." % phrase
					sys.exit (-1)
			except socket.error, e:
				print socket.error,e
				print "we pause 15s now:)"
				time.sleep(15)
			except urllib2.URLError,e:
				print urllib2.URLError, e
				print "we have to wait 15s :("
				time.sleep(15)
			except KeyboardInterrupt, e:
				print >> sys.stderr, "Exit"
				sys.exit (1)
			except :
				print >> sys.stderr, "retry"
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
	#~ os.system ("svn update data")
	remove_out = lambda x : x[:-4]
	done_files = map (remove_out, glob.glob ("data/phrase.????.out"))

	files_new = list (set (files) - set (done_files))
	if files_new:
		return files_new [random.randint (0, len (files_new) - 1)]
	else:
		return None

if __name__ == "__main__":
	#for keyword in sys.argv[1:]:
	#	print get_search_result (keyword)
	socket.setdefaulttimeout(timeout)
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
		print fname + " finished"
