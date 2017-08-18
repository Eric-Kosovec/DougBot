from dougbot.dougbot import DougBot


def main():
    bot = DougBot("./dougbot/config/config.ini")
    bot.run()
    return


if __name__ == "__main__":
    main()
