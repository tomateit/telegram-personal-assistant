from dotenv import load_dotenv
from telethon import TelegramClient, events, sync
import os
import logging
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
load_dotenv()

API_ID = os.environ["API_ID"]
API_HASH = os.environ["API_HASH"]

api_id = API_ID
api_hash = API_HASH

client = TelegramClient('TelegramPA_session', api_id, api_hash)
client.start()
me = client.get_me()

async def main():
    async for draft in client.iter_drafts():
        print(draft.text)
    # print(me.stringify())
    # username = me.username
    # print(username)
    # print(me.phone)
    # client.send_message('me', 'Hello! Talking to you from Telethon')

    # You can print all the dialogs/conversations that you are part of:
    # async for dialog in client.iter_dialogs():
    #     print(dialog.name, 'has ID', dialog.id)

    # You can send messages to yourself...
    # message = await client.send_message('me', 'Hello, myself!')

    # Sending a message returns the sent message object, which you can use
    # print(message.raw_text)

    # You can reply to messages directly if you have a message object
    # await message.reply('Cool!')

# @client.on(events.NewMessage(pattern='(?i)hi|hello'))
# async def handler(event):
#     await event.respond('Hey!')

UPPERCASE_PATTERN = r'^\$~$'
import re
# @client.on(events.NewMessage(outgoing=True, pattern=UPPERCASE_PATTERN))
# async def uppercase_command(event):
#     chat = await event.get_chat()
#     # chat_id = event.chat_id
#     sender = await event.get_sender()
#     # sender_id = event.sender_id
#     if sender != client.get_me():
#         raise RuntimeError("Only I can trigger this")

#     n_iter, limit_iter = 0, 4
#     async for message in client.iter_messages(chat):
#         n_iter += 1
#         if event.id != message.id:
#             if (await message.get_sender() == me):
#                 text = message.raw_text
#                 await message.edit(text)
#                 print("Edited message")
#                 break
#         if n_iter == limit_iter:
#             print("Too many iterations")
#             break

EDITED_UPPERCASE_PATTERN = r'\$~'
@client.on(events.MessageEdited(outgoing=True, pattern=EDITED_UPPERCASE_PATTERN))
async def uppercase_command(event):
    text = event.message.raw_text
    # chat_id = event.chat_id
    await event.message.edit(text.upper())

if __name__ == "__main__":
    with client:
        try:
            client.loop.run_until_complete(main())
        except Exception as e:
            logging.exception(e) 
            client.log_out()