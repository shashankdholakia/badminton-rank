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
def stripseed(namestring):
    if "[" in namestring:
        n = namestring.index('[')
        return namestring[0:n-1]
    else:
        return namestring

    
def scraper(tournamentlink):    
    """
    Scrapes the tournamentsoftware website to find a list of every match played
    and winners and losers. 
    
    Inputs: link to the main tournament page on tournamentsoftware.com
    
    Outputs: Dictionary containing
    Player links: dictionary containing links to all players as the key and the players' names as values
    Singles Winners: list containing all singles winners in chronological format
    Singles Losers: list containing all singles losers in chronological format
    Doubles Winners: list containing all doubles winners in chronological format
    Doubles Losers: list containing all doubles losers in chronological format
    
    Note: the singles winners/losers and doubles winners/losers should correspond ie
    the zeroth element from singles winners and singles losers should be the winner and loser of that game
    
    """
    
    string = 'http://tournamentsoftware.com'
    s = requests.Session() 
    ###gets past the GDPR cookie wall in tournamentsoftware.com
    #note: test on other machines and test after clearing cookies to see if it still works
    s.post(tournamentlink, cookies = {'st': r'l=1033&exp=43841.9228685648&c=1'})
    matcheslistlink = nth_repl(tournamentlink,'tournament','matches',2)
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
    playernamedict = {}
    
    for day in dayslist:
        r = s.get(string+day)
        html_page_matchesofthatday = r.content
        soup = BeautifulSoup(html_page_matchesofthatday, "lxml")
        for line in soup.find_all('a'):
            if ("draw=" in line.get('href')) or ("player.aspx" in line.get('href')):
                list_of_matches.append(line.get('href'))
                if "player.aspx" in line.get('href'):
                    playernamedict[line.get('href')] = stripseed(line.string)

        
        for i,line in enumerate(list_of_matches):
            if "draw=" in line:
                try:
                    if 'player.aspx' not in list_of_matches[i+3] and 'player.aspx' in list_of_matches[i+1]:
                        singleswinnerlist.append(list_of_matches[i+1])
                        singlesloserlist.append(list_of_matches[i+2])
                    if 'player.aspx' in list_of_matches[i+3]:
                        doubleswinnerlist.append(list_of_matches[i+1])
                        doubleswinnerlist.append(list_of_matches[i+2])
                        doublesloserlist.append(list_of_matches[i+3])
                        doublesloserlist.append(list_of_matches[i+4])
                except(IndexError):
                        singleswinnerlist.append(list_of_matches[i+1])
                        singlesloserlist.append(list_of_matches[i+2])
                    
    return {"Player links": playernamedict,"Singles Winners": singleswinnerlist,"Singles Losers": singlesloserlist,"Doubles Winners": doubleswinnerlist,"Doubles Losers": doublesloserlist}
#html_page_draws = r.content
#soup = BeautifulSoup(html_page_draws, "lxml")
#for namelink in soup.find_all('a'):
#    print(namelink.get('href'))
#drawslink = nth_repl(tournamentlink,'tournament','draws',2)
#html_page_draws = urllib2.urlopen(drawslink)
#soup = BeautifulSoup(html_page_draws, "lxml")
#for link in soup.find_all('a'):
#    print "http://tournamentsoftware.com" + link.get('href') 



