#!/usr/bin/python

from bs4 import BeautifulSoup
import requests
from abc import ABC, abstractmethod


class AccessWebsite(ABC):
    @abstractmethod
    def __init__(self, inputURL):
        self.inputURL = inputURL
        self.currentPrice = None
        self.soupParser = None

    def makeRequest(self):
        return requests.get(self.inputURL)

    @abstractmethod
    def retrieveContent(self):
        self.soupParser = BeautifulSoup(self.makeRequest().content, 'html.parser')

    @abstractmethod
    def returnCurrentPrice(self):
        return self.currentPrice.replace(',', '')


class AccessCoinDesk(AccessWebsite):
    def __init__(self, cryptoSymbol):
        self.cryptoSymbol = cryptoSymbol
        self.thisURL = f'https://www.coindesk.com/price/{self.cryptoSymbol.lower()}'
        super(AccessCoinDesk, self).__init__(self.thisURL)

    def retrieveContent(self):
        super(AccessCoinDesk, self).retrieveContent()
        divContent = self.soupParser.find('div', {'class': 'price-large'})
        self.currentPrice = divContent.contents[1]

    def returnCurrentPrice(self):
        return super(AccessCoinDesk, self).returnCurrentPrice()
