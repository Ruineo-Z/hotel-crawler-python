# hotel-crawler-python

这是一个基于 [APScheduler](https://apscheduler.readthedocs.io/) 与 [Playwright](https://playwright.dev/python/)
实现的定时爬虫项目，用于每日定时爬取指定酒店页面中的房型及价格信息，并写入数据库。

## 功能特性

- ⏰ 每天早上 8:00 定时自动执行爬取任务
- 🌐 使用 Playwright 处理页面渲染
- 📅 使用 APScheduler 作为任务调度器
- 🏨 可配置多家酒店目标链接
- 🛠 数据结果结构标准，方便后续存储与分析

---

## 项目结构

```
├── schedule.py # 任务调度主脚本，定义定时任务与酒店列表
├── hotel_crawler.py # 核心爬虫逻辑及数据库接口定义
├── requirements.txt # 依赖库
├── logger.py # 日志配置
├── run.sh # 项目启动脚本
└── README.md # 项目说明文件
```

---

## 使用方式

```bash
chmod +x run.sh
./run.sh
```

## 参数配置

* 在 schedule.py 中设置目标页面列表`HOTEL_LIST`
* 在 hotel_crawler.py 中的 HotelCrawler 类定义数据库地址`database_url`

## 爬取数据结构示例

```json
[
  {"room_name": "经典客房, 客房, 2 张单人床, 城市景观", "room_lowest_price": 588},
  {"room_name": "豪华客房, 客房, 2 张单人床, 双塔景观", "room_lowest_price": 630},
  {"room_name": "高级客房, 客房, 1 张特大床", "room_lowest_price": 672},
  {"room_name": "行政豪华客房, 行政酒廊礼遇, 客房, 2 张单人床", "room_lowest_price": 672},
  {"room_name": "豪华客房, 客房, 1 张特大床, 双塔景观", "room_lowest_price": 714},
  {"room_name": "主题亲子房, 客房, 2 张单人床", "room_lowest_price": 739},
  {"room_name": "行政豪华客房, 行政酒廊礼遇, 客房, 1 张特大床", "room_lowest_price": 756},
  {"room_name": "主题亲子房, 客房, 1 张特大床", "room_lowest_price": 835},
  {"room_name": "副总统套房, 行政酒廊礼遇, 套房, 1 张特大床, 城市景观", "room_lowest_price": 3429}
]
```