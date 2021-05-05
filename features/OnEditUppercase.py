from _AbstractFeature import AbstractFeature

class OnEditUppercase(AbstractFeature):
    @staticmethod
    def _feature(event):
        EDITED_UPPERCASE_PATTERN = r'\$~'

async def on_edit_uppercase(event):
    text = event.message.raw_text
    text = re.sub(EDITED_UPPERCASE_PATTERN, "", text)
    print("Event on_edit_uppercase triggered")
    # chat_id = event.chat_id
    await event.message.edit(text.upper())