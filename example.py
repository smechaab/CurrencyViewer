# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 20:11:34 2017

@author: smechaab
"""
import CurrencyViewer as cv

a = cv.CurrencyViewer()
a.processCViewer(log=True, currency="USD", time="rfc1123") #time format: unixtime or rfc1123
