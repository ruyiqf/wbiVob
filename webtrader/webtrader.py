#coding: utf-8
import logging
import os
import re
import time

from threading import Thread
from log import log

class WebTrader(object):
    """Base wbi trader interface"""
    global_config_path = os.path.dirname(__file__) + '/conf/global.json'
    config_path = ''

    def __init__(self):
        self.__read_config()
        self.trade_prefix = self.config['prefix']
        self.account_config = ''
        self.heart_active = True
        self.heart_thread = Thread(target=self.send_heartbeat)
        self.heart_thread.setDaemon(True)

    def read_config(self, path):
        try:
            self.account_config = helpers.file2dict(path)
        except ValueError:
            log.error('Config file format of configuration has errors')

    def prepare(self, need_data):
        """Virtual function entrance of login
        :need_data: data which login need
        """
        self.read_config(need_data)
        self.autologin()

    def autologin(self, limit=5):
        """Auto login
        :limit: numbers of login
        """
        for _ in range(limit):
            if self.login():
                break
        else:
            raise NotLoginError('Login failed pls check config/broker status/connection of internet')
        self.keepalive()

    def login(self):
        """Virtul function need be heritted"""
        pass

    def keepalive(self):
        """Maintain alive tatus for process"""
        if self.heart_thread.is_alive():
            self.heart_active = True
        else:
            self.heart_thread.start()

    def send_heartbeat(self):
        """Sending heartbeat packet in order to keep alive
        1) if special requirement, need be herrited othrewise using default activity
        2) Default time interval is 300 seconds
        """
        while True:
            if self.heart_active:
                try:
                    log_level = log.level
                    log.setLevel(logging.ERROR)
                    self.heartbeat()
                    log.setLevel(log_level)
                except:
                    self.autologin()
                time.sleep(300)
            else:
                time.sleep(1)

    def heartbeat(self): 
        return self.balance

    def exit(self):
        """Over process"""
        self.heart_active = False

    def __read_config(self):
        """Read config file"""
        self.config = helpers.file2dict(self.config_path)
        self.global_config = helpers.file2dict(self.global_config_path)
        self.config.update(self.global_config)

    @property
    def balance(self):
        return self.get_balance()

    def get_balance(self):
        return self.do(self.config['balance'])

    @property
    def position(self):
        return self.get_position()

    def get_position(self):
        return self.do(self.config['position'])

    @property
    def entrust(self):
        return self.get_entrust()

    def get_entrust(self):
        """Get current day entrust list"""
        return self.do(self.config['entrust'])

    def do(self, params):
        """Spawn request which is common function
        :params: exchang dynamic parameters"""
        request_params = self.create_basic_params()
        request_params.update(params)
        response_data = self.request(request_params)
        try:
            format_json_data = self.format_response_data(response_data)
        except:
            # Caused by server force logged out
            return None
        return_data = self.fix_error_data(format_json_data)
        try:
            self.check_login_status(return_data)
        except NotLoginError:
            self.autologin()
        return return_data

    def create_basic_params(self):
        """Generate basic parameters"""
        pass

    def request(self, params):
        """Send request and fetch data of json
        :params: parameters"""
        pass

def main():
    print('euxyacg')
    wt = WebTrader()

if __name__ == '__main__':
    main()

