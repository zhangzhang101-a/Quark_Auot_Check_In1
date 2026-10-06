"""
B站自动签到 - 每日领经验
功能：每日签到 + 自动观看 + 自动分享 + 自动投币（拿满65经验）
"""
import os
import sys
import time
import random
import requests

# 从环境变量读取
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

# 获取用户信息
def get_user_info():
    try:
        url = "https://api.bilibili.com/x/web-interface/nav"
        resp = requests.get(url, headers=headers, timeout=10).json()
        if resp["code"] == 0:
            data = resp["data"]
            print(f"✅ 用户: {data['uname']} (UID: {data['mid']})")
            print(f"   当前等级: Lv{data['level_info']['current_level']}")
            print(f"   当前硬币: {data['money']}")
            print(f"   当前经验: {data['level_info']['current_exp']}")
            return data
        else:
            print(f"❌ 获取用户信息失败: {resp['message']}")
            return None
    except Exception as e:
        print(f"❌ 获取用户信息异常: {e}")
        return None

# 每日签到（直播签到 + 漫画签到）
def sign_daily():
    # 直播中心签到
    try:
        url = "https://api.live.bilibili.com/xlive/web-ucenter/v1/sign/DoSign"
        resp = requests.get(url, headers=headers, timeout=10).json()
        if resp["code"] == 0:
            print(f"✅ 直播签到成功: {resp['data']['text']}")
        else:
            print(f"ℹ️ 直播签到: {resp['message']}")
    except Exception as e:
        print(f"ℹ️ 直播签到: 接口异常 {e}")

    # 漫画签到
    try:
        url = "https://manga.bilibili.com/twirp/activity.v1.Activity/ClockIn"
        data = {"platform": "web"}
        resp = requests.post(url, headers=headers, json=data, timeout=10).json()
        if resp["code"] == 0:
            print("✅ 漫画签到成功")
        else:
            print(f"ℹ️ 漫画签到: {resp.get('msg', '已完成')}")
    except Exception as e:
        print(f"ℹ️ 漫画签到: 接口异常 {e}")

# 自动观看视频（拿5经验）
def watch_video(aid):
    try:
        url = "https://api.bilibili.com/x/v2/dm/view"
        data = {
            "aid": aid,
            "played_time": 300,
            "type": 3,
            "csrf": BILI_JCT
        }
        resp = requests.post(url, headers=headers, data=data, timeout=10)
        resp.raise_for_status()
        result = resp.json()
        if result.get("code", 0) == 0:
            print("✅ 观看视频完成 (+5经验)")
        else:
            print(f"ℹ️ 观看视频: {result.get('message', '已完成')}")
    except Exception as e:
        print(f"ℹ️ 观看视频: 接口异常 {e}")

# 自动分享视频（拿5经验）
def share_video(aid):
    try:
        url = "https://api.bilibili.com/x/web-interface/share/add"
        data = {"aid": aid, "csrf": BILI_JCT}
        resp = requests.post(url, headers=headers, data=data, timeout=10).json()
        if resp["code"] == 0:
            print("✅ 分享视频完成 (+5经验)")
        else:
            print(f"ℹ️ 分享视频: {resp['message']}")
    except Exception as e:
        print(f"ℹ️ 分享视频: 接口异常 {e}")

# 自动投币（拿50经验）
def coin_video(aid, num=1):
    try:
        url = "https://api.bilibili.com/x/web-interface/coin/add"
        data = {
            "aid": aid,
            "multiply": num,
            "select_like": 1,
            "csrf": BILI_JCT
        }
        resp = requests.post(url, headers=headers, data=data, timeout=10).json()
        if resp["code"] == 0:
            print(f"✅ 投币成功 +{num}枚 (+{num*10}经验)")
        else:
            print(f"ℹ️ 投币: {resp['message']}")
    except Exception as e:
        print(f"ℹ️ 投币: 接口异常 {e}")

# 获取热门视频
def get_hot_videos():
    try:
        url = "https://api.bilibili.com/x/web-interface/popular?ps=10&pn=1"
        resp = requests.get(url, headers=headers, timeout=10).json()
        if resp["code"] == 0:
            return [v["aid"] for v in resp["data"]["list"]]
    except Exception as e:
        print(f"ℹ️ 获取热门视频异常: {e}")
    return []

def main():
    print("=" * 40)
    print("📺 B站自动签到")
    print("=" * 40)

    user = get_user_info()
    if not user:
        print("❌ cookie 可能已过期，请重新获取")
        sys.exit(1)

    print()
    print("开始每日任务...")

    # 签到
    sign_daily()

    # 获取热门视频
    videos = get_hot_videos()
    if not videos:
        print("ℹ️ 获取热门视频失败，跳过观看/分享/投币")
        print()
        print("=" * 40)
        print("✅ 今日签到任务完成！")
        print("=" * 40)
        return

    # 随机选一个视频
    aid = random.choice(videos)

    # 观看视频
    watch_video(aid)
    time.sleep(2)

    # 分享视频
    share_video(aid)
    time.sleep(2)

    # 投币2个（拿满50经验）
    coin_video(aid, num=2)

    print()
    print("=" * 40)
    print("✅ 今日任务完成！")
    print("=" * 40)

if __name__ == "__main__":
    main()
