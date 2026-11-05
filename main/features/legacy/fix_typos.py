from ._AbstractFeature import AbstractFeature
from telethon.events import NewMessage
import re
from pathlib import Path
import logging


class FixTypos(AbstractFeature):
    COMMAND_PATTERN = r'^\+\+\+$'
    def __init__(self):
        raise NotImplementedError()

    

    
    async def on_new_message(self, event):
        raise NotImplementedError()
        # logging.info("Event on_newmessage_fix triggered")
        # chat = await event.get_chat()
        # await event.delete()

        # async for message in event.client.iter_messages(chat, limit=1, from_user='me'):
        #     if event.id != message.id:
        #         text = message.raw_text
        #         await message.edit(self.corrector.FixFragment(text))
        #         break
        