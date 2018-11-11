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
        report_fiat = "Z" + self.cvObject.default_currency

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

    def test_get_fiat_price_in_btc_usd(self):
        """Test of get price function from XBT -> USD"""
        usd_price = self.krakenex.query_public('Ticker', {'pair': "XBT" + 'USD', })['result']['XXBTZUSD']['c'][0]
        assert abs(float(self.cvObject.get_fiat_price_in_btc('USD')) - float(usd_price)) < self.DELTA
        
    def test_get_fiat_price_in_btc_eur(self):
        """Test of get price function from XBT -> EUR"""
        eur_price = self.krakenex.query_public('Ticker', {'pair': "XBT" + 'EUR', })['result']['XXBTZEUR']['c'][0]
        assert abs(float(self.cvObject.get_fiat_price_in_btc('EUR')) - float(eur_price)) < self.DELTA

    def test_get_crypto_price_in_btc_ada(self):
        """Test of get price function from ADA -> XBT"""
        ada_xbt_price = self.krakenex.query_public('Ticker', {'pair': 'ADA' + 'XBT', })['result']['ADAXBT']['c'][0]
        assert abs(float(self.cvObject.get_crypto_price_in_btc('ADA')[0]) - float(ada_xbt_price)) < self.DELTA

    def test_get_crypto_price_in_btc_eos(self):
        """Test of get price function from EOS -> XBT"""
        eos_xbt_price = self.krakenex.query_public('Ticker', {'pair': 'EOS' + 'XBT', })['result']['EOSXBT']['c'][0]
        assert abs(float(self.cvObject.get_crypto_price_in_btc('EOS')[0]) - float(eos_xbt_price)) < self.DELTA

    def test_get_crypto_price_in_btc_eth(self):
        """Test of get price function from ETH -> XBT"""
        eth_xbt_price = self.krakenex.query_public('Ticker', {'pair': 'ETH' + 'XBT', })['result']['XETHXXBT']['c'][0]
        market_prices = self.cvObject.get_crypto_price_in_btc('ETH')
        print(eth_xbt_price)
        print(eth_market_price)
        assert abs(float(market_prices[0]) - float(eth_xbt_price)) < self.DELTA

    def test_get_crypto_price_in_btc_dash(self):
        """Test of get price function from DASH -> XBT"""
        dash_xbt_price = self.krakenex.query_public('Ticker', {'pair': 'DASH' + 'XBT', })['result']['DASHXBT']['c'][0]
        assert abs(float(self.cvObject.getMarketPrice('DASH')[0]) - float(dash_xbt_price)) < self.DELTA

    def test_update_fiat_amount_in_total_usd_functional(self):  # Module Test (not unitary)
        """Test of process and update Total dict file {fiat : total_xbt_in_fiat_price}"""
        self.cvObject.update_fiat_amount_in_total('USD')
        assert 'USD' in self.cvObject.fiatbtc_pair.keys()
        assert abs(float(self.cvObject.fiatbtc_pair['USD']) - float(self.cvObject.get_fiat_price_in_btc('USD'))) < self.DELTA
        assert self.cvObject.total['USD'] >= 0

    def test_update_fiat_amount_in_total_usd_10_btc(self):  # Module Test (not unitary)
        """Test of process and update Total dict file {fiat : total_xbt_in_fiat_price}
        with 10 btc"""
        self.cvObject.btc_total = 10
        self.cvObject.update_fiat_amount_in_total('USD')
        assert abs(self.cvObject.total['USD'] - self.cvObject.btc_total * float(self.cvObject.get_fiat_price_in_btc('USD'))) < self.DELTA
  
    def test_update_fiat_amount_in_total_usd_0_btc(self):  # Module Test (not unitary)
        """Test of process and update Total dict file {fiat : total_xbt_in_fiat_price}
        with 0 btc"""
        self.cvObject.btc_total = 0
        self.cvObject.update_fiat_amount_in_total('USD')
        assert abs(self.cvObject.total['USD'] - self.cvObject.btc_total * float(self.cvObject.get_fiat_price_in_btc('USD'))) < self.DELTA
        
    def test_update_fiat_amount_in_total_eur_functional(self):  # Module Test (not unitary)
        """Test of process and update Total dict file {fiat : total_xbt_in_fiat_price}"""
        self.cvObject.update_fiat_amount_in_total('EUR')
        assert 'EUR' in self.cvObject.fiatbtc_pair.keys()
        assert abs(float(self.cvObject.fiatbtc_pair['EUR']) - float(self.cvObject.get_fiat_price_in_btc('EUR'))) < self.DELTA
        assert self.cvObject.total['EUR'] >= 0

    def test_update_fiat_amount_in_total_eur_10_btc(self):  # Module Test (not unitary)
        """Test of process and update Total dict file {fiat : total_xbt_in_fiat_price}
        with 10 btc"""
        self.cvObject.btc_total = 10
        self.cvObject.update_fiat_amount_in_total('EUR')
        assert abs(self.cvObject.total['EUR'] - self.cvObject.btc_total * float(self.cvObject.get_fiat_price_in_btc('EUR'))) < self.DELTA

    def test_update_fiat_amount_in_total_eur_0_btc(self):  # Module Test (not unitary)
        """Test of process and update Total dict file {fiat : total_xbt_in_fiat_price}
        with 0 btc"""
        self.cvObject.btc_total = 0
        self.cvObject.update_fiat_amount_in_total('EUR')
        assert abs(self.cvObject.total['EUR'] - self.cvObject.btc_total * float(self.cvObject.get_fiat_price_in_btc('EUR'))) < self.DELTA

