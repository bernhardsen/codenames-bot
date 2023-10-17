import random

STATUS_NOT_STARTED = 1
STATUS_MAKING = 2
STATUS_RUNNING = 3
STATUS_POST_GAME = 4

WAITING_FOR_TEAM1_HINT = 1
TEAM1_GUESSING = 2
WAITING_FOR_TEAM2_HINT = 3
TEAM2_GUESSING = 4


class GameState:
    def __init__(self):
        self.status = STATUS_NOT_STARTED
        self.players = []
        self.nomaster = []
        self.player_names = []
        self.teams = [[], []]
        self.words = []
        self.inner_state = 1
        self.winner = 0

    def create_game(self):
        self.players = []
        self.status = STATUS_MAKING

    def add_player(self, player):
        self.players.append(player)

    def no_master(self, player):
        self.nomaster.append(player)

    def has_player(self, player):
        return player in self.players

    def remove_player(self, player):
        self.players.remove(player)

    def master_for_team(self, player):
        if self.teams[0][0] == player:
            return 1
        elif self.teams[1][0] == player:
            return 2
        return 0

    def get_team(self, player):
        if self.teams[0].__contains__(player):
            return 1
        if self.teams[1].__contains__(player):
            return 2
        return 0

    def start_game(self, dictionary):
        self.winner = 0
        self.create_teams()
        self.status = STATUS_RUNNING
        self.words = []
        random.shuffle(dictionary)
        for i in range(25):
            self.words.append(Word(dictionary[i]))

        for i in range(9):
            self.words[i].owner = 1

        for i in range(8):
            self.words[9 + i].owner = 2

        self.words[17].owner = 3
        random.shuffle(self.words)

    def get_word(self, position):
        if position < 0 or position > 24:
            return ""
        return self.words.__getitem__(position)

    def get_word_position(self, word):
        for position in range(25):
            if self.words[position].word.lower() == word.lower():
                return position

        return -1

    def get_remaining_words(self, team):
        count = 0
        for word in self.words:
            if word.owner == team and not word.marked:
                count += 1

        if count == 0:
            self.status = STATUS_POST_GAME
            self.winner = team
        return count

    def create_teams(self):
        self.teams = [[], []]
        random.shuffle(self.players)
        team = 0
        for player in self.players:
            self.teams[team].append(player)
            team = 1 - team
        if len(self.players) - len(self.nomaster) >= 2 and (self.teams[0][0] in self.nomaster or self.teams[1][0] in self.nomaster):
            self.create_teams()

    def create_game_board(self):
        pass


class Word:
    def __init__(self, word):
        self.word = word
        self.owner = 0
        self.marked = False
