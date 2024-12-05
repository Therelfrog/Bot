import discord
from discord.ext import commands
from discord.commands import slash_command
from discord.commands import Option


class Greet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Grüße einen Spieler")
    async def greet(self, ctx, user: Option(discord.Member, "User den du grüßen willst")):
        await ctx.respond(f"Hallo {user.mention}!")

def setup(bot):
    bot.add_cog(Greet(bot))
