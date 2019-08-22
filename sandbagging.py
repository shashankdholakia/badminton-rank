#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 26 22:10:18 2019

@author: shashank
"""

import pandas as pd
from scraper import Alias
from ranking import Ranking
from ranking import num_there
import numpy as np
import math
import matplotlib.pyplot as plt
import csv

def get_skills(leaderboard,event,height,exclude_errors=False):
    
    """
    if exlcude_errors is False:
        this includes all players. Even if a player's partner isn't signed up,
        it will assume the players' partner's skill is average with the starting STD DEV
    if exclude_errors is True:
        this will exclude players whose partners are not signed up yet. It will include
        teams in which one or both players aren't in the standings, and assume default
        skill and STD DEV
    if exclude_errors is all:
        this will exclude teams in which either partner is not in the standings, or who
        haven't yet signed up
    if exclude_errors is assume partner:
        this assumes that if a player is not in the standings, that player
        has the same skill level as his partner, but with the default STD DEV
    """
    aliases = Alias()
    aliases.read_csv()
    
    event_players = []
    for index,row in event.iterrows():
        if (not math.isnan(row['Number'])) and (math.isnan(event.iloc[index+1]['Number'])):
            event_players.append([event.iloc[index]['player'],event.iloc[index+1]['player']])
    CS_players = []
    CS_values = []
    not_in_rankings = []
    
    for value in event_players:
        if (not pd.isna(value[0])):
            try:
                player1_id = aliases.get_default_id(value[0])
                player1_name = aliases.get_default_name(player1_id)
            except IndexError:
                player1_name=value[0]
                not_in_rankings.append(value[0])

        else:
             player1_name="None"
        
        
        if (not pd.isna(value[1])):
            try:
                player2_id = aliases.get_default_id(value[1])
                player2_name = aliases.get_default_name(player2_id)
            except IndexError:
                player2_name=value[1]
                not_in_rankings.append(value[1])


        else:
             player2_name="None"
        
        player1 = np.where(leaderboard == player1_name)[0]
        player2 = np.where(leaderboard == player2_name)[0]
        
        if len(player1) == 1:
            player1_name = leaderboard.iloc[player1[0]][0]
            player1_average = leaderboard.iloc[player1[0]]['Average']
            player1_std = leaderboard.iloc[player1[0]]['95% CI']
        else:
            player1_average = 25
            player1_std = 8.333*2
            
        if len(player2) == 1:
            player2_name = leaderboard.iloc[player2[0]][0]
            player2_average = leaderboard.iloc[player2[0]]['Average']
            player2_std = leaderboard.iloc[player2[0]]['95% CI']
        else:
            player2_average = 25
            player2_std = 8.333*2
            
        if exclude_errors:
            if player1_name!='None' and player2_name!='None':
                CS_players.append([player1_name,player2_name])
                CS_values.append(player1_average-player1_std+player2_average-player2_std)
        elif exclude_errors=='all':
            if (not player1_name in not_in_rankings) and (not player2_name in not_in_rankings):
                CS_players.append([player1_name,player2_name])
                CS_values.append(player1_average-player1_std+player2_average-player2_std)
        elif exclude_errors=='assume partner':
            if (player1_name in not_in_rankings) and (not player2_name in not_in_rankings):
                CS_players.append([player1_name,player2_name])
                CS_values.append(player2_average-player1_std+player2_average-player2_std)
            elif (not player1_name in not_in_rankings) and (player2_name in not_in_rankings):
                CS_players.append([player1_name,player2_name])
                CS_values.append(player1_average-player1_std+player1_average-player2_std)
            elif (not player1_name in not_in_rankings) and (not player2_name in not_in_rankings):
                CS_players.append([player1_name,player2_name])
                CS_values.append(player1_average-player1_std+player2_average-player2_std)
        else:
            CS_players.append([player1_name,player2_name])
            CS_values.append(player1_average-player1_std+player2_average-player2_std)
            
    ones = []
    for i in range(len(CS_values)):
        ones.append(height)
    CS_skill, CS_players = zip(*sorted(zip(CS_values, CS_players)))
    return CS_skill,CS_players,ones,not_in_rankings

def get_skills_singles(leaderboard,event,height,exclude_errors=False):
    
    """
    if exlcude_errors is False:
        this includes all players. Even if a player's partner isn't signed up,
        it will assume the players' partner's skill is average with the starting STD DEV
    if exclude_errors is True:
        this will exclude players whose partners are not signed up yet. It will include
        teams in which one or both players aren't in the standings, and assume default
        skill and STD DEV
    if exclude_errors is all:
        this will exclude teams in which either partner is not in the standings, or who
        haven't yet signed up
    if exclude_errors is assume partner:
        this assumes that if a player is not in the standings, that player
        has the same skill level as his partner, but with the default STD DEV
    """
    aliases = Alias()
    aliases.read_csv()
    
    event_players = []
    for index,row in event.iterrows():
        event_players.append(event.iloc[index]['player'])
    CS_players = []
    CS_values = []
    not_in_rankings = []
    
    for value in event_players:
        try:
            player_id = aliases.get_default_id(value)
            player_name = aliases.get_default_name(player_id)
        except IndexError:
            player_name=value
            not_in_rankings.append(value)

        
        player = np.where(leaderboard == player_name)[0]

        
        if len(player) == 1:
            player_name = leaderboard.iloc[player[0]][0]
            player_average = leaderboard.iloc[player[0]]['Average']
            player_std = leaderboard.iloc[player[0]]['95% CI']
        else:
            player_average = 25
            player_std = 8.333*2

            
        if exclude_errors:
            if not (player_name in not_in_rankings):
                CS_players.append(player_name)
                CS_values.append(player_average-player_std)

        else:
            CS_players.append(player_name)
            CS_values.append(player_average-player_std)
            
    ones = []
    for i in range(len(CS_values)):
        ones.append(height)
    CS_skill, CS_players = zip(*sorted(zip(CS_values, CS_players)))
    return CS_skill,CS_players,ones,not_in_rankings





            
            
leaderboard = pd.read_csv("ranking.csv")
amd = pd.read_csv("amd.csv",names=['Number','player'])
bmd = pd.read_csv("bmd.csv",names=['Number','player'])
cmd = pd.read_csv("cmd.csv",names=['Number','player'])
dmd = pd.read_csv("dmd.csv",names=['Number','player'])
CS_skill_amd,CS_players_amd,ones_amd,not_in_rankings_amd = get_skills(leaderboard,amd,3,exclude_errors='assume partner')
CS_skill_bmd,CS_players_bmd,ones_bmd,not_in_rankings_bmd = get_skills(leaderboard,bmd,2,exclude_errors='assume partner')
CS_skill_cmd,CS_players_cmd,ones_cmd,not_in_rankings_cmd = get_skills(leaderboard,cmd,1,exclude_errors='assume partner')
CS_skill_dmd,CS_players_dmd,ones_dmd,not_in_rankings_dmd = get_skills(leaderboard,dmd,0,exclude_errors='assume partner')

print()
print("Mens Doubles:")

#print(set(not_in_rankings_amd)|set(not_in_rankings_bmd)|set(not_in_rankings_cmd)|set(not_in_rankings_dmd))

print(CS_players_amd,CS_skill_amd)
print(' ')
print(CS_players_bmd,CS_skill_bmd)
print(' ')
print(CS_players_cmd,CS_skill_cmd)
print(' ')
print(CS_players_dmd,CS_skill_dmd)
print(' ')
print(set(not_in_rankings_amd)|set(not_in_rankings_bmd)|set(not_in_rankings_cmd)|set(not_in_rankings_dmd))

with open('MD.csv', 'wb') as csvfile:
    spamreader = csv.writer(csvfile, delimiter=',')
    spamreader.writerow(['AMD name','AMD skill'])
    for name,skill in zip(CS_players_amd,CS_skill_amd):
        spamreader.writerow([name,skill])
    spamreader.writerow(['',''])
    spamreader.writerow(['BMD name','BMD skill'])
    for name,skill in zip(CS_players_bmd,CS_skill_bmd):
        spamreader.writerow([name,skill])
    spamreader.writerow(['',''])
    spamreader.writerow(['CMD name','CMD skill'])
    for name,skill in zip(CS_players_cmd,CS_skill_cmd):
        spamreader.writerow([name,skill])  
    spamreader.writerow(['',''])
    spamreader.writerow(['DMD name','DMD skill'])
    for name,skill in zip(CS_players_dmd,CS_skill_dmd):
        spamreader.writerow([name,skill])
     
plt.clf()
plt.scatter(CS_skill_amd,ones_amd,label='AMD')
plt.scatter(CS_skill_bmd,ones_bmd,label='BMD')
plt.scatter(CS_skill_cmd,ones_cmd,label='CMD')
plt.scatter(CS_skill_dmd,ones_dmd,label='DMD')
plt.xlabel('Minimum Likely Skill (95% Confidence)')
plt.yticks([])
plt.legend()
plt.savefig('MD.png')

axd = pd.read_csv("axd.csv",names=['Number','player'])
bxd = pd.read_csv("bxd.csv",names=['Number','player'])
cxd = pd.read_csv("cxd.csv",names=['Number','player'])
dxd = pd.read_csv("dxd.csv",names=['Number','player'])

CS_skill_axd,CS_players_axd,ones_axd,not_in_rankings_axd = get_skills(leaderboard,axd,3,exclude_errors='assume partner')
CS_skill_bxd,CS_players_bxd,ones_bxd,not_in_rankings_bxd = get_skills(leaderboard,bxd,2,exclude_errors='assume partner')
CS_skill_cxd,CS_players_cxd,ones_cxd,not_in_rankings_cxd = get_skills(leaderboard,cxd,1,exclude_errors='assume partner')
CS_skill_dxd,CS_players_dxd,ones_dxd,not_in_rankings_dxd = get_skills(leaderboard,dxd,0,exclude_errors='assume partner')

print()
print("Mixed Doubles:")

plt.clf()
plt.scatter(CS_skill_axd,ones_axd,label='AXD')
plt.scatter(CS_skill_bxd,ones_bxd,label='BXD')
plt.scatter(CS_skill_cxd,ones_cxd,label='CXD')
plt.scatter(CS_skill_dxd,ones_dxd,label='DXD')
plt.xlabel('Minimum Likely Skill (95% Confidence)')
plt.yticks([])
plt.legend()
plt.savefig('MX.png')

print(CS_players_axd,CS_skill_axd)
print(' ')
print(CS_players_bxd,CS_skill_bxd)
print(' ')
print(CS_players_cxd,CS_skill_cxd)
print(' ')
print(CS_players_dxd,CS_skill_dxd)
print(' ')
print(set(not_in_rankings_axd)|set(not_in_rankings_bxd)|set(not_in_rankings_cxd)|set(not_in_rankings_dxd))
with open('MX.csv', 'wb') as csvfile:
    spamreader = csv.writer(csvfile, delimiter=',')
    spamreader.writerow(['AXD name','AXD skill'])
    for name,skill in zip(CS_players_axd,CS_skill_axd):
        spamreader.writerow([name,skill])
    spamreader.writerow(['',''])
    spamreader.writerow(['BXD name','BXD skill'])
    for name,skill in zip(CS_players_bxd,CS_skill_bxd):
        spamreader.writerow([name,skill])
    spamreader.writerow(['',''])
    spamreader.writerow(['CXD name','CXD skill'])
    for name,skill in zip(CS_players_cxd,CS_skill_cxd):
        spamreader.writerow([name,skill])  
    spamreader.writerow(['',''])
    spamreader.writerow(['DXD name','DXD skill'])
    for name,skill in zip(CS_players_dxd,CS_skill_dxd):
        spamreader.writerow([name,skill])

awd = pd.read_csv("awd.csv",names=['Number','player'])
bwd = pd.read_csv("bwd.csv",names=['Number','player'])
cwd = pd.read_csv("cwd.csv",names=['Number','player'])
dwd = pd.read_csv("dwd.csv",names=['Number','player'])

CS_skill_awd,CS_players_awd,ones_awd,not_in_rankings_awd = get_skills(leaderboard,awd,3,exclude_errors='assume partner')
CS_skill_bwd,CS_players_bwd,ones_bwd,not_in_rankings_bwd = get_skills(leaderboard,bwd,2,exclude_errors='assume partner')
CS_skill_cwd,CS_players_cwd,ones_cwd,not_in_rankings_cwd = get_skills(leaderboard,cwd,1,exclude_errors='assume partner')
CS_skill_dwd,CS_players_dwd,ones_dwd,not_in_rankings_dwd = get_skills(leaderboard,dwd,0,exclude_errors='assume partner')

print()
print("Womens Doubles:")

plt.clf()
plt.scatter(CS_skill_awd,ones_awd,label='AWD')
plt.scatter(CS_skill_bwd,ones_bwd,label='BWD')
plt.scatter(CS_skill_cwd,ones_cwd,label='CWD')
plt.scatter(CS_skill_dwd,ones_dwd,label='DWD')
plt.xlabel('Minimum Likely Skill (95% Confidence)')
plt.yticks([])
plt.legend()
plt.savefig('WD.png')

print(CS_players_awd,CS_skill_awd)
print(' ')
print(CS_players_bwd,CS_skill_bwd)
print(' ')
print(CS_players_cwd,CS_skill_cwd)
print(' ')
print(CS_players_dwd,CS_skill_dwd)
print(' ')
print(set(not_in_rankings_awd)|set(not_in_rankings_bwd)|set(not_in_rankings_cwd)|set(not_in_rankings_dwd))

with open('WD.csv', 'wb') as csvfile:
    spamreader = csv.writer(csvfile, delimiter=',')
    spamreader.writerow(['AWD name','AWD skill'])
    for name,skill in zip(CS_players_awd,CS_skill_awd):
        spamreader.writerow([name,skill])
    spamreader.writerow(['',''])
    spamreader.writerow(['BWD name','BWD skill'])
    for name,skill in zip(CS_players_bwd,CS_skill_bwd):
        spamreader.writerow([name,skill])
    spamreader.writerow(['',''])
    spamreader.writerow(['CWD name','CWD skill'])
    for name,skill in zip(CS_players_cwd,CS_skill_cwd):
        spamreader.writerow([name,skill])  
    spamreader.writerow(['',''])
    spamreader.writerow(['DWD name','DWD skill'])
    for name,skill in zip(CS_players_dwd,CS_skill_dwd):
        spamreader.writerow([name,skill])

abws = pd.read_csv("abws.csv",names=['Number','player'])
cws = pd.read_csv("cws.csv",names=['Number','player'])
dws = pd.read_csv("dws.csv",names=['Number','player'])

CS_skill_abws,CS_players_abws,ones_abws,not_in_rankings_abws = get_skills_singles(leaderboard,abws,2,exclude_errors=True)
CS_skill_cws,CS_players_cws,ones_cws,not_in_rankings_cws = get_skills_singles(leaderboard,cws,1,exclude_errors=True)
CS_skill_dws,CS_players_dws,ones_dws,not_in_rankings_dws = get_skills_singles(leaderboard,dws,0,exclude_errors=True)

print()
print("Womens Singles:")

plt.clf()
plt.scatter(CS_skill_abws,ones_abws,label=r'A/BWS')
plt.scatter(CS_skill_cws,ones_cws,label='CWS')
plt.scatter(CS_skill_dws,ones_dws,label='DWS')
plt.xlabel('Minimum Likely Skill (95% Confidence)')
plt.yticks([])
plt.legend()
plt.savefig('WS.png')

print(CS_players_abws,CS_skill_abws)
print(' ')
print(CS_players_cws,CS_skill_cws)
print(' ')
print(CS_players_dws,CS_skill_dws)
print(' ')
print(set(not_in_rankings_abws)|set(not_in_rankings_cws)|set(not_in_rankings_dws))

with open('WS.csv', 'wb') as csvfile:
    spamreader = csv.writer(csvfile, delimiter=',')
    spamreader.writerow(['ABWS name','ABWS skill'])
    for name,skill in zip(CS_players_abws,CS_skill_abws):
        spamreader.writerow([name,skill])
    spamreader.writerow(['',''])
    spamreader.writerow(['CWS name','CWS skill'])
    for name,skill in zip(CS_players_cws,CS_skill_cws):
        spamreader.writerow([name,skill])  
    spamreader.writerow(['',''])
    spamreader.writerow(['DWS name','DWS skill'])
    for name,skill in zip(CS_players_dws,CS_skill_dws):
        spamreader.writerow([name,skill])
ams = pd.read_csv("ams.csv",names=['Number','player'])
bms = pd.read_csv("bms.csv",names=['Number','player'])
cms = pd.read_csv("cms.csv",names=['Number','player'])
dms = pd.read_csv("dms.csv",names=['Number','player'])

CS_skill_ams,CS_players_ams,ones_ams,not_in_rankings_ams = get_skills_singles(leaderboard,ams,3,exclude_errors=True)
CS_skill_bms,CS_players_bms,ones_bms,not_in_rankings_bms = get_skills_singles(leaderboard,bms,2,exclude_errors=True)
CS_skill_cms,CS_players_cms,ones_cms,not_in_rankings_cms = get_skills_singles(leaderboard,cms,1,exclude_errors=True)
CS_skill_dms,CS_players_dms,ones_dms,not_in_rankings_dms = get_skills_singles(leaderboard,dms,0,exclude_errors=True)

print()
print("Mens Singles:")

plt.clf()
plt.scatter(CS_skill_ams,ones_ams,label='AMS')
plt.scatter(CS_skill_bms,ones_bms,label='BMS')
plt.scatter(CS_skill_cms,ones_cms,label='CMS')
plt.scatter(CS_skill_dms,ones_dms,label='DMS')
plt.xlabel('Minimum Likely Skill (95% Confidence)')
plt.yticks([])
plt.legend()
plt.savefig('MS.png')

with open('MS.csv', 'wb') as csvfile:
    spamreader = csv.writer(csvfile, delimiter=',')
    spamreader.writerow(['AMS name','AMS skill'])
    for name,skill in zip(CS_players_ams,CS_skill_ams):
        spamreader.writerow([name,skill])
    spamreader.writerow(['',''])
    spamreader.writerow(['BMS name','BMS skill'])
    for name,skill in zip(CS_players_bms,CS_skill_bms):
        spamreader.writerow([name,skill])
    spamreader.writerow(['',''])
    spamreader.writerow(['CMS name','CMS skill'])
    for name,skill in zip(CS_players_cms,CS_skill_cms):
        spamreader.writerow([name,skill])  
    spamreader.writerow(['',''])
    spamreader.writerow(['DMS name','DMS skill'])
    for name,skill in zip(CS_players_dms,CS_skill_dms):
        spamreader.writerow([name,skill])

print(CS_players_ams,CS_skill_ams)
print(' ')
print(CS_players_bms,CS_skill_bms)
print(' ')
print(CS_players_cms,CS_skill_cms)
print(' ')
print(CS_players_dms,CS_skill_dms)
print(' ')
print(set(not_in_rankings_ams)|set(not_in_rankings_bms)|set(not_in_rankings_cms)|set(not_in_rankings_dms))
plt.show()
