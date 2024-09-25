import sqlite3
import time
import requests

# Connect to the SQLite database
conn = sqlite3.connect('chatlog.db')
cursor = conn.cursor()

try:
    while True:
        # Retrieve messages where sent = False
        cursor.execute('SELECT id, username, message FROM chatlog WHERE sent = ?', (False,))
        unsent_messages = cursor.fetchall()

        for message in unsent_messages:
            message_id = message[0]
            username = message[1]
            message_content = message[2]

            # Print the message
            print(f"Username: {username}, Message: {message_content}")

            # Send a POST request
            # {"mobile_network_type":"unknown","content":"test5","nonce":null,"tts":false,"flags":0}
            payload = {
                'mobile_network_type': 'unknown',
                'content': message_content,
                "nonce": None,
                'tts': False,
                'flags': 0
            }

            headers = {
                'Authorization': 'Discord Token'
            }

            response = requests.post('https://discord.com/api/v9/channels/1288177400529686561/messages', headers=headers, json=payload)
            if response.status_code == 200:
                # Update sent = True for this message
                cursor.execute('UPDATE chatlog SET sent = ? WHERE id = ?', (True, message_id))
                conn.commit()
            else:
                print(f"Failed to send message {message_id}: {response.status_code}")

            # Update sent = True for this message
            cursor.execute('UPDATE chatlog SET sent = ? WHERE id = ?', (True, message_id))
            conn.commit()

        # Wait for 5 seconds
        time.sleep(5)

except KeyboardInterrupt:
    # Close the database connection when the script is interrupted
    conn.close()
    print("\nScript terminated.")
