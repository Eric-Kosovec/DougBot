ALIASES = ["harvey", "oceanman", "harveyman"]

async def run(alias, message, args, client):
    try:
        if alias == "harveyman":
            resp = ALIASES_TO_RESPONSE["harvey"] + "\n" + ALIASES_TO_RESPONSE["oceanman"] + "\n" + ALIASES_TO_RESPONSE["harvey"]
        else:
            resp = ALIASES_TO_RESPONSE[alias]

        await client.send_message(message.channel, resp)
    except KeyError as e:
        pass

ALIASES_TO_RESPONSE = {
    "harvey": ":ocean: :ocean: :house_abandoned: :ocean::house_abandoned::ocean:",
    "oceanman": "OCEAN MAN :ocean: :heart_eyes: Take me by the hand :raised_hand: lead me to the land "
                "that you understand :raised_hands: :ocean: OCEAN MAN :ocean: :heart_eyes: The voyage :bike: "
                "to the corner of the :earth_americas: globe is a real trip :ok_hand: :ocean: OCEAN MAN :ocean: "
                ":heart_eyes: The crust of a tan man :man_with_turban: imbibed by the sand :thumbsup: Soaking up "
                "the :sweat_drops: thirst of the land :100:"
}