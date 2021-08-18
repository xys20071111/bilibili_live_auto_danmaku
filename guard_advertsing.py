##############################
#                            #
#          模块测试中          #
#                            #
##############################
import asyncio
from utils.logger import print_log
from config import config
from utils.send_danmaku import send_danmaku

LIVEROOM = config.get_live_room()
ADVERTISE = config.get_danmakes()['advertisment']
COLD_DOWN = config.get_advertising_cold_down()
print_log('宣传语模块初始化完毕')

async def guard_advertsing():
    is_living:bool = (await LIVEROOM.get_room_info())['room_info']['live_status'] == 1
    if is_living:
        await send_danmaku(ADVERTISE,LIVEROOM)
    await asyncio.sleep(COLD_DOWN)
