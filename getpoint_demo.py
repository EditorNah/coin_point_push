import requests
import json

# 定义请求的URL
url_points = "https://kx58j6x5me.execute-api.us-east-1.amazonaws.com/scroll/wallet-points"
url_linea = "https://kx58j6x5me.execute-api.us-east-1.amazonaws.com/linea/getUserPointsSearch"


# 定义钱包地址列表，有几个地址就有几行，如果只有一个就删除只留一行，最后不要有逗号
wallet_addresses = {
    "eth1": "钱包1的地址",
    "eth2": "钱包2的地址",
    "eth3": "钱包3的地址"
}
# 钉钉机器人的推送地址
dingtalk_url = "https://oapi.dingtalk.com/robot/send?access_token=c4daa4b7e7d01bfbcdc020de61dd0fce2d63b09bd66159f52xxxxxxxxxxxxx15c"


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
                scroll_results.append(f"{eth}: {points}\n")
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
                linea_results.append(f"{eth}: {xp}，Rank排名: {rank_xp}\n")
            else:
                print(f"Wallet Address: {address} - No data available from linea endpoint")
        else:
            print(f"Failed to get data for address {address} from linea endpoint, status code: {response.status_code}")
            print("Response:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"Request failed for address {address} from linea endpoint: {e}")

# 准备推送的消息内容
markdown_text = "## 积分推送\n"
markdown_text += "### scroll积分：\n"
for result in scroll_results:
    markdown_text += f"{result} \n"

markdown_text += "### linea积分：\n"
for result in linea_results:
    markdown_text += f"{result}\n"

# 构建推送的JSON数据
payload = {
    "msgtype": "markdown",
    "markdown": {
        "title": "scroll积分推送",
        "text": markdown_text
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
dingtalk_url = f"https://oapi.dingtalk.com/robot/send?access_token={dingaccess_token}"

try:
    response = requests.post(dingtalk_url, json=payload, headers=headers)
    if response.status_code == 200:
        print("Data pushed successfully to DingTalk.")
    else:
        print(f"Failed to push data to DingTalk, status code: {response.status_code}")
        print("Response:", response.text)
except requests.exceptions.RequestException as e:
    print(f"Push request failed: {e}")

