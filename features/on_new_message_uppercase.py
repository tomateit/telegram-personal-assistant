from ._AbstractFeature import AbstractFeature
from telethon.events import NewMessage
import re

class OnNewMessageUppsercase(AbstractFeature):
    UPPERCASE_PATTERN = r'^\$~$'
    @staticmethod
    def event_builder():
        return NewMessage(outgoing=True, pattern=OnNewMessageUppsercase.UPPERCASE_PATTERN)

    @staticmethod
    async def feature(event):
        print("Event on_newmessage_uppercase triggered")
        chat = await event.get_chat()
        # chat_id = event.chat_id
        await event.delete()

        async for message in event.client.iter_messages(chat, limit=4, from_user='me'):
            if event.id != message.id:
                text = message.raw_text
                await message.edit(text.upper())
                break
