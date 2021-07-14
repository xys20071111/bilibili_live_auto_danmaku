#!/usr/bin/python3
import asyncio
import json
import time
from bilibili_api import live, Credential
from bilibili_api.utils import Danmaku
from utils.logger import print_log
from utils.send_danmaku import send_danmaku
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class not_thanks_user(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        with open('user_not_thanks.json', mode='r', encoding='utf8') as f:
            self.list = json.load(f)
        print_log('不感谢用户列表已加载')

    def on_modified(self, event):
        with open('user_not_thanks.json', mode='r', encoding='utf8') as f:
            self.list = json.load(f)
        print_log('不感谢用户列表已更新')


def main():
    print_log("弹幕冷却时间:{}".format(config['cold_down_time']))
    # 解析验证信息
    verify_info = config['verify']
    # 创建验证数据
    verify = Credential(sessdata=verify_info['sessdata'],
                        bili_jct=verify_info['csrf'],
                        buvid3=verify_info['buvid3'])
    display_room_id = int(config['room_id'])
    # 解析房间信息
    liveroom = live.LiveRoom(
        room_display_id=display_room_id, credential=verify)
    # 由于bilibili_api的全异步操作，调用asyncio
    loop = asyncio.get_event_loop()
    task = loop.create_task(liveroom.get_room_play_info())
    loop.run_until_complete(task)
    room_info = task.result()
    room_real_id = room_info['room_id']
    # 连接到房间弹幕
    global live_danmaku
    live_danmaku = live.LiveDanmaku(room_real_id)
    # 激活 不感谢用户列表 的实时更新（有问题）
    not_thanks_user_watcher = Observer()
    ntu = not_thanks_user()
    not_thanks_user_watcher.schedule(
        ntu, './user_not_thanks.json', True)
    not_thanks_user_watcher.start()
    # 弹幕事件回调

    @live_danmaku.on('GUARD_BUY')
    async def 感谢舰长(info):
        data = info['data']['data']
        user_nickname = data['username']
        text = config['danmakus']['guard'].format(name=user_nickname)
        if not data['uid'] in ntu.list:
            await send_danmaku(text=text, liveroom=liveroom)
        print_log('{}购买了舰长'.format(user_nickname))
    # 以下为感谢礼物的逻辑
    cold_time = {'last_cold_down': -1}
    lock = asyncio.Lock()

    @live_danmaku.on('SEND_GIFT')
    async def 感谢礼物(info):
        data = info['data']['data']
        user_nickname = data['uname']
        gift_name = data['giftName']
        gift_num = data['super_gift_num']
        text = config['danmakus']['gift'].format(
            name=user_nickname, gift=gift_name)
        log_text = '{name}投喂了{count}个{gift}'.format(
            name=user_nickname, count=gift_num, gift=gift_name)
        print_log(log_text)
        await lock.acquire()
        if lock.locked():
            if (cold_time['last_cold_down'] + config['cold_down_time']) < int(time.time()) or cold_time['last_cold_down'] == -1:
                if not data['uid'] in ntu.list:
                    await send_danmaku(text=text, liveroom=liveroom)
                    cold_time['last_cold_down'] = time.time()
            lock.release()
    # 以上为感谢礼物的逻辑

    @live_danmaku.on('COMBO_SEND')
    async def 礼物连击(info):
        data = info['data']['data']
        user_nickname = data['uname']
        gift_name = data['gift_name']
        gift_count = data['total_num']
        text = config['danmakus']['gift_total'].format(
            name=user_nickname, count=gift_count, gift=gift_name)
        print_log(text)
        if not data['uid'] in ntu.list:
            await send_danmaku(text=text, liveroom=liveroom)

    @live_danmaku.on('SUPER_CHAT_MESSAGE')
    async def 感谢SC(info):
        data = info['data']['data']
        user_nickname = data['user_info']['uname']
        text = config['danmakus']['sc'].format(name=user_nickname)
        if not data['uid'] in ntu.list:
            await send_danmaku(text=text, liveroom=liveroom)
        print_log('感谢{}的SC'.format(user_nickname))

    @live_danmaku.on('LIVE')
    async def 直播开始(useless_arg):
        dan = Danmaku.Danmaku(config['danmakus']['live_start'])
        await liveroom.send_danmaku(danmaku=dan)
        print_log('直播开始')

    @live_danmaku.on('PREPARING')
    async def 直播结束(useless_arg):
        dan = Danmaku.Danmaku(config['danmakus']['live_end'])
        await liveroom.send_danmaku(danmaku=dan)
        print_log('直播结束')
        # ga.live_end()

    @live_danmaku.on('ROOM_BLOCK_MSG')
    async def 有人被禁言(info):
        data = info['data']['data']
        print_log('用户 {} uid:{} 被禁言'.format(data['uname'], data['uid']))

    # 可选功能列表
    function_list = config['optional_function']
    # 可选功能 不受欢迎的用户提示
    if function_list['not_wellcome']:
        print_log('不受欢迎用户提示功能已打开')

        @live_danmaku.on('INTERACT_WORD')
        async def 不受欢迎的人通知(info):
            data = info['data']['data']
            with open('./user_not_welcome.json', mode='r', encoding='utf8') as f:
                black_list = json.load(f)
                if data['uid'] in black_list:
                    text = config['danmakus']['unwelcome'].format(
                        name=data['uname'])
                    dan = Danmaku.Danmaku(text=text)
                    await liveroom.send_danmaku(danmaku=dan)
                    print_log('不受欢迎的用户{}进入'.format(data['uname']))
    if function_list['debug']:
        @live_danmaku.on('ALL')
        async def 调试信息(info):
            print(info['data']['cmd'])
    if function_list['guard_adveritse']:
        from guard_advertsing import guard_advertsing
        # 初始化 宣传语模块
        ga = guard_advertsing(credential=verify, room_id=room_real_id)
        ga.start()

        @live_danmaku.on('LIVE')
        async def 宣传开始(useless_arg):
            ga.live_start()

        @live_danmaku.on('PREPARING')
        async def 宣传结束():
            ga.live_end()

    asyncio.get_event_loop().run_until_complete(live_danmaku.connect())


if __name__ == '__main__':
    print('B站直播场控系统v0.2')
    with open('./config.json', 'r', encoding='utf8') as f:
        global config
        config = json.load(f)
        print_log('配置已加载')
    main()
