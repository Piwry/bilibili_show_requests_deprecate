# Bilibili_show_ticket_order

> 目前仍未达到运行要求, 在第一个版本发布前不建议使用......

Bilibili会员购抢票助手, 通过B站接口抢购目标漫展/演出

本脚本仅供学习交流使用, 不得用于商业用途, 如有侵权请联系删除

## 使用

### 傻瓜式

请先安装[Python](https://www.python.org/downloads/)到目录**D:\Program Files\Python**, 除非你打算自己设置cookie, 然后安装[Chrome浏览器](https://www.google.com/chrome/), 然后在[Release页面](https://github.com/Hobr/Bilibili_show_ticket_order/releases)下载预载了运行环境的压缩包

解压后进入目录, 点击**run.cmd**运行, 根据提示输入信息即可

### 命令行

```bash
git clone https://github.com/Hobr/Bilibili_show_ticket_order.git
cd Bilibili_show_ticket_order
pip install -r requirements.txt
python init.py
```

## 模式

- API模式
  - 使用requests, 调用B站的API接口抢票
  - 效率更高, 适合开票时抢票
  - B站更新API后可能失效
  - 短时间内抢不到的话有可能被风控BanIP

- 浏览器模式
  - 使用selenium, 模拟浏览器操作抢票
  - 更稳定, 适合长期蹲退票
  - 速度较慢, 是一款高端连点器, 且需要浏览器driver

## 配置说明

- global 全局配置
  - init 初始化状态, 0为未初始化, 1为已初始化
  - mode 运行模式, 0为API模式, 1为浏览器模式
  - process 进程数, 1为单进程, 大于1为多线程
  - timeout 请求超时时间, 单位为秒, 调用api时使用
  - timestop 操作间隔时间, 单位为秒, 避免过快请求被风控
  - step 当前执行进度
  - url 目标商品详情页地址, 用于获取project_id
  - buyerList 购票人
  - screennum 横向场次序号, 从0开始
  - skunum 横向价格序号, 从0开始
  - auth 实名认证, 0为不实名, 1为实名
  - type 商品类型, 0为常规, 1为选座, 2为纸质票(选择收货人)
  - fullToken 完整的token, 由firToken和secToken拼接而成
  - firToken 时间戳token, 通过api第一步获取
  - secToken 商品token
  - cookie 用户cookie
  - version 脚本版本

- api
  - project_id 商品id, 对应url里的'id'
  - screen_id 场次id
  - sku_id 价格id
  - buyer 处理后的购票人, 对应buyList里的'name'
  - pay_money 支付金额
  - order_token 订单token
  - order_id 订单id
  - headers 请求头

- browser
  - headless 是否无头模式, 0为否, 1为是

## API文档

记录一下会员购下单api的参数, 以便后续更新

参考商品:

- 选座+实名 <https://show.bilibili.com/platform/detail.html?id=71951>
- 非实名 <https://show.bilibili.com/platform/detail.html?id=72099>
- 纸质票+非实名 <https://show.bilibili.com/platform/detail.html?id=72271>
- 选择日期+非实名 <https://show.bilibili.com/platform/detail.html?id=71519>
