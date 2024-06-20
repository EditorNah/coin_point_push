import requests
import json

# 定义请求的URL
url = "https://kx58j6x5me.execute-api.us-east-1.amazonaws.com/scroll/wallet-points"

# 定义钱包地址列表，有几个地址就有几行，如果只有一个就删除只留一行，最后不要有逗号
wallet_addresses = {
    "eth1": "钱包1的地址",
    "eth2": "钱包2的地址",
    "eth3": "钱包3的地址"
}
# 钉钉机器人的推送地址
dingtalk_url = "https://oapi.dingtalk.com/robot/send?access_token=c4daa4b7e7d01bfbcdc020de61dd0fce2d63b09bd66159f527241361ac5da15c"


# 汇总的结果字符串
results = []

# 循环遍历每个钱包地址
for eth, address in wallet_addresses.items():
    params = {
        "walletAddress": address
    }

    try:
        # 发送GET请求
        response = requests.get(url, params=params)
        
        # 检查响应状态码
        if response.status_code == 200:
            # 解析JSON响应
            data = response.json()
            if data:
                # 提取points值，保留小数点后4位，并加入汇总字符串
                points = round(data[0].get("points"), 4)
                results.append(f"{eth}: {points}")
            else:
                print(f"Wallet Address: {address} - No data available")
        else:
            print(f"Failed to get data for address {address}, status code: {response.status_code}")
            print("Response:", response.text)

    except requests.exceptions.RequestException as e:
        # 打印请求异常错误
        print(f"Request failed for address {address}: {e}")

# 准备推送的消息内容
markdown_text = f"## 积分推送\n\nscroll积分：\n"
for result in results:
    markdown_text += f"- {result}\n"

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



try:
    response = requests.post(dingtalk_url, json=payload, headers=headers)
    # 检查响应状态码
    if response.status_code == 200:
        print("Data pushed successfully to DingTalk.")
    else:
        print(f"Failed to push data to DingTalk, status code: {response.status_code}")
        print("Response:", response.text)
except requests.exceptions.RequestException as e:
    # 打印推送请求异常错误
    print(f"Push request failed: {e}")
