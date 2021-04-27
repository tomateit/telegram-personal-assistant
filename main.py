from dotenv import load_dotenv
from telethon import TelegramClient, events, sync
import os
load_dotenv()

API_ID = os.environ["API_ID"]
API_HASH = os.environ["API_HASH"]

api_id = API_ID
api_hash = API_HASH

client = TelegramClient('session_name', api_id, api_hash)
client.start()

print(client.get_me().stringify())

client.send_message('trent', 'Hello! Talking to you from Telethon')
# client.send_file('username', '/home/myself/Pictures/holidays.jpg')

# client.download_profile_photo('me')
# messages = client.get_messages('username')
# messages[0].download_media()

@client.on(events.NewMessage(pattern='(?i)hi|hello'))
async def handler(event):
    await event.respond('Hey!')