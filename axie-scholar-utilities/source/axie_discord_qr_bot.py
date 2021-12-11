import asyncio
import configparser
import io
import os

from discord import File
from discord.ext import commands


def runDiscordBot(discord_token, discord_guild_id, dbpath):

    from axie.DatabaseReader import DatabaseReader
    from axie.qr_code import createQRImage

    def is_in_guild(guild_id):
        async def predicate(ctx):
            return ctx.guild and ctx.guild.id == int(guild_id)
        return commands.check(predicate)

    bot = commands.Bot(command_prefix="!")


    @bot.command(
        name="qrcode",
        help="Sends a QR Code to the requestor."
    )
    @is_in_guild(discord_guild_id)
    async def send_qr_code(context):
        dbreader = DatabaseReader(dbpath)
        users = dbreader.getScholarByDiscordName(
            "{}#{}".format(
                context.author.name,
                context.author.discriminator
            )
        )
        user = bot.get_user(context.author.id) or await bot.fetch_user(context.author.id)
        if users and user:

            userData = users[0]
            image, qrCodeValid = createQRImage(userData)
            output = io.BytesIO()
            image.save(output, format="PNG")
            output.seek(0)

            await user.send(file=File(output, "qrcode.png"))
        else:
            await user.send("Cannot find scholar {}.".format(context.author.name))

    @send_qr_code.error
    async def secretguilddata_error(ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('Nothing to see here comrade.')

    bot.run(discord_token)


if __name__ == '__main__':
    os.makedirs('logs', exist_ok=True)

    config = configparser.ConfigParser()
    config.read("config.ini")

    dbpath = None
    discord_token = None
    discord_guild_id = None
    try:
        dbpath = config["DEFAULT"]["DATABASE_FILE"]
        discord_token = config["DEFAULT"]["DISCORD_TOKEN"]
        discord_guild_id = int(config["DEFAULT"]["DISCORD_GUILD_ID"])
    except KeyError:
        pass

    print("Starting Axie Discord QR Bot . . .")
    runDiscordBot(discord_token, discord_guild_id, dbpath)
