from setuptools import setup
import os

setup(name = 'currency_viewer',
      version = '0.2.1',
      author = 'Semy Mechaab',
      author_email = 's.mechaab@protonmail.com',
      maintainer = 'Semy Mechaab',
      maintainer_email = 's.mechaab@protonmail.com',
      keywords = 'cryptocurrencies kraken wallet bitcoin api converter currency exchange csv-files module package',
      packages = ['currency_viewer'],
      description = 'Currency Viewer is a Kraken exchange framework',
      long_description = open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
      license = 'GPL V3',
      platforms = 'ALL',
      url = 'https://github.com/smechaab/CurrencyViewer',
      install_requires = ['krakenex>=2.1.0']
      )
