#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  6 21:08:20 2018

@author: shashank
"""
from ranking import Ranking
from ranking import num_there


r = Ranking()
r.deleteValues()

games = r.readCSV('matches.csv')

for i in games:
    if (i[0] not in r.ratings):
        r.addPlayer(i[0])
    if (i[1] not in r.ratings):
        r.addPlayer(i[1])
    if (i[2] not in r.ratings and not num_there(i[2])):
        r.addPlayer(i[2])
    if (i[3] not in r.ratings and not num_there(i[3])):
        r.addPlayer(i[3])
    if not num_there(i[2]):
        r.playDoubles(i[0],i[1],i[2],i[3])
    else:
        r.playSingles(i[0],i[1])
        
r.printLeaderboard(toCSV=True,path='leaderboard.csv')