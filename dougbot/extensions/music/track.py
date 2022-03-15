class Track:

    def __init__(self, ctx, voice, src, is_link, repeat=1):
        self.ctx = ctx
        self.voice = voice
        self.src = src
        self.is_link = is_link
        self.repeat = repeat
