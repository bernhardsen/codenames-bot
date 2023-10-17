
import GameState

# Most of the time, these things should return something to be passed on to the text service


class GameService:
    def __init__(self, channel_service, chat_service):
        self.channel_service = channel_service
        self.chat_service = chat_service

    def player_joined(self, message):
        state = self.channel_service.get_state(message.channel)
        player = message.author
        if state.status == GameState.STATUS_MAKING and not state.players.__contains__(player):
            state.add_player(player)
            self.chat_service.player_joined(message, player, state.player_count())

    def player_left(self, message):
        state = self.channel_service.get_state(message.channel)
        player = message.author
        if state.status == GameState.STATUS_MAKING and state.players.__contains__(player):
            state.remove_player(player)
            self.chat_service.player_left(message, player, state.player_count())

    def give_hint(self, message):
        state = self.channel_service.get_state(message.channel)
        if state.waiting_for_hint() and state.current_team() == state.get_team(message.author) and state.is_master(message.author):
            parts = self.chat_service.get_argument(message).split(" ")
            if len(parts) == 2:
                word = parts[0]
                hint_count = int(parts[1])
                state.give_hint(word, hint_count)
                self.chat_service.output_state(state)

    def guess(self, message):
        state = self.channel_service.get_state(message.channel)
        guesser = message.author
        if state.current_team() == state.get_team(guesser) and state.is_guessing() and not state.is_master(guesser):

            state.make_guess()
