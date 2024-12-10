import requests
import logging

# 以下内容需要根据自己的实际情况进行修改
USERNAME = "xxxxx"
PASSWORD = "xxxx"
CHECK_ADDRESS = "xx市xxxx"
LATITUDE = "xx.xxxxxx"
LONGITUDE = "xxx.xxxxxx"

LOGIN_URL = "https://passport.eteams.cn/papi/passport/login/appLogin"  # 登录页面
CHECK_URL = "https://weapp.eteams.cn/api/app/attend/web/sign/getAttendStatus"  # 检测打卡
ATTEND_URL = "https://weapp.eteams.cn/api/app/attend/web/sign/sign"  # 打卡接口
SIGNATURE_URL = "https://weapp.eteams.cn/papi/app/eb/open/wxcard" # 获取签名
IYUUAPI = "https://iyuu.cn/IYUU56813T6e6f966ad0f13c70141c4b111b072215c84a9f14.send"  # 微信推送

# 变量
JSESSIONID = ""
TENANTKEY = ""
UID = ""
ETEAMSID = ""
MESSAGE = ""
TIMECARD_STATUS = ""
SIGNATURE=""

# 日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


# 微信推送
def push_wechat():
    if not MESSAGE:
        return
    params = {
        "text": MESSAGE,
    }
    try:
        response = requests.get(IYUUAPI, params=params)
        response.raise_for_status()
        logging.info("微信推送成功！")
    except requests.RequestException as e:
        logging.error(f"微信推送失败: {e}")


# 登录
def login():
    global JSESSIONID, TENANTKEY, UID, ETEAMSID
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) weapp/4.3.9/public//1.0/",
    }
    queryparam = {
        "username": USERNAME,
        "password": PASSWORD,
        "loginTyp": "app_account",
        "imei": "F1A480AB-1A98-44D2-8200-91220A4529F4",
        "version": "15.1.1",
        "secondImei": "",
        "adviceInfo": "iPhone",
    }
    try:
        response = requests.post(LOGIN_URL, headers=headers, params=queryparam)
        response.raise_for_status()
        result = response.json()
        JSESSIONID, TENANTKEY, UID, ETEAMSID = parse_login_result(result)
        if all([JSESSIONID, TENANTKEY, UID, ETEAMSID]):
            logging.info("登录成功！")
        else:
            logging.error("登录失败！")


    except requests.RequestException as e:
        logging.error(f"登录请求失败: {e}")


# 解析登录结果
def parse_login_result(result):
    jsessionid = result.get("jsessionid", "")
    tenantkey = result.get("tenantkey", "")
    uid = result.get("uid", "")
    eteamsid = result.get("ETEAMSID", "")
    return jsessionid, tenantkey, uid, eteamsid


# 检测打卡类型
def check_attendance():
    global TIMECARD_STATUS
    headers = {
        "Cookie": f"ETEAMSID={ETEAMSID}; JSESSIONID={JSESSIONID}",
        "Content-Type": "application/json;charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) weapp/4.3.9/public//1.0/",
    }
    try:
        response = requests.get(CHECK_URL, headers=headers)
        response.raise_for_status()
        result = response.json()
        TIMECARD_STATUS = result.get("data", {}).get("signStatus", "")
        logging.info(f"打卡类型检测结果: {TIMECARD_STATUS}")
    except requests.RequestException as e:
        logging.error(f"检测打卡类型失败: {e}")


# 打卡
def attendance():
    global MESSAGE
    headers = {
        "Cookie": f"ETEAMSID={ETEAMSID}; JSESSIONID={JSESSIONID}",
        "Content-Type": "application/json;charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) weapp/4.3.9/public//1.0/",
    }
    payload = {
        "checkAddress": CHECK_ADDRESS,
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "type": TIMECARD_STATUS,
        "sign": SIGNATURE,
        "userId": UID,
    }
    params = {
        "device": "Mobile",
        "engine": "WebKit",
        "browser": "Weapp",
        "os": "iOS",
        "osVersion": "15.1.1",
        "version": "4.3.9",
        "language": "zh_CN",
    }
    try:
        response = requests.post(ATTEND_URL, headers=headers, json=payload, params=params)
        response.raise_for_status()
        result = response.json()
        status = result.get("status", False)
        if status:
            MESSAGE = "签到成功！" if TIMECARD_STATUS == "CHECKIN" else "签退成功！"
            logging.info(MESSAGE)
        else:
            MESSAGE = "签到异常！"
            logging.error(MESSAGE)
    except requests.RequestException as e:
        logging.error(f"打卡请求失败: {e}")

# 获取签名
def get_signature():
    global SIGNATURE
    headers = {
        "Cookie": f"ETEAMSID={ETEAMSID}",
        "Content-Type": "application/json;charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) weapp/4.3.9/public//1.0/",
    }
    params = {
        "clientVersion": "4.0.216",
        "clientTag": "public",
        "clientPackage": "com.weaver.teams",
        "devType": "1"
    }
    try:
        response = requests.get(SIGNATURE_URL, headers=headers, params=params)
        response.raise_for_status()
        result = response.json()
        SIGNATURE = result.get("data", {}).get("signature", "")
        logging.info("获得签名成功！")
    except requests.RequestException as e:
        logging.error(f"获取签名失败: {e}")


def main():
    login()
    get_signature()
    check_attendance()
    attendance()
    push_wechat()


if __name__ == "__main__":
    main()
