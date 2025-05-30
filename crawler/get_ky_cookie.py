import webbrowser
import browser_cookie3
import time
import subprocess
import psutil
import os
import sqlite3
import shutil


def get_hyatt_cookie_via_browser():
    """通过webbrowser打开Chrome并获取cookie"""
    # 使用webbrowser打开Chrome访问Hyatt网站
    url = 'https://www.hyatt.com/zh-CN/home'
    webbrowser.open(url)
    time.sleep(20)

    # 从Chrome中读取cookie
    try:
        cj = browser_cookie3.chrome(domain_name='hyatt.com')
        for cookie in cj:
            if cookie.name == 'tkrm_alpekz_s1.3':
                return cookie.value
    except Exception as e:
        print(f"获取cookie失败: {e}")

    return None


def close_chrome():
    """关闭Chrome浏览器进程"""
    try:
        # macOS系统
        subprocess.run(['pkill', '-f', 'Google Chrome'], check=False)

        # 或者使用psutil更精确地控制
        for proc in psutil.process_iter(['pid', 'name']):
            if 'chrome' in proc.info['name'].lower():
                proc.kill()

        print("Chrome浏览器已关闭")
    except Exception as e:
        print(f"关闭Chrome失败: {e}")


def delete_hyatt_cookies():
    """删除Chrome中Hyatt网站的所有cookie"""
    # Chrome cookie数据库路径
    db_path = os.path.join(
        os.path.expanduser("~"),
        "Library/Application Support/Google/Chrome/Default/Cookies"
    )

    # 复制数据库文件（避免锁定问题）
    temp_db = "temp_cookies.db"
    shutil.copyfile(db_path, temp_db)

    try:
        # 连接数据库
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # 删除Hyatt相关的cookie
        cursor.execute(
            "DELETE FROM cookies WHERE host_key LIKE '%hyatt.com%'"
        )

        conn.commit()
        conn.close()

        # 将修改后的数据库复制回原位置
        shutil.copyfile(temp_db, db_path)
        os.remove(temp_db)

        print("Hyatt网站cookie已删除")

    except Exception as e:
        print(f"删除cookie失败: {e}")


if __name__ == '__main__':
    cookie = get_hyatt_cookie_via_browser()
    print(cookie)
    close_chrome()
    delete_hyatt_cookies()
