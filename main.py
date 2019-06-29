#!usr/bin/env python3
import discord
import datetime
import json
import os

f = open("token.txt", "r")
TOKEN = f.readline()

client = discord.Client()


# Startup messages
@client.event
async def on_ready():
    print("Discord bot is ready!")

    # Initialize cmd_chars.json if it is not present
    if not os.path.exists('data/cmd_chars.json'):
        with open('data/cmd_chars.json', 'w') as cmd_chars_init:
            json.dump({}, cmd_chars_init)


@client.event
async def on_message(message):
    # Prevent bot from detecting its own messages
    if message.author == client.user:
        return

    # Gets the server id
    server_id = message.guild.id

    # Check if server_id is in cmd_chars
    with open('data/cmd_chars.json', 'r') as cmd_chars:
        chars = json.load(cmd_chars)

    if server_id not in chars:
        cmd_char = '!'
    else:
        cmd_char = chars[server_id]

    # Check if JSON is already present
    if os.path.exists(f'data/events/{server_id}.json'):
        with open(f'data/events/{server_id}.json', 'r') as e_data:
            events = json.load(e_data)

        with open(f'data/dates/{server_id}.json', 'r') as d_data:
            date_lst = json.load(d_data)

    # Generate new JSON (Generation occurs below)
    else:
        events = {}
        date_lst = []

    # Add event command
    # !add event <yyyy> <mm> <dd> <Event name>
    if message.content.startswith(f'{cmd_char}events add'):
        await add_event(message, events, server_id, date_lst)

    # List all events
    if message.content.startswith(f'{cmd_char}events list'):
        await list_events(message, events, date_lst)

    # Delete an event
    # !remove event <yyyy> <mm> <dd> <num>
    if message.content.startswith(f'{cmd_char}events remove'):
        await delete_event(message, events, server_id, date_lst)

    if message.content.startswith(f'{cmd_char}events clear'):
        os.remove(f'data/events/{server_id}.json')
        os.remove(f'data/dates/{server_id}.json')
        await message.channel.send("Removed all events!")

    if message.content.startswith('!events set cmd'):
        pass

    if message.content.startswith('!help'):
        await message.channel.send(
            "```List of all commands:\n"
            "!events add <yyyy> <mm> <dd> <event name> (Add an event)\n"
            "!events remove <yyyy> <mm> <dd> <index> (Remove an event)\n"
            "!events list (Lists all events)\n"
            "!events clear (Removes all events)\n"
            "!help (Displays this message)```"
        )


async def add_event(message, events, server_id, date_lst):
    msg = message.content[12:].split(' ')
    if len(msg) < 4:
        await message.channel.send("Invalid Input Length")
        return

    year, month, day = msg[0], msg[1], msg[2]

    if year.isnumeric() and month.isnumeric() and day.isnumeric():
        try:
            date = datetime.date(int(year), int(month), int(day))
        except ValueError:
            await message.channel.send("Invalid Date")
            return
    else:
        await message.channel.send("Invalid Date Input")
        return

    # Generate event name
    event = ''
    for char in msg[3:]:
        event += char + ' '

    # Convert to string to input into JSON
    date = str(date)

    # Add events to dict
    if date in events:
        events[date].append(str(len(events[date]) + 1) + ") " + event)
    else:
        events[date] = ["1) " + event.strip()]
        date_lst.append(date)

    # Write both objects to JSON files per server
    with open(f'data/events/{server_id}.json', 'w') as events_file:
        json.dump(events, events_file)

    with open(f'data/dates/{server_id}.json', 'w') as dates_file:
        json.dump(date_lst, dates_file)

    # Confirmation that event was added
    await message.channel.send(f"Added event '{event}' for {date}")


async def list_events(message, events, date_lst):
    if len(date_lst) == 0:
        await message.channel.send("```No Upcoming Events```")
        return

    date_lst.sort()
    s = ''
    for d in date_lst:
        s += str(d) + '\n'
        for e in events[d]:
            s += e + '\n'

    await message.channel.send("```List of all Upcoming Events: \n" + s + "```")


async def delete_event(message, events, server_id, date_lst):
    msg = message.content[15:].split(' ')
    if len(msg) != 4:
        await message.channel.send("Invalid Input (Format)")
        return

    year, month, day, num = msg[0], msg[1], msg[2], msg[3]

    # Verify all integers
    if year.isnumeric() and month.isnumeric() and day.isnumeric() and num.isnumeric():
        try:
            date = datetime.date(int(year), int(month), int(day))
        except ValueError:
            await message.channel.send("Invalid Date")
            return
    else:
        await message.channel.send("Invalid Date (Date not integers)")
        return

    date = str(date)
    if date in events:
        if 1 <= int(num) <= len(events[date]):
            event = events[date].pop(int(num) - 1)

            if len(events[date]) == 0:
                del events[date]
                date_lst.remove(date)

            # Write both objects to JSON files per server
            with open(f'data/events/{server_id}.json', 'w') as events_file:
                json.dump(events, events_file)

            with open(f'data/dates/{server_id}.json', 'w') as dates_file:
                json.dump(date_lst, dates_file)

            await message.channel.send(f"Successfully removed event '{event[2:]}' on {date}")
        else:
            await message.channel.send("Event not found")
            return
    else:
        await message.channel.send("Date not found")


if __name__ == '__main__':
    client.run(TOKEN)
