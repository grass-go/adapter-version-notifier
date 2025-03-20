import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime,timedelta
import os

def getExtensionVersion(gName, gId):
    url = f"https://chrome.google.com/webstore/detail/{gName}/{gId}"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")
    selectedObjs = soup.select("section div ul li div")
    extensionInfo={}
    for i in range(len(selectedObjs)-1):
        currKey = selectedObjs[i].get_text("content") if selectedObjs[i] else "未找到"
        currValue = selectedObjs[i + 1].get_text("content") if selectedObjs[i + 1] else "未找到"
        if currKey == "Version" or currKey == "Updated" or currKey == "Size":
            extensionInfo[currKey] = currValue
    # print(extensionInfo)
    return extensionInfo

def write_json_file(file_path,data):
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
            print(f"数据已成功写入文件{file_path}")
    except Exception as e:
        print(f"写入文件{file_path}时，发生异常{e}")

def getTodayExtInfo(versionFile):
    allExtInfo = {}
    for eachExtension in extensionDict:
        curExtensionInfo = getExtensionVersion(extensionDict[eachExtension]["gname"],
                                               extensionDict[eachExtension]["id"])
        allExtInfo[eachExtension] = curExtensionInfo
    print(allExtInfo)
    write_json_file(versionFile, allExtInfo)
    return allExtInfo

def getYesterdayExtInfo(yesterdayFile):
    with open(yesterdayFile, 'r') as file:
        data = json.load(file)
    return data

def sendSlackNotification(text):
    WEBHOOK_URL = "https://hooks.slack.com/services/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"
    payload = {
        "text": text,
        "username": "我的机器人",  # 自定义显示名称
        "channel": "adapter-notifier"  # 可覆盖默认频道
    }

    response = requests.post(
        WEBHOOK_URL,
        data=json.dumps(payload),
        headers={'Content-Type': 'application/json'}
    )
    return response.status_code == 200

def SendNotificationOrNot(todayInfo, yesterdayInfo):
    for eachExt in yesterdayInfo:
        if eachExt in todayInfo:
            if todayInfo[eachExt]["Version"] != yesterdayInfo[eachExt]["Version"]:
                sendSlackNotification(f'{eachExt} Version changed from {yesterdayInfo[eachExt]["Version"]} to {todayInfo[eachExt]["Version"]}')
        else:
            sendSlackNotification(f"{eachExt} lacked today!")





if __name__ == "__main__":
    # 目前不好说，随着插件更新版本，插件的id是不是也跟着变化。
    '''
    # "imtoken":{"gname":"", "id":""}, #目前没有插件
    # ledger:{}, #不需要
    '''
    current_path = os.getcwd()
    today = datetime.now()
    today_str = today.strftime('%Y-%m-%d')
    yesterday = today - timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y-%m-%d')
    todayFile = f"{current_path}/{today_str}.txt"
    yesterdayFile = f"{current_path}/{yesterday_str}.txt"
    extensionDict = {"tronlink":{"gname": "tronlink", "id": "ibnejdfjmmkpcnlpebklmnkoeoihofec"},
                     "bitkeep": {"gname": "bitget-wallet-crypto-web3", "id": "jiidiaalihmmhddjgbnbgdfflelocpak"},
                     "bybit": {"gname": "bybit-wallet", "id": "pdliaogehgdbhbnmkklieghmmjkpigpa"},
                     "foxwallet": {"gname": "foxwallet-aleo-wallet", "id": "pmmnimefaichbcnbndcfpaagbepnjaig",},
                     "gatewallet": {"gname": "gate-wallet", "id": "cpmkedoipcpimgecpmgpldfpohjplkpp"},
                     "metaMask": {"gname": "metamask", "id": "nkbihfbeogaeaoehlefnkodbefgpgknn", "pName": ""},
                     "okxwallet": {"gname": "okx-wallet", "id": "mcohilncbfahbmgdjkbpemcciiolgcge", "pName": ""},
                     "tokenpocket": {"gname": "tokenpocket-web3-nostr-wa", "id": "mfgccjchihfkkindfppnaooecgfneiii"}
                     }

    todayInfo = getTodayExtInfo(todayFile)
    yesterdayInfo = getYesterdayExtInfo(yesterdayFile)
    print(todayInfo)
    print(yesterdayInfo)
    SendNotificationOrNot(todayInfo, yesterdayInfo)








'''
curl -X POST -H 'Content-type: application/json' --data '{"text":"Hello, World!"}' https://hooks.slack.com/services/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

'''