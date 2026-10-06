import os
import sys
import time
import random
import requests

SESSDATA = os.environ.get("SESSDATA", "")
BILI_JCT = os.environ.get("BILI_JCT", "")
DEDE_USER_ID = os.environ.get("DEDE_USER_ID", "")

if not SESSDATA or not BILI_JCT or not DEDE_USER_ID:
    print("❌ 请先配置 SESSDATA、BILI_JCT、DEDE_USER_ID 三个 secret")
    sys.exit(1)

cookie = f"SESSDATA={SESSDATA}; bili_jct={BILI_JCT}; DedeUserID={DEDE_USER_ID}"

headers = {
    "Cookie": cookie,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com/"
}

def get_user_info():
    url = "https://api.bilibili.com/x/web-interface/nav"
    resp = requests.get(url, headers=headers, timeout=10).json()
    if resp["code"] == 0:
        data = resp["data"]
        print(f"✅ 用户: {data['uname']} (UID: {data['mid']})")
        print(f"   当前等级: Lv{data['level_info']['current_level']}")
        print(f"   当前硬币: {data['money']}")
        return data
    else:
        print(f"❌ 获取用户信息失败: {resp['message']}")
        return None

def sign_daily():
    url = "https://api.live.bilibili.com/xlive/web-ucenter/v1/sign/DoSign"
    resp = requests.get(url, headers=headers, timeout=10).json()
    if resp["code"] == 0:
        print(f"✅ 直播签到成功: {resp['data']['text']}")
    else:
        print(f"ℹ️ 直播签到: {resp['message']}")

    url = "https://manga.bilibili.com/twirp/activity.v1.Activity/ClockIn"
    data = {"platform": "web"}
    resp = requests.post(url, headers=headers, json=data, timeout=10).json()
    if resp["code"] == 0:
        print("✅ 漫画签到成功")
    else:
        print(f"ℹ️ 漫画签到: {resp['msg']}")

def watch_video(aid):
    url = "https://api.bilibili.com/x/click/exposure/v2"
    data = {"aid": aid, "played_time": 300, "type": 3, "csrf": BILI_JCT}
    resp = requests.post(url, headers=headers, data=data, timeout=10).json()
    if resp["code"] == 0:
        print("✅ 观看视频完成 (+5经验)")
    else:
        print(f"ℹ️ 观看视频: {resp['message']}")

def share_video(aid):
    url = "https://api.bilibili.com/x/web-interface/share/add"
    data = {"aid": aid, "csrf": BILI_JCT}
    resp = requests.post(url, headers=headers, data=data, timeout=10).json()
    if resp["code"] == 0:
        print("✅ 分享视频完成 (+5经验)")
    else:
        print(f"ℹ️ 分享视频: {resp['message']}")

def coin_video(aid, num=1):
    url = "https://api.bilibili.com/x/web-interface/coin/add"
    data = {"aid": aid, "multiply": num, "select_like": 1, "csrf": BILI_JCT}
    resp = requests.post(url, headers=headers, data=data, timeout=10).json()
    if resp["code"] == 0:
        print(f"✅ 投币成功 +{num}枚 (+{num*10}经验)")
    else:
        print(f"ℹ️ 投币: {resp['message']}")

def get_hot_videos():
    url = "https://api.bilibili.com/x/web-interface/popular?ps=10&pn=1"
    resp = requests.get(url, headers=headers, timeout=10).json()
    if resp["code"] == 0:
        return [v["aid"] for v in resp["data"]["list"]]
    return []

def main():
    print("=" * 40)
    print("📺 B站自动签到")
    print("=" * 40)
    user = get_user_info()
    if not user:
        print("❌ cookie 可能已过期，请重新获取")
        sys.exit(1)
    print("\n开始每日任务...")
    sign_daily()
    videos = get_hot_videos()
    if not videos:
        print("❌ 获取热门视频失败")
        return
    aid = random.choice(videos)
    watch_video(aid)
    time.sleep(2)
    share_video(aid)
    time.sleep(2)
    coin_video(aid, num=2)
    print("\n" + "=" * 40)
    print("✅ 今日任务完成！")
    print("=" * 40)

if __name__ == "__main__":
    main()
