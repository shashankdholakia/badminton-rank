from trueskill import Rating, rate_1vs1
from collections import OrderedDict
import pandas
import csv
import trueskill
import math
from scipy.special import ndtri

Ratings = {}
env = trueskill.TrueSkill(draw_probability=0.0)
env.make_as_global() 



def readCSV(filename):
    games=[]
    
    with open(filename) as csvfile:
        CSV = csv.reader(csvfile, delimiter=',')
        for row in CSV:
            if len(row)>=6:
                games.append([row[0],row[1],row[2],row[3],row[4],row[5]])
            else: 
                games.append([row[0],row[1],row[2],row[3]])
    return games


def addPlayer(name, rating=Rating()):
    Ratings[name]=rating
   
#enter winner first, loser second
def playSingles(name1,name2):
    
    Ratings[name1],Ratings[name2] = env.rate_1vs1(Ratings[name1],Ratings[name2])

#enter winning pair first, losing pair second
def playDoubles(name1,name2,name3,name4):
    t1 = (Ratings[name1],Ratings[name2])
    t2 = (Ratings[name3],Ratings[name4])
    newt1, newt2 = env.rate([t1,t2])
    Ratings[name1],Ratings[name2] = newt1
    Ratings[name3],Ratings[name4] = newt2
    
#enter winning pair first, losing pair second
#same as playDoubles() but takes score into account
def playDoubles_score(name1,name2,name3,name4,winner_score,loser_score):
    t1 = (Ratings[name1],Ratings[name2])
    t2 = (Ratings[name3],Ratings[name4])
    newt1, newt2 = env.rate([t1,t2])
    name1_average = newt1[0].mu
    name1_sigma = newt1[0].sigma
    name2_average = newt1[1].mu
    name2_sigma = newt1[1].sigma
    name3_average = newt2[0].mu
    name3_sigma = newt2[0].sigma
    name4_average = newt2[1].mu
    name4_sigma = newt2[1].sigma
    Ratings[name1] = Rating()
    Ratings[name2] = Rating()
    Ratings[name3] = Rating()
    Ratings[name4] = Rating()
    
    Ratings[name1],Ratings[name2] = newt1
    Ratings[name3],Ratings[name4] = newt2
    
def resetValues():
    for key, value in Ratings.iteritems():
        Ratings[key]=Rating()
        
def deleteValues():
    Ratings = {}

def printLeaderboard(toCSV=False,path=''):
    list_to_be_sorted = []
    for i in Ratings.items():
        list_to_be_sorted.append((i[0],[i[1].mu,i[1].sigma*2]))
    Ratings_sorted_by_value = OrderedDict(sorted(list_to_be_sorted, key=lambda x: x[1][0],reverse=True))
    leaderboard = pandas.DataFrame.from_items(Ratings_sorted_by_value.items(),["Average","95% CI"], orient='index')
    print(leaderboard)
    if toCSV:
        leaderboard.to_csv('/Users/shashank/Documents/Badminton/ranking.csv')
    
def printLeaderboard_CSE(toCSV=False,path=''):
    list_to_be_sorted = []
    for i in Ratings.items():
        list_to_be_sorted.append((i[0],[i[1].mu-i[1].sigma*3]))
    Ratings_sorted_by_value = OrderedDict(sorted(list_to_be_sorted, key=lambda x: x[1][0],reverse=True))
    leaderboard = pandas.DataFrame.from_items(Ratings_sorted_by_value.items(),["Conservative Skill Estimate"], orient='index')
    print(leaderboard)
    if toCSV:
        leaderboard.to_csv('/Users/shashank/Documents/Badminton/ranking.csv')
    
def Pwin_singles(name1, name2):
    rA = Ratings[name1]
    rB = Ratings[name2]
    deltaMu = rA.mu - rB.mu
    rsss = math.sqrt(rA.sigma**2 + rB.sigma**2)
    return trueskill.TrueSkill().cdf(deltaMu/rsss)


def Pwin_singles_lowsigma(name1, name2):
    """
    Useful for when both players have a low uncertainty (sigma < 2)
    and in professional matches, where absolute differences in skill are less
    """
    rA = Ratings[name1]
    rB = Ratings[name2]
    deltaMu = rA.mu - rB.mu
    rsss = math.sqrt(rA.sigma**2 + rB.sigma**2)
    trueskill_winprob = trueskill.TrueSkill().cdf(deltaMu/rsss)
    if ((ndtri(trueskill_winprob)/(np.exp(-(rsss/2.0)+3.8)+1) + 0.5) > 0.0 and (ndtri(trueskill_winprob)/(np.exp(-(rsss/2.0)+3.8)+1) + 0.5) < 1):
        return ndtri(trueskill_winprob)/(np.exp(-(rsss/2.0)+3.8)+1) + 0.5 #scaled with best fit probit function (created using historical bwf data)
    elif ((ndtri(trueskill_winprob)/(np.exp(-(rsss/2.0)+3.8)+1) + 0.5) < 0.0):
        return 0.0
    elif ((ndtri(trueskill_winprob)/(np.exp(-(rsss/2.0)+3.8)+1) + 0.5) > 1.0):
        return 1.0

def Pwin_doubles(name1,name2,name3,name4):
    rAlist=[Ratings[name1],Ratings[name2]]
    rBlist=[Ratings[name3],Ratings[name4]]
    deltaMu = sum( [x.mu for x in rAlist])  - sum( [x.mu for x in  rBlist])
    rsss = math.sqrt(sum( [x.sigma**2 for x in  rAlist]) + sum( [x.sigma**2 for x in rBlist]) )
    return trueskill.TrueSkill().cdf(deltaMu/rsss)

def num_there(s):
    return any(i.isdigit() for i in s)

def predict_score(name1,name2,name3,name4):
    """
    Useful for when both players have a low uncertainty (sigma < 2)
    and in professional matches, where absolute differences in skill are less
    """
    
    winprob = Pwin_doubles(name1,name2,name3,name4)
    percent_score = winprob*0.273698660319+0.363123884308
    if percent_score < .5:
        team2 = 21
        team1 = round((21*percent_score)/(1-percent_score))
    elif percent_score >.5:
        team1 = 21
        
        team2 = round((21*(1-percent_score))/(percent_score))
    return team1,team2

def printPwin_singles(name1,name2):
    print(name1+": "+str(Pwin_singles(name1,name2)*100)+"%")
    print(name2+": "+str(Pwin_singles(name2,name1)*100)+"%")
    
def printPwin_doubles(name1,name2,name3,name4):
    print(name1+", "+name2+": "+str(Pwin_doubles(name1,name2,name3,name4)))
    print(name3+", "+name4+": "+str(Pwin_doubles(name3,name4,name1,name2)))
    
def main():
    resetValues()
    games = readCSV("/Users/shashank/Documents/Badminton/badminton.csv")
    for i in games:
        if (i[0] not in Ratings):
            addPlayer(i[0])
        if (i[1] not in Ratings):
            addPlayer(i[1])
        if (i[2] not in Ratings and not num_there(i[2])):
            addPlayer(i[2])
        if (i[3] not in Ratings and not num_there(i[3])):
            addPlayer(i[3])
        if not num_there(i[2]):
            printPwin_doubles(i[0],i[1],i[2],i[3])
            print predict_score(i[0],i[1],i[2],i[3])
            print("_____")
            playDoubles(i[0],i[1],i[2],i[3])
        else:
            playSingles(i[0],i[1])
    printLeaderboard(toCSV=True,path="/Users/shashank/Documents/Badminton/ranking.csv")

#if running this code itself, find and print the rankings
if __name__ == "__main__":
    main()
