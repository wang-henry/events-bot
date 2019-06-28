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


@client.event
async def on_message(message):
    # Prevent bot from detecting its own messages
    if message.author == client.user:
        return

    # Gets the server id
    server_id = message.guild.id

    # Check if JSON is already present
    if os.path.exists('data/events/{}.json'.format(server_id)):
        with open('data/events/{}.json'.format(server_id), 'r') as e_data:
            events = json.load(e_data)

        with open('data/dates/{}.json'.format(server_id), 'r') as d_data:
            date_lst = json.load(d_data)

    # Generate new JSON (Generation occurs below)
    else:
        events = {}
        date_lst = []

    # Add event command
    # !add event <yyyy> <mm> <dd> <Event name>
    if message.content.startswith('!add event '):
        msg = message.content[11:].split(' ')
        if len(msg) < 4:
            await message.channel.send("Invalid Input LEN")
            return

        year, month, day = msg[0], msg[1], msg[2]

        if year.isnumeric() and month.isnumeric() and day.isnumeric():
            try:
                date = datetime.date(int(year), int(month), int(day))
            except ValueError:
                await message.channel.send("Indavlid Date")
                return
        else:
            await message.channel.send("Invalid Date (Date not integers)")
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
        with open('data/events/{}.json'.format(server_id), 'w') as events_file:
            json.dump(events, events_file)

        with open('data/dates/{}.json'.format(server_id), 'w') as dates_file:
            json.dump(date_lst, dates_file)

        # Confirmation that event was added
        await message.channel.send("Added event '{}' for {}".format(event, date))

    # List all events
    if message.content.startswith('!list events'):
        if len(date_lst) == 0:
            await message.channel.send("No Upcoming Events")
            return

        date_lst.sort()
        s = ''
        for d in date_lst:
            s += str(d) + '\n'
            for e in events[d]:
                s += e + '\n'

        await message.channel.send("List of all events: \n" + s)

    # Delete an event
    # !remove event <yyyy> <mm> <dd> <num>
    if message.content.startswith('!remove event'):
        msg = message.content[14:].split(' ')
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
                del events[date]
                date_lst.remove(date)

                # Write both objects to JSON files per server
                with open('data/events/{}.json'.format(server_id), 'w') as events_file:
                    json.dump(events, events_file)

                with open('data/dates/{}.json'.format(server_id), 'w') as dates_file:
                    json.dump(date_lst, dates_file)

                await message.channel.send("Successfully removed event '{}' on {}".format(event[2:], date))
            else:
                await message.channel.send("Event not found")
                return
        else:
            await message.channel.send("Date not found")

    if message.content.startswith('!help'):
        await message.channel.send(
            "```List of all commands:\n!add event <yyyy> <mm> <dd> <event name> (Add an event)\n!remove event <yyyy> <mm> <dd> <index> (Remove an event)\n!list events (Lists all events)\n!help (Displays this message)```")


client.run(TOKEN)
