# 凯悦酒店Cookie提取工具

这个工具用于从凯悦酒店网站提取cookie信息，使用Chrome DevTools Protocol (CDP)通过pyppeteer库实现，避免被网站的反爬机制检测到。

## 功能特点

- 使用CDP协议控制Chrome浏览器，比WebDriver更难被检测
- 隐藏浏览器自动化特征，模拟真实用户行为
- 提取所有cookie，包括由JavaScript设置的和标记为HttpOnly的cookie
- 将cookie按不同方式分类保存到JSON文件中
- 适用于Linux服务器环境

## 安装方法

### 在Linux服务器上安装

1. 克隆或下载此项目到服务器
2. 赋予安装脚本执行权限：
   ```
   chmod +x setup.sh
   ```
3. 以root权限运行安装脚本：
   ```
   sudo ./setup.sh
   ```

### 手动安装

1. 确保已安装Python 3和pip
2. 安装所需依赖：
   ```
   pip install -r requirements.txt
   ```
3. 如果在Linux环境下，需要安装Chromium/Chrome相关依赖：
   ```
   sudo apt-get install -y fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 libatspi2.0-0 libcups2 libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 libnspr4 libnss3 libpango-1.0-0 libxcomposite1 libxdamage1 libxfixes3 libxkbcommon0 libxrandr2 xdg-utils libu2f-udev libvulkan1
   ```

## 使用方法

运行以下命令启动程序：

```
python3 test.py
```

程序会：
1. 启动无头Chrome浏览器（隐藏自动化特征）
2. 访问凯悦酒店网站并等待页面完全加载
3. 提取所有cookie信息，包括HttpOnly标记的cookie
4. 将cookie保存到三个不同文件中：
   - `cookies.json`: 所有cookie
   - `httponly_cookies.json`: 只包含HttpOnly的cookie
   - `cookies_by_domain.json`: 按域名分类的cookie

## 工作原理

本工具使用pyppeteer库（Python版的Puppeteer），通过Chrome DevTools Protocol (CDP)控制Chrome浏览器。与传统WebDriver方法相比，CDP：

1. 更难被网站检测到
2. 可以更完整地模拟真实用户行为
3. 可以访问所有cookie，包括由JavaScript设置的
4. 避免了许多反爬虫检测机制

此外，代码还实现了多种反检测措施：
- 修改WebDriver特征
- 随机生成浏览器插件信息
- 修改权限查询行为
- 使用真实的用户代理信息

## 注意事项

- 此工具仅用于教育和研究目的
- 请遵守网站的使用条款和政策
- 频繁使用可能导致您的IP地址被网站封禁