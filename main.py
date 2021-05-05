from dotenv import load_dotenv
from telethon import TelegramClient, events, sync
import os
import logging
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
load_dotenv()

API_ID = os.environ["API_ID"]
API_HASH = os.environ["API_HASH"]

client = TelegramClient('TelegramPA_session', API_ID, API_HASH)
client.start()
me = client.get_me()

async def main():
    async for draft in client.iter_drafts():
        print(draft.text)


client.on()(on_newmessage_uppercase)




client.add_event_handler(on_edit_uppercase, events.MessageEdited(outgoing=True, pattern=EDITED_UPPERCASE_PATTERN))


if __name__ == "__main__":
    with client:
        try:
            print("Launching client")
            # client.loop.run_until_complete(main())
            client.run_until_disconnected()
        except Exception as e:
            print("Stopping client")
            logging.exception(e) 
            client.disconnect()