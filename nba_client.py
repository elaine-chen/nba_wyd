import requests
from datetime import datetime
from teams import TeamConstants

class NbaClient:

    """for clarity of the user, the constructor takes the date
    in the format of yyyy-mm-dd and the dashes are removed afterwards"""
    base_url = "http://data.nba.com/data"
    gen_games_url = "/5s/json/cms/noseason/scoreboard/{}/games.json"
    team_games_url = "/10s/prod/v1/2017/teams/{}/schedule.json"
    boxscore_url = "/10s/prod/v1/{0}/{1}_mini_boxscore.json"
    standings_url = "/10s/prod/v1/{}/standings_conference.json"
    league_teams_url = "/10s/prod/v1/{}/teams.json"

    def __init__(self):
        pass

    @staticmethod
    def format_date(date):
        d = datetime.today()
        d = '{:%Y%m%d}'.format(d)
        if date != "today":
            d = ""
            for letter in date:
                if letter != "-":
                    d += letter
        return d

    def league_info(self, date):
        d = NbaClient.format_date(date)
        formatted_url = (NbaClient.base_url + NbaClient.gen_games_url).format(d)
        r = requests.get(formatted_url)
        r_page = r.json()
        gen_list = r_page[u'sports_content']['games']['game']
        return gen_list

    @staticmethod
    def get_team_code(name):
        if name not in TeamConstants.TEAMS:
            return None
        return TeamConstants.TEAMS[name]['teamId']

    def team_info(self, name):
        try:
            c = NbaClient.get_team_code(name)
            if c != None:
                print NbaClient.base_url + NbaClient.team_games_url
                formatted_url = (NbaClient.base_url + NbaClient.team_games_url).format(name)
                print formatted_url
                r = requests.get(formatted_url)
                page = r.json()
                return page['league']['standard']
        except KeyError:
            print "not a valid team name!"

    def get_mini_boxscore(self, date, gameId):
        url = (NbaClient.base_url + NbaClient.boxscore_url).format(date, gameId)
        r = requests.get(url)
        r_page = r.json()
        game_data = r_page['basicGameData']
        return game_data

    def get_conference_standings(self, date):
        url = (NbaClient.base_url + NbaClient.standings_url).format(date)
        r = requests.get(url)
        r_page = r.json()
        standings_data = r_page['league']['standard']
        return standings_data

    def get_league_teams(self, season_year):
        url = (NbaClient.base_url + NbaClient.league_teams_url).format(season_year)
        r = requests.get(url)
        r_page = r.json()
        teams_data = r_page['league']['standard']
        return teams_data
