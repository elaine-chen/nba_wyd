from nba_client import NbaClient
from game import Game
from teams import TeamConstants
from datetime import datetime, timedelta
from pytz import timezone

class ScheduleMaker:

    def __init__(self):
        self.client = NbaClient()

    def get_game_info(self, date):
        schedule = []
        gen_list = self.client.league_info(date)
        for g in gen_list:
            v, h = g['visitor'], g['home']
            v_team, v_score = v['nickname'], v['score']
            h_team, h_score = h['nickname'],h['score']
            start_time = g['time']
            start_time_E = start_time[:2]+':'+start_time[2:] + " ET"
            start_time_W = str(int(start_time[:2])-3)+ ':'+start_time[2:]+"PT /"
            start_time_combined = start_time_W + start_time_E
            game_status = g['period_time']
            score = v['score']+ ":"+ h['score']
            game = Game(v_team, h_team, game_status, start_time_combined, score)
            game.set_period_status()
            schedule.append(game)
        return schedule

    @staticmethod
    def team_helper(teamID):
        try:
            for team in TeamConstants.TEAMS:
                if TeamConstants.TEAMS[team]["teamId"] == int(teamID):
                    return TeamConstants.TEAMS[team]['simpleName']
        except KeyError, e:
            print "Invalid team code!"

    @staticmethod
    def time_cmp(g_time, utc):
        return datetime(utc.year, utc.month, utc.day) - datetime(g_time.year,
        g_time.month, g_time.day)

    @staticmethod
    def utc_to_us(game_in_utc):
        eastern_tz = timezone("US/Eastern")
        western_tz = timezone("US/Pacific")
        utc = timezone("UTC")
        g_aware = game_in_utc.replace(tzinfo=utc)
        gt_east = g_aware.astimezone(eastern_tz)
        gt_west = g_aware.astimezone(western_tz)
        return (gt_east, gt_west)


# make a separate list/schedule for past games?
    # @staticmethod
    # def format_date(datetime):
    def get_team_schedule(self, team):
        game_history = []
        future_games = []
        team_schedule = self.client.team_info(team)
        utc = datetime.utcnow()
        myTeamId = TeamConstants.TEAMS[team]['teamId']
        for g in team_schedule:
            is_preseason = g['seasonStageId'] == 1
            if is_preseason:
                continue
            g_time = datetime.strptime(g['startTimeUTC'], "%Y-%m-%dT%H:%M:%S.%fZ")
            time_comp = ScheduleMaker.time_cmp(g_time, utc)
            if g['statusNum'] == 3:
                    game_status = {'period_status': 'Final', 'game_clock': ""}
                    score = str(g['vTeam']['score']) +":"+ str(g['hTeam']['score'])
                    start_time = ""
            elif time_comp < timedelta(): #if the game date is after today
                score = "tba"
                unformatted_start_time = ScheduleMaker.utc_to_us(g_time)
                start_time= unformatted_start_time[1].strftime("%a %m/%d %I:%M%p")
                game_status = {'period_status': start_time, 'game_clock': ""}
            else:
                if time_comp == timedelta(): #if game date == today's date
                    game_info = self.client.get_mini_boxscore(g['startDateEastern'],
                    g['gameId'])
                    # if game is on-going or (isToday but has yet to start)
                    game_status = game_info['period']
                    game_status['game_clock'] = game_info['clock']
                    game_status['isGameActivated'] = game_info['isGameActivated']
                    score = game_info['vTeam']['score'] + ":" + game_info['hTeam']['score']
                    start_time = "Today " + game_info['startTimeEastern']
            if g['isHomeTeam'] == True:
                v_team = ScheduleMaker.team_helper(g['vTeam']['teamId'])
                h_team = team.capitalize()
            else:
                h_team = ScheduleMaker.team_helper(g['hTeam']['teamId'])
                v_team = team.capitalize()
            game = Game(v_team, h_team, game_status, start_time, score)
            game.set_period_status()
            if len(start_time) == 0:
                game_history.append(game)
            else:
                future_games.append(game)
        abridged_schedule = game_history[-5:] + future_games[:10]
        return abridged_schedule

    def team_standing(self, team, date):
        conference_standings = self.client.get_conference_standings(date)
        season_year = conference_standings['seasonYear']
        league_teams = self.client.get_league_teams(season_year)
        mini_standing = {}
        for t in league_teams:
            if t['nickname'].lower() == team.lower():
                teamId = t['teamId']
                conf_name = t['confName']
                team_full_name = t['fullName']
        conf = conference_standings['conference'][conf_name.lower()]
        for t in conf:
            if t['teamId'] == teamId:
                    mini_standing['full_name'] = team_full_name
                    mini_standing['conf_standing'] = "#" + t['confRank'] + " in " + conf_name.capitalize()+"ern Conference"
                    mini_standing["win_loss"] = t['win'] + "-" + t["loss"]
        return mini_standing
