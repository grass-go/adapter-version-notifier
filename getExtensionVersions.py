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
    write_json_file(versionFile, allExtInfo)
    return allExtInfo

def getYesterdayExtInfo(yesterdayFile):
    with open(yesterdayFile, 'r') as file:
        data = json.load(file)
    return data

def sendSlackNotification(text):
    SLACK_POST_URL = "https://slack.com/api/chat.postMessage"
    payload = {
        "text": text,
        "channel": "C08HD8FNXC6"  # adapter-notifier频道
    }
    response = requests.post(
        SLACK_POST_URL,
        data=json.dumps(payload),
        headers={'Content-Type': 'application/json; charset=utf-8'}
    )
    return response.status_code == 200

def SendNotificationOrNot(todayInfo, yesterdayInfo, today_str):
    sendCounts = 0
    for eachExt in yesterdayInfo:
        if eachExt in todayInfo:
            if todayInfo[eachExt]["Version"] != yesterdayInfo[eachExt]["Version"]:
                sendSlackNotification(f'{eachExt} Version changed from {yesterdayInfo[eachExt]["Version"]} to {todayInfo[eachExt]["Version"]} on {today_str}!')
                sendCounts = sendCounts + 1

        else:
            sendSlackNotification(f"{eachExt} lacked on {today_str}!")
            sendCounts = sendCounts + 1
    if sendCounts == 0:
        sendSlackNotification(f"Extensions have no update on {today_str}")
    else:
        sendSlackNotification(f"Extensions update check finished!")


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
    print("Today's Info:")
    print(todayInfo)
    print("Yesterday's Info:")
    print(yesterdayInfo)
    SendNotificationOrNot(todayInfo, yesterdayInfo, today_str)