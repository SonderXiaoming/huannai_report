from datetime import datetime
import traceback

from .util import clear_old_file
from .data_source import (
    get_epic_image,
    get_history_today_image,
    get_hitokoto_text,
    get_moyu_image,
    get_oil_image,
    get_today_bangumi,
    get_week_bangumi,
    get_report_image,
)
from hoshino import Service
from hoshino.typing import MessageSegment, CQHttpError, CQEvent, HoshinoBot
from .api import api_client
from .constant import FilePath

HELP_MSG = """每日早报
启用后会在每天早上发送一份早报
[@bot 环奈日报] 手动发送一份早报
[今日早报] 手动发送一份60s早报
[今日番剧] 手动发送一份今日番剧
[本周番剧] 手动发送一份本周番剧
[每日一言] 手动发送一条每日一言
[摸鱼日历] 手动发送一份摸鱼日历
[地区 + 今日油价 + 省份] 发送今日油价，如上海今日油价，不写则显示主要城市油价
[历史上的今天] 手动发送一份历史上的今天海报
[epic免费游戏] 手动发送一份epic免费游戏海报
"""

sv = Service(
    "huannai_report",
    enable_on_default=True,
    help_=HELP_MSG,
)


@sv.on_fullmatch("日报帮助")
async def send_help(bot: HoshinoBot, ev: CQEvent):
    await bot.send(ev, HELP_MSG)


@sv.on_fullmatch("环奈日报", only_to_me=True)
async def send_report(bot: HoshinoBot, ev: CQEvent):
    try:
        img = await get_report_image(False)
        await bot.send(ev, img)
    except Exception:
        traceback.print_exc()
        await bot.send(ev, "wuwuwu~出了点问题")


@sv.on_fullmatch("今日早报")
async def handnews(bot: HoshinoBot, ev: CQEvent):
    resp = await api_client.get_today60s()
    await bot.send(ev, MessageSegment.image(resp.data.image, cache=True))


@sv.on_fullmatch("每日番剧", "本周番剧")
async def send_week_bangumi(bot, ev: CQEvent):
    try:
        img = await get_week_bangumi()
        await bot.send(ev, img)
    except Exception:
        traceback.print_exc()
        await bot.send(ev, "wuwuwu~出了点问题")


@sv.on_fullmatch("今日番剧")
async def send_today_bangumi(bot, ev: CQEvent):
    try:
        img = await get_today_bangumi()
        await bot.send(ev, img)
    except Exception:
        traceback.print_exc()
        await bot.send(ev, "wuwuwu~出了点问题")


@sv.on_fullmatch("每日一言")
async def send_daily_hitokoto(bot, ev: CQEvent):
    try:
        saying = await get_hitokoto_text()
        await bot.send(ev, saying)
    except Exception:
        traceback.print_exc()
        await bot.send(ev, "wuwuwu~出了点问题")


@sv.on_fullmatch("摸鱼日历")
async def send_moyu_calendar(bot, ev: CQEvent):
    try:
        img = await get_moyu_image()
        await bot.send(ev, img)
    except Exception:
        traceback.print_exc()
        await bot.send(ev, "wuwuwu~出了点问题")


@sv.on_suffix("今日油价")
async def send_oil_price(bot, ev: CQEvent):
    try:
        await bot.send(ev, await get_oil_image(ev.message.extract_plain_text().strip()))
    except Exception:
        traceback.print_exc()
        await bot.send(ev, "wuwuwu~出了点问题")


@sv.on_fullmatch("epic免费游戏")
async def send_epic_free(bot, ev: CQEvent):
    try:
        img = await get_epic_image()
        await bot.send(ev, img)
    except Exception:
        traceback.print_exc()
        await bot.send(ev, "wuwuwu~出了点问题")


@sv.on_fullmatch("历史上的今天")
async def send_history_today(bot, ev: CQEvent):
    try:
        await bot.send(ev, await get_history_today_image())
    except Exception:
        traceback.print_exc()
        await bot.send(ev, "wuwuwu~出了点问题")


@sv.scheduled_job("cron", hour="0", minute="5")
async def auto_send_daily_bangumi():
    now = datetime.now()
    if now.weekday() == 6:
        clear_old_file(FilePath.bangumi_cache.value)  # 每周日清理缓存
        clear_old_file(FilePath.epic_cache.value)  # 顺便清理一下epic缓存
    img = await get_today_bangumi()
    await sv.broadcast(img, "auto_send_daily_bangumi", 2)


@sv.scheduled_job("cron", hour="8", minute="40", jitter=50)
async def autoreport():
    try:
        img = await get_report_image()
        await sv.broadcast(img, "huannai_report", 2)
    except CQHttpError as e:
        sv.logger.error(f"daily news error {e}")
        raise


@sv.scheduled_job("cron", hour="10", minute="00", jitter=50)
async def auto_moyu_calendar():
    try:
        img = await get_moyu_image()
        await sv.broadcast(img, "auto_moyu_calendar", 2)
    except CQHttpError as e:
        sv.logger.error(f"moyu calendar error {e}")
        raise
