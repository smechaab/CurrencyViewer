import unittest
import krakenex
from currency_viewer import currency_viewer as cv


class ProcessTest(unittest.TestCase):

    """TestCase for process of data processing."""

    def setUp(self):
        """Test init"""
        self.cvObject = cv.CurrencyViewer()
        self.krakenex = krakenex.API()
        self.krakenex.load_key('kraken.key')

    def test_collectData_crypto(self):
        """Test of collectData function :
            crypto symbols should match with raw data from Krakenex API"""
        data, crypto_index, fiat_index = self.cvObject.collectData()
        data_with_symbol = data['result']
        print(data_with_symbol)

        for crypto_symbol in crypto_index:
            self.assertIn(crypto_symbol, data_with_symbol)

    def test_collectData_fiat(self):
        """Test of collectData function :
            fiat symbols should match with raw data from Krakenex API"""
        data, crypto_index, fiat_index = self.cvObject.collectData()
        data_with_symbol = data['result']
        print(data_with_symbol)

        for fiat_symbol in fiat_index:
            self.assertIn(fiat_symbol, data_with_symbol)

    def test_getXBTtoFiatPrice_usd(self):
        """Test of get price function from XBT -> USD"""
        usd_price = self.krakenex.query_public('Ticker', {'pair': "XBT" + 'USD', })['result']['XXBTZUSD']['c'][0]
        self.assertAlmostEqual(float(self.cvObject.getXBTtoFiatPrice('USD')), float(usd_price))

    def test_getXBTtoFiatPrice_eur(self):
        """Test of get price function from XBT -> EUR"""
        eur_price = self.krakenex.query_public('Ticker', {'pair': "XBT" + 'EUR', })['result']['XXBTZEUR']['c'][0]
        self.assertAlmostEqual(float(self.cvObject.getXBTtoFiatPrice('EUR')), float(eur_price))

    def test_getMarketPrice_ada(self):
        """Test of get price function from ADA -> XBT
        assertAlmostEqual compares rounded values with reduced decimal places to 5 (default is 7)"""
        ada_xbt_price = self.krakenex.query_public('Ticker', {'pair': 'ADA' + 'XBT', })['result']['ADAXBT']['c'][0]
        self.assertAlmostEqual(float(self.cvObject.getMarketPrice('ADA')[0]), float(ada_xbt_price), places=5)

    def test_getMarketPrice_eos(self):
        """Test of get price function from EOS -> XBT
        assertAlmostEqual compares rounded values with reduced decimal places to 5 (default is 7)"""
        eos_xbt_price = self.krakenex.query_public('Ticker', {'pair': 'EOS' + 'XBT', })['result']['EOSXBT']['c'][0]
        self.assertAlmostEqual(float(self.cvObject.getMarketPrice('EOS')[0]), float(eos_xbt_price), places=5)

    def test_getMarketPrice_eth(self):
        """Test of get price function from ETH -> XBT
        assertAlmostEqual compares rounded values with reduced decimal places to 5 (default is 7)"""
        eth_xbt_price = self.krakenex.query_public('Ticker', {'pair': 'ETH' + 'XBT', })['result']['XETHXXBT']['c'][0]
        self.assertAlmostEqual(float(self.cvObject.getMarketPrice('ETH')[0]), float(eth_xbt_price), places=5)

    def test_getMarketPrice_dash(self):
        """Test of get price function from DASH -> XBT
        assertAlmostEqual compares rounded values with reduced decimal places to 5 (default is 7)"""
        dash_xbt_price = self.krakenex.query_public('Ticker', {'pair': 'DASH' + 'XBT', })['result']['DASHXBT']['c'][0]
        self.assertAlmostEqual(float(self.cvObject.getMarketPrice('DASH')[0]), float(dash_xbt_price), places=5)

    def test_updateFiatInTotal_usd_functional(self):  # Module Test (not unitary)
        """Test of process and update Total dict file {fiat : total_xbt_in_fiat_price}"""
        self.cvObject.updateFiatInTotal('USD')

        self.assertIn('USD', self.cvObject.fiatbtc_pair.keys())
        self.assertAlmostEqual(float(self.cvObject.fiatbtc_pair['USD']), float(self.cvObject.getXBTtoFiatPrice('USD')))
        self.assertGreaterEqual(self.cvObject.total['USD'], 0)

    def test_updateFiatInTotal_usd_10_btc(self):  # Module Test (not unitary)
        """Test of process and update Total dict file {fiat : total_xbt_in_fiat_price}
        with 10 btc"""
        self.cvObject.btc_total = 10
        self.cvObject.updateFiatInTotal('USD')

        self.assertAlmostEqual(self.cvObject.total['USD'],
                               self.cvObject.btc_total * float(self.cvObject.getXBTtoFiatPrice('USD')))

    def test_updateFiatInTotal_usd_0_btc(self):  # Module Test (not unitary)
        """Test of process and update Total dict file {fiat : total_xbt_in_fiat_price}
        with 0 btc"""
        self.cvObject.btc_total = 0
        self.cvObject.updateFiatInTotal('USD')

        self.assertAlmostEqual(self.cvObject.total['USD'],
                               self.cvObject.btc_total * float(self.cvObject.getXBTtoFiatPrice('USD')))

    def test_updateFiatInTotal_eur_functional(self):  # Module Test (not unitary)
        """Test of process and update Total dict file {fiat : total_xbt_in_fiat_price}"""
        self.cvObject.updateFiatInTotal('EUR')

        self.assertIn('EUR', self.cvObject.fiatbtc_pair.keys())
        self.assertAlmostEqual(float(self.cvObject.fiatbtc_pair['EUR']), float(self.cvObject.getXBTtoFiatPrice('EUR')))
        self.assertGreaterEqual(self.cvObject.total['EUR'], 0)

    def test_updateFiatInTotal_eur_10_btc(self):  # Module Test (not unitary)
        """Test of process and update Total dict file {fiat : total_xbt_in_fiat_price}
        with 10 btc"""
        self.cvObject.btc_total = 10
        self.cvObject.updateFiatInTotal('EUR')

        self.assertAlmostEqual(self.cvObject.total['EUR'],
                               self.cvObject.btc_total * float(self.cvObject.getXBTtoFiatPrice('EUR')))

    def test_updateFiatInTotal_eur_0_btc(self):  # Module Test (not unitary)
        """Test of process and update Total dict file {fiat : total_xbt_in_fiat_price}
        with 0 btc"""
        self.cvObject.btc_total = 0
        self.cvObject.updateFiatInTotal('EUR')

        self.assertAlmostEqual(self.cvObject.total['EUR'],
                               self.cvObject.btc_total * float(self.cvObject.getXBTtoFiatPrice('EUR')))

