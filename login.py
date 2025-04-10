from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import time
import os
import sys
from dotenv import load_dotenv
import requests
import urllib3
from pathlib import Path

urllib3.disable_warnings()

# 加载环境变量
load_dotenv()


def get_platform_info():
    """获取平台信息"""
    system = platform.system()
    machine = platform.machine()
    is_windows = system == 'Windows'
    is_mac = system == 'Darwin'
    is_linux = system == 'Linux'
    is_arm = 'arm' in machine.lower()
    return {
        'system': system,
        'machine': machine,
        'is_windows': is_windows,
        'is_mac': is_mac,
        'is_linux': is_linux,
        'is_arm': is_arm
    }


def check_internet_connection():
    """检查网络连接"""
    try:
        # 尝试访问一个可靠的网站
        requests.get("https://www.google.com", timeout=5)
        return True
    except requests.RequestException:
        return False


def check_target_site():
    """检查目标网站是否可访问"""
    try:
        response = requests.get("https://prod.anna-dsb.com/", timeout=10, verify=False)
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"目标网站访问错误: {str(e)}")
        return False


def setup_download_directory():
    download_dir=os.getenv('DSB_DOWNLOAD_DIR')
    if not download_dir:
        # 获取当前用户的下载目录
        platform_info = get_platform_info()
        if platform_info['is_windows']:
            # Windows 系统使用绝对路径
            download_dir = os.path.join(os.path.expanduser('~'), 'Downloads', 'dsb_downloads')
        else:
            # Mac/Linux 系统使用相对路径
            download_dir = os.path.join(os.getcwd(), "downloads")
    else:
        if download_dir.endswith('\\'):
            download_dir = download_dir[:-1]
    # 确保目录存在
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    return download_dir



    return os.path.abspath(download_dir)  # 返回绝对路径


def get_chrome_path():
    """获取 Chrome 浏览器路径"""
    platform_info = get_platform_info()

    if platform_info['is_windows']:
        paths = [
            os.path.join(os.environ.get('PROGRAMFILES', ''), 'Google/Chrome/Application/chrome.exe'),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Google/Chrome/Application/chrome.exe'),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google/Chrome/Application/chrome.exe')
        ]
        for path in paths:
            if os.path.exists(path):
                return path
    elif platform_info['is_mac']:
        return '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    elif platform_info['is_linux']:
        paths = [
            '/usr/bin/google-chrome',
            '/usr/bin/google-chrome-stable'
        ]
        for path in paths:
            if os.path.exists(path):
                return path

    return None


def setup_driver():
    """设置 Chrome 驱动"""
    platform_info = get_platform_info()
    chrome_options = Options()

    # 基本设置
    if os.getenv("DSB_HEADLESS") and os.getenv("DSB_HEADLESS") in ["false", "False", "0"]:
        print("chromedriver 禁用无头模式, DSB_HEADLESS: ", os.getenv("DSB_HEADLESS") )
    else:
        print("chromedriver 启用无头模式， DSB_HEADLESS: ", os.getenv("DSB_HEADLESS") )
        chrome_options.add_argument('--headless')  # 启用无头模式
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-gpu')  # 对于无头模式推荐启用
    chrome_options.add_argument('--window-size=1920,1080')  # 设置窗口大小
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # 设置下载选项
    download_dir = setup_download_directory()
    print("下载文件的文件夹为：", download_dir)
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "profile.default_content_settings.popups": 0,
        "profile.default_content_setting_values.automatic_downloads": 1
    }

    # Windows 特定设置
    if platform_info['is_windows']:
        prefs["download.default_directory"] = download_dir.replace('/', '\\')

    chrome_options.add_experimental_option('prefs', prefs)

    # 平台特定配置
    chrome_path = get_chrome_path()
    print(chrome_path)
    if chrome_path:
        chrome_options.binary_location = chrome_path

    if platform_info['is_mac'] and platform_info['is_arm']:
        chrome_options.add_argument('--disable-gpu')

    try:

        service = Service(ChromeDriverManager().install())
        if not service:
            raise Exception("无法安装 chrome driver!")
        print("============ 成功下载了 chrome driver: ", service.path)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # base_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
        # chromedriver_path = os.path.join(base_dir, 'chromedriver.exe')
        # print("chromedriver path is: ", chromedriver_path)
        # service = Service(chromedriver_path)
        # driver = webdriver.Chrome(service=service, options=chrome_options)
        # 执行 JavaScript 来隐藏自动化特征
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" if
            platform_info['is_windows'] else
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        return driver

    except Exception as e:
        print(f"ChromeDriver 设置错误: {str(e)}")
        print("尝试使用系统 ChromeDriver...")

        try:
            if platform_info['is_windows']:
                service = Service('chromedriver.exe')
            else:
                service = Service('/usr/local/bin/chromedriver')
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as e2:
            print(f"系统 ChromeDriver 设置也失败: {str(e2)}")
            raise


def download_file(driver, url):
    """下载文件"""
    target_file = url.split("/")[-1] # for example, target_file = "Rates-20250102.records"
    try:
        print("准备下载文件 {} ...".format(target_file))
        platform_info = get_platform_info()

        # 等待确保登录状态完全生效
        time.sleep(5)

        # 直接使用浏览器下载
        print(f"正在访问下载链接: {url}")
        driver
        driver.get(url)

        # 等待下载开始
        time.sleep(3)

        # 获取下载目录和目标文件路径
        downloaded_file = os.path.join(setup_download_directory(), target_file)

        # 等待文件下载完成
        timeout = 60  # 最长等待60秒
        start_time = time.time()
        while not os.path.exists(downloaded_file):
            if time.time() - start_time > timeout:
                print("文件下载超时")
                print(f"期望文件路径: {downloaded_file}")
                return False
            time.sleep(1)

        print(f"文件已成功下载到: {downloaded_file}")
        return True

    except Exception as e:
        print(f"下载文件时出错: {str(e)}")
        # print("详细错误信息:")
        # import traceback
        # print(traceback.format_exc())
        return False


def login_to_dsb(username, password):
    """登录到 DSB 系统"""
    try:
        # 检查网络连接
        # if not check_internet_connection():
        #     print("错误：无法连接到互联网，请检查网络连接")
        #     return None

        # 检查目标网站
        if not check_target_site():
            print("错误：目标网站无法访问，请检查网站状态或网络代理设置")
            return None

        driver = setup_driver()

        # 访问主页
        print("正在访问主页...")
        driver.get("https://prod.anna-dsb.com/")

        # 等待页面加载完成
        time.sleep(3)  # 给页面一些加载时间

        # 尝试多种方式定位登录按钮
        print("等待登录按钮...")
        try:
            # 方式1：通过文本内容定位
            login_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'LOGIN HERE')]"))
            )
        except:
            try:
                # 方式2：通过class定位
                login_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-primary"))
                )
            except:
                # 方式3：通过链接文本定位
                login_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.LINK_TEXT, "LOGIN HERE"))
                )

        print("点击登录按钮...")
        driver.execute_script("arguments[0].click();", login_button)
        time.sleep(2)  # 等待跳转

        # 等待并填写用户名
        print("填写用户名...")
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
        )
        email_input.send_keys(username)

        # 填写密码
        print("填写密码...")
        password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        password_input.send_keys(password)

        # 点击继续按钮
        print("点击继续按钮...")
        continue_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        continue_button.click()

        # 等待登录成功
        try:
            print("等待登录成功...")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "logged-user"))
            )
            print("登录成功！")
        except Exception:
            raise Exception("登录失败，很可能是用户名密码错误， 请检查 .env/config 文件内容")

        # 等待更长时间以确保所有认证信息都已设置
        time.sleep(5)

        # 执行一些额外的 JavaScript 来保持会话
        driver.execute_script("localStorage.setItem('isAuthenticated', 'true');")

        return driver

    except Exception as e:
        print(f"登录过程中出现错误: {str(e)}")
        print("详细错误信息:")
        import traceback
        print(traceback.format_exc())
        if 'driver' in locals():
            driver.quit()
        return None


def get_base_dir():
    """Gets the base directory for the application."""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return os.path.dirname(sys.executable)
    else:
        # Running as a script
        return os.path.dirname(os.path.abspath(__file__))

def load_config(filepath="config.txt"):
    """Loads configuration variables from a file."""
    config = {}
    try:
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):  # Ignore empty lines and comments
                    key, value = line.split("=", 1)
                    config[key] = value
    except FileNotFoundError:
        print(f"Config file not found: {filepath}")
    if config:
        for key,value in config.items():
            os.environ[key] = value

# To build it: pyinstaller --onefile --add-data "C:\EnvironmentVariables\ChromeDriver\chromedriver.exe;." login.py
# To run it, have a .env file beside it, and run it:
#
def main():
    # 检查操作系统
    platform_info = get_platform_info()
    print(f"\n[系统信息] 操作系统: {platform_info['system']}, 架构: {platform_info['machine']}")
    dotenv_path = os.path.join(get_base_dir(), 'config.txt')
    if os.path.exists(dotenv_path):
        # load_dotenv(dotenv_path=dotenv_path)
        load_config(dotenv_path)
        print(f"\n[加载环境变量] 环境变量加载成功: {dotenv_path}")
    else:
        print(f"\n[加载环境变量] 环境变量加载失败: 没有发现.env/config 文件在路径 {dotenv_path}")

    username = os.getenv('DSB_USERNAME')
    password = os.getenv('DSB_PASSWORD')

    download_date=os.getenv('DSB_DOWNLOAD_DATE')
    if not download_date:
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        download_date = yesterday.strftime("%Y%m%d")
        print("没有设置下载日期, 采用默认日期 D-1 : ", download_date)
    else:
        print("下载日期为: ", download_date)
    download_year=download_date[:4] # 2025 0131

    # if not download_path:
    #     download_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    # print(" 下载文件的文件夹为：", download_path)

    if not username or not password:
        print("[错误] 请在 .env/config 文件中设置 DSB_USERNAME 和 DSB_PASSWORD")
        return

    # 所有要下载的网址放在这里
    download_url_delta_upi_rate = "https://prod.anna-dsb.com/file-download/Records/OTC-Products/Delta/UPI/{}/{}/Rates/Rates-{}.records".format(download_year, download_date, download_date)
    download_url_snapshots_upi_equity = "https://prod.anna-dsb.com/file-download/Records/OTC-Products/Snapshots/UPI/{}/{}/Equity/Equity-{}.records".format(download_year, download_date, download_date)
    download_urls = [
        download_url_delta_upi_rate,
        download_url_snapshots_upi_equity,
        ]

    print("\n[开始] 启动自动化流程...")
    driver = login_to_dsb(username, password)
    if driver:
        try:
            print("[进度] 登录成功，准备下载文件...")

            # 下载文件
            for download_url in download_urls:
                if download_file(driver, download_url):
                    print("\n[成功] 文件下载完成！")
                    print(f"[信息] 文件保存位置: {setup_download_directory()}")
                else:
                    print("\n[失败] 文件 {} 下载到 {} 失败！请确认这个文件真的在网站上存在. ".format(download_url, setup_download_directory()))

            print("\n[完成] 程序执行结束")
        finally:
            sleep(10)
            driver.quit()
    else:
        print("\n[错误] 登录失败，程序终止")


if __name__ == "__main__":
    import platform

    main()