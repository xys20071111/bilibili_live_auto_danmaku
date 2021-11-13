import json
import sys
from bilibili_api import Credential, live


class __Config:
    def __init__(self, conf_path: str) -> None:
        with open(conf_path, mode='r', encoding='utf8') as f:
            config = json.load(f)
            self.__room_id = config['room_id']
            credential = config['verify']
            self.__credential = Credential(
                sessdata=credential['sessdata'], bili_jct=credential['csrf'], buvid3=credential['buvid3'])
            self.__optfunc = config['optional_function']
            self.__danmaku_cold_down = config['cold_down_time']
            self.__danmakus = config['danmakus']
            self.__liveroom = live.LiveRoom(
                room_display_id=config['room_id'], credential=self.__credential)
            self.__livedanmaku = live.LiveDanmaku(
                room_display_id=config['room_id'], credential=self.__credential, max_retry=1145141919810, retry_after=2)
            self.__advertising_cold_down = config['advertising_cold_down']

    def get_room_id(self) -> int:
        return self.__room_id

    def get_credential(self) -> Credential:
        return self.__credential

    def get_optfunc(self) -> dict:
        return self.__optfunc

    def get_danmaku_cold_down_time(self) -> int:
        return self.__danmaku_cold_down

    def get_danmakes(self) -> dict:
        return self.__danmakus

    def get_live_room(self) -> live.LiveRoom:
        return self.__liveroom

    def get_live_danmaku(self) -> live.LiveDanmaku:
        return self.__livedanmaku

    def get_advertising_cold_down(self) -> int:
        return self.__advertising_cold_down



DEFAULT_CONFIG_PATH = './config.json'

global config
if len(sys.argv) > 1:  
    config = __Config(sys.argv[1])
else:
    config = __Config(DEFAULT_CONFIG_PATH)


print('配置加载完毕')
