import discord
import GameState
from wordpacks import Norwegian, Gaming
from Visualisation import Visualizer


class BotClient(discord.Client):
    def __init__(self, **options):
        super().__init__(**options)
        self.vis = Visualizer()
        self.state = GameState.GameState()

        self.last_state_img = None
        self.state_msg = None

        self.hint_word = ""
        self.hint_count = ""
        self.allowed_guesses = 0

        self.my_channel = None

        self.wordlist = Norwegian
        self.wordlist_name = "Norsk"

    async def on_ready(self):
        print('Logged in as ')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        if message.author.name == 'Scha' and message.content == '!init wordz':
            self.my_channel = message.channel
            return

        if message.channel != self.my_channel:
            return

        if message.content.startswith('!create'):
            wl = message.content[7:]
            if wl == ' norsk':
                self.wordlist = Norwegian
                self.wordlist_name = "Norsk"
            elif wl == ' gaming':
                self.wordlist = Gaming
                self.wordlist_name = "Gaming"
            await self.create_game(message)
        if message.content == '!blimed' or message.content == '!otto':
            await self.add_player(message, False)
        if message.content == '!ikkemaster':
            await self.add_player(message, True)
        if message.content == '!leave':
            await self.remove_player(message)
        if message.content == '!start':
            if self.state.status != GameState.STATUS_MAKING or len(self.state.players) < 4:
                await message.delete()
                return
            self.state.start_game(self.wordlist)
            word_count = len(self.wordlist)
            await message.channel.send('New game starting using '
                                       '"' + self.wordlist_name + '" dictionary. '
                                       '(' + str(word_count) + ' words)')
            await message.channel.send('Type "!hint <word> <count>" to give hint. '
                                       'Type "!guess <Word>" to make a guess. '
                                       'Type !end to end your turn.')

            # Make initial images
            self.vis.draw(self.state, True, "masters.png")
            self.vis.draw(self.state, False, "players.png")
            # PM "masters.png" to masters
            await self.state.teams[0][0].send(file=discord.File('masters.png'))
            await self.state.teams[1][0].send(file=discord.File('masters.png'))
            # Send "players.png" to channel
            await self.post_game_state(message)

        if message.content.startswith("!guess "):
            if self.state.status != GameState.STATUS_RUNNING:
                await message.delete()
                return
            # check that player is allowed to guess
            team = self.state.get_team(message.author)
            if team == 0 or (team == 1 and self.state.inner_state != 2) \
                    or self.state.master_for_team(message.author) == team \
                    or (team == 2 and self.state.inner_state != 4):
                await message.delete()
                return
            guess = message.content[7:]
            # await message.channel.send(message.author.name + ' guessed "' + guess + '"')
            pos = self.state.get_word_position(guess)
            if pos >= 0 and not self.state.words[pos].marked:
                self.allowed_guesses -= 1
                self.state.words[pos].marked = True
                self.vis.draw(self.state, False, "players.png")
                # Check if the guess was the bomb
                if self.state.words[pos].owner == 3:
                    self.state.status = GameState.STATUS_POST_GAME
                    self.state.winner = 1 if self.state.inner_state == 3 else 2
                if self.allowed_guesses == 0 or team != self.state.words[pos].owner:
                    self.state.inner_state = 1 if self.state.inner_state == 4 else 3
                await self.post_game_state(message)

        if message.content.startswith("!hint "):
            if self.state.status != GameState.STATUS_RUNNING:
                return
            team = self.state.master_for_team(message.author)
            if team == 0:
                await message.delete()
                return
            if team == 1 and self.state.inner_state != 1:
                await message.delete()
                return
            if team == 2 and self.state.inner_state != 3:
                await message.delete()
                return

            parts = message.content[6:].split(" ")
            self.set_hint(parts[0], parts[1])
            self.allowed_guesses = int(parts[1]) + 1
            self.state.inner_state += 1
            await self.post_game_state(message)

        if message.content == '!end':
            team = self.state.get_team(message.author)
            if team == 0 or (team == 1 and self.state.inner_state != 2) \
                    or self.state.master_for_team(message.author) == team \
                    or (team == 2 and self.state.inner_state != 4):
                await message.delete()
                return

            if self.state.inner_state == 1 or self.state.inner_state == 3:
                await message.delete()
                return
            elif self.state.inner_state == 2:
                self.state.inner_state = 3
            elif self.state.inner_state == 4:
                self.state.inner_state = 1
            await self.post_game_state(message)

        await message.delete()

    def set_hint(self, word, count):
        self.hint_word = word
        self.hint_count = count

    async def post_game_state(self, message):
        # Delete old state messages
        if self.last_state_img is not None:
            await self.last_state_img.delete()
        if self.state_msg is not None:
            await self.state_msg.delete()

        player_names = ""
        for player in self.state.teams[0]:
            if len(player_names) == 0:
                player_names = "__" + player.name + "__"
            else:
                player_names += " - " + player.name
        team1_state = ":red_circle::red_circle::red_circle: **" \
                      + str(self.state.get_remaining_words(1)) + " words left** - " \
                      + player_names + " :red_circle::red_circle::red_circle:"

        player_names = ""
        for player in self.state.teams[1]:
            if len(player_names) == 0:
                player_names = "__" + player.name + "__"
            else:
                player_names += " - " + player.name
        team2_state = ":blue_circle::blue_circle::blue_circle: **" \
                      + str(self.state.get_remaining_words(2)) + " words left** - " \
                      + player_names + " :blue_circle::blue_circle::blue_circle:"

        current_team = ""
        if self.state.status == GameState.STATUS_POST_GAME:
            winner_name = ":red_circle:" if self.state.winner == 1 else ":blue_circle:"
            current_team = 'Game over. Winner: **Team ' + winner_name + "**"
        elif self.state.inner_state == 1:
            current_team = ":red_circle: Waiting for hint :red_circle:"
        elif self.state.inner_state == 2:
            current_team = ":red_circle: Team Red hint: **" + self.hint_word + "** " + self.hint_count + '. ' + str(self.allowed_guesses) + ' guesses left :red_circle:'
        elif self.state.inner_state == 3:
            current_team = ":blue_circle: Waiting for hint :blue_circle:"
        elif self.state.inner_state == 4:
            current_team = ":blue_circle: Team Blue hint: **" + self.hint_word + "** " + self.hint_count + '. ' + str(self.allowed_guesses) + ' guesses left :blue_circle:'

        self.last_state_img = await message.channel.send(file=discord.File('players.png'))
        self.state_msg = await message.channel.send(team1_state + "\n" + team2_state + "\n" + current_team)

    async def add_player(self, message, nomaster):
        if self.state.status != GameState.STATUS_MAKING:
            return
        if self.state.has_player(message.author):
            return
        self.state.add_player(message.author)
        if nomaster:
            self.state.no_master(message.author)
        count = str(len(self.state.players))
        await message.channel.send(message.author.name + ' has joined. Currently ' + count + ' players in game.')

    async def remove_player(self, message):
        if self.state.status != GameState.STATUS_MAKING:
            return
        if not self.state.has_player(message.author):
            return
        self.state.remove_player(message.author)
        count = str(len(self.state.players))
        await message.channel.send(message.author.name + ' has left. Currently ' + count + ' players in game.')

    async def create_game(self, message):
        self.state.create_game()
        await message.channel.send('New game started. Type !blimed to join. Type !leave to leave.')
        await message.channel.send('When a minimum of 4 players have joined, you can type !start to start the game.')
        await message.channel.send('Type !abort to cancel.')

    async def cancel_game(self, message):
        self.state.destroy_game()
        message.channel.send('Game cancelled. Type !create to start a new game')
