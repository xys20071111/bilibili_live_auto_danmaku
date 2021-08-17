import json
import sys
from bilibili_api import Credential, live


class _Config:
    def __init__(self, room_id: int, credential: dict, optfunc: dict, danmaku_cold_down: int, danmakus: dict) -> None:
        self._room_id = room_id
        self._credential = Credential(
            sessdata=credential['sessdata'], bili_jct=credential['csrf'], buvid3=credential['buvid3'])
        self._optfunc = optfunc
        self._danmaku_cold_down = danmaku_cold_down
        self._danmakus = danmakus
        self._liveroom = live.LiveRoom(
            room_display_id=room_id, credential=self._credential)
        self._livedanmaku = live.LiveDanmaku(
            room_display_id=room_id, credential=self._credential)

    def get_room_id(self) -> int:
        return self._room_id

    def get_credential(self) -> Credential:
        return self._credential

    def get_optfunc(self) -> dict:
        return self._optfunc

    def get_danmaku_cold_down_time(self) -> int:
        return self._danmaku_cold_down

    def get_danmakes(self) -> dict:
        return self._danmakus

    def get_live_room(self) -> live.LiveRoom:
        return self._liveroom

    def get_live_danmaku(self) -> live.LiveDanmaku:
        return self._livedanmaku


config_path = './config.json'
def read_arg(argv):
    if len(argv) > 1:
        global config_path
        config_path = argv[1]

read_arg(sys.argv)
config_file = open(config_path, mode='r', encoding='utf8')
config_json = json.load(config_file)
config_file.close()

config = _Config(room_id=config_json['room_id'], credential=config_json['verify'], optfunc=config_json['optional_function'],
                 danmaku_cold_down=config_json['cold_down_time'], danmakus=config_json['danmakus'])
print('配置加载完毕')