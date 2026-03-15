# 环奈日报

《HoshinoBot 每日资讯辅助工具》

★ 如果你喜欢的话，请给仓库点一个 Star 支持一下 23333 ★

本项目地址：
https://github.com/SonderXiaoming/huannai_report

## 部署教程

### 1. 下载或 git clone 本插件

在 HoshinoBot/hoshino/modules 目录下使用以下命令拉取本项目：

```bash
git clone https://github.com/SonderXiaoming/huannai_report
```

### 2. 启用插件

在 HoshinoBot/hoshino/config/bot.py 文件的 MODULES_ON 加入：

```python
'huannai_report'
```

然后重启 HoshinoBot。

### 3. 依赖安装

在插件目录执行：

```bash
pip install -r requirements.txt
```

项目使用了 htmlrender（Playwright 截图），可能还需要执行：

```bash
playwright install chromium
```

## 指令

### 帮助

【日报帮助】 查看插件帮助。

### 手动触发

【@bot 环奈日报】 手动发送一份日报。

【今日早报】 手动发送一份 60s 早报。

【今日番剧】 手动发送今日番剧海报。

【每日番剧】 或 【本周番剧】 手动发送本周番剧海报。

【每日一言】 手动发送一条每日一言。

【摸鱼日历】 手动发送摸鱼日历海报。

【地区 + 今日油价】 发送今日油价，例如：上海今日油价。

【历史上的今天】 手动发送历史上的今天海报。

【epic免费游戏】 手动发送 Epic 免费游戏海报。

## 自动推送

本插件默认支持定时自动推送：

1. 每天 00:05 推送今日番剧。
2. 每天 08:40（带随机抖动）推送日报。
3. 每天 10:00（带随机抖动）推送摸鱼日历。

另外，每周日会自动清理番剧缓存与 Epic 缓存。

## 预览

![日报预览](https://github.com/user-attachments/assets/b6725400-bcff-4612-8f60-76ba9a3734f4)

![摸鱼日历预览](https://github.com/user-attachments/assets/de11a6a6-c03f-459d-9ead-640137cf328b)

![长图预览](https://github.com/user-attachments/assets/a0c07d03-c55e-4061-81ff-605412e805af)

## 说明

1. 若出现截图渲染失败，请先检查 Playwright 浏览器是否安装。
2. 若第三方接口波动，可能出现偶发获取失败，稍后重试即可。
3. 缓存目录建议加入忽略规则，避免缓存图片提交到 Git。

## TODO

1. 适配更多 60s API 报告类型，扩展更多可视化内容。
2. 欢迎 PR，一起完善这个插件。
3. 作者最近比较忙，维护时间有限，更新节奏可能较慢。

## 项目参考

1. 60s 项目（本插件核心数据源）
   https://github.com/vikiboss/60s

2. 60s 在线 API（项目默认使用）
   https://60s.viki.moe/

3. Bangumi API（番剧日历）
   https://api.bgm.tv/calendar

4. Hitokoto API（每日一言）
   https://v1.hitokoto.cn/

5. 哔哩哔哩热搜接口（热点数据）
   https://s.search.bilibili.com/main/hotword

6. IT 之家 RSS（IT 资讯）
   https://www.ithome.com/rss/

7. ALAPI（可选早报数据源，需自行配置 token）
   https://v3.alapi.cn/
