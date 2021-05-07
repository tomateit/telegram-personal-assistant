from ._AbstractFeature import AbstractFeature
import re 
from telethon.events import MessageEdited

class OnEditUppercase(AbstractFeature):

    EDITED_UPPERCASE_PATTERN = r'\$~'

    @staticmethod
    def event_builder():
        return MessageEdited(outgoing=True, pattern=OnEditUppercase.EDITED_UPPERCASE_PATTERN)


    @staticmethod
    async def feature(event):
        text = event.message.raw_text
        text = re.sub(OnEditUppercase.EDITED_UPPERCASE_PATTERN, "", text)
        print("Event on_edit_uppercase triggered")
        # chat_id = event.chat_id
        await event.message.edit(text.upper())

