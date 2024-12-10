# eteams_auto_check
泛微eteams自动打卡

## 项目简介
该项目用于泛微eteams打卡，支持自定义位置经纬度，支持通过GitHub Actions定时运行，并通过爱语飞飞微信推送打卡结果。

## 使用教程

### 1. 克隆项目
首先，克隆该项目到本地：
```bash
git clone https://github.com/dongxuecheng/eteams_auto_check.git
cd eteams_auto_check
```

### 2. 安装依赖
确保你已经安装了Python 3.6或更高版本，然后安装项目依赖：
```bash
pip install requests
```

### 3. 配置参数
在运行脚本之前，需要配置用户名、密码、打卡地址(填写公司名称)、经纬度(通过地图软件获取)和IYUUAPI（爱语飞飞官网免费注册获取Token）。你可以通过命令行参数传递这些信息：
```bash
python main.py --username <你的用户名> --password <你的密码> --check_address <打卡地址> --latitude <纬度> --longitude <经度> --iyuuapi <IYUUAPI>
```

### 4. 运行脚本
配置好参数后，可以运行脚本：
```bash
python main.py --username <你的用户名> --password <你的密码> --check_address <打卡地址> --latitude <纬度> --longitude <经度> --iyuuapi <IYUUAPI>
```
### 5. 可在已有服务器上设置定时运行该python脚本

## 使用GitHub Actions定时运行（推荐）

### 1. 配置GitHub Secrets
在GitHub仓库中，配置以下Secrets：
- `USERNAME`: 你的用户名
- `PASSWORD`: 你的密码
- `CHECK_ADDRESS`: 打卡地址
- `LATITUDE`: 纬度
- `LONGITUDE`: 经度
- `IYUUAPI`: 爱语飞飞Token

### 2. 配置GitHub Actions
在项目根目录下的`.github/workflows/python-app.yml`文件中，已经配置好了GitHub Actions工作流。该工作流会在北京时间每个工作日的08:20和18:10自动运行脚本。

### 3. 手动触发工作流
你也可以在GitHub Actions页面手动触发工作流。

## 许可证
该项目使用MIT许可证，详情请参见LICENSE文件。
