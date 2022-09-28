from ._AbstractFeature import AbstractFeature
import re
from telethon.errors.rpcerrorlist import MessageNotModifiedError

class InstantMath(AbstractFeature):
    @staticmethod
    def COMMAND_PATTERN(text):
        res = re.search(r'\([.1234567890+-/*^ ]{3,}\)', text)
        return bool(res)

    @staticmethod
    def __solver(expr) -> str:
        # print(f"Got {expr}")
        # Eval is ok, cuz it's my messages
        return f"{expr.group()} = {str(eval(expr.group()))}"

    async def on_new_message(self, event):
        text = event.message.raw_text
        print("Event instant math triggered", text)
        text = re.sub(r"\([.1234567890+-/*^\ ]{3,}\)", InstantMath.__solver, text)
        try:
            await event.message.edit(text)
        except MessageNotModifiedError:
            print("Message was not modified")