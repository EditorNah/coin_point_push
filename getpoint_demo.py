import os
import configparser
import requests
import json
import time

# 获取脚本当前所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, 'config.ini')

# 读取配置文件
config = configparser.ConfigParser()
config.read(config_path)

# 从配置文件中获取钱包地址和钉钉access_token
wallet_addresses = {key: value.lower() for key, value in config['wallets'].items() if value.strip()}
dingaccess_token = config['dingtalk']['access_token']
serverchan_key = config['server酱'].get('key', '')

# 定义请求的URL
url_points = "https://kx58j6x5me.execute-api.us-east-1.amazonaws.com/scroll/wallet-points"
url_linea = "https://kx58j6x5me.execute-api.us-east-1.amazonaws.com/linea/getUserPointsSearch"

# 汇总的结果字符串
scroll_results = []
linea_results = []

# 循环遍历每个钱包地址
for eth, address in wallet_addresses.items():
    # 请求scroll接口
    params = {
        "walletAddress": address
    }

    try:
        response = requests.get(url_points, params=params)
        if response.status_code == 200:
            data = response.json()
            if data:
                points = round(data[0].get("points"), 4)
                scroll_results.append(f"* {eth}: {points}")
            else:
                print(f"Wallet Address: {address} - No data available")
        else:
            print(f"Failed to get data for address {address} from scroll endpoint, status code: {response.status_code}")
            print("Response:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"Request failed for address {address}: {e}")


    # 请求linea接口
    params_linea = {
        "user": address
    }

    try:
        response = requests.get(url_linea, params=params_linea)
        if response.status_code == 200:
            data = response.json()
            if data:
                rank_xp = data[0].get("rank_xp")
                xp = data[0].get("xp")
                linea_results.append(f"* {eth}: {xp}，Rank排名: {rank_xp}")
            else:
                print(f"Wallet Address: {address} - No data available from linea endpoint")
        else:
            print(f"Failed to get data for address {address} from linea endpoint, status code: {response.status_code}")
            print("Response:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"Request failed for address {address} from linea endpoint: {e}")

    # 增加1秒间隔
    time.sleep(1)

# 准备推送的消息内容
markdown_text = "# 积分推送\n"
markdown_text += "## scroll积分：\n"
for result in scroll_results:
    markdown_text += f"{result} \n"

markdown_text += "## linea积分：\n"
for result in linea_results:
    markdown_text += f"{result}\n"

def push_to_dingtalk(access_token, message):
    if not access_token:
        print("Access token is empty, skipping DingTalk push.")
        return

    # 构建推送的JSON数据
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": "积分推送",
            "text": message
        },
        "at": {
            "atMobiles": [],
            "atUserIds": [],
            "isAtAll": True
        }
    }

    # 设置钉钉机器人的请求头
    headers = {
        "Content-Type": "application/json"
    }

    # 发送POST请求到钉钉机器人接口
    dingtalk_url = f"https://oapi.dingtalk.com/robot/send?access_token={access_token}"

    try:
        response = requests.post(dingtalk_url, json=payload, headers=headers)
        if response.status_code == 200:
            print("Data pushed successfully to DingTalk.")
        else:
            print(f"Failed to push data to DingTalk, status code: {response.status_code}")
            print("Response:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"Push request failed: {e}")

def push_to_serverchan(key, message):
    if not key:
        print("Server酱 key is empty, skipping Server酱 push.")
        return

    # 构建推送的JSON数据
    payload = {
        "title": "积分推送",
        "desp": message,
        "short": message
    }

    # 设置Server酱的请求头
    headers = {
        "Content-Type": "application/json"
    }

    # 发送POST请求到Server酱接口
    serverchan_url = f"https://sctapi.ftqq.com/{key}.send"

    try:
        response = requests.post(serverchan_url, json=payload, headers=headers)
        if response.status_code == 200:
            print("Data pushed successfully to Server酱.")
        else:
            print(f"Failed to push data to Server酱, status code: {response.status_code}")
            print("Response:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"Push request failed: {e}")

# 调用钉钉推送函数
push_to_dingtalk(dingaccess_token, markdown_text)

# 调用Server酱推送函数
push_to_serverchan(serverchan_key, markdown_text)
