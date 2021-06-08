#!/usr/bin/python3
import asyncio
import json
import sys
import time
from bilibili_api import live, Credential
from bilibili_api.utils import Danmaku
from guard_advertsing import guard_advertsing
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
    # 打开验证信息文件
    verify_file = open(sys.argv[2], mode='r', encoding='utf8')
    # 解析验证信息
    verify_info = json.load(verify_file)
    verify_file.close()
    # 创建验证数据
    verify = Credential(sessdata=verify_info['sessdata'],
                        bili_jct=verify_info['csrf'],
                        buvid3=verify_info['buvid3'])
    display_room_id = int(sys.argv[1])
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
    # 初始化 发送宣传语 模块（模块故障，无法发送弹幕）
    ga = guard_advertsing(credential = verify, room_id = room_real_id)
    #ga.start()
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
        text = '感谢{}的舰长'.format(user_nickname)
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
        text = '感谢{}投喂的{}'.format(user_nickname, gift_name)
        log_text = '{}投喂了{}个{}'.format(user_nickname, gift_num, gift_name)
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
        text = '感谢{}投喂的一共{}个{},感谢！'.format(
            user_nickname, gift_count, gift_name)
        print_log(text)
        if not data['uid'] in ntu.list:
            await send_danmaku(text=text, liveroom=liveroom)

    @live_danmaku.on('SUPER_CHAT_MESSAGE')
    async def 感谢SC(info):
        data = info['data']['data']
        user_nickname = data['user_info']['uname']
        text = '感谢{}的SC'.format(user_nickname)
        if not data['uid'] in ntu.list:
            await send_danmaku(text=text, liveroom=liveroom)
        print_log('感谢{}的SC'.format(user_nickname))

    @live_danmaku.on('LIVE')
    async def 直播开始(useless_arg):
        dan = Danmaku.Danmaku(config['live_start'])
        await liveroom.send_danmaku(danmaku=dan)
        print_log('直播开始')
        # ga.live_start()

    @live_danmaku.on('PREPARING')
    async def 直播结束(useless_arg):
        dan = Danmaku.Danmaku(config['live_end'])
        await liveroom.send_danmaku(danmaku=dan)
        print_log('直播结束')
        # ga.live_end()

    @live_danmaku.on('ROOM_BLOCK_MSG')
    async def 有人被禁言(info):
        data = info['data']['data']
        print_log('用户 {} uid:{} 被禁言'.format(data['uname'], data['uid']))

    # 可选功能放在这行注释下面的with里
    function_list = config['optional_function']
    #可选功能 不受欢迎的用户提示
    if function_list['not_wellcome']:
        print_log('不受欢迎用户提示功能已打开')

        @live_danmaku.on('INTERACT_WORD')
        async def 不受欢迎的人通知(info):
            data = info['data']['data']
            with open('./user_not_welcome.json', mode='r', encoding='utf8') as f:
                black_list = json.load(f)
                if data['uid'] in black_list:
                    text = '{}入场，房管注意禁言'.format(data['uname'])
                    dan = Danmaku.Danmaku(text=text)
                    await liveroom.send_danmaku(danmaku=dan)
                    print_log('不受欢迎的用户{}进入'.format(data['uname']))
    if function_list['debug']:
        @live_danmaku.on('ALL')
        async def 调试信息(info):
            print(info['data']['cmd'])

    asyncio.get_event_loop().run_until_complete(live_danmaku.connect())


if __name__ == '__main__':
    print('B站直播场控系统v0.2')
    if len(sys.argv) < 3:
        print('使用方法：./__main__.py <房间号> <验证文件>')
        sys.exit(1)
    with open('./config.json', 'r', encoding='utf8') as f:
        global config
        config = json.load(f)
        print_log('配置已加载')
    main()
