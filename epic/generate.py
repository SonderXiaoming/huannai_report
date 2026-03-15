import asyncio
from typing import Dict, List, Optional, Tuple

from PIL import Image, ImageDraw
import httpx

from ..download import download_image_with_retries
from ..model import EpicGame
from ..util import ellipsize, wrap_text

from ..constant import FilePath, Theme, Font


def placeholder_cover(size: Tuple[int, int]) -> Image.Image:
    w, h = size
    im = Image.new("RGB", (w, h), (230, 233, 238))
    d = ImageDraw.Draw(im)
    txt = "NO\nCOVER"
    # 居中
    tw = max(
        d.textlength(line, font=Font.font_large.value) for line in txt.splitlines()
    )
    th = 0
    for line in txt.splitlines():
        bbox = d.textbbox((0, 0), line, font=Font.font_large.value)
        th += (bbox[3] - bbox[1]) + 6
    x = (w - tw) // 2
    y = (h - th) // 2
    for line in txt.splitlines():
        d.text((x, y), line, font=Font.font_large.value, fill=(120, 128, 140))
        y += 30
    return im


async def download_epic_cover_image(data: List[EpicGame]) -> Dict[str, Optional[bytes]]:
    sem = asyncio.Semaphore(12)
    images = [(item.cover, item.title) for item in data]
    async with httpx.AsyncClient(follow_redirects=True) as client:
        tasks = [
            download_image_with_retries(
                client, url, sem, cache_path=FilePath.epic_cache.value / name
            )
            for url, name in images
        ]
        await asyncio.gather(*tasks)


def generate_epic_free_poster(
    data: List[EpicGame],
    width=1200,
    outer_padding=38,  # 外边距
    card_gap=18,  # 卡片间距
    radius=26,  # 圆角
    inner_padding=24,  # 卡片内边距
    cover_w=280,
    cover_h=160,
) -> Image.Image:
    # 字体
    f_title = Font.font_extra_large.value
    f_h2 = Font.font_large.value
    f_small = Font.font_medium.value

    # 卡片高度估算（按描述行数）
    card_heights = []
    for item in data:
        desc_lines = wrap_text(
            item.description,
            f_small,
            width - 2 * outer_padding - cover_w - 32 - 32,
            max_lines=4,
        )
        h = max(
            cover_h, 38 + 30 + 26 + 26 + len(desc_lines) * 28
        )  # 标题/元信息/描述/链接
        card_heights.append(h + 48)  # card 内 padding

    H = (
        outer_padding
        + 88
        + card_gap
        + sum(card_heights)
        + card_gap * max(0, len(data) - 1)
        + outer_padding
    )

    # 正式画布
    im = Image.new("RGB", (width, H), Theme.bg)
    draw = ImageDraw.Draw(im)

    # Header
    y = outer_padding
    # 顶部标题
    draw.text((outer_padding, y), "Epic 免费游戏速览", font=f_title, fill=Theme.text)

    y += 64

    draw.line((outer_padding, y, width - outer_padding, y), fill=Theme.border, width=2)
    y += card_gap

    # Cards
    for idx, item in enumerate(data):
        card_h = card_heights[idx]
        x1, y1 = outer_padding, y
        x2, y2 = width - outer_padding, y + card_h

        # card 背景
        draw.rounded_rectangle(
            (x1, y1, x2, y2),
            radius=radius,
            fill=Theme.card,
            outline=Theme.border,
            width=2,
        )
        cx1 = x1 + 24
        cy1 = y1 + 24

        # 封面
        cover = FilePath.epic_cache.value / item.title
        if not cover.exists():
            cover = placeholder_cover((cover_w, cover_h))
        else:
            cover = Image.open(str(cover)).resize((cover_w, cover_h))
        im.paste(cover, (cx1, cy1))

        # 文本区
        tx = cx1 + cover_w + 28
        ty = cy1

        # 标题（可能很长 -> 省略）
        max_title_w = x2 - inner_padding - tx - 180
        title_show = ellipsize(item.title, f_h2, max_title_w)
        draw.text((tx, ty), title_show, font=f_h2, fill=Theme.text)

        # 免费标签
        if item.is_free_now:
            tag_txt = "FREE NOW"
            tag_color = Theme.ok
        else:
            tag_txt = "UPCOMING"
            tag_color = Theme.warn

        tw = int(draw.textlength(tag_txt, font=f_small)) + 26
        tag_x2 = x2 - inner_padding
        tag_x1 = tag_x2 - tw
        draw.rounded_rectangle(
            (tag_x1, ty - 2, tag_x2, ty + 34), radius=16, fill=tag_color, outline=None
        )
        draw.text((tag_x1 + 13, ty + 4), tag_txt, font=f_small, fill=(255, 255, 255))

        ty += 44

        # 元信息行
        meta1 = f"发行商：{item.seller}    原价：{item.original_price_desc}"
        draw.text((tx, ty), meta1, font=f_small, fill=Theme.subtext)
        ty += 30

        # 时间窗
        time_line = f"免费时间：{item.free_start}  →  {item.free_end}"
        draw.text((tx, ty), time_line, font=f_small, fill=Theme.subtext)
        ty += 34

        # 描述（最多 4 行）
        desc_max_w = x2 - inner_padding - tx
        desc_lines = wrap_text(item.description, f_small, desc_max_w, max_lines=4)
        for line in desc_lines:
            draw.text((tx, ty), line, font=f_small, fill=Theme.text)
            ty += 28

        y = y2 + card_gap

    return im
