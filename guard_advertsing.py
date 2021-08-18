##############################
#                            #
#          模块测试中          #
#                            #
##############################
import asyncio
from utils.logger import print_log
from config import config
from utils.send_danmaku import send_danmaku
from utils.logger import print_log

LIVEROOM = config.get_live_room()
ADVERTISE = config.get_danmakes()['advertisment']
COLD_DOWN = config.get_advertising_cold_down()
print_log('宣传语模块初始化完毕')

async def guard_advertsing():
    while True:
        if (await LIVEROOM.get_room_info())['room_info']['live_status'] == 1:
            await send_danmaku(ADVERTISE,LIVEROOM)
            print_log('发送宣传语')
        await asyncio.sleep(COLD_DOWN)
