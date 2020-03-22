#!usr/bin/env python3
import discord
from discord.ext import commands
import datetime
import json
import os

f = open("token.txt", "r")
TOKEN = f.readline()

bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    print("Discord bot is ready!")


@bot.command()
async def add(ctx, year_in, month_in, day_in, event_name):
    valid_year = True
    valid_month = True
    valid_day = True

    error_msg = "Invalid"

    # Error checking
    if len(year_in) != 4 or not year_in.isnumeric():
        valid_year = False
        error_msg = error_msg + " year"

    if len(month_in) != 2 or not month_in.isnumeric():
        valid_month = False
        error_msg = error_msg + " month"

    if len(day_in) != 2 or not day_in.isnumeric():
        valid_day = False
        error_msg = error_msg + " day"

    # Error detected send error message and exit
    if valid_year is False or valid_month is False or valid_day is False:
        await ctx.message.channel.send(error_msg)
        return

    # Set values
    year = int(year_in)
    month = int(month_in)
    day = int(day_in)

    # Obtain server ID
    server_id = ctx.guild.id

    date_lst = []
    # Check if JSON is already present
    if os.path.exists(f'data/events/{server_id}.json'):
        with open(f'data/events/{server_id}.json', 'r') as e_data:
            events = json.load(e_data)

        with open(f'data/dates/{server_id}.json', 'r') as d_data:
            temp = json.load(d_data)["dates"]

        # Convert to datetime objects
        for date_str_item in temp:
            temp_year = int(date_str_item[0:4])
            temp_month = int(date_str_item[5:7])
            temp_day = int(date_str_item[8:])
            date_lst.append(datetime.date(temp_year, temp_month, temp_day))

    # Generate new JSON (Generation occurs below)
    else:
        events = {}

    # Create Date object
    try:
        date = datetime.date(int(year), int(month), int(day))
    except:
        await ctx.message.channel.send("Invalid Date")
        return

    date_str = str(date)

    # Check if in dictionary
    if date_str in events:
        events[date_str].append(event_name)
    else:
        events[date_str] = [event_name]

        # Add to date_lst and sort
        date_lst.append(date)
        date_lst.sort()

    # Write both objects to JSON files per server
    with open(f'data/events/{server_id}.json', 'w') as events_file:
        json.dump(events, events_file)

    # Convert date objects in sorted date list to str
    date_lst_str = []
    for date_item in date_lst:
        date_lst_str.append(str(date_item))

    with open(f'data/dates/{server_id}.json', 'w') as dates_file:
        json.dump({"dates": date_lst_str}, dates_file)

    # Confirmation that event was added
    await ctx.channel.send(f"Added event '{event_name}' for {date_str}")


@bot.command()
async def remove(ctx, year_in, month_in, day_in, index_in):
    valid_year = True
    valid_month = True
    valid_day = True

    error_msg = "Invalid"

    # Error checking
    if len(year_in) != 4 or not year_in.isnumeric():
        valid_year = False
        error_msg = error_msg + " year"

    if len(month_in) != 2 or not month_in.isnumeric():
        valid_month = False
        error_msg = error_msg + " month"

    if len(day_in) != 2 or not day_in.isnumeric():
        valid_day = False
        error_msg = error_msg + " day"

    # Error detected send error message and exit
    if valid_year is False or valid_month is False or valid_day is False:
        await ctx.message.channel.send(error_msg)
        return

    # Set values
    year = int(year_in)
    month = int(month_in)
    day = int(day_in)
    index = int(index_in)

    # Obtain server ID
    server_id = ctx.guild.id

    # Check if JSON is already present
    if os.path.exists(f'data/events/{server_id}.json'):
        with open(f'data/events/{server_id}.json', 'r') as e_data:
            events = json.load(e_data)

        with open(f'data/dates/{server_id}.json', 'r') as d_data:
            date_lst = json.load(d_data)["dates"]

    # Generate new JSON (Generation occurs below)
    else:
        events = {}
        date_lst = []

    # Create Date object
    try:
        date = datetime.date(int(year), int(month), int(day))
    except:
        await ctx.message.channel.send("Invalid Date")
        return

    date_str = str(date)

    if date_str not in events:
        await ctx.message.channel.send("Event not found")

    if index > len(events[date_str]) or index < 1:
        await ctx.message.channel.send("Invalid index")

    # Remove
    removed_event = events[date_str][index - 1]
    del events[date_str][index - 1]

    # No more events at given date, remove date from date_lst and events
    if len(events[date_str]) == 0:
        date_lst.remove(date_str)
        del events[date_str]

    # Write both objects to JSON files per server
    with open(f'data/events/{server_id}.json', 'w') as events_file:
        json.dump(events, events_file)

    with open(f'data/dates/{server_id}.json', 'w') as dates_file:
        json.dump({"dates": [date_lst]}, dates_file)

    await ctx.message.channel.send(f"Successfully removed {removed_event} on {date_str}")


@bot.command()
async def list(ctx):
    # Obtain server ID
    server_id = ctx.guild.id

    # Check if JSON is already present
    if os.path.exists(f'data/events/{server_id}.json'):
        with open(f'data/events/{server_id}.json', 'r') as e_data:
            events = json.load(e_data)

        with open(f'data/dates/{server_id}.json', 'r') as d_data:
            date_lst = json.load(d_data)["dates"]

    # Generate new JSON (Generation occurs below)
    else:
        events = {}
        date_lst = []

    embed = discord.Embed(title="Events", description="List of upcoming events:", color=0xeee657)

    for date in date_lst:
        event_display = ''
        count = 1
        for event in events[date]:
            event_display = event_display + str(count) + ") " + event + "\n"
            count += 1
            embed.add_field(name=date, value=event_display, inline=False)

    await ctx.send(embed=embed)


@bot.command()
async def clear(ctx):
    # Obtain server ID
    server_id = ctx.guild.id

    # Check if JSON is already present
    if os.path.exists(f'data/events/{server_id}.json'):
        with open(f'data/events/{server_id}.json', 'r') as e_data:
            events = json.load(e_data)

        with open(f'data/dates/{server_id}.json', 'r') as d_data:
            date_lst = json.load(d_data)["dates"]
    else:
        await ctx.message.channel.send("No Events to clear")
        return

    # Write both objects to JSON files per server
    with open(f'data/events/{server_id}.json', 'w') as events_file:
        json.dump({}, events_file)

    with open(f'data/dates/{server_id}.json', 'w') as dates_file:
        json.dump({"dates": []}, dates_file)


# Remove default help command
bot.remove_command('help')


@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Events Bot", description="List of commands are:", color=0xeee657)

    embed.add_field(name="!add <yyyy> <mm> <dd> <event name>", value="Add an event", inline=False)
    embed.add_field(name="!remove <yyyy> <mm> <dd> <index>", value="Remove an event", inline=False)
    embed.add_field(name="!list", value="Lists all events", inline=False)
    embed.add_field(name="!clear", value="Removes all events", inline=False)

    await ctx.send(embed=embed)


if __name__ == '__main__':
    bot.run(TOKEN)
