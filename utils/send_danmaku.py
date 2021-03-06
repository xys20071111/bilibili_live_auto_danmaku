import asyncio
from bilibili_api.utils import Danmaku
from bilibili_api import live

async def send_danmaku(text,liveroom:live.LiveRoom):
    dan = []
    if len(text) > 20:
        dan.append(Danmaku.Danmaku(text[0:18]))
        dan.append(Danmaku.Danmaku(text[18:]))
    else:
        dan.append(Danmaku.Danmaku(text))
    for v in dan:
        await liveroom.send_danmaku(danmaku=v)
        await asyncio.sleep(3)