class EmojiRacer:
    def __init__(self, id: int, name: str, quote: str, move_chance: float, min_move: int, max_move: int, all_increase_move_chance: int, all_increase_max_move: int, all_decrease_move_chance: int, all_decrease_max_move: int, wins: int, total_races: int ):
        self.id = id
        self.name = name
        self.quote = quote
        self.move_chance = move_chance
        self.min_move = min_move
        self.max_move = max_move
        self.all_increase_move_chance = all_increase_move_chance
        self.all_increase_max_move = all_increase_max_move
        self.all_decrease_move_chance = all_decrease_move_chance
        self.all_decrease_max_move = all_decrease_max_move
        self.wins = wins
        self.total_races = total_races
        self.owner = None