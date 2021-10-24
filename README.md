# bilibili_live_auto_danmaku

[![LICENSE](https://img.shields.io/github/license/xys20071111/bilibili_live_auto_danmaku)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.9-blue)  
B站直播弹幕助手----自动感谢礼物/开通舰长/续费舰长/SC  
只在Python 3.9下测试过  

## 使用方法

1. pip3 install -r requirements.txt
2. 重命名 `user_not_thanks.example.json` 为 `user_not_thanks.json`
3. 重命名 `user_not_welcome.example.json` 为 `user_not_welcome.json`
4. 重命名 `config.example.json` 为 `config.json` ,并将 `config.json` 中 `room_id` 改为你的直播间id，verify中的各项改为你的对应参数，参数获取方法https://www.moyu.moe/bilibili-api/#/get-credential)
   注意：bili_jct 对应 csrf
5. 运行 `./__main__.py config.json`

