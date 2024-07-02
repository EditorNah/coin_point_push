import os
import configparser
import requests
import json
import time
import argparse

# 设置命令行参数
parser = argparse.ArgumentParser(description="积分推送脚本")
parser.add_argument('-nt', '--no-push', action='store_true', help='不进行推送，仅打印推送内容')
args = parser.parse_args()

# 获取脚本当前所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, 'config.ini')
history_file = os.path.join(script_dir, 'history.json')

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

# 读取历史记录
if os.path.exists(history_file):
    with open(history_file, 'r') as file:
        history = json.load(file)
else:
    history = {}

# 当前积分数据
current_data = {}

# 汇总的结果字符串
scroll_results = []
linea_results = []

# 循环遍历每个钱包地址
for eth, address in wallet_addresses.items():
    current_data[eth] = {}

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
                current_data[eth]['scroll'] = points
                if eth in history and 'scroll' in history[eth]:
                    prev_points = history[eth]['scroll']
                    diff = points - prev_points
                    if diff != 0:
                        scroll_results.append(f"* {eth}: {points}，分数相比上次增加{diff:.4f}分")
                    else:
                        scroll_results.append(f"* {eth}: {points}")
                else:
                    scroll_results.append(f"* {eth}: {points}")
            else:
                print(f"Wallet Address: {address} - No data available from scroll endpoint")
        else:
            print(f"Failed to get data for address {address} from scroll endpoint, status code: {response.status_code}")
            print("Response:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"Request failed for address {address} from scroll endpoint: {e}")

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
                current_data[eth]['linea'] = {'xp': xp, 'rank_xp': rank_xp}
                if eth in history and 'linea' in history[eth]:
                    prev_xp = history[eth]['linea']['xp']
                    prev_rank_xp = history[eth]['linea']['rank_xp']
                    xp_diff = xp - prev_xp
                    rank_diff = rank_xp - prev_rank_xp
                    rank_direction = "上涨" if rank_diff < 0 else "下降"
                    rank_diff = abs(rank_diff)
                    if xp_diff != 0 or rank_diff != 0:
                        linea_results.append(f"* {eth}: {xp}，Rank排名: {rank_xp}，分数相比上次增加{xp_diff}分，排名{rank_direction}{rank_diff}名")
                    else:
                        linea_results.append(f"* {eth}: {xp}，Rank排名: {rank_xp}")
                else:
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
            "title": "scroll积分推送",
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

# 根据参数决定推送方式
if args.no_push:
    print(markdown_text)
else:
    # 保存当前数据到历史记录文件
    with open(history_file, 'w') as file:
        json.dump(current_data, file, ensure_ascii=False, indent=4)
    
    push_to_dingtalk(dingaccess_token, markdown_text)
    push_to_serverchan(serverchan_key, markdown_text)
