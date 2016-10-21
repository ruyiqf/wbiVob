#coding: utf-8
from __future__ import division

import os
import random
import re
import tempfile
from .webtrader import  WebTrader
from .log import log

import requests

class PaTrader(WebTrader):
    config_path = os.path.dirname(__file__) + '/conf/pa.json'

    def __init__(self):
        super(PaTrader, self).__init__()
        self.s = None

    def login(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
        }
        self.s = requests.session()
        self.s.headers.update(headers)
        verify_code = self.__handle_recognize_code() 
        print(verify_code)
        if not verify_code:
            return False
        is_login, result = self.__check_login_status(verify_code)
        if not is_login:
            if throw:
                raise NotLoginError(result)
            return False
        return True
     
    def __handle_recognize_code(self):
        verify_code_response = self.s.get(self.config['verify_code_api'])
        image_path = os.path.join(tempfile.gettempdir(), 'vcode_%d' % os.getpid())
        with open(image_path, 'wb') as f:
            f.write(verify_code_response.content)
        verify_code = self.detect_pa_verifycode(image_path)
        os.remove(image_path)
        return verify_code

    def detect_pa_verifycode(self, image_path):
        from PIL import ImageFilter, Image
        import pytesseract
        img = Image.open(image_path)
        brightness = list()
        for x in range(img.width):
            for y in range(img.height):
                (r,g,b) = img.getpixel((x,y))
                brightness.append(r + g + b)
        avg_brightness = sum(brightness) // len(brightness)

        for x in range(img.width):
            for y in range(img.height):
                (r,g,b) = img.getpixel((x,y))
                if ((r + g + b) > avg_brightness / 1.5) or (y < 3) or (y > 17) or (x < 5) or (x > (img.width - 5)):
                    img.putpixel((x, y), (256, 256, 256))
        return pytesseract.image_to_string(img)

    def __check_login_status(self, verify_code):
        params = dict(
            fund_account=self.account_config['fund_account'],
            password=self.account_config['password'],
            ticket=verify_code
        )
        params.update(self.config['login'])
        print('euxyacg')
        print(params)
        log.debug('login params: %s' % params)
        login_api_response = self.s.post(self.config['login_api'], params)
        print(login_api_response.text)
        return True, None

     
