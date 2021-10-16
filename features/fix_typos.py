from ._AbstractFeature import AbstractFeature
from telethon.events import NewMessage
import re
from pathlib import Path
import jamspell
import logging
model_path = Path("./vendor/ru_news.bin")


class FixTypos(AbstractFeature):
    COMMAND_PATTERN = r'^\+\+\+$'
    def __init__(self):
        logging.debug(f"Loadin model from {model_path}")
        if not model_path.exists():
            print("NO MODEL")
            return
        self.corrector = jamspell.TSpellCorrector()
        ok = self.corrector.LoadLangModel(str(model_path.resolve()))
        if ok:
            logging.debug(f"Loaded model")
        else:
            logging.debug(f"Failed to load model")

    

    
    async def on_new_message(self, event):
        logging.info("Event on_newmessage_fix triggered")
        chat = await event.get_chat()
        await event.delete()

        async for message in event.client.iter_messages(chat, limit=1, from_user='me'):
            if event.id != message.id:
                text = message.raw_text
                await message.edit(self.corrector.FixFragment(text))
                break
        