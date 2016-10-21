# coding=utf-8
import logging

from .patrader import PaTrader

def use(broker, debug=True, **kwargs):
    """用于生成特定的券商对象
    """
    if broker.lower() in ['pa']:
        return PaTrader()
