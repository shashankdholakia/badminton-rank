import os
from trueskill import Rating, rate_1vs1
from collections import OrderedDict
import pandas
import csv
import trueskill
import math
from scipy.special import ndtri
from scraper import scraper


class Ranking:
    
    def __init__(self, Ratings={}):
        self.ratings = Ratings
        env = trueskill.TrueSkill(draw_probability=0.0)
        env.make_as_global()
    
    def __str__(self):
        """
        the default string representation for the ranking class is a leaderboard
        with [Player, Average Skill, Std. Dev Skill]
        """
        list_to_be_sorted = []
        for i in self.ratings.items():
            list_to_be_sorted.append((i[0],[i[1].mu,i[1].sigma*2]))
        Ratings_sorted_by_value = OrderedDict(sorted(list_to_be_sorted, key=lambda x: x[1][0],reverse=True))
        return pandas.DataFrame.from_items(Ratings_sorted_by_value.items(),["Average","95% CI"], orient='index')

    #update to run and read in data from scraper
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
    
    #add new player
    def addPlayer(self, name, rating=Rating()):
        self.ratings[name]=rating
       
    #enter winner first, loser second
    def playSingles(self,name1,name2):
        
        self.ratings[name1], self.ratings[name2] = env.rate_1vs1(self.ratings[name1],self.ratings[name2])
    
    #enter winning pair first, losing pair second
    def playDoubles(self,name1,name2,name3,name4):
        """
        'Plays' a game of singles with no score given
        """
        t1 = (self.ratings[name1],self.ratings[name2])
        t2 = (self.ratings[name3],self.ratings[name4])
        newt1, newt2 = env.rate([t1,t2])
        self.ratings[name1],self.ratings[name2] = newt1
        self.ratings[name3],self.ratings[name4] = newt2
        
    #enter winning pair first, losing pair second
    #same as playDoubles() but takes score into account
    def playDoubles_score(self,name1,name2,name3,name4,winner_score,loser_score):
        t1 = (self.ratings[name1],self.ratings[name2])
        t2 = (self.ratings[name3],self.ratings[name4])
        newt1, newt2 = env.rate([t1,t2])
        name1_average = newt1[0].mu
        name1_sigma = newt1[0].sigma
        name2_average = newt1[1].mu
        name2_sigma = newt1[1].sigma
        name3_average = newt2[0].mu
        name3_sigma = newt2[0].sigma
        name4_average = newt2[1].mu
        name4_sigma = newt2[1].sigma
        self.ratings[name1] = Rating()
        self.ratings[name2] = Rating()
        self.ratings[name3] = Rating()
        self.ratings[name4] = Rating()
        
        self.ratings[name1], self.ratings[name2] = newt1
        self.ratings[name3], self,ratings[name4] = newt2
        
    def resetValues(self):
        """
        Resets all ratings to average, or default, for an unknown player
        but preserves the players themselves
        """
        for key, value in self.ratings.items():
            self.ratings[key]=Rating()
            
    def deleteValues(self):
        """
        Deletes all players from the rankings
        """
        self.ratings = {}
    
    def printLeaderboard(self, toCSV=False, path=''):
        """
        Prints leaderboard to console, or if toCSV is True, creates a CSV
        with leaderboard and saves it to the path provided
        Path must include filename, for instance "\shashank\Documents\leaderboard.csv"
        
        Leaderboard is a table containing [Player, Average skill, Std. Dev. skill]
        in every row
        """
        list_to_be_sorted = []
        for i in self.ratings.items():
            list_to_be_sorted.append((i[0],[i[1].mu,i[1].sigma*2]))
        Ratings_sorted_by_value = OrderedDict(sorted(list_to_be_sorted, key=lambda x: x[1][0],reverse=True))
        leaderboard = pandas.DataFrame.from_items(Ratings_sorted_by_value.items(),["Average","95% CI"], orient='index')
        print(leaderboard)
        #need to make more graceful exit if path provided is not valid
        if toCSV:
            if path is '':
                raise ValueError('if toCSV is true, then a path must be specified!')
            else:
                leaderboard.to_csv(path)
        
    def printLeaderboard_CSE(self,toCSV=False,path=''):
        """
        Prints the leaderboard same as printLeaderboard, except instead of an average skill
        it instead prints the Conservative Skill Estimate, defined as
        Average skill - 3*(sigma skill). This is a useful metric, as it conveys in a single
        number what TrueSkill presents as an average skill and a std. dev.
        
        Note: in this case, conservative is taken to mean the *minimum* skill that a player is likely
        to have. It may in many cases be more instructive to instead know the *maximum* skill a player
        is likely to have.
        """
        list_to_be_sorted = []
        for i in self.ratings.items():
            list_to_be_sorted.append((i[0],[i[1].mu-i[1].sigma*3]))
        Ratings_sorted_by_value = OrderedDict(sorted(list_to_be_sorted, key=lambda x: x[1][0],reverse=True))
        leaderboard = pandas.DataFrame.from_items(Ratings_sorted_by_value.items(),["Conservative Skill Estimate"], orient='index')
        print(leaderboard)
        if toCSV:
            if path is '':
                raise ValueError('if toCSV is true, then a path must be specified!')
            else:
                leaderboard.to_csv('/Users/shashank/Documents/Badminton/ranking.csv')
    
    def Pwin_singles(self,name1, name2):
        """
        Win probability in singles
        """
        rA = self.ratings[name1]
        rB = self.ratings[name2]
        deltaMu = rA.mu - rB.mu
        rsss = math.sqrt(rA.sigma**2 + rB.sigma**2)
        return trueskill.TrueSkill().cdf(deltaMu/rsss)
    
    
    def Pwin_singles_lowsigma(self,name1, name2):
        """
        Useful for when both players have a low uncertainty (sigma < 2)
        and in professional matches, where absolute differences in skill are less
        
        Uses an original empirical formula calibrated on all professional games from BWF website
        before and during 2017.
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
    
    def Pwin_doubles(self,name1,name2,name3,name4):
        """
        Win probability for a doubles pair
        """
        rAlist=[self.ratings[name1],self.ratings[name2]]
        rBlist=[self.ratings[name3],self.ratings[name4]]
        deltaMu = sum( [x.mu for x in rAlist])  - sum( [x.mu for x in  rBlist])
        rsss = math.sqrt(sum( [x.sigma**2 for x in  rAlist]) + sum( [x.sigma**2 for x in rBlist]) )
        return trueskill.TrueSkill().cdf(deltaMu/rsss)

    
    def predict_score(self,name1,name2,name3,name4):
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

    
def num_there(s):
    """helper function for main()"""
    return any(i.isdigit() for i in s)

def main():
    r = Ranking()
    r.resetValues()
    
    tournamentlinks = [line.rstrip('\n') for line in open('tournaments.txt')]
    for link in tournamentlinks[0:1]:
        print(link)
        tournamentdata = scraper(link)
        playerlinks = tournamentdata["Player links"]
        singleswinners = tournamentdata["Singles Winners"]
        singleslosers = tournamentdata["Singles Losers"]
        doubleswinners = tournamentdata["Doubles Winners"]
        doubleslosers = tournamentdata["Doubles Losers"]
        
        
#        for i in games:
#            if (i[0] not in r.ratings):
#                r.addPlayer(i[0])
#            if (i[1] not in r.ratings):
#                r.addPlayer(i[1])
#            if (i[2] not in r.ratings and not num_there(i[2])):
#                r.addPlayer(i[2])
#            if (i[3] not in r.ratings and not num_there(i[3])):
#                r.addPlayer(i[3])
#            if not num_there(i[2]):
#                print(r.Pwin_doubles(i[0],i[1],i[2],i[3]))
#                print(r.predict_score(i[0],i[1],i[2],i[3]))
#                print("_____")
#                r.playDoubles(i[0],i[1],i[2],i[3])
#            else:
#                r.playSingles(i[0],i[1])

#if running this code itself, find and print the rankings
if __name__ == "__main__":
    main()
    
    
