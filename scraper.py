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
def winnerlister(list_of_matches):

    for i,line in enumerate(list_of_matches):
        if "draw=" in line:
            if 'match-info' in list_of_matches[i+3]:
                singleswinnerlist.append(list_of_matches[i+1])
                singlesloserlist.append(list_of_matches[i+2])
            if 'match-info' in list_of_matches[i+5]:
                doubleswinnerlist.append(list_of_matches[i+1])
                doubleswinnerlist.append(list_of_matches[i+2])
                doublesloserlist.append(list_of_matches[i+3])
                doublesloserlist.append(list_of_matches[i+4])
    return[singleswinnerlist,singlesloserlist,doubleswinnerlist,doublesloserlist]
    
    
string = 'http://tournamentsoftware.com'
lines = [line.rstrip('\n') for line in open('tournaments.txt')]
#for line in lines:
line = lines[0]
print(line)
print('blah')
s = requests.Session() 
s.post(line, cookies = {'st': r'l=1033&exp=43841.9228685648&c=1'})
matcheslistlink = nth_repl(line,'tournament','matches',2)
r = s.get(matcheslistlink)
html_page = r.content
soup = BeautifulSoup(html_page, "lxml")
list_of_matches = []
dayslist = []
singleswinnerlist = []
doubleswinnerlist = []
doublesloserlist = []
singlesloserlist = []
for link in soup.find_all('a'):
    if '&d=' in link.get('href'):
        dayslist.append(link.get('href'))
for day in dayslist:
    r = s.get(string+day)
    html_page_matchesofthatday = r.content
    soup = BeautifulSoup(html_page_matchesofthatday, "lxml")
    list_of_matches = [line.get('href') for line in soup.find_all('a')]
    print(len(list_of_matches))
    singleswinnerlist,singlesloserlist,doubleswinnerlist,doublesloserlist = winnerlister(list_of_matches)
        
#html_page_draws = r.content
#soup = BeautifulSoup(html_page_draws, "lxml")
#for namelink in soup.find_all('a'):
#    print(namelink.get('href'))
#drawslink = nth_repl(tournamentlink,'tournament','draws',2)
#html_page_draws = urllib2.urlopen(drawslink)
#soup = BeautifulSoup(html_page_draws, "lxml")
#for link in soup.find_all('a'):
#    print "http://tournamentsoftware.com" + link.get('href') 



