#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  8 20:19:32 2019

@author: shishir
"""

from bs4 import BeautifulSoup
import urllib3
import requests
#define a function to replace the nth occurence of a substring in a string
def nth_repl(s, sub, repl, nth):
    find = s.find(sub)
    # if find is not p1 we have found at least one match for the substring
    i = find != -1
    # loop util we find the nth or we find no match
    while find != -1 and i != nth:
        # find + 1 means we start at the last match start index + 1
        find = s.find(sub, find + 1)
        i += 1
    # if i  is equal to nth we found nth matches so replace
    if i == nth:
        return s[:find]+repl+s[find + len(sub):]
    return s


lines = [line.rstrip('\n') for line in open('tournaments.txt')]
#for line in lines:
line = lines[0]
print(line)
s = requests.Session() 
s.post(line, headers = {"ASP.NET_SessionId": "04hvjzcryj1t0zlxk21o0msc",'st': 'l=1033&exp=43839.48702875'})
r = s.get(line)

html_page = r.content
soup = BeautifulSoup(html_page, "lxml")
for link in soup.find_all('a'):
    print(link.get('href')) 
#drawslink = nth_repl(tournamentlink,'tournament','draws',2)
#html_page_draws = urllib2.urlopen(drawslink)
#soup = BeautifulSoup(html_page_draws, "lxml")
#for link in soup.find_all('a'):
#    print "http://tournamentsoftware.com" + link.get('href') 



