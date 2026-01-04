import time
import requests
import json
import re
import socket
from BuceaSrunLogin.LoginManager import LoginManager

# 认证服务器检查接口
user_info_api = "http://10.1.1.131/cgi-bin/rad_user_info"


def check_internet_connection(host="223.5.5.5", port=53, timeout=3):
    """
    通过连接公共DNS(阿里DNS)来检测真实的互联网连接
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False


def is_online() -> bool:
    """
    检测在线状态：优先检查服务器返回的状态，兼容多种字段格式
    """
    try:
        # 构造模拟请求，带上时间戳防止缓存
        timestamp = str(int(time.time() * 1000))
        params = {
            "callback": "jQuery" + timestamp,
            "_": timestamp
        }

        response = requests.get(user_info_api, params=params, timeout=5)
        text = response.text

        # 提取JSONP中的JSON数据
        match = re.search(r'\((.*)\)', text)
        if not match:
            print("Error: 无法解析服务器响应格式")
            return False

        data = json.loads(match.group(1))

        # 打印状态以便调试 (只在离线时打印，避免刷屏)
        # print(f"Server Response: {data}")

        # 兼容性判断：旧版用 error="ok"，新版可能用 code=0 或 error="ok"
        # 只要满足其中一个成功条件即视为在线
        is_success = False

        if "error" in data and data["error"] == "ok":
            is_success = True
        elif "code" in data and str(data["code"]) == "0":  # 兼容数字0或字符串"0"
            is_success = True

        # 如果服务器说在线，但error不是ok（比如余额不足），通常也会包含在data里
        # 这里只返回是否"认证成功"
        return is_success

    except Exception as e:
        print(f"检测在线状态时出错: {e}")
        return False


def always_login(username, password, checkinterval):
    lm = LoginManager()

    def try_login():
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 正在尝试登录...")
        try:
            lm.login(username=username, password=password)
        except Exception as e:
            print(f"登录发生异常: {e}")

    # 启动时先检测一次，如果不在线则登录
    if not is_online():
        try_login()
    else:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 当前已在线，无需登录。")

    # 循环监控
    while True:
        time.sleep(checkinterval)

        # 1. 首先检查服务器状态接口
        server_says_online = is_online()

        # 2. (可选) 如果服务器说在线，但你觉得不稳，可以开启下面的双重检查
        # real_internet = check_internet_connection()

        if not server_says_online:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 检测到掉线！")
            try_login()
        # else:
        # print("保持在线中...") # 调试时可开启


if __name__ == "__main__":
    # 请确认账号密码正确
    username = ""
    password = ""  # 记得替换回你的密码
    checkinterval = 10  # 检测间隔(秒)

    print("开始运行掉线自动重连脚本...")
    always_login(username, password, checkinterval)
