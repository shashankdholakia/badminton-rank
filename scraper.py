#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  8 20:19:32 2019

@author: shishir
"""

from bs4 import BeautifulSoup
import urllib3
import requests
import pandas as pd

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
    #the variant links are the player links that change depending on the tournament
    #basically the variant link links to a players' performance in that tournament
    #but we will want the players' profile link, which does not change from tournament to tournament
    variantlinks = {}
    counter = 0
    doubles_df = pd.DataFrame(columns=["Winner1","Winner2", "Loser1","Loser2"])
    singles_df = pd.DataFrame(columns=["Winner","Loser"])
    for link in soup.find_all('a'):
        if '&d=' in link.get('href'):
            dayslist.append(link.get('href'))
    playernamedict = {}
    #iterate over every link corresponding to a given tournament day
    for day in dayslist:
        #Get an HTML page for one specific day of a tournament
        r = s.get(string+day)
        html_page_matchesofthatday = r.content
        soup = BeautifulSoup(html_page_matchesofthatday, "lxml")
        #iterate over ALL links in that day of the tournament
        #This contains all the matches played that day -- players, draws, etc
        for line in soup.find_all('a'):
            #if the link is a draw, add it to a list that tabulates all the matches in a coherent form
            if "draw=" in line.get('href'):
                list_of_matches.append(line.get('href'))
            #if the link is a player, click on their name and add that profile link to the aforementioned list
            #also add that link to a dictionary pairing those player profile links to the names of the players
            #list_of_matches will now be formatted into a draw, winning player(s), losing player(s), draw, etc format
            if "player.aspx" in line.get('href'):
                if line.get('href') not in variantlinks.keys():
                    r_playerprofile = s.get(string+'/sport/'+line.get('href'))
                    html_page_playerprofiles = r_playerprofile.content
                    soup_playerprofile = BeautifulSoup(html_page_playerprofiles, "lxml")
                    try:
                        playerprofilelink = [playerprofile.get('href') for playerprofile in soup_playerprofile.find_all('a') if "/player/" in playerprofile.get('href')][0]
                        list_of_matches.append(playerprofilelink)
                        playernamedict[playerprofilelink] = stripseed(line.string)
                        variantlinks[line.get('href')] = playerprofilelink
                    except(IndexError):
                        list_of_matches.append('/player/'+stripseed(line.string))
                        playernamedict['/player/'+stripseed(line.string)] = stripseed(line.string)

                #the player profile link has already been accessed, no need to access it again
                else:
                    list_of_matches.append(variantlinks[line.get('href')])
                    
        for i,line in enumerate(list_of_matches):
            if "draw=" in line:
                try:
                    #if it's a singles game, add the first player to the winners list and the second to the losers'
                    if r'/player/' not in list_of_matches[i+3] and r'/player/' in list_of_matches[i+1]:
                        temp_df = pd.DataFrame({'Winner':list_of_matches[i+1],'Loser':list_of_matches[i+2]},index=[1])
                        singles_df = pd.concat([singles_df,temp_df],ignore_index=True)
                    #if it's a doubles game, add the first and second players to the winners list and the third and fourth to the losers'
                    if r'/player/' in list_of_matches[i+3]:
                        temp_df = pd.DataFrame({'Winner1':list_of_matches[i+1],'Winner2':list_of_matches[i+2],
                                                'Loser1':list_of_matches[i+3],'Loser2':list_of_matches[i+4]},index=[1])
    
                        doubles_df = pd.concat([doubles_df,temp_df],ignore_index=True)
                #unless the last game of the list is a singles game; then add it differently
                except(IndexError):
                    temp_df = pd.DataFrame({'Winner':list_of_matches[i+1],'Loser':list_of_matches[i+2]},index=[1])
                    singles_df = pd.concat([singles_df,temp_df],ignore_index=True)
    return {"Player links": playernamedict,"Singles results": singles_df,"Doubles results":doubles_df}
#html_page_draws = r.content
#soup = BeautifulSoup(html_page_draws, "lxml")
#for namelink in soup.find_all('a'):
#    print(namelink.get('href'))
#drawslink = nth_repl(tournamentlink,'tournament','draws',2)
#html_page_draws = urllib2.urlopen(drawslink)
#soup = BeautifulSoup(html_page_draws, "lxml")
#for link in soup.find_all('a'):
#    print "http://tournamentsoftware.com" + link.get('href') 



