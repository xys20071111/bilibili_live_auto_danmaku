# bilibili_live_auto_danmaku
B站直播弹幕助手----自动感谢礼物/开通舰长/续费舰长/SC  
只在Python 3.9下测试过  
[![LICENSE](https://img.shields.io/badge/LICENSE-GPLv3-red)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.9-blue)
## 使用方法

1、pip3 install -r requirements.txt  
2、打开 verify.example.json 
```
{
    "sessdata": "sessdata",
    "csrf": "bili_jct",
    "buvid3":"buvid3"
}

```
将各项改为你的对应参数，参数获取方法见[https://www.passkou.com/bilibili-api/#/get-credential]  
注意：bili_jct 对应 csrf  
3、重命名 user_not_thanks.example.json 为 user_not_thanks.json  
4、重命名 user_not_welcome.example.json 为 user_not_welcome.json  
4、运行 python3 ./\_\_main\_\_.py <房间号> verify.example.json  
