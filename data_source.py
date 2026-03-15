from datetime import datetime
import asyncio
import io
import random
import traceback
from typing import Optional


from nonebot import MessageSegment
from PIL import Image

from .history_today.generate import generate_history_today_poster

from ..convert2img.convert2img import json2imgb64

from .bangumi.generate import (
    generate_calendar,
    download_bangumi_cover_image,
    generate_single_day_calendar,
)
from .epic.generate import download_epic_cover_image, generate_epic_free_poster

from .htmlrender import template_to_pic
from .config import SHOW_FULL
from .constant import FilePath, MainChinaCity, MoyuData, WeekDay, ZodiacInfo
from .api import api_client
from .util import clear_old_file, num_to_string, safe_call
from hoshino.util import pic2b64


async def get_hitokoto_text() -> str:
    try:
        hitokoto = await api_client.get_hitokoto()
        author = hitokoto.from_who or ""
        from_where = f"【{hitokoto.from_}】" if hitokoto.from_ else ""
        return f"{hitokoto.hitokoto} ---{author}{from_where}"
    except Exception as e:
        print(f"获取一言失败: {e}")
        return "如果不能忠于自己的心，胜负又有什么价值呢？ ---【塔希里亚故事集】"


async def get_week_bangumi() -> MessageSegment:

    schedule = await api_client.get_anime()
    image_dict = await download_bangumi_cover_image(schedule)
    saying = await get_hitokoto_text()
    calendar_image = generate_calendar(schedule, image_dict, saying)

    return MessageSegment.image(pic2b64(calendar_image))


async def get_today_bangumi() -> MessageSegment:

    schedule = await api_client.get_anime()
    week_day = datetime.now().weekday()
    data = [schedule[week_day]]
    image_dict = await download_bangumi_cover_image(data)
    saying = await get_hitokoto_text()
    calendar_image = generate_single_day_calendar(
        data[0].items, image_dict, saying, week_day
    )

    return MessageSegment.image(pic2b64(calendar_image))


async def get_moyu_image(use_cache: bool = True) -> MessageSegment:
    now = datetime.now()
    today = now.date()
    file = FilePath.moyu_cache.value / f"{now.date()}.png"
    if use_cache and file.exists():
        return MessageSegment.image(pic2b64(Image.open(str(file))))
    clear_old_file(FilePath.moyu_cache.value)
    fish_index = random.randint(1, 100)
    image_bytes = await template_to_pic(
        template_path=str(FilePath.template.value / "moyu"),
        template_name="main.html",
        templates={
            "top_gif_url": "https://xximg1.meitudata.com/wechat-program/693e5bf550fd1bl4gs928f7732.gif",
            "year_month_text": f"{today.year}年{today.month}月",
            "week_text": f"星期{WeekDay.get_by_value(today.weekday()).name_cn}",
            "day_num": today.day,
            "is_weekend": today.weekday() >= 5,
            "weekend_num": max(0, 5 - today.weekday()),
            "greeting_text": f"{MoyuData.get_geeting(now.hour)}，摸鱼人！工作再忙一定不要忘记休息哦！起身去茶水间，去厕所走走，钱是老板的但命是自己的，祝愿摸鱼人愉快的渡过每一天...`",
            "fortune_text": MoyuData.random_fortune(),
            "fish_index": fish_index,
            "fish_level_text": MoyuData.get_moyu_level(fish_index),
            "zodiac": ZodiacInfo.get_zodiac(today.month, today.day),
            "zodiac_quote": MoyuData.random_zodiac_quote(),
            "fish_img_url": MoyuData.random_fish_img(),
            "salary_lines": MoyuData.calc_salary_lines(today),
            "footer_quote": await get_hitokoto_text(),
        },
        pages={
            "base_url": f"file://{FilePath.template.value}",
            "viewport": {"width": 640, "height": 100},
        },
        wait=2,
    )
    image = Image.open(io.BytesIO(image_bytes))
    image.save(file)
    return MessageSegment.image(pic2b64(image))


async def get_epic_image() -> MessageSegment:
    today = datetime.now().date()
    file = FilePath.epic_cache.value / f"{today}.png"
    if file.exists():
        return MessageSegment.image(pic2b64(Image.open(str(file))))
    games = await api_client.get_epic_free()
    await download_epic_cover_image(games.data)
    result = generate_epic_free_poster(games.data)
    result.save(file)
    return MessageSegment.image(pic2b64(result))


async def get_history_today_image() -> MessageSegment:
    today = datetime.now()
    file = FilePath.history_today_cache.value / f"{today.date()}.png"
    if file.exists():
        return MessageSegment.image(pic2b64(Image.open(str(file))))
    clear_old_file(FilePath.history_today_cache.value)
    data = await api_client.get_today_in_history()
    return MessageSegment.image(pic2b64(generate_history_today_poster(data)))


async def get_report_image(use_cache: bool = True) -> MessageSegment:
    """获取数据"""
    now = datetime.now()
    file = FilePath.report_cache.value / f"{now.date()}.png"
    if use_cache and file.exists():
        return MessageSegment.image(pic2b64(Image.open(str(file))))
    clear_old_file(FilePath.report_cache.value)
    month_cn = f"{num_to_string(now.month)}月"
    day_cn = f"{num_to_string(now.day)}日"
    current_holiday = ""
    data_festival = None
    next_holiday = []
    try:
        moyu = await api_client.get_moyu()
        month_cn = moyu.data.date.lunar.monthCN
        day_cn = moyu.data.date.lunar.dayCN
        if moyu.data.currentHoliday:
            current_holiday = f"【{moyu.data.currentHoliday.name}】假期进行中"
        elif moyu.data.today.isWorkday:
            current_holiday = (
                "悲报: 今天周末要调休上班，但也要坚持摸鱼"
                if moyu.data.today.isWeekend
                else "工作日：低调摸鱼，注意老板"
            )
        elif moyu.data.today.isWeekend:
            current_holiday = "太好了！今天是周末，可以愉快摸鱼！"
        elif moyu.data.today.isHoliday:
            current_holiday = f"节假日：{moyu.data.today.holidayName}，尽情摸鱼吧！"

        data_festival = [
            ("周末", moyu.data.countdown.toWeekEnd),
            ("周五", moyu.data.countdown.toFriday),
            (moyu.data.nextHoliday.name, moyu.data.nextHoliday.until),
        ]
        next_holiday = [
            f"下个带薪摸鱼日【{moyu.data.nextHoliday.name}】",
            f"开始时间：{moyu.data.nextHoliday.date}",
            f"可摸时长：{moyu.data.nextHoliday.duration}天",
            f"是否调休：{'，'.join(moyu.data.nextHoliday.workdays) if moyu.data.nextHoliday.workdays else '无需调休，爽'}",
        ]

    except Exception:
        traceback.print_exc()
        moyu = None

    hitokoto_data, bili_data, six_data, it_data, anime_data = await asyncio.gather(
        safe_call(api_client.get_hitokoto()),
        safe_call(api_client.get_bili()),
        safe_call(api_client.get_today60s()),
        safe_call(api_client.get_it()),
        safe_call(api_client.get_anime()),
    )

    if hitokoto_data:
        hitokoto = (
            f"{hitokoto_data.hitokoto} ---{hitokoto_data.from_who or ''}"
            f"{f'【{hitokoto_data.from_}】' if hitokoto_data.from_ else ''}"
        )
    else:
        hitokoto = None

    bili = (
        [(item.show_name, item.icon) for item in bili_data.list[:11]]
        if bili_data
        else None
    )

    if six_data:
        six_news = six_data.data.news
        six = six_news[:11] if len(six_news) > 11 else six_news
    else:
        six = None

    it = it_data or None

    if anime_data and 0 <= now.weekday() < len(anime_data):
        day_schedule = anime_data[now.weekday()]
        anime_items = [
            (data.name_cn or data.name, data.image) for data in day_schedule.items
        ]
        anime = anime_items[:8] if len(anime_items) > 8 else anime_items
    else:
        anime = None

    image_bytes = await template_to_pic(
        template_path=str(FilePath.template.value / "huannai_report"),
        template_name="main.html",
        templates={
            "data": {
                "current_holiday": current_holiday,
                "next_holiday": next_holiday,
                "data_festival": data_festival or [("获取节日信息失败 QAQ", 0)],
                "data_hitokoto": hitokoto or "获取一言失败 QAQ",
                "data_bili": bili or [("获取B站热点失败 QAQ", None)],
                "data_six": six or ["获取60秒读世界失败 QAQ"],
                "data_anime": anime or ["获取动漫资讯失败 QAQ"],
                "data_it": it or ["获取IT资讯失败 QAQ"],
                "week": WeekDay.get_by_value(now.weekday()).name_cn,
                "date": now.date(),
                "zh_date": f"{month_cn}{day_cn}",
                "full_show": SHOW_FULL,
            }
        },
        pages={
            "viewport": {"width": 578, "height": 1885},
            "base_url": f"file://{FilePath.template.value}",
        },
        wait=2,
    )
    image = Image.open(io.BytesIO(image_bytes))
    if (
        hitokoto and bili and six and it and anime and moyu
    ):  # 只有在数据全部获取成功的情况下才缓存图片
        image.save(file)
    return MessageSegment.image(pic2b64(image))


async def get_oil_image(region: Optional[str] = None) -> MessageSegment:
    region = (
        [region]
        if region
        else [f"{city.value}" for city in MainChinaCity.__members__.values()]
    )
    data = await asyncio.gather(
        *[safe_call(api_client.get_oil_msg(city)) for city in region]
    )

    if not (data := [d for d in data if d]):
        return MessageSegment.text("获取油价信息失败 QAQ")
    tip = "暂无数据"
    if data[0].trend:
        tip = data[0].trend.description
        tip += (
            "，大家相互转告油价又涨了。"
            if data[0].trend.direction == "上调"
            else "，大家赶紧加满油。"
        )
    table = []
    for d in data:
        temp = {"地区": d.region}
        for item in d.items:
            temp[item.name] = str(item.price)
        table.append(temp)

    return json2imgb64(table) + MessageSegment.text(f"{tip}")
