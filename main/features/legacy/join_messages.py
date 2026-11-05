from ._AbstractFeature import AbstractFeature
from telethon.events import NewMessage
import re

class JoinMessages(AbstractFeature):
    COMMAND_PATTERN = r'^\*\+\*$'

    async def on_new_message(self, event):
        print("Event on_newmessage_join triggered")
        chat = await event.get_chat()
        await event.delete()

        joined_message = ""
        async for message in event.client.iter_messages(chat, limit=20):
            if message.out:
                #TODO: media shall break too
                joined_message = message.raw_text + "\n" + joined_message
                await message.delete()
            else:
                break
        # joined_message = joined_message.strip()
        await event.client.send_message(chat, joined_message, silent=True)
