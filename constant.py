from datetime import date, timedelta
from pathlib import Path
from enum import Enum
import random
from typing import List, Optional, Tuple
from PIL import ImageFont, Image


class Theme:
    bg: Tuple[int, int, int] = (245, 246, 248)
    card: Tuple[int, int, int] = (255, 255, 255)
    border: Tuple[int, int, int] = (225, 228, 235)
    text: Tuple[int, int, int] = (20, 24, 32)
    subtext: Tuple[int, int, int] = (90, 98, 112)
    accent: Tuple[int, int, int] = (0, 120, 212)  # 蓝
    ok: Tuple[int, int, int] = (16, 185, 129)  # 绿
    warn: Tuple[int, int, int] = (245, 158, 11)  # 橙


class FilePath(Enum):
    resource = Path(__file__).parent / "resource"
    cache = resource / "cache"
    icon = resource / "icon"
    report_cache = cache / "huannai_report"
    bangumi_cache = cache / "bangumi"
    moyu_cache = cache / "moyu"
    epic_cache = cache / "epic"
    history_today_cache = cache / "history_today"

    template = resource / "html"
    font = resource / "font" / "SourceHanSansCN-Medium.otf"


class Font(Enum):
    font_small = ImageFont.truetype(str(FilePath.font.value), size=14)
    font_medium = ImageFont.truetype(str(FilePath.font.value), size=20)
    font_large = ImageFont.truetype(str(FilePath.font.value), size=24)
    font_extra_large = ImageFont.truetype(str(FilePath.font.value), size=40)


class HistoryTitle(Enum):
    birth = "出生"
    event = "事件"
    death = "逝世"

    @staticmethod
    def get(title: str) -> Optional["HistoryTitle"]:
        if title == "birth":
            return HistoryTitle.birth
        elif title == "event":
            return HistoryTitle.event
        elif title == "death":
            return HistoryTitle.death
        else:
            return None

    @property
    def icon(self) -> Image.Image:
        if self == HistoryTitle.birth:
            return Image.open(FilePath.icon.value / "birth.png")
        elif self == HistoryTitle.event:
            return Image.open(FilePath.icon.value / "event.png")
        elif self == HistoryTitle.death:
            return Image.open(FilePath.icon.value / "death.png")

    @property
    def color(self) -> Tuple[int, int, int]:
        if self == HistoryTitle.birth:
            return (34, 197, 94)
        elif self == HistoryTitle.event:
            return (59, 130, 246)
        elif self == HistoryTitle.death:
            return (239, 68, 68)


class WeekDay(Enum):
    Monday = 0
    Tuesday = 1
    Wednesday = 2
    Thursday = 3
    Friday = 4
    Saturday = 5
    Sunday = 6
    WEEKDAY_COLORS = [
        "#FF0000",
        "#FF8800",
        "#FFCC00",
        "#99FF00",
        "#00FF00",
        "#00CCFF",
        "#0088FF",
    ]
    WEEK = ["一", "二", "三", "四", "五", "六", "日"]

    @property
    def name_cn(self):
        return self.WEEK.value[self.value]

    @property
    def color(self):
        return self.WEEKDAY_COLORS.value[self.value]

    @staticmethod
    def get_by_value(value):
        for day in WeekDay:
            if day.value == value:
                return day
        raise ValueError(f"Invalid weekday value: {value}")


class HackerNewsType:
    top = "top"
    new = "new"
    best = "best"


class SixAPI:
    main_api = "https://60s.viki.moe/"  # 如域名无法访问，可使用公共实例: https://docs.60s-api.viki.moe/7306811m0
    today60s = f"{main_api}v2/60s"
    moyu = f"{main_api}v2/moyu"
    fuel_price = f"{main_api}v2/fuel-price"
    bing = f"{main_api}v2/bing"
    today_history = f"{main_api}v2/today-in-history"
    epic = f"{main_api}v2/epic"

    douying = f"{main_api}v2/douying"
    rednote = f"{main_api}v2/rednote"
    bili = f"{main_api}v2/bili"
    weibo = f"{main_api}v2/weibo"
    baidu_hot = f"{main_api}v2/baidu/hot"
    baidu_teleplay = f"{main_api}v2/baidu/teleplay"
    baidu_tieba = f"{main_api}v2/baidu/tieba"
    toutiao = f"{main_api}v2/toutiao"
    zhihu = f"{main_api}v2/zhihu"
    dongchedi = f"{main_api}v2/dongchedi"
    ncm_rank_list = f"{main_api}v2/ncm-rank/list"

    @staticmethod
    def ncm_rank(rank_id: int):
        return f"{SixAPI.main_api}v2/ncm-rank/{rank_id}"

    @staticmethod
    def hackernews(news_type: str):
        return f"{SixAPI.main_api}v2/hacker-news/{news_type}"

    maoyan_all_movie = f"{main_api}v2/maoyan/all/movie"

    maoyan_realtime_movie = f"{main_api}v2/maoyan/realtime/movie"

    maoyan_realtime_tv = f"{main_api}v2/maoyan/realtime/tv"

    maoyan_realtime_web = f"{main_api}v2/maoyan/realtime/web"


class OtherApi(Enum):
    # 其他API
    hitokoto = "https://v1.hitokoto.cn/?c=a"
    alapi = "https://v3.alapi.cn/api/zaobao"
    bili = "https://s.search.bilibili.com/main/hotword"
    it = "https://www.ithome.com/rss/"
    anime = "https://api.bgm.tv/calendar"


class ZodiacInfo:
    arr = [20, 19, 21, 20, 21, 22, 23, 23, 23, 24, 23, 22]
    zodiacs = [
        "水瓶座",
        "双鱼座",
        "白羊座",
        "金牛座",
        "双子座",
        "巨蟹座",
        "狮子座",
        "处女座",
        "天秤座",
        "天蝎座",
        "射手座",
        "摩羯座",
    ]

    def __init__(self):
        pass

    @staticmethod
    def get_zodiac(month: int, day: int) -> str:
        return (
            ZodiacInfo.zodiacs[month - 1]
            if day < ZodiacInfo.arr[month - 1]
            else ZodiacInfo.zodiacs[month % 12]
        )


class MoyuData:
    fish_img_list = [
        "https://xximg1.meitudata.com/wechat-program/693e5bf1688897bivh8u605913.jpg",
        "https://xximg1.meitudata.com/wechat-program/693e5bf19ebbd9t5mu2zzc9443.jpg",
        "https://xximg1.meitudata.com/wechat-program/693e5bf1947e1ur17sr4i37516.jpg",
        "https://xximg1.meitudata.com/wechat-program/693e5bf1989d2m0bumtx1l8208.jpg",
        "https://xximg1.meitudata.com/wechat-program/693e5bf199b7fhsdrc1q4e1153.jpg",
    ]
    quotes = [
        "奥德彪至死都认为他生活过得不好是因为香蕉拉得不够多",
        "想买一件羽绒服，但是999感冒灵才22块钱，于是我又穿着短裤出门了！早安，打工人！",
        "我真的太喜欢上班了，这种低人一等，累死累活还赚不到钱的感觉，真的太让人着迷了",
        "工资就像大姨妈，一个月来一次，一个星期左右就没了。",
        "小时候不明白章鱼哥天天上班为什么拉着个脸，直到我天天上班我才明白",
        "什么叫万死不辞，就是每天被气死一万次，依然不辞职。",
        "你每天都很忙的样子，可是你又穷，所以你在忙什么？",
        "去看牙，牙医问我年纪轻轻的牙齿怎么磨损这么严重？我说这些年，我都是咬着牙过来的。",
        "办公室为什么一直弥漫着一股海鲜味？原来都是你们在摸鱼？",
        "世界上最痛苦的三件事：上班、早起为了上班、早睡为了早起上班",
        "皮革厂会倒，小姨子会跑，只有你打工到老！加油打工人！",
        "当我一觉醒来精神焕发，我就知道，我迟到了。",
        "上班前：我真的很需要这份工作；上班后：那你去开除我啊",
        "上班还没有存款的人那都叫自费打工",
        "摸鱼时：这钱还挺好赚；认真工作时：你他妈的给我几个钱啊",
        "有人相爱，有人夜里看海，有人七八个闹钟起不来",
        "打工打工两手空空，闹钟一响就要开工",
        "上辈子作恶多端，这辈子早起上班",
        "枯藤老树昏鸦，上班摸鱼，下班回家",
        "古道西风瘦马，老板坐车，我骑爱玛",
        "打工的快乐是你想象不到的，因为打工根本就没有快乐",
        "我上班领的不是薪水，而是精神损失费",
        "世界上只有一种英雄主义，那就是早起上班。",
        "努力不一定被看到 但摸鱼休息一定会。",
        "每天早上睡着都要骂自己几句，怎么找了个早八的工作",
        "今天打工不努力，明日回村掰苞米",
        "只要我一直不努力，老板，就过不上他想要的生活",
        "装模做样上班，真心实意下班",
        "日常四个期盼：等周五、等下班、等快递、等发工资",
        "金窝银窝不如我的办公桌",
        "锄禾日当午，打工好辛苦",
        "放假发的朋友圈叫朋友圈，上班发的朋友圈叫劳改日记",
        "我上班的怨气可以复活十个邪剑仙",
        "余额：你最好创造心情",
        "今日心情：没心情工作",
        "生活不是卡通，请你起床打工。",
        "人之初性本善 不想上班怎么办",
        "如果坐牢有平替，那一定是上班。",
        "刚喝了一杯美式，好苦，跟我的命一样苦。",
        "漫长的岁月 竟没有一天适合上班",
        "没有困难的工作，只有勇敢的打工人",
        "打工只是一场戏，大家因为贫困而相聚",
        "早上多睡了五分钟，电动车都能拧冒烟",
        "一星期 总有那么5天摸鱼上班",
        "葡萄酒开了都要醒五分钟，人醒了却要立刻去上班",
        "加班不是福报 摸鱼才是王道",
    ]
    zodiac_quotes = [
        "灵感爆棚，先摸再说",
        "摸鱼需谨慎，老板在附近",
        "适合摸鱼，不宜内卷",
        "摸鱼效率MAX",
        "小心摸鱼被抓",
    ]

    fortunes = [
        "今日宜摸鱼，忌认真工作",
        "摸鱼时记得屏蔽老板，财运+1",
        "适合带薪拉屎，摸鱼指数拉满",
        "小心领导突击检查，建议低调摸鱼",
        "摸鱼虽好，可不要贪杯哦",
    ]

    def __init__(self):
        pass

    @staticmethod
    def random_fortune() -> str:
        return random.choice(MoyuData.fortunes)

    @staticmethod
    def random_zodiac_quote() -> str:
        return random.choice(MoyuData.zodiac_quotes)

    @staticmethod
    def random_fish_img() -> str:
        return random.choice(MoyuData.fish_img_list)

    @staticmethod
    def get_geeting(hour: int) -> str:

        if 5 <= hour < 9:
            return "早上好"
        elif 9 <= hour < 12:
            return "上午好"
        elif 12 <= hour < 14:
            return "中午好"
        elif 14 <= hour < 18:
            return "下午好"
        else:
            return "晚上好"

    @staticmethod
    def get_moyu_level(fish_index: int) -> str:
        if fish_index >= 90:
            return "🐠 鱼王"
        if fish_index >= 80:
            return "🦈 鱼鲨"
        if fish_index >= 70:
            return "🐟 老油条"
        return "🐡 熟练工" if fish_index >= 60 else "🐣 新手"

    @staticmethod
    def calc_salary_lines(today: date) -> List[str]:
        current_day = today.day
        year, month = today.year, today.month
        # 当月最后一天
        if month == 12:
            last_day = (date(year + 1, 1, 1) - timedelta(days=1)).day
        else:
            last_day = (date(year, month + 1, 1) - timedelta(days=1)).day

        salary_configs = [
            ("月初", 1),
            ("10号", 10),
            ("15号", 15),
            ("20号", 20),
            ("25号", 25),
            ("月底", last_day),
        ]

        lines: List[str] = []
        for name, day in salary_configs:
            if current_day <= day:
                target = date(year, month, day)
            else:
                # 下个月
                ny, nm = (year + 1, 1) if month == 12 else (year, month + 1)
                if name == "月底":
                    # 下个月月底
                    if nm == 12:
                        next_last = (date(ny + 1, 1, 1) - timedelta(days=1)).day
                    else:
                        next_last = (date(ny, nm + 1, 1) - timedelta(days=1)).day
                    target = date(ny, nm, next_last)
                else:
                    target = date(ny, nm, day)

            diff = (target - today).days
            if diff == 0:
                lines.append(f"{name}：今天发薪！🎉")
            elif diff == 1:
                lines.append(f"{name}：明天发！🥳")
            else:
                lines.append(f"{name}：{diff}天")
        return lines


class MainChinaCity(Enum):
    beijing = "北京"
    shanghai = "上海"
    tianjing = "天津"
    chongqing = "重庆"
    fujian = "福建"
    shenzhen = "深圳"
    gansu = "甘肃"
    guangdong = "广东"
    guangxi = "广西"
    guizhou = "贵州"
    hainan = "海南"
    hebei = "河北"
    henan = "河南"
    hubei = "湖北"
    hunan = "湖南"
    jilin = "吉林"
    jiangsu = "江苏"
    jiangxi = "江西"
    liaoning = "辽宁"
    zhejiang = "浙江"
    neimenggu = "内蒙古"
    anhui = "安徽"
    ningxia = "宁夏"
    qinghai = "青海"
    shandong = "山东"
    shanxi = "山西"
    sichuan = "四川"
    xizang = "西藏"
    heilongjiang = "黑龙江"
    xinjiang = "新疆"
    yunnan = "云南"
