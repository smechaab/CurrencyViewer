#!/usr/bin/python

import krakenex
from currency_viewer import currency_viewer as cv

class TestProcess:

    """TestCase for process of data processing."""
    DELTA = 0.0001

    @classmethod
    def setup_class(cls):
        cls.cvObject = cv.CurrencyViewer()
        cls.krakenex = krakenex.API()
        cls.krakenex.load_key('kraken.key')
        cls.request_result = cls.cvObject.request_balance()

    def test_request_balance(self):
        """Test of request_balance function :
            'result' shouldn't be empty"""
        print(self.request_result)
        assert self.request_result

    def test_extract_fiat_balance(self):
        """Test of extract_fiat_balance function :
            fiat symbols should match with raw data from Krakenex API"""
        data_with_symbol = self.request_result
        self.cvObject.extract_fiat_balance(data_with_symbol)
        print(data_with_symbol)
        report_fiat = "Z" + self.cvObject.report_currency

        assert report_fiat in self.cvObject.currencies['fiat']
        for fiat_symbol in self.cvObject.currencies['fiat']:
            if fiat_symbol != report_fiat:
                assert fiat_symbol in data_with_symbol
    
    def test_extract_crypto_balance(self):
        """Test of extract_crypto_balance function :
            crypto symbols should match with raw data from Krakenex API"""
        data_with_symbol = self.request_result
        self.cvObject.extract_crypto_balance(data_with_symbol)
        print(data_with_symbol)

        for crypto_symbol in self.cvObject.currencies['crypto']:
            assert crypto_symbol in data_with_symbol

    def test_getXBTtoFiatPrice_usd(self):
        """Test of get price function from XBT -> USD"""
        usd_price = self.krakenex.query_public('Ticker', {'pair': "XBT" + 'USD', })['result']['XXBTZUSD']['c'][0]
        assert abs(float(self.cvObject.getXBTtoFiatPrice('USD')) - float(usd_price)) < self.DELTA
        
    def test_getXBTtoFiatPrice_eur(self):
        """Test of get price function from XBT -> EUR"""
        eur_price = self.krakenex.query_public('Ticker', {'pair': "XBT" + 'EUR', })['result']['XXBTZEUR']['c'][0]
        assert abs(float(self.cvObject.getXBTtoFiatPrice('EUR')) - float(eur_price)) < self.DELTA

    def test_getMarketPrice_ada(self):
        """Test of get price function from ADA -> XBT"""
        ada_xbt_price = self.krakenex.query_public('Ticker', {'pair': 'ADA' + 'XBT', })['result']['ADAXBT']['c'][0]
        assert abs(float(self.cvObject.getMarketPrice('ADA')[0]) - float(ada_xbt_price)) < self.DELTA

    def test_getMarketPrice_eos(self):
        """Test of get price function from EOS -> XBT"""
        eos_xbt_price = self.krakenex.query_public('Ticker', {'pair': 'EOS' + 'XBT', })['result']['EOSXBT']['c'][0]
        assert abs(float(self.cvObject.getMarketPrice('EOS')[0]) - float(eos_xbt_price)) < self.DELTA

    def test_getMarketPrice_eth(self):
        """Test of get price function from ETH -> XBT"""
        eth_xbt_price = self.krakenex.query_public('Ticker', {'pair': 'ETH' + 'XBT', })['result']['XETHXXBT']['c'][0]
        market_prices = self.cvObject.getMarketPrice('ETH')
        print(eth_xbt_price)
        print(eth_market_price)
        assert abs(float(market_prices[0]) - float(eth_xbt_price)) < self.DELTA

    def test_getMarketPrice_dash(self):
        """Test of get price function from DASH -> XBT"""
        dash_xbt_price = self.krakenex.query_public('Ticker', {'pair': 'DASH' + 'XBT', })['result']['DASHXBT']['c'][0]
        assert abs(float(self.cvObject.getMarketPrice('DASH')[0]) - float(dash_xbt_price)) < self.DELTA

    def test_updateFiatInTotal_usd_functional(self):  # Module Test (not unitary)
        """Test of process and update Total dict file {fiat : total_xbt_in_fiat_price}"""
        self.cvObject.updateFiatInTotal('USD')

        assert 'USD' in self.cvObject.fiatbtc_pair.keys()
        assert abs(float(self.cvObject.fiatbtc_pair['USD']) - float(self.cvObject.getXBTtoFiatPrice('USD'))) < self.DELTA
        assert self.cvObject.total['USD'] >= 0

    def test_updateFiatInTotal_usd_10_btc(self):  # Module Test (not unitary)
        """Test of process and update Total dict file {fiat : total_xbt_in_fiat_price}
        with 10 btc"""
        self.cvObject.btc_total = 10
        self.cvObject.updateFiatInTotal('USD')

        assert abs(self.cvObject.total['USD'] - self.cvObject.btc_total * float(self.cvObject.getXBTtoFiatPrice('USD'))) < self.DELTA

    def test_updateFiatInTotal_usd_0_btc(self):  # Module Test (not unitary)
        """Test of process and update Total dict file {fiat : total_xbt_in_fiat_price}
        with 0 btc"""
        self.cvObject.btc_total = 0
        self.cvObject.updateFiatInTotal('USD')

        assert abs(self.cvObject.total['USD'] - self.cvObject.btc_total * float(self.cvObject.getXBTtoFiatPrice('USD'))) < self.DELTA

    def test_updateFiatInTotal_eur_functional(self):  # Module Test (not unitary)
        """Test of process and update Total dict file {fiat : total_xbt_in_fiat_price}"""
        self.cvObject.updateFiatInTotal('EUR')

        assert 'EUR' in self.cvObject.fiatbtc_pair.keys()
        assert abs(float(self.cvObject.fiatbtc_pair['EUR']) - float(self.cvObject.getXBTtoFiatPrice('EUR'))) < self.DELTA
        assert self.cvObject.total['EUR'] >= 0

    def test_updateFiatInTotal_eur_10_btc(self):  # Module Test (not unitary)
        """Test of process and update Total dict file {fiat : total_xbt_in_fiat_price}
        with 10 btc"""
        self.cvObject.btc_total = 10
        self.cvObject.updateFiatInTotal('EUR')

        assert abs(self.cvObject.total['EUR'] - self.cvObject.btc_total * float(self.cvObject.getXBTtoFiatPrice('EUR'))) < self.DELTA

    def test_updateFiatInTotal_eur_0_btc(self):  # Module Test (not unitary)
        """Test of process and update Total dict file {fiat : total_xbt_in_fiat_price}
        with 0 btc"""
        self.cvObject.btc_total = 0
        self.cvObject.updateFiatInTotal('EUR')

        assert abs(self.cvObject.total['EUR'] - self.cvObject.btc_total * float(self.cvObject.getXBTtoFiatPrice('EUR'))) < self.DELTA