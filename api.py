from datetime import datetime
from typing import List
import httpx

from .config import ALAPI_TOKEN

from .model import (
    BiliHot,
    EpicGameData,
    Hitokoto,
    MoyuCalendar,
    OilPriceData,
    Today60SModel,
    TodayHistoryData,
    WeekdaySchedule,
)
from .constant import OtherApi, SixAPI
import xml.etree.ElementTree as ET

CLIENT = httpx.AsyncClient()


class APIClient:
    def __init__(self):
        pass

    async def get_today60s(self):
        resp = await CLIENT.get(SixAPI.today60s)
        return Today60SModel.parse_obj(resp.json())

    async def get_moyu(self):
        resp = await CLIENT.get(SixAPI.moyu)
        return MoyuCalendar.parse_obj(resp.json())

    async def get_oil_msg(self, region: str = "昆山") -> OilPriceData:
        """获取今日油价信息"""
        resp = await CLIENT.get(SixAPI.fuel_price, params={"region": region})
        data = resp.json()
        return OilPriceData.parse_obj(data["data"])

    async def get_epic_free(self):
        """获取Epic免费游戏信息"""
        resp = await CLIENT.get(SixAPI.epic)
        return EpicGameData.parse_obj(resp.json())

    async def get_today_in_history(self):
        """获取历史上的今天信息"""
        resp = await CLIENT.get(SixAPI.today_history)
        return TodayHistoryData.parse_obj(resp.json()["data"])

    async def get_hitokoto(self):
        """获取今日一言"""
        resp = await CLIENT.get(OtherApi.hitokoto.value)
        return Hitokoto.parse_obj(resp.json())

    async def get_bili(self):
        """获取B站热点"""
        resp = await CLIENT.get(
            OtherApi.bili.value,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Referer": "https://www.bilibili.com/",
                "Origin": "https://www.bilibili.com",
            },
        )
        return BiliHot.parse_obj(resp.json())

    async def get_alapi_data(self) -> list[str]:
        """获取alapi数据"""
        res = await CLIENT.post(
            OtherApi.alapi.value,
            data={"token": ALAPI_TOKEN, "format": "json"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if res.status_code != 200:
            return ["Error: Unable to fetch data"]
        data = res.json()
        news_items = data.get("data", {}).get("news", [])
        return news_items[:11] if len(news_items) > 11 else news_items

    async def get_it(self) -> list[str]:
        """获取IT资讯"""
        res = await CLIENT.get(OtherApi.it.value)
        root = ET.fromstring(res.text)
        titles = []
        for item in root.findall("./channel/item"):
            title_element = item.find("title")
            if title_element is not None:
                titles.append(title_element.text)
        return titles[:11] if len(titles) > 11 else titles

    async def get_anime(self) -> List[WeekdaySchedule]:
        resp = await CLIENT.get(OtherApi.anime.value)
        return [WeekdaySchedule(**day) for day in resp.json()]


api_client = APIClient()
