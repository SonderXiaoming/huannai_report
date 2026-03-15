import asyncio
import datetime
import io
import math
from pathlib import Path
from typing import Dict, List, Optional
from PIL import Image, ImageDraw, ImageFilter
import httpx

from ..util import ellipsize

from ..download import download_image_with_retries
from ..constant import FilePath, Font, Theme, WeekDay
from ..model import EventDetail, WeekdaySchedule

PADDING = 8
CANVAS_W = 1080
MARGIN = 48
CARD_BG = (255, 255, 255)


FONT_H1 = Font.font_extra_large.value
FONT_H2 = Font.font_large.value
FONT_BODY = Font.font_large.value
FONT_SMALL = Font.font_medium.value
FONT_TINY = Font.font_small.value


def choose_image_url(item: EventDetail) -> Optional[str]:
    if not item.images:
        return None
    for attr in ("common", "grid", "small", "medium", "large"):
        if url := getattr(item.images, attr, None):
            return str(url)
    return None


async def download_bangumi_cover_image(
    schedule: List[WeekdaySchedule],
) -> Dict[str, Optional[bytes]]:
    images = [
        (url, item.name_cn or item.name)
        for day in schedule
        for item in day.items
        if (url := choose_image_url(item))
    ]
    sem = asyncio.Semaphore(12)
    async with httpx.AsyncClient(follow_redirects=True) as client:
        tasks = [
            download_image_with_retries(
                client,
                url,
                sem,
                cache_path=FilePath.bangumi_cache.value / Path(url.split("/")[-1]),
            )
            for (url, _) in images
        ]
        results_list = await asyncio.gather(*tasks)
        results = {name: content for (_, name), content in zip(images, results_list)}

    return results


# ============================
# Config
# ============================


def add_shadow(base_img, rect_xy, radius=24, offset=(0, 8), shadow_alpha=70):
    x1, y1, x2, y2 = rect_xy
    w = x2 - x1
    h = y2 - y1
    shadow = Image.new("RGBA", (w + 80, h + 80), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle(
        [40, 40, 40 + w, 40 + h], radius=radius, fill=(0, 0, 0, shadow_alpha)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(16))
    base_img.paste(shadow, (x1 - 40 + offset[0], y1 - 40 + offset[1]), shadow)


def round_corners(im, radius=16):
    im = im.convert("RGBA")
    mask = Image.new("L", im.size, 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, im.size[0], im.size[1]], radius=radius, fill=255)
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    return out


def draw_title(title: str, saying: str) -> Image.Image:
    canvas = Image.new("RGBA", (CANVAS_W, 78), Theme.bg)
    draw = ImageDraw.Draw(canvas)

    draw.text((MARGIN, 0), title, font=FONT_H1, fill=Theme.text)

    now_str = datetime.datetime.now().strftime("%Y-%m-%d")
    draw.text(
        (CANVAS_W - MARGIN * 3, 14),
        now_str,
        font=FONT_SMALL,
        fill=Theme.subtext,
        anchor="ra",
    )
    draw.text(
        (CANVAS_W - MARGIN * 2, 40),
        ellipsize(saying.split("-")[0], FONT_SMALL, CANVAS_W // 2),
        font=FONT_SMALL,
        fill=Theme.subtext,
        anchor="ra",
    )

    return canvas


def render_day_section(
    data: List[EventDetail],
    image_dict: Dict[str, Optional[bytes]],
    week_num: int,
    is_today=False,
) -> Image.Image:
    week = WeekDay.get_by_value(week_num)
    # sizing
    pad = 18
    header_h = 64
    gap_y = 14
    cols = 4
    tile_gap_x = 10  # 减小间距以留出更多空间给卡片
    tile_gap_y = 12
    w = CANVAS_W - 2 * MARGIN - pad * 2
    # 确保最后一列不会超出边界：w = pad + col0 + gap + col1 + gap + col2 + gap + col3 + pad
    tile_w = (w - 2 * pad - tile_gap_x * (cols - 1)) // cols
    tile_h = 158

    rows = max(1, math.ceil(len(data) / cols)) if data else 1
    h_total = pad + header_h + gap_y + rows * tile_h + (rows - 1) * tile_gap_y + pad
    img = Image.new("RGBA", (w, h_total), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # shadow + card
    add_shadow(img, (0, 0, w, h_total), radius=26, offset=(0, 10), shadow_alpha=55)

    # today highlight border
    draw.rounded_rectangle(
        (0, 0, w, h_total),
        radius=26,
        fill=CARD_BG,
        outline=week.color if is_today else Theme.border,
        width=3 if is_today else 1,
    )

    # header
    dot_r = 10
    dot_x = pad + 4
    dot_y = pad + 22
    draw.ellipse(
        [dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r], fill=week.color
    )

    draw.text((pad + 26, pad + 6), f"星期{week.name_cn}", font=FONT_H2, fill=Theme.text)

    # TODAY badge
    if is_today:
        badge = "TODAY / 今天"
        bw = draw.textlength(badge, font=FONT_SMALL)
        bx2 = w - pad
        bx1 = bx2 - bw - 20
        by1 = pad + 8
        by2 = by1 + 34
        draw.rounded_rectangle(
            (bx1, by1, bx2, by2),
            radius=16,
            fill=(255, 245, 246),
            outline=week.color,
            width=2,
        )
        draw.text((bx1 + 10, by1 + 6), badge, font=FONT_SMALL, fill=Theme.text)

    # divider
    div_y = pad + header_h
    draw.line((pad, div_y, w - pad, div_y), fill=Theme.border, width=1)

    # grid
    start_y = div_y + gap_y
    for idx, it in enumerate(data):
        r = idx // cols
        c = idx % cols
        tx = pad + c * (tile_w + tile_gap_x)
        ty = start_y + r * (tile_h + tile_gap_y)

        draw.rounded_rectangle(
            (tx, ty, tx + tile_w, ty + tile_h),
            radius=20,
            fill=(255, 255, 255),
            outline=Theme.border,
            width=1,
        )
        title = it.name_cn or it.name
        if cover := image_dict.get(title):
            cover = Image.open(io.BytesIO(cover)).convert("RGB")
            cover = cover.resize((80, 110))
        else:
            cover = Image.new("RGB", (80, 110), (220, 220, 225))
            d = ImageDraw.Draw(cover)
            d.line((0, 0, 80, 110), fill=(180, 180, 190), width=3)
            d.line((0, 110, 80, 0), fill=(180, 180, 190), width=3)
        cover = round_corners(cover, radius=14)
        # cover 放在左中部（竖直居中在内容区）
        img.paste(cover, (tx + 15, ty + 8), cover)

        score = (
            (
                f"{it.rating.score:.1f}"
                if it.rating.total is None
                else f"{it.rating.score:.1f} ({it.rating.total})"
            )
            if it.rating and it.rating.score
            else None
        )
        doing = (
            it.collection.doing
            if it.collection and it.collection.doing is not None
            else None
        )

        dtext = f"观看：{doing}" if doing else "—"
        draw.text(
            (tx + tile_w - 14, ty + 25),
            dtext,
            font=FONT_TINY,
            fill=Theme.subtext,
            anchor="ra",
        )

        # 评分和 doing 在中部
        left_line = f"评分：{score}" if score else "—"
        draw.text(
            (tx + tile_w - 14, ty + 55),
            left_line,
            font=FONT_TINY,
            fill=Theme.subtext,
            anchor="ra",
        )

        draw.text(
            (tx + tile_w - 14, ty + 85),
            f"放送 {it.air_date}",
            font=FONT_TINY,
            fill=Theme.subtext,
            anchor="ra",
        )

        # 名称放在最下面
        title_y = ty + tile_h - 28
        draw.text(
            (tx + 10, title_y),
            ellipsize(title, FONT_TINY, tile_w - 20),
            font=FONT_TINY,
            fill=Theme.text,
        )

    # empty state
    if not data:
        draw.text(
            (pad, start_y + 10),
            "（今天没有条目）",
            font=FONT_BODY,
            fill=Theme.subtext,
        )

    return img


def generate_calendar(
    data: List[WeekdaySchedule],
    image_dict: Dict[str, Optional[bytes]],
    saying: str,
    title="Bangumi 周放送",
):
    today = datetime.datetime.now()  # Mon=0..Sun=6
    today_week = today.weekday()
    title = draw_title(title, saying)
    days = [
        render_day_section(day.items, image_dict, i, is_today=(i == today_week))
        for i, day in enumerate(data)
    ]
    CANVAS_H = sum(day.size[1] + 18 for day in days) + 2 * MARGIN + title.size[1] + 14
    img = Image.new("RGBA", (CANVAS_W, CANVAS_H), Theme.bg)
    img.paste(title, (0, MARGIN), title)
    y = MARGIN + title.size[1] + 14
    for day in days:
        img.paste(day, (MARGIN + 18, y), day)
        y += day.size[1] + 18

    return img


def generate_single_day_calendar(
    data: List[EventDetail],
    image_dict: Dict[str, Optional[bytes]],
    saying: str,
    week_num: int,
    title="Bangumi 每日放送",
):
    title = draw_title(title, saying)
    day_section = render_day_section(
        data,
        image_dict,
        week_num,
        is_today=True,
    )
    CANVAS_H = day_section.size[1] + 2 * MARGIN + title.size[1] + 14
    img = Image.new("RGBA", (CANVAS_W, CANVAS_H), Theme.bg)
    img.paste(title, (0, MARGIN), title)
    img.paste(day_section, (MARGIN + 18, MARGIN + title.size[1] + 14), day_section)

    return img
