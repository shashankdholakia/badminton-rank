# badminton-rank
Ranking code for badminton tournaments using Microsoft's TrueSkill algorithm. Uses html scraping to aggregate match data over multiple tournaments from www.tournamentsoftware.com. Represents each players' skill as a Gaussian distribution with a mean and standard deviation. TrueSkill uses Bayesian inference to "update" each player's skill with each match played, which we implement to inherently account for propagation of uncertainties and recency. Also has ability to generate win probabilities for singles or doubles matches. Because tournamentsoftware is used by regional tournaments and the Badminton World Federation, this approach will work for both amateur and professional players and rankings.

We make certain simplifying assumptions in order to rank singles, doubles and mixed games. Firstly, we assume that the skill of a doubles pair is the sum of the skills of the individual partners. Presently, we also assume that players have approximately equal skill in all formats of the game.


## Getting Started

### Dependencies

Requires Python 3.0 or greater

Uses the python packages:
* TrueSkill (https://trueskill.org/)
* BeautifulSoup (https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
* numpy
* requests
* pandas
* scipy

### Installation

First make sure Python and all dependencies are installed. We recommend installing Anaconda Distribution. Then install trueskill from the command line by typing `pip install trueskill`.

Now get this repository by typing 
```git clone https://github.com/shashankdholakia/badminton-rank.git```. 
Navigate inside the code directory by typing `cd badminton-rank`. 

### Usage

#### Basic Usage

To run on the default list of tournaments in tournaments.txt, just run `python ranking.py`. If you wish to add a tournament to the list of default tournaments, paste in the links to the tournaments so that all tournaments are *in chronological order*. If you wish to run on a different list of tournaments, clear the tournaments.txt file and paste in the links to the main pages of all the tournaments you wish to run on, in chronological order. 

#### Aliases
Often, there is the problem of players creating multiple accounts and using different names in different tournaments. This duplication may affect the final rankings, especially inflating the skill uncertainty of these players. In order to remedy this, the code will automatically consolidate accounts with the same name (temporary and not ideal in case two players have the same first and last name!). In order to account for player aliases, first clear the contents of the alias.csv file (the code will rewrite this during runtime), and add all names used by a single player in one row, separated by a comma. If available, also include a link to each players' profile on tournamentsoftware.com minus the www.tournamentsoftware.com. Write the name and account link you want in the final standings in the first and second column respectively
For instance:

Jane Doe, /player/C36A90FE-DFA8-414B-A8B6-F2BCF6B9B8BD/31423424, Jane FemaleDeer, /player/C36A90FE-DFA8-414B-A8B6-F2BCF6B9B8BD/23234909

#### Win probabilities

Coming soon!

## Authors

* Shashank Dholakia
* Shishir Dholakia

See also the list of [contributors](https://github.com/shashankdholakia/badminton-rank/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

