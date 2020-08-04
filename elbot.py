# elbot.py
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import json
import riotapi
import riothandle as rh
import fantasymanager as fm

load_dotenv()  # get .env file
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='$')  # Bot is like discord.Client


# OPEN JSON OF USER DATA
with open('./json/temp.json') as j_file:  # get user data from local json file
    j_dat = json.load(j_file)
    strikes = j_dat["strikes"]  # user strikes as list of dicts
    ranks = j_dat["ranks"]  # user ranks as list of dicts


# SAVE TO TEMP.JSON
def save_dat():  # for writing j_dat to local json file
    with open('./json/temp.json', 'w') as outfile:
        json.dump(j_dat, outfile, indent=4)


# CALCULATE "STRIKES"
def strike(user_name, category):  # add strike to 'strikes' in temp.json
    culprit = next((item for item in strikes if item["name"] == user_name), None)  # get user vector

    # ADD TO EXISTING CATEGORY
    if culprit is not None:  # if previous offender add one to correct strike category
        culprit[category] += 1
        print('CULPRIT: \n ', culprit)
        j_dat['strikes'] = strikes  # i have no idea how strikes is updated tbh
        save_dat()

    # OR ADD USER TO TEMP.JSON
    else:  # new offender
        culprit = strikes.append({'name': user_name, 'xds': 0, '@everyones': 0})  # makes new entry in j_dat
        culprit[category] += 1
        print('CULPRIT (new): \n ', culprit)
        save_dat()
    return culprit


@bot.event  # readyuup
async def on_ready():
    print('- R E A D Y -')


# DELETE MESSAGES IN A CHANNEL
@bot.command()  # clean channel
async def clean(ctx):  # UOP
    channel = discord.utils.get(ctx.guild.channels, name=ctx.message.channel.name)  # get channel (default UOP)
    delete_count = 0
    async for message in channel.history(limit=100):  # delete elbert's messages for 100 messages
        if message.author.name == 'elbert' or message.content[0] == '$':  # also delete commands ($)
            await message.delete()
            delete_count += 1
    await ctx.message.channel.send(f'deleted {delete_count} messages')


@bot.command()
async def draft(ctx, *, args):
    await ctx.send('***STARTING DRAFT***')
    arglist = args.split(' ')
    for a in arglist:
        await ctx.send(a)


# DRAFT ROYALE!
@bot.command()
async def draftr(ctx, *, args):
    await ctx.send('***STARTING DRAFT ROYALE***')
    arglist = args.split(' ')


# COUNT XDs, @ALLs
@bot.event  # on message!!!
async def on_message(message):

    content = message.content
    channel = message.channel  # bot_testing
    user_name = message.author.name

    # STRIKE FOR @EVERYONE
    if message.mention_everyone:  # everyone counter
        await channel.send(f'{message.author.name} you dumb fuck')
        strike(message.author.name, '@everyones')
        return

    # STRIKE FOR XDs
    if 'xd' in content.lower() and message.author.name != 'elbert':  # xd counter
        xder = strike(message.author.name, 'xds')
        await channel.send(f'* xd counter: {xder["xds"]}')
        return

    await bot.process_commands(message)  # so that other on-message funcs will work


# STATE CHANGES
@bot.event  # announce streaming and afk
async def on_voice_state_update(user, before, after):

    # STREAMING
    stream_channel = bot.get_channel(537761321551265821)  # xanation #general
    if after.self_stream and not before.self_stream:  # if streaming now but not before
        await stream_channel.send(f'-----\n**{user}** is now streaming in **# {after.channel}**\n-----')

    # AFK
    if after.afk and not before.afk:
        await stream_channel.send(f'*{user} is taking an ed nap*')


# CREATE VOTE MSG
@bot.command()  # uo quadra/penta invoke
async def vote(ctx, text='PENTA?'):
    uo_pentas = bot.get_channel(688561224891236451)  # get channel to post to
    author = ctx.message.author.name
    await uo_pentas.send(f'**{author} HAS STARTED A VOTE!**')
    msg = await uo_pentas.send(text)
    emojis = [bot.get_emoji(537877317339447298), bot.get_emoji(537877317075337226)]  # pre set emojis
    for emoji in emojis:  # add emojis
        await msg.add_reaction(emoji)

# LOOK UP SOLOQ GAME
@bot.command()  # look up game
async def lookup(ctx, summoner):
    await ctx.send("**GETTING GAME FOR {}...**".format(summoner))
    matchups = riotapi.get_game(summoner)
    if type(matchups) == str:
        await ctx.send(matchups)
    else:
        await ctx.send(matchups[100])
        await ctx.send(matchups[200])
        await ctx.send(matchups['mmrs'])


# VOTE COUNTER
@bot.event
async def on_raw_reaction_add(payload):  # count votes
    if payload.channel_id == 677685580141690881:  # if you vote in uo-pentas
        reaction, user = await bot.wait_for('reaction_add')
        channel = reaction.message.channel

        if reaction.count < 4 and channel.id == 677685580141690881:  # announce vote on <4 votes in uo-pentas
            await channel.send(f'{user} has voted {reaction}')

        elif reaction.count == 4:  # end at 4 votes of any kind
            await channel.send(f'{user} has closed the voting! \n the result is: {reaction}')
            await reaction.message.delete()


# BAD COMMAND
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

bot.run(TOKEN)