#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 23:09:09 2019

@author: shishir
"""

#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  8 20:19:32 2019

@author: shishir
"""
import os
import csv
from bs4 import BeautifulSoup
import requests
import pandas as pd


class Alias:
    """
    Defines an Alias object which deals with duplicate names of players in
    different tournaments. For instance, if a player makes multiple accounts with
    the same name after forgetting their password (very common!), the Alias object can track these
    different accounts and link them to the same person. In addition, if a person uses 
    a different name through different tournaments, the Alias object can keep track of
    this also.
    
    In order to merge two tournamentsoftware accounts belonging to the same person
    manually, you need to write both full names used in both accounts and the link to
    both accounts in the same row in alias.csv.
    
    For instance write in any row in alias.csv:
    Jane Doe, www.tournamentsoftware.com/2342342/233, Jane FemaleDeer, www.tournamentsoftware.com/2342342/234
    
    The first column down alias.csv corresponds to the default (used) name for every player.
    """
    def __init__(self, filename='alias.csv'):
        if os.path.exists(filename):
            self.aliases = self.read_csv(filename)

        else:
            self.aliases = []
            self.dump_csv(filename)
            
            
    def read_csv(self,filename='alias.csv'):
        with open(filename, 'rU') as f:  #opens PW file
            data = list(list(row) for row in csv.reader(f, delimiter=',')) #reads csv into a list of lists
            f.close() #close the csv
            self.aliases = data
    
    def dump_csv(self,filename='alias.csv'):
        with open (filename,'w') as f:
            wtr = csv.writer(f)
            for row in self.aliases:
                wtr.writerow(row)
                
    def add_alias(self,name,currentid):
        namerow = self.case_insensitive_search(name)
        currentidrow = self.case_insensitive_search(currentid)
        if currentidrow != -1:
            #this means the id is already in the alias.csv file, so this account already is known
            if namerow == -1:
            #in case the account url is in the aliases but not the name, add the name
                self.aliases[currentidrow].append(name)
        else:
            #check to see if the same name exists somewhere in the aliases file
            if namerow !=-1:
                self.aliases[namerow].append(currentid)
            else:
                self.aliases.append([name,currentid])
        self.dump_csv()
           
            
    def case_insensitive_search(self, term):
        """
        Searches a list of lists for a string insensitive of case
        and returns the row number corresponding to the location of the string
        
        Returns -1 if not found
        """
        for index,row in enumerate(self.aliases):
            for name in row:
                if name.lower() == term.lower():
                    return index
        return -1
    
    def get_default_name(self, currentid,name = None):
        rownum = self.case_insensitive_search(term=currentid)
        if rownum !=-1:
            return self.aliases[rownum][0]
        else:
            raise IndexError("No such ID exists")
    
    def get_default_id(self, name,currentid = None):
        rownum = self.case_insensitive_search(term=name)
        if rownum !=-1:
            return self.aliases[rownum][1]
        else:
            raise IndexError("No such name exists")
    
    
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

#badly writed cod that takes the html title and strips it to the essentials
def strip_title(html_title):
    html_title = str(html_title)
    s = html_title[html_title.find(' - ')+3:]
    s = s[:s.find(' - ')]
    return s
            

def dict_to_csv(mydict,filepath):
    with open(filepath, 'w') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in mydict.items():
            writer.writerow([key, value])
            
def csv_to_dict(filepath):
    with open(filepath) as csv_file:
        reader = csv.reader(csv_file)
        mydict = dict(reader)
    return mydict
            
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
    
    string = 'http://tournamentsoftware.com/sport/'
    s = requests.Session() 
    ###gets past the GDPR cookie wall in tournamentsoftware.com
    #note: test on other machines and test after clearing cookies to see if it still works
    s.post(tournamentlink, cookies = {'st': r'l=1033&exp=43841.9228685648&c=1'})
    matcheslistlink = nth_repl(tournamentlink,'tournament','draws',2)
    print(matcheslistlink)
    r = s.get(matcheslistlink)
    html_page = r.content
    soup = BeautifulSoup(html_page, "lxml")
    tournament_name = strip_title(soup.title)
    print(tournament_name)
    
    #check if a cached version exists already:
    if (os.path.exists('tournament_data/'+tournament_name.replace(" ", "")+'_singles.csv') and
        os.path.exists('tournament_data/'+tournament_name.replace(" ", "")+'_doubles.csv') and
        os.path.exists('tournament_data/'+tournament_name.replace(" ", "")+'_players.csv')):
        
        singles_df = pd.read_csv('tournament_data/'+tournament_name.replace(" ", "")+'_singles.csv',index_col = 0)
        doubles_df = pd.read_csv('tournament_data/'+tournament_name.replace(" ", "")+'_doubles.csv',index_col = 0)
        playernamedict = csv_to_dict('tournament_data/'+tournament_name.replace(" ", "")+'_players.csv')
        return {"Player links": playernamedict,"Singles results": singles_df,"Doubles results":doubles_df}
    
    
    #if not, scrape tournamentsoftware to get the tournament data
    else:
        list_of_matches = []
        drawslist = []
        #the variant links are the player links that change depending on the tournament
        #basically the variant link links to a players' performance in that tournament
        #but we will want the players' profile link, which does not change from tournament to tournament
        variantlinks = {}
        doubles_df = pd.DataFrame(columns=["Winner1","Winner2", "Loser1","Loser2"])
        singles_df = pd.DataFrame(columns=["Winner","Loser"])
        #Iterate over every draw, not every draw
        for link in soup.find_all('a'):
            if '&draw=' in link.get('href'):
                drawmatch = nth_repl(link.get('href'),'draw','drawmatches',1)
                drawslist.append(drawmatch)

                
        
        playernamedict = {}
        #iterate over every link corresponding to a given tournament day
        for draw in drawslist:
            print('~~~~~~~~~')
            #Get an HTML page for one specific day of a tournament            
            r = s.get(string+draw)
            html_page_matchesofthatdraw = r.content
            soup = BeautifulSoup(html_page_matchesofthatdraw, "lxml")
            #iterate over ALL links in that day of the tournament
            
            #This contains all the matches played that day -- players, draws, etc
            
            for line in soup.find_all('tbody'):
                for tag in line.children:
                    if tag.name == 'tr':
                        lst = []
                        print(tag.name)
                        for element in tag.find_all('a'):
                            if "player.aspx" in element.get('href'):
                                if element.get('href') not in variantlinks.keys():
                                    r_playerprofile = s.get(string+'/sport/'+element.get('href'))
                                    html_page_playerprofiles = r_playerprofile.content
                                    soup_playerprofile = BeautifulSoup(html_page_playerprofiles, "lxml")
                                    try:
                                        playerprofilelink = [playerprofile.get('href') for playerprofile in soup_playerprofile.find_all('a') if "/player/" in playerprofile.get('href')][0]
                                        lst.append(playerprofilelink)
                                        playernamedict[playerprofilelink] = stripseed(element.string)
                                        variantlinks[element.get('href')] = playerprofilelink
                                    except(IndexError):
                                        lst.append('/player/'+stripseed(element.string))
                                        playernamedict['/player/'+stripseed(element.string)] = stripseed(element.string)
                                 #the player profile link has already been accessed, no need to access it again
                                else:
                                    lst.append(variantlinks[line.get('href')])
                        #Add the length of the list to the front of the list
                        #If it is doubles, len = 4 and 2 if singles
                        if (len(lst) == 4 or len(lst) == 2):
                            list_of_matches += [len(lst)] + lst
                        
      
            for i,value in enumerate(list_of_matches):
                try:
                    if value == 2:
                        temp_df = pd.DataFrame({'Winner':list_of_matches[i+1],'Loser':list_of_matches[i+2]},index=[1])
                        singles_df = pd.concat([singles_df,temp_df],ignore_index=True)
                    elif value == 4: 
                        temp_df = pd.DataFrame({'Winner1':list_of_matches[i+1],'Winner2':list_of_matches[i+2],
                                                        'Loser1':list_of_matches[i+3],'Loser2':list_of_matches[i+4]},index=[1])
            
                        doubles_df = pd.concat([doubles_df,temp_df],ignore_index=True)
                except:
                    pass
      

        singles_df.to_csv('tournament_data/'+tournament_name.replace(" ", "")+'_singles.csv')
        doubles_df.to_csv('tournament_data/'+tournament_name.replace(" ", "")+'_doubles.csv')
        dict_to_csv(mydict=playernamedict,filepath=('tournament_data/'+tournament_name.replace(" ", "")+'_players.csv'))
        print("Cached results of tournament: "+tournament_name)
        return {"Player links": playernamedict,"Singles results": singles_df,"Doubles results":doubles_df}          
        '''
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
                        if r'/player/' not in list_of_matches[i+3] and r'/player/' in list_of_matches[i+1] and r'/player/' in list_of_matches[i+2]:
                            temp_df = pd.DataFrame({'Winner':list_of_matches[i+1],'Loser':list_of_matches[i+2]},index=[1])
                            singles_df = pd.concat([singles_df,temp_df],ignore_index=True)
                        #if it's a doubles game, add the first and second players to the winners list and the third and fourth to the losers'
                        if r'/player/' in list_of_matches[i+3] and r'/player/' in list_of_matches[i+1] and r'/player/' in list_of_matches[i+2] and r'/player/' in list_of_matches[i+4]:
                            temp_df = pd.DataFrame({'Winner1':list_of_matches[i+1],'Winner2':list_of_matches[i+2],
                                                    'Loser1':list_of_matches[i+3],'Loser2':list_of_matches[i+4]},index=[1])
        
                            doubles_df = pd.concat([doubles_df,temp_df],ignore_index=True)
                        else:
                            pass
                    #unless the last game of the list is a singles game; then add it differently
                    except(IndexError):
                        temp_df = pd.DataFrame({'Winner':list_of_matches[i+1],'Loser':list_of_matches[i+2]},index=[1])
                        singles_df = pd.concat([singles_df,temp_df],ignore_index=True)
        singles_df.to_csv('tournament_data/'+tournament_name.replace(" ", "")+'_singles.csv')
        doubles_df.to_csv('tournament_data/'+tournament_name.replace(" ", "")+'_doubles.csv')
        dict_to_csv(mydict=playernamedict,filepath=('tournament_data/'+tournament_name.replace(" ", "")+'_players.csv'))
        print("Cached results of tournament: "+tournament_name)
        return {"Player links": playernamedict,"Singles results": singles_df,"Doubles results":doubles_df}
        '''



