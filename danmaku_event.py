import json
import asyncio
import time
from utils.send_danmaku import send_danmaku
from utils.logger import print_log
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from config import config


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


# 激活 不感谢用户列表 的实时更新（有问题）
not_thanks_user_watcher = Observer()
ntu = not_thanks_user()
not_thanks_user_watcher.schedule(
    ntu, './user_not_thanks.json', True)
not_thanks_user_watcher.start()

liveroom = config.get_live_room()
danmaku_template = config.get_danmakes()
danmaku_cold_time = config.get_danmaku_cold_down_time()

print_log("弹幕冷却时间:{}".format(danmaku_cold_time))


async def guard_buy(info):
    data = info['data']['data']
    user_nickname = data['username']
    text = danmaku_template['guard'].format(name=user_nickname)
    if not data['uid'] in ntu.list:
        await send_danmaku(text=text, liveroom=liveroom)
    print_log('{}购买了舰长'.format(user_nickname))

# 以下为感谢礼物的逻辑
cold_time = {'last_cold_down': -1}
lock = asyncio.Lock()


async def send_gift(info):
    data = info['data']['data']
    user_nickname = data['uname']
    gift_name = data['giftName']
    gift_num = data['super_gift_num']
    text = danmaku_template['gift'].format(
        name=user_nickname, gift=gift_name)
    log_text = '{name}投喂了{count}个{gift}'.format(
        name=user_nickname, count=gift_num, gift=gift_name)
    print_log(log_text)
    await lock.acquire()
    if lock.locked():
        if (cold_time['last_cold_down'] + danmaku_cold_time) < int(time.time()) or cold_time['last_cold_down'] == -1:
            if not data['uid'] in ntu.list:
                await send_danmaku(text=text, liveroom=liveroom)
                cold_time['last_cold_down'] = time.time()
        lock.release()
# 以上为感谢礼物的逻辑


async def combo_send(info):
    data = info['data']['data']
    user_nickname = data['uname']
    gift_name = data['gift_name']
    gift_count = data['total_num']
    text = danmaku_template['gift_total'].format(
        name=user_nickname, count=gift_count, gift=gift_name)
    print_log(text)
    if not data['uid'] in ntu.list:
        await send_danmaku(text=text, liveroom=liveroom)


async def super_chat_message(info):
    data = info['data']['data']
    user_nickname = data['user_info']['uname']
    text = danmaku_template['sc'].format(name=user_nickname)
    if not data['uid'] in ntu.list:
        await send_danmaku(text=text, liveroom=liveroom)
    print_log('感谢{}的SC'.format(user_nickname))


async def live_start(useless_arg):
    text = danmaku_template['live_start']
    await send_danmaku(text=text, liveroom=liveroom)
    print_log('直播开始')


async def live_end(useless_arg):
    text = danmaku_template['live_end']
    await send_danmaku(text=text, liveroom=liveroom)
    print_log('直播结束')
    # ga.live_end()


async def room_block_msg(info):
    data = info['data']['data']
    print_log('用户 {} uid:{} 被禁言'.format(data['uname'], data['uid']))


async def not_welcome(info):
    data = info['data']['data']
    with open('./user_not_welcome.json', mode='r', encoding='utf8') as f:
        black_list = json.load(f)
        if data['uid'] in black_list:
            print_log('不受欢迎的用户{}进入'.format(data['uname']))
