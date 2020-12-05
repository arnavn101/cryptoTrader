#!/usr/bin/python

from abc import ABC, abstractmethod
from utils import UnixTimeToLocal, percent_difference
from hitEndpoint import CryptoCompareEndpoint


class TradingStrategy(ABC):
    """

    Basic Abstract Method to model all the Trading Strategies

    """

    @abstractmethod
    def __init__(self, initialPortfolioValue):
        self.initialPortfolioValue = initialPortfolioValue
        self.portfolioValue = initialPortfolioValue
        self.numberCoins = 0
        self.numberTransactions = 0

    @abstractmethod
    def executeStrategy(self):
        pass

    def returnPortfolioValue(self):
        return self.portfolioValue

    def returnNumberCoins(self):
        return self.numberCoins

    def returnNumberTransactions(self):
        return self.numberTransactions

    def calculateProfit(self, currentPrice):
        currentPortfolioValue = self.portfolioValue + (currentPrice * self.numberCoins)
        return currentPortfolioValue - self.initialPortfolioValue

    def makeTransaction(self, transactionType, transactionCoins, currentCoinPrice, specificTransactionFee=0):
        self.numberTransactions += 1
        amountTransact = currentCoinPrice * transactionCoins

        if transactionType == 'buy':
            if (self.portfolioValue - amountTransact) > 0:
                self.portfolioValue -= amountTransact * (1 + specificTransactionFee)
                self.numberCoins += transactionCoins

        elif transactionType == 'sell':
            if self.numberCoins > 0:
                self.portfolioValue += amountTransact * (1 - specificTransactionFee)
                self.numberCoins -= transactionCoins

        else:
            return False


class PercentageStrategy(TradingStrategy):
    """

    Based on Simple Percentage Changes of Crypto price over time.
    - Simple Trading Strategy based on percent of change of Crypto every X hours.
    - A threshold decrease in Crypto connotes selling and increase connotes buying.

    """

    def __init__(self, initialPortfolioValue, fractionCoin, percentThreshold,
                 timePeriod, thresholdTransaction, transactionFees, typeTime='hour'):
        super(PercentageStrategy, self).__init__(initialPortfolioValue)
        self.fractionCoin = fractionCoin
        self.percentThreshold = percentThreshold
        self.thresholdTransaction = thresholdTransaction
        self.transactionFees = transactionFees
        self.profitCounter, self.lossCounter = 0, 0
        self.CryptoPriceAPI = CryptoCompareEndpoint('BTC', 'USD', timePeriod, typeData=typeTime)
        self.executeStrategy()

    def executeStrategy(self):
        listPrices = self.CryptoPriceAPI.returnSpecificData('close')

        for i in range(1, len(listPrices)):

            currentPrice = float(listPrices[i])
            previousPrice = float(listPrices[i - 1])
            percentDiff = percent_difference(currentPrice, previousPrice)

            if self.numberCoins > 0:
                ultimateTransactionMade = False

                if self.lossCounter >= self.thresholdTransaction:
                    ultimateTransactionMade = True
                    self.lossCounter -= 1

                elif self.profitCounter >= self.thresholdTransaction:
                    ultimateTransactionMade = True
                    self.profitCounter -= 1

                if ultimateTransactionMade:
                    self.makeTransaction('sell', self.numberCoins, currentPrice, self.transactionFees)
                    continue

            if percentDiff > self.percentThreshold:
                self.profitCounter += 1
                self.makeTransaction('buy', self.fractionCoin, currentPrice, self.transactionFees)

            elif percentDiff < -self.percentThreshold:
                self.lossCounter += 1
                if self.calculateProfit(currentPrice) > 0:
                    self.makeTransaction('sell', self.fractionCoin, currentPrice, self.transactionFees)

        self.finalizeStrategy(listPrices)

    def finalizeStrategy(self, listPrices):
        print(f"Coins in Holding: {self.numberCoins}")
        print(f"Current Portfolio Value: {self.portfolioValue}")

        finalPrice = float(listPrices[-1])
        finalPortfolioValue = self.portfolioValue + (finalPrice * self.numberCoins)
        print(f"Total number of Transactions: {self.numberTransactions}")
        print(f"Total Portfolio Value: {finalPortfolioValue}")

        print(f"Total Amount of Profit: {finalPortfolioValue - self.initialPortfolioValue}")


#  (initialPortfolioValue, fractionCoin, percentThreshold, timePeriod, thresholdTransaction, transactionFees, typeTime)
# realtimeStrategy = PercentageStrategy(100000, 3, 0.005, 24, 2, 0, 'hour')
