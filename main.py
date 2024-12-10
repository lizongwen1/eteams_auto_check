import requests
import logging
import argparse

# Constants
USERNAME = "xxxxx"
PASSWORD = "xxxx"
CHECK_ADDRESS = "xx市xxxx"
LATITUDE = "xx.xxxxxx"
LONGITUDE = "xxx.xxxxxx"
IYUUAPI = "xxxxtokenxxxx"  # 爱语飞飞微信推送

LOGIN_URL = "https://passport.eteams.cn/papi/passport/login/appLogin"  # 登录页面
CHECK_URL = "https://weapp.eteams.cn/api/app/attend/web/sign/getAttendStatus"  # 检测打卡
ATTEND_URL = "https://weapp.eteams.cn/api/app/attend/web/sign/sign"  # 打卡接口
SIGNATURE_URL = "https://weapp.eteams.cn/papi/app/eb/open/wxcard"  # 获取签名

# Variables
jsessionid = ""
tenantkey = ""
uid = ""
eteamsid = ""
message = ""
timecard_status = ""
signature = ""

def configure_logging():
    """Configure logging settings."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

configure_logging()

def push_wechat():
    """Push notification to WeChat."""
    if not message:
        return
    params = {
        "text": message,
    }
    try:
        response = requests.get(IYUUAPI, params=params)
        response.raise_for_status()
        logging.info("微信推送成功！")
    except requests.RequestException as e:
        logging.error(f"微信推送失败: {e}")

def login():
    """Login to the system."""
    global jsessionid, tenantkey, uid, eteamsid
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
        jsessionid, tenantkey, uid, eteamsid = parse_login_result(result)
        if all([jsessionid, tenantkey, uid, eteamsid]):
            logging.info("登录成功！")
        else:
            logging.error("登录失败！")
    except requests.RequestException as e:
        logging.error(f"登录请求失败: {e}")

def parse_login_result(result):
    """Parse login result."""
    jsessionid = result.get("jsessionid", "")
    tenantkey = result.get("tenantkey", "")
    uid = result.get("uid", "")
    eteamsid = result.get("ETEAMSID", "")
    return jsessionid, tenantkey, uid, eteamsid

def check_attendance():
    """Check attendance status."""
    global timecard_status
    headers = {
        "Cookie": f"ETEAMSID={eteamsid}; JSESSIONID={jsessionid}",
        "Content-Type": "application/json;charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) weapp/4.3.9/public//1.0/",
    }
    try:
        response = requests.get(CHECK_URL, headers=headers)
        response.raise_for_status()
        result = response.json()
        timecard_status = result.get("data", {}).get("signStatus", "")
        logging.info(f"打卡类型检测结果: {timecard_status}")
    except requests.RequestException as e:
        logging.error(f"检测打卡类型失败: {e}")

def attendance():
    """Perform attendance check-in or check-out."""
    global message
    headers = {
        "Cookie": f"ETEAMSID={eteamsid}; JSESSIONID={jsessionid}",
        "Content-Type": "application/json;charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) weapp/4.3.9/public//1.0/",
    }
    payload = {
        "checkAddress": CHECK_ADDRESS,
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "type": timecard_status,
        "sign": signature,
        "userId": uid,
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
            message = "签到成功！" if timecard_status == "CHECKIN" else "签退成功！"
            logging.info(message)
        else:
            message = "签到异常！"
            logging.error(message)
    except requests.RequestException as e:
        logging.error(f"打卡请求失败: {e}")

def get_signature():
    """Get signature for attendance."""
    global signature
    headers = {
        "Cookie": f"ETEAMSID={eteamsid}",
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
        signature = result.get("data", {}).get("signature", "")
        logging.info("获得签名成功！")
    except requests.RequestException as e:
        logging.error(f"获取签名失败: {e}")

def main():
    """Main function to execute the attendance process."""
    parser = argparse.ArgumentParser(description="Eteams Auto Check-in")
    parser.add_argument("--username", required=True, help="Username for login")
    parser.add_argument("--password", required=True, help="Password for login")
    parser.add_argument("--check_address", required=True, help="Check-in address")
    parser.add_argument("--latitude", required=True, help="Latitude for check-in location")
    parser.add_argument("--longitude", required=True, help="Longitude for check-in location")
    parser.add_argument("--iyuuapi", required=True, help="IYUUAPI for WeChat push notifications")
    
    args = parser.parse_args()
    
    global USERNAME, PASSWORD, CHECK_ADDRESS, LATITUDE, LONGITUDE, IYUUAPI
    USERNAME = args.username
    PASSWORD = args.password
    CHECK_ADDRESS = args.check_address
    LATITUDE = args.latitude
    LONGITUDE = args.longitude
    IYUUAPI =  f"https://iyuu.cn/{args.iyuuapi}.send"
    
    login()
    get_signature()
    check_attendance()
    attendance()
    push_wechat()

if __name__ == "__main__":
    main()
