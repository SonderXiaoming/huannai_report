from uuid import UUID
from pydantic import BaseModel, Field, HttpUrl
from typing import Any, Dict, List, Optional


# =========================60秒读世界数据模型========================
class Today60SData(BaseModel):
    api_updated: str
    api_updated_at: int
    cover: str
    created: str
    created_at: int
    date: str
    day_of_week: str
    image: str
    link: str
    lunar_date: str
    news: List[str]
    tip: str
    updated: str
    updated_at: int


class Today60SModel(BaseModel):
    code: int
    data: Today60SData
    message: str


# =========================摸鱼日历数据模型========================
class LunarDate(BaseModel):
    year: int
    month: int
    day: int
    yearCN: str
    monthCN: str
    dayCN: str
    isLeapMonth: bool
    yearGanZhi: str
    monthGanZhi: str
    dayGanZhi: str
    zodiac: str


class DateInfo(BaseModel):
    gregorian: str
    weekday: str
    dayOfWeek: int
    lunar: LunarDate


class TodayInfo(BaseModel):
    isWeekend: bool
    isHoliday: bool
    isWorkday: bool
    holidayName: Optional[str] = None
    solarTerm: Optional[str] = None
    lunarFestivals: List[str] = Field(default_factory=list)


class ProgressUnit(BaseModel):
    passed: int
    total: int
    remaining: int
    percentage: int


class ProgressInfo(BaseModel):
    week: ProgressUnit
    month: ProgressUnit
    year: ProgressUnit


class CurrentHolidayInfo(BaseModel):
    name: str
    dayOfHoliday: int
    daysRemaining: int
    totalDays: int


class NextHolidayInfo(BaseModel):
    name: str
    date: str
    until: int
    duration: int
    workdays: List[Any] = Field(default_factory=list)


class NextWeekendInfo(BaseModel):
    date: str
    weekday: str
    daysUntil: int


class CountdownInfo(BaseModel):
    toWeekEnd: int
    toFriday: int
    toMonthEnd: int
    toYearEnd: int


class DataPayload(BaseModel):
    date: DateInfo
    today: TodayInfo
    progress: ProgressInfo
    currentHoliday: Optional[CurrentHolidayInfo] = None
    nextHoliday: NextHolidayInfo
    nextWeekend: NextWeekendInfo
    countdown: CountdownInfo
    moyuQuote: str


class DebugInfo(BaseModel):
    api_name: str
    api_version: str
    api_docs: str
    author: str
    user_group: str
    github_repo: str
    updated: str
    updated_at: int


class MoyuCalendar(BaseModel):

    code: int
    message: str
    data: DataPayload
    debug: Optional[DebugInfo] = Field(default=None, alias="__debug__")


# =========================动漫日程数据模型========================
class Weekday(BaseModel):
    en: str
    cn: str
    ja: str
    id: int


class Rating(BaseModel):
    total: int
    count: Dict[str, int]
    score: float


class Images(BaseModel):
    large: Optional[HttpUrl] = None
    common: Optional[HttpUrl] = None
    medium: Optional[HttpUrl] = None
    small: Optional[HttpUrl] = None
    grid: Optional[HttpUrl] = None


class Collection(BaseModel):
    doing: Optional[int] = 0


class EventDetail(BaseModel):
    id: int
    url: HttpUrl
    type: int
    name: str
    name_cn: Optional[str] = None
    summary: Optional[str] = ""
    air_date: Optional[str] = None
    air_weekday: Optional[int] = None
    rating: Optional[Rating] = None
    rank: Optional[int] = None
    images: Optional[Images] = None
    collection: Optional[Collection] = None

    @property
    def image(self) -> str:
        return self.images.large if self.images else ""


class WeekdaySchedule(BaseModel):
    weekday: Weekday
    items: List[EventDetail]


# =========================今日一言数据模型========================
class Hitokoto(BaseModel):
    id: int
    uuid: UUID
    hitokoto: str
    type: str
    from_: str = Field(..., alias="from")  # “from” 是保留字，用 alias
    from_who: Optional[str] = None
    creator: str
    creator_uid: int
    reviewer: int
    commit_from: str
    created_at: str
    length: int


# =========================B站热点数据模型========================
class StatDatas(BaseModel):
    stime: Optional[str] = None
    etime: Optional[str] = None
    is_commercial: Optional[str] = None


class HotItem(BaseModel):
    hot_id: int
    keyword: str
    show_name: str
    score: float
    word_type: int
    goto_type: int
    goto_value: str
    icon: str
    live_id: List[int]
    call_reason: int
    heat_layer: str
    pos: int
    id: int
    status: str
    name_type: str
    resource_id: int
    set_gray: int
    card_values: List[Any]
    heat_score: int
    stat_datas: StatDatas


class BiliHot(BaseModel):
    code: int
    exp_str: str
    list: List[HotItem]
    top_list: List[Any]
    hotword_egg_info: str
    seid: str
    timestamp: int
    total_count: int


# ========================今日油价数据模型========================
class OilTrend(BaseModel):
    next_adjustment_date: str
    direction: str
    change_ton: int
    change_ton_desc: str
    change_liter_min: float
    change_liter_max: float
    change_liter_desc: str
    description: str


class OilItem(BaseModel):
    name: str
    price: float
    price_desc: str


class OilPriceData(BaseModel):
    trend: OilTrend
    items: List[OilItem]
    link: str
    region: str
    updated: str
    updated_at: int


# =========================epic========================


class EpicGame(BaseModel):
    """游戏封面图"""

    cover: str
    """游戏描述"""
    description: str
    """免费结束时间字符串"""
    free_end: str
    """免费结束时间戳（13 位）"""
    free_end_at: int
    """免费开始时间字符串"""
    free_start: str
    """免费开始时间戳（13 位）"""
    free_start_at: int
    """ID"""
    id: str
    """当前是否免费"""
    is_free_now: bool
    """游戏详情页"""
    link: str
    """原价（数字，单位为人民币元）"""
    original_price: int
    """已格式化原价描述（带单位）"""
    original_price_desc: str
    """发行厂商/销售商"""
    seller: str
    """游戏名称"""
    title: str


class EpicGameData(BaseModel):
    code: int
    data: List[EpicGame]
    message: str


# =========================今日历史数据模型========================


class HistoryEventDetail(BaseModel):
    """事件描述"""

    description: str
    """事件类型，death/event/birth"""
    event_type: str
    """百科详情链接"""
    link: str
    """标题"""
    title: str
    """年份"""
    year: str


class TodayHistoryData(BaseModel):
    """日期（几月几号）"""

    date: str
    """日"""
    day: int
    """事件列表"""
    items: List[HistoryEventDetail]
    """月份"""
    month: int
