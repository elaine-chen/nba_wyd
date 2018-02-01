#!/usr/bin/env python
import sys
import click
import requests
from nba_client import NbaClient
from schedule_maker import ScheduleMaker
from colorama import init, Fore, Back, Style
from blessings import Terminal
from terminaltables import SingleTable
from datetime import datetime

init()
terminal = Terminal()
@click.command()
@click.option('-d', '--date', default = 'today')
@click.option('-t', '--team', default = None)
def nba_schedule(date, team):
    table_data = []
    maker = ScheduleMaker()
    if team == None:
        schedule = maker.get_game_info(date)
        to_table = format_league_schedule(date, schedule)
        title = league_schedule_header(date)
        table = SingleTable(to_table, title= title)
    else:
        schedule = maker.get_team_schedule(team)
        d = datetime.today()
        today = '{:%Y%m%d}'.format(d)
        conf_standing = maker.team_standing(team, today)
        title = (team_schedule_header(conf_standing))
        table_data = format_team_schedule(team, schedule)
        table_data.insert(0, title)
        table = SingleTable(table_data)
        # table.inner_heading_row_border = False
    print "\n"
    print table.table

def league_schedule_header(date):
    if date == "today":
        today = datetime.today()
        title = " Games for " + today.strftime("%A %m/%d %Y") + " <<<"
    else:
        date_requested = datetime.strptime(date, "%Y-%m-%d")
        title = " Games for " + date_requested.strftime("%A %m/%d %Y") + " <<<"
    return title

def team_schedule_header(standing_dict):
    title = []
    title.append(standing_dict['full_name'] + "\n"+ standing_dict['conf_standing'] + "\n")
    # title.append(standing_dict['conf_standing'])
    title.append(standing_dict['win_loss'])
    return title

def format_league_schedule(date, schedule):
    to_table = []
    headers = [Fore.RED+"Away", Fore.BLUE+"Home", Fore.RED+"Status",
    Fore.BLUE+"Score" + Fore.RESET]
    to_table.append(headers)
    for game in schedule:
        row = []
        row.append(game.get_away())
        row.append(game.get_home())
        row.append(game.get_period_status()[0] + " "+ (Fore.GREEN +
        game.get_period_status()[1] +
        Fore.RESET))
        row.append(game.score)
        to_table.append(row)
    return to_table

def format_team_schedule(team, schedule):
    to_table = []
    team = team.capitalize()
    for game in schedule:
        row = []
        is_hometeam = team == game.get_home()
        splitted_score = game.get_score().split(":")
        score_string = ""
        if is_hometeam:
            if len(splitted_score) > 1:
               score_string = str(splitted_score[0]) + ":" + (Fore.BLUE + str(splitted_score[1]) + Fore.RESET)
            opp = "vs. " + game.get_away()
        else:
            if len(splitted_score) > 1:
                score_string = (Fore.BLUE + str(splitted_score[0]) + Fore.RESET) + ":" + str(splitted_score[1])
            opp = "@ " + game.get_home()
        if game.get_period_status()[0] == "Final":
            score = [int(x) for x in splitted_score]
            winner_index = score.index(max(score))
            winner = [game.get_away(), game.get_home()][winner_index]
            if winner == team:
                result = Fore.GREEN + "W" + Fore.RESET
            else:
                result = Fore.RED + "L" + Fore.RESET
        else:
            result = ""
        row.append(opp)
        row.append(game.get_period_status()[0] + " "+ (Fore.GREEN + game.get_period_status()[1] +
        Fore.RESET))
        row.append(result)
        row.append(score_string)
        to_table.append(row)
    return to_table

if __name__ == '__main__':
    nba_schedule()

"""takes in request for the type of schedule and
retrieves games that match the criteria through schedule_maker.py and returns
a formatted schedule"""
