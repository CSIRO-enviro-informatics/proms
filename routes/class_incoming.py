from abc import ABCMeta, abstractmethod
import database


class IncomingClass:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, data, mimetype):
        self.data = data
        self.mimetype = mimetype
        self.graph = None
        self.uri = None
        self.error_messages = None

    @abstractmethod
    def valid(self):
        pass

    @abstractmethod
    def determine_uri(self):
        pass

    def stored(self):
        """ Add an item to PROMS"""
        try:
            database.insert(self.graph, self.uri)
            return True
        except Exception as e:
            self.error_messages = ['Could not connect to the provenance database']
            return False
