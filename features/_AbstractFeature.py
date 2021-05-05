from abc import ABCMeta, abstractclassmethod
from telethon.events import Event,

class AbstractFeature(metaclass=ABCMeta):
    @abstractclassmethod
    def _event_builder()-> Event:

    @abstractclassmethod
    def _feature(event: Event)