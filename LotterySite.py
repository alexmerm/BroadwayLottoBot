from abc import ABC, abstractmethod

class LotterySite(ABC):
    """Abstract class that lotteries implement"""
    @abstractmethod
    def getShows(self)-> dict[str:int]:
        """Returns Dict(showTitle,maxTickets) of shows available from lotterysite"""
        pass

    """ OTHERTEST
    """
    @abstractmethod
    def enterLotteries(self, showsToEnter : dict[str,int]):
        """Takes Dict(showtitle:numTickets) of lotteries to enter

        Parameters:
        showsToEnter : dict[str,int]
            the test
        """
        pass


class TeleCharge(LotterySite):
    def enterLotteries(self, showsToEnter):
        return super().enterLotteries(showsToEnter)
    def getShows(self):
        return super().getShows()