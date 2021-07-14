import threading
import time
import json
from bilibili_api import live
from bilibili_api.utils.Danmaku import Danmaku
from utils.logger import print_log
from utils.send_danmaku import send_danmaku

class guard_advertsing(threading.Thread):

    def __init__(self,credential,room_id):
        super().__init__(daemon=True)
        self.credential= credential
        self.room_id = room_id
        self._liveroom = live.LiveRoom(room_display_id=self.room_id,credential=credential)
        self.is_living = False
        with open('guard_advertsing_config.json',mode='r',encoding='utf8') as f:
            self.config = json.load(f)
        self._lock = threading.Lock()
        print_log('宣传语模块初始化完毕')

    def run(self):
        while True:
            self._lock.acquire()
            if self.is_living:
                send_danmaku(self.config['advertise'],self._liveroom).send(None)
                print_log('发送宣传语')
            self._lock.release()
            time.sleep(self.config['interval'])

    def live_start(self):
        self._lock.acquire()
        self.is_living = True
        self._lock.release()

    def live_end(self):
        self._lock.acquire()
        self.is_living = False
        self._lock.release()

