#!/usr/bin/env python3
import asyncio
from utils.logger import print_log
from config import config
import danmaku_event


def main():
    live_danmaku = config.get_live_danmaku()

    # 弹幕事件回调
    live_danmaku.add_event_listener(
        name='GUARD_BUY', handler=danmaku_event.guard_buy)
    live_danmaku.add_event_listener(
        name='SEND_GIFT', handler=danmaku_event.send_gift)
    live_danmaku.add_event_listener(
        name='COMBO_SEND', handler=danmaku_event.combo_send)
    live_danmaku.add_event_listener(
        name='SUPER_CHAT_MESSAGE', handler=danmaku_event.super_chat_message)
    live_danmaku.add_event_listener(
        name='LIVE', handler=danmaku_event.live_start)
    live_danmaku.add_event_listener(
        name='PREPARING', handler=danmaku_event.live_end)
    live_danmaku.add_event_listener(
        name='ROOM_BLOCK_MSG', handler=danmaku_event.room_block_msg)

    # 可选功能列表
    function_list = config.get_optfunc()
    # 可选功能 不受欢迎的用户提示
    if function_list['not_wellcome']:
        print_log('不受欢迎用户提示功能已打开')
        live_danmaku.add_event_listener(
            name='INTERACT_WORD', handler=danmaku_event.danmaku_event.not_welcome)

    if function_list['debug']:
        @live_danmaku.on('ALL')
        async def 调试信息(info):
            print(info['data']['cmd'])
    asyncio.get_event_loop().run_until_complete(live_danmaku.connect())


if __name__ == '__main__':
    print('B站直播场控系统v0.2')
    main()
