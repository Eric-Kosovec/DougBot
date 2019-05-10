from discord import Webhook, RequestsWebhookAdapter

DOUG_HOOK_URL = 'https://discordapp.com/api/webhooks/565341847417913354/' \
                'qLWInhejw5CpIU_3k112b_rjCCB-nLyHx1PvvI5ZyWln8K7BxC90h8-Qns5ckfP2WQ0R'

DOUG_CHANNEL = 'https://discordapp.com/api/channels/245632003570008084/messages'

USERNAME = 'DougHook'


def main():
    webhook = Webhook.from_url(DOUG_HOOK_URL, adapter=RequestsWebhookAdapter())
    webhook.send('Hello World', username=USERNAME)


if __name__ == '__main__':
    main()
