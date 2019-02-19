import os

from discord.ext import commands


class ImageViewer:
    _IMG_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    _IMG_DIR = os.path.join(_IMG_DIR, 'res', 'image')

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['imgview'], pass_context=True, no_pm=True)
    async def img(self, ctx, image: str):
        path = await self._find_image(image)
        if path is None:
            await self.bot.confusion(ctx.message)
        else:
            await self.bot.upload(path)

    @commands.command(no_pm=True)
    async def images(self):
        images = []

        for file in os.listdir(self._IMG_DIR):
            last_dot = file.rfind('.')
            if last_dot >= 0:
                images.append(file[:last_dot])

        enter = ''
        message = 'Images:\n'
        for image in images:
            message += enter + image
            enter = '\n'

        await self.bot.say(message)

    async def _find_image(self, image):
        if image is None:
            return None

        if '..' in image:
            return None

        for file in os.listdir(self._IMG_DIR):
            if file.startswith(f'{image}.'):
                return os.path.join(self._IMG_DIR, file)

        return None


def setup(bot):
    bot.add_cog(ImageViewer(bot))
