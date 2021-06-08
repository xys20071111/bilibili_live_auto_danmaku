"""
模块损坏，无法正常工作
"""
import asyncio
import threading
import time
import json
from bilibili_api import live
from bilibili_api.utils.Danmaku import Danmaku
from utils.logger import print_log

class guard_advertsing(threading.Thread):

    def __init__(self,credential,room_id):
        super().__init__(daemon=True)
        self.credential= credential
        self.room_id = room_id
        with open('guard_advertsing_config.json',mode='r',encoding='utf8') as f:
            self.config = json.load(f)
        print_log('宣传语模块初始化完毕')

    def run(self):
        while True:
            loop = asyncio.new_event_loop()
            liveroom = live.LiveRoom(room_display_id=self.room_id)
            task = loop.create_task(liveroom.get_room_play_info())
            loop.run_until_complete(task)
            room_info = task.result()
            if room_info['live_status'] == 1:
                text=self.config['advertise']
                dan = Danmaku(text=text)
                asyncio.run_coroutine_threadsafe(self.liveroom.send_danmaku(danmaku=dan),loop)
                print_log('发送宣传语')
            time.sleep(self.config['interval'])

    def live_start(self):
        self.is_living = True

    def live_end(self):
        self.is_living = False

