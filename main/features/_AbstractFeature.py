from abc import ABCMeta, abstractmethod
from telethon.events import NewMessage, MessageEdited

class AbstractFeature(metaclass=ABCMeta):
    COMMAND_PATTERN: str

    def on_new_message_event_builder(self):
        return NewMessage(outgoing=True, pattern=self.COMMAND_PATTERN)

    def on_edited_message_event_builder(self):
        return MessageEdited(outgoing=True, pattern=self.COMMAND_PATTERN)

    
    def feature(self, event):
        raise NotImplementedError

   
    def on_new_message(self, event):
        raise NotImplementedError

   
    def on_edited_message(self, event):
        raise NotImplementedError