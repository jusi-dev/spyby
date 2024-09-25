import requests
import sqlite3
import time

# Database setup
conn = sqlite3.connect('chatlog.db')
cursor = conn.cursor()

# Create the table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS chatlog (
        id TEXT PRIMARY KEY,
        username TEXT NOT NULL,
        message TEXT NOT NULL,
        sent BOOLEAN NOT NULL
    )
''')
conn.commit()

def fetch_messages():
    try:
        headers = {
            'Authorization': 'Discord Token'
        }
        response = requests.get('https://discord.com/api/v9/channels/1204030142939144224/messages?limit=50', headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        messages = response.json()
        print('Got new messages')
        return messages
    except requests.exceptions.RequestException as e:
        print(f"Error fetching messages: {e}")
        return []

def insert_message(message_id, username, content):
    try:
        cursor.execute('''
            INSERT INTO chatlog (id, username, message, sent)
            VALUES (?, ?, ?, ?)
        ''', (message_id, username, content, False))
        conn.commit()
    except sqlite3.IntegrityError:
        # Message ID already exists in the database
        pass

def message_exists(message_id):
    cursor.execute('SELECT 1 FROM chatlog WHERE id = ?', (message_id,))
    return cursor.fetchone() is not None

def process_messages(messages):
    for message in messages:
        message_id = message.get('id')
        content = message.get('content')
        author = message.get('author', {})
        username = author.get('username')

        if message_id and content is not None and username:
            if not message_exists(message_id):
                insert_message(message_id, username, content)

def main():
    try:
        while True:
            messages = fetch_messages()
            process_messages(messages)
            time.sleep(5)
    except KeyboardInterrupt:
        conn.close()
        print("\nScript terminated.")

if __name__ == '__main__':
    main()
