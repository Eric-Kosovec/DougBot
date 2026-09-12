from dataclasses import dataclass


@dataclass(frozen=True)
class EmojiRacer:

    emoji: str
    quote: str
    move_chance: float
    min_move: float
    max_move: float
    field_chance_effect: float = 0.0
    field_speed_effect: float = 0.0
    protection: bool = False


EMOJI_RACERS: tuple[EmojiRacer, ...] = (
    EmojiRacer("<:protection:401942229943320586>", "...",
               move_chance=10, min_move=1, max_move=1, protection=True),
    EmojiRacer("<:uhnS:819393028795531275>", "AAAAAAAHHHHHHHHHHHHHHHHHHHH",
               move_chance=5, min_move=0, max_move=5, field_speed_effect=-3),
    EmojiRacer("<:frog:309612203944706048>", "A frog in the hand is worth a win",
               move_chance=0.1, min_move=20, max_move=20),
    EmojiRacer("<:mushWalk:255486412403638274>", "...",
               move_chance=10, min_move=1, max_move=1),
    EmojiRacer("<:trumpWall:337019075773595658>", "AND WE MADE THEM PAY FOR IT!!!",
               move_chance=6, min_move=0, max_move=3, field_chance_effect=-3),
    EmojiRacer("<:tim:884220118056448011>", "Was that a Tim Hortons",
               move_chance=10, min_move=0, max_move=2,
               field_chance_effect=3, field_speed_effect=2),
    EmojiRacer("<:lookBack:874197310245068881>", "Huh, what was that.",
               move_chance=3, min_move=0, max_move=5),
    EmojiRacer("<:lurking:718952796942106675>", "Only thing down here is rice krispies",
               move_chance=5, min_move=0, max_move=7),
    EmojiRacer("<:gaston:338610840699666443>", "I'll have another 3 dozen eggs to celebrate",
               move_chance=9, min_move=0, max_move=1,
               field_chance_effect=-2, field_speed_effect=5),
    EmojiRacer("<:turt:338606580801208330>", "...",
               move_chance=7, min_move=0, max_move=3, field_speed_effect=-2),
)