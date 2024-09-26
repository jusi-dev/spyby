import sqlite3
import time
import requests
import discord
from discord.ext import tasks
import asyncio

# Initalize discord bot
client = discord.Client(intents=discord.Intents.all())

# Connect to the SQLite database
conn = sqlite3.connect('chatlog.db')
cursor = conn.cursor()

async def send_bot_message(username, message_content, target_channel_id, avatar, user_id):
    await client.wait_until_ready()
    channel = client.get_channel(int(target_channel_id))
    if channel is None:
        print('Channel not found')
        return

    webhook = await channel.create_webhook(name=username)
    await webhook.send(
        str(message_content), username=username, avatar_url=f'https://cdn.discordapp.com/avatars/{user_id}/{avatar}.png'
    )

    webhook = await channel.webhooks()
    for webhook in webhook:
        await webhook.delete()

    print('Message sent')

async def process_messages():
    try:
        while True:
            # Retrieve messages where sent = False
            cursor.execute('SELECT id, username, message, destination_channel_id, avatar, user_id FROM chatlog WHERE sent = ?', (False,))
            unsent_messages = cursor.fetchall()
            print('Fetching...')

            for message in unsent_messages:
                print('Processing message: ', message)
                message_id = message[0]
                username = message[1]
                message_content = message[2]
                target_channel_id = message[3]
                avatar = message[4]
                user_id = message[5]

                # Print the message
                print(f"Username: {username}, Message: {message_content}, Target Channel ID: {target_channel_id}")

                # Bot logic
                
                await send_bot_message(username, message_content, target_channel_id, avatar, user_id)

                # Update sent = True for this message
                cursor.execute('UPDATE chatlog SET sent = ? WHERE id = ?', (True, message_id))
                conn.commit()

            # Wait for 5 seconds
            time.sleep(5)

    except KeyboardInterrupt:
        # Close the database connection when the script is interrupted
        conn.close()
        print("\nScript terminated.")

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await process_messages()

client.run('')
