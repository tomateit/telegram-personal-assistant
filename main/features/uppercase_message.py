from ._AbstractFeature import AbstractFeature
import re 
from telethon.events import MessageEdited

class UppercaseMessage(AbstractFeature):
    COMMAND_PATTERN = r'\$~'

    async def on_edited_message(self, event):
        text = event.message.raw_text
        text = re.sub(self.COMMAND_PATTERN, "", text)
        print("Event on_edit_uppercase triggered")
        # chat_id = event.chat_id
        await event.message.edit(text.upper())

    async def on_new_message(self, event):
        print("Event on_newmessage_uppercase triggered")
        chat = await event.get_chat()
        # chat_id = event.chat_id
        await event.delete()

        async for message in event.client.iter_messages(chat, limit=4, from_user='me'):
            if event.id != message.id:
                text = message.raw_text
                await message.edit(text.upper())
                break

