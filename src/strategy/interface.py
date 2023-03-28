from abc import *


class Strategy(metaclass=ABCMeta):

    @abstractmethod
    def check_signal(self):
        pass

    def buy(self, current_price):
        pass

    def sell(self, current_price):
        pass

