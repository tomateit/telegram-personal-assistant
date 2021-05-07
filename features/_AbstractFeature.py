from abc import ABCMeta, abstractmethod

class AbstractFeature(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def event_builder():
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def feature(event):
        raise NotImplementedError