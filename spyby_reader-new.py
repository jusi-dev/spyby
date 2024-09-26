import requests
import sqlite3
import time

# Database setup
conn = sqlite3.connect('chatlog.db')
cursor = conn.cursor()

# Create the table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS chatlog (
        id TEXT NOT NULL,
        username TEXT NOT NULL,
        message TEXT NOT NULL,
        destination_channel_id TEXT NOT NULL,
        sent BOOLEAN NOT NULL,
        avatar TEXT,
        user_id TEXT,
        PRIMARY KEY (id, destination_channel_id)
    )
''')

# Create the channel_mappings table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS channel_mappings (
        target_channel_id TEXT NOT NULL,
        authToken TEXT NOT NULL,
        destination_channel_id TEXT NOT NULL
    )
''')
conn.commit()

def fetch_messages(target_channel_id, authToken):
    try:
        headers = {
            'Authorization': f'{authToken}'
        }
        response = requests.get(
            f'https://discord.com/api/v9/channels/{target_channel_id}/messages?limit=5',
            headers=headers
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
        messages = response.json()
        print(f'Got new messages from channel {target_channel_id}')
        return messages
    except requests.exceptions.RequestException as e:
        print(f"Error fetching messages from channel {target_channel_id}: {e}")
        return []

def insert_message(message_id, username, content, destination_channel_id, avatar, user_id):
    try:
        cursor.execute('''
            INSERT INTO chatlog (id, username, message, sent, destination_channel_id, avatar, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (message_id, username, content, False, destination_channel_id, avatar, user_id))
        conn.commit()
    except sqlite3.IntegrityError:
        # Message ID and destination_channel_id already exist in the database
        pass


def message_exists(message_id, destination_channel_id):
    cursor.execute('SELECT 1 FROM chatlog WHERE id = ? AND destination_channel_id = ?', (message_id, destination_channel_id))
    return cursor.fetchone() is not None

def process_messages(messages, authToken, destination_channel_id):
    for message in messages:
        message_id = message.get('id')
        content = message.get('content')
        author = message.get('author', {})
        username = author.get('global_name')
        avatar = author.get('avatar')
        user_id = author.get('id')

        if message_id and content is not None and username:
            if not message_exists(message_id, destination_channel_id):
                insert_message(message_id, username, content, destination_channel_id, avatar, user_id)

def main():
    try:
        while True:
            # Fetch all mappings from the channel_mappings table
            cursor.execute('SELECT target_channel_id, authToken, destination_channel_id FROM channel_mappings')
            mappings = cursor.fetchall()
            for mapping in mappings:
                target_channel_id, authToken, destination_channel_id = mapping
                messages = fetch_messages(target_channel_id, authToken)
                process_messages(messages, authToken, destination_channel_id)
            time.sleep(5)
    except KeyboardInterrupt:
        conn.close()
        print("\nScript terminated.")

if __name__ == '__main__':
    main()
