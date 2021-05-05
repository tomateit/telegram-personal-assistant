
UPPERCASE_PATTERN = r'^\$~$'
import re
async def on_newmessage_uppercase(event):
    print("Event on_newmessage_uppercase triggered")
    chat = await event.get_chat()
    # chat_id = event.chat_id
    await event.delete()

    async for message in client.iter_messages(chat, limit=4, from_user=me):
        if event.id != message.id:
            text = message.raw_text
            await message.edit(text.upper())
            break

events.NewMessage(outgoing=True, pattern=UPPERCASE_PATTERN)