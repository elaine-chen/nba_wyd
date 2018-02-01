class Game:

    """object representing the details of each game"""
    """if on-going game: status = cur_quarter & remaining time (status), if future
    game, status = starting time (s_time), if past game, status = 'FINAL'
    if game date = today && """

    def __init__(self, away, home, game_status, start_time, score):
        self.away = away
        self.home = home
        self.game_status = game_status
        self.score = score
        self.start_time = start_time
        self.period_status = ()

    """get_score needs to depend on whether the game has started, not the score"""

    @staticmethod
    def modify_score(status, score):
        if status[0] != "Final" and status[0] != "Halftime" and len(status[1]) == 0:
            return ""
        else:
            return score

    def get_score(self):
        s = Game.modify_score(self.period_status, self.score)
        return s

    def get_period_status(self):
        return self.period_status

    def get_home(self):
        return self.home

    def get_away(self):
        return self.away

    def game_on_schedule(self):
        self.period_status = (self.start_time, "")

    @staticmethod
    def to_string_period(p_num):
        ordinal_qtr = ["st", "nd", "rd", "th"]
        if p_num in [str(x) for x in range(5,11)]:
            return "OT" + str(p_num - 4)
        else:
            q_ordinal = str(p_num) + ordinal_qtr[p_num-1]
            return q_ordinal

    def set_period_status(self):
        p_status = self.game_status.get('period_status')
        if self.game_status.get('isGameActivated') == False and p_status == None:
            self.period_status = (self.start_time, "")
            return
        game_clock = self.game_status['game_clock']
        # deals with ongoing games that come from mini_boxscore
        if self.game_status.get('isGameActivated') == True:
            if self.game_status['isHalftime'] == True:
                self.period_status = ("Halftime", "")
                return
            p = Game.to_string_period(self.game_status['current'])
            if self.game_status['isEndOfPeriod'] == True:
                self.period_status = ("End of" + p + " Qtr", "")
                return
            else:
                self.period_status = (p + " Qtr", game_clock)
                return
        if len(game_clock) > 0 and game_clock != "0.0":
            self.period_status = (p_status, game_clock)
            return
        p_val = self.game_status.get('period_value')
        if p_val in [str(x) for x in range(5,11)]:
            self.period_status = (p_status, "OT"+ str(int(p_val)-4))
        else:
            self.period_status = (p_status, "")
        return True
