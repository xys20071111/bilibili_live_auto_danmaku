import asyncio
import threading
import time
import json
from bilibili_api import live
from bilibili_api.utils.Danmaku import Danmaku
from utils.logger import print_log

class guard_advertsing(threading.Thread):

    def __init__(self,credential,room,room_info):
        super().__init__(daemon=True)
        self.credential= credential
        self.liveroom = room
        with open('guard_advertsing_config.json',mode='r',encoding='utf8') as f:
            self.config = json.load(f)
        status = room_info['live_status']
        if status == 0:
            self.is_living = False
        else:
            self.is_living = True
        print_log('宣传语模块初始化完毕')

    def run(self):
        while True:
            if self.is_living:
                text=self.config['advertise']
                dan = Danmaku(text=text)
                loop = asyncio.new_event_loop()
                asyncio.run_coroutine_threadsafe(self.liveroom.send_danmaku(danmaku=dan),loop)
                print_log('发送宣传语')
            time.sleep(self.config['interval'])

    def live_start(self):
        self.is_living = True

    def live_end(self):
        self.is_living = False

