import discord
import os
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord import slash_command, Option
import asyncio
import sqlite3
import time
import datetime
from datetime import timedelta
from discord.ext.commands import MissingPermissions

load_dotenv()
TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.reactions = True

status = discord.Status.dnd
activity = discord.Activity(type=discord.ActivityType.watching, name="Günter97")

bot = discord.Bot(
    intents=intents,
    debug_guilds=[1284155944863010931, 1279453923815460905],
    status=status,
    activity=activity
)



@bot.slash_command(guild_ids = [1284155944863010931, 1279453923815460905], name = 'timeout', description = "Timeoute einen Member")
@commands.has_permissions(moderate_members = True)
async def timeout(ctx, member: Option(discord.Member, required = True), reason: Option(str, required = False), days: Option(int, max_value = 27, default = 0, required = False), hours: Option(int, default = 0, required = False), minutes: Option(int, default = 0, required = False), seconds: Option(int, default = 0, required = False)): #setting each value with a default value of 0 reduces a lot of the code
    if member.id == ctx.author.id:
        await ctx.respond("Bro warum Timeoutest du dich selber?")
        return
    if member.guild_permissions.moderate_members:
        await ctx.respond("Stopp diese funktion ist nur für das Team zugänglich")
        return
    duration = timedelta(days = days, hours = hours, minutes = minutes, seconds = seconds)
    if duration >= timedelta(days = 28): #added to check if time exceeds 28 days
        await ctx.respond("Das Timeout Limit liegt bei 27 Tagen wende dich bei Anliegen an TheFrogY!", ephemeral = True) #responds, but only the author can see the response
        return
    if reason == None:
        await member.timeout_for(duration)
        await ctx.respond(f"<@{member.id}> wurde für {days} Tage , {hours} Stunden, {minutes} Minuten und {seconds} Sekunden von <@{ctx.author.id}> getimeoutet.")
    else:
        await member.timeout_for(duration, reason = reason)
        await ctx.respond(f"<@{member.id}> wurde für {days} Tage , {hours} Stunden, {minutes} Minuten und {seconds} Sekunden von <@{ctx.author.id}> getimeoutet. Grund: '{reason}'.")

@timeout.error
async def timeouterror(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.respond("Error!")
    else:
        raise error

@bot.slash_command(guild_ids = [1284155944863010931, 1279453923815460905], name = 'unmute', description = "Unmutet einen Member")
@commands.has_permissions(moderate_members = True)
async def unmute(ctx, member: Option(discord.Member, required = True), reason: Option(str, required = False)):
    if reason == None:
        await member.remove_timeout()
        await ctx.respond(f"<@{member.id}> wurde ungemuted von <@{ctx.author.id}>.")
    else:
        await member.remove_timeout(reason = reason)
        await ctx.respond(f"<@{member.id}> wurde ungemutet von  <@{ctx.author.id}> Grund: '{reason}'.")

@unmute.error
async def unmuteerror(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.respond("Error!")
    else:
        raise error


@bot.slash_command(guild_ids=[1284155944863010931, 1279453923815460905], name="ban", description="Banne einen member")
@commands.has_permissions(ban_members=True, administrator=True)
async def ban(ctx, member: Option(discord.Member, description="Wen willst du bannen?"),
              reason: Option(str, description="Why?", required=False)):
    if member.id == ctx.author.id:  # checks to see if they're the same
        await ctx.respond("BRUH! Du kannst dich nicht selber bannen!")
    elif member.guild_permissions.administrator:
        await ctx.respond("Versuche nicht einen Admin zu bannen! :rolling_eyes:")
    else:
        if reason == None:
            reason = f"None provided by {ctx.author}"
        await member.ban(reason=reason)
        await ctx.respond(
            f"<@{ctx.author.id}>, <@{member.id}> wurde erfolgreich vom Server gebannt!\n\nReason: {reason}")


@ban.error
async def banerror(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.respond("Du hast nicht die richtigen Rechte dafür!!")
    else:
        await ctx.respond("Irgendetwas scheint nicht zu funktionieren wende dich bitte an TheFrogY...")  
        raise error


@bot.slash_command(guild_ids=[1284155944863010931, 1279453923815460905], name="kick", description="Kicks a member")
@commands.has_permissions(kick_members=True, administrator=True)
async def kick(ctx, member: Option(discord.Member, description="Who do you want to kick?"),
               reason: Option(str, description="Why?", required=False)):
    if member.id == ctx.author.id:  # checks to see if they're the same
        await ctx.respond("BRUH! Du kannst dich selber nicht kicken!")
    elif member.guild_permissions.administrator:
        await ctx.respond("Versuche nicht einen Admin zu kicken! :rolling_eyes:")
    else:
        if reason == None:
            reason = f"None provided by {ctx.author}"
        await member.kick(reason=reason)
        await ctx.respond(f"<@{ctx.author.id}>, <@{member.id}> wurde vom Server gekickt!\n\nReason: {reason}")


@kick.error
async def kickerror(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.respond("Error!!")
    else:
        await ctx.respond("Irgendetwas scheint nicht zu funktionieren wende dich bitte an TheFrogY...")  
@bot.event
async def on_ready():
    print(f"{bot.user} ist online")
    


#Cogs Starten
if __name__ == '__main__':
    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")
  

#Bot Starten
bot.run("TOKEN")
