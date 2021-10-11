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

# async def main():
#     async for draft in client.iter_drafts():
#         print(draft.text)


from features import OnNewMessageUppsercase, OnEditUppercase, OnNewMessageJoin

client.add_event_handler(OnEditUppercase.feature, OnEditUppercase.event_builder())
client.add_event_handler(OnNewMessageUppsercase.feature, OnNewMessageUppsercase.event_builder())
client.add_event_handler(OnNewMessageJoin.feature, OnNewMessageJoin.event_builder())



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