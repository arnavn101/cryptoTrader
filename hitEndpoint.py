#!/usr/bin/python

from requests import Session
import requests
import json
import time


class CoinMarketEndpoint:
    def __init__(self, coinMarketApiKey):
        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': f'{coinMarketApiKey}',
        }
        self.session = Session()
        self.session.headers.update(self.headers)

    def hitSpecifiedURL(self, endpointURL, endpointParameters):
        return self.session.get(endpointURL, params=endpointParameters)

    def getLatestData(self, outputLimit=1, cryptoSymbol='BTC'):
        endpointURL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        endpointParameters = {
            'start': '1',
            'limit': f'{outputLimit}',
        }
        formattedResponseData = json.loads(self.hitSpecifiedURL(endpointURL, endpointParameters).text)
        latestDataCypto = [dataPoint for dataPoint in formattedResponseData['data'] if
                           dataPoint['symbol'] == cryptoSymbol]
        return latestDataCypto


class CryptoCompareEndpoint:
    # https://min-api.cryptocompare.com
    def __init__(self, fromCurr, toCurr, limitData, endTimeStamp=None, typeData='hour'):
        self.baseURL = f'https://min-api.cryptocompare.com/data/histo{typeData}?'

        if not endTimeStamp:
            endTimeStamp = str(int(time.time()))

        # CryptoCompare only allows upto 2000 results per call
        self.maxLimit = 2000
        self.limExceededBy = None
        self.thisURL = self.formulateURL(fromCurr, toCurr, str(limitData - 1), endTimeStamp)
        self.responseData = CryptoCompareEndpoint.hitSpecifiedURL(self.thisURL)

    def formulateURL(self, fromCurr, toCurr, limitData, endTimeStamp):
        requestArguments = list()
        limitData = int(limitData)

        requestArguments.append('fsym=' + fromCurr)
        requestArguments.append('tsym=' + toCurr)
        requestArguments.append('limit=' + str(max(self.maxLimit, limitData)))

        if limitData > self.maxLimit:
            self.limExceededBy = limitData - self.maxLimit

        requestArguments.append('toTs=' + endTimeStamp)

        return self.baseURL + '&'.join(requestArguments)

    @staticmethod
    def hitSpecifiedURL(specificURL):
        rawData = requests.get(specificURL)
        rawData.encoding = 'utf-8'

        if rawData.status_code != 200:
            rawData.raise_for_status()
            return False

        try:
            if rawData.json()['Response'] != "Success":
                raise ValueError(f'CryptoCompare API Error: {rawData.json()["Message"]}')
            return rawData.json()['Data']
        except NameError:
            raise ValueError('Cannot parse to json.')

    def returnSpecificData(self, dataColumnName):
        return [float(d[dataColumnName]) for d in self.responseData if dataColumnName in d]

    def returnResponseData(self):
        return self.responseData

