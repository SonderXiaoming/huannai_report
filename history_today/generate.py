from datetime import date
from typing import List, Optional

from PIL import Image, ImageDraw

from ..model import TodayHistoryData


from ..util import wrap_text

from ..constant import HistoryTitle, Theme, Font, WeekDay


# ----------------------------
# Theme
# ----------------------------
THEME = {
    "bg": (248, 249, 252),
    "card_border": (228, 232, 240),
    "text": (25, 35, 55),
    "timeline": (210, 216, 228),
}


def generate_history_today_poster(
    data: TodayHistoryData,
    width: int = 1100,
    margin: int = 64,
    max_items: Optional[int] = None,
    card_radius=20,
    card_pad_x=28,
    card_pad_y=22,
    gap=18,
) -> str:
    items = data.items
    if max_items is not None:
        items = items[:max_items]

    items.sort(key=lambda it: int(it.year) if it.year.isdigit() else 0)

    today = date(year=date.today().year, month=data.month, day=data.day)  # 防没更新

    # Layout
    timeline_x = margin + 88
    content_left = margin + 125
    content_right = width - margin
    content_w = content_right - content_left

    # Header height: big date block + weekday + title/sub
    header_h = 30 + 22 + 64
    # Cards height estimate
    card_heights: List[int] = []
    for it in items:

        # reserve right emoji column ~ 90px
        inner_max_w = content_w - 96
        title_lines = wrap_text(
            it.title, Font.font_large.value, inner_max_w - 120, max_lines=2
        )
        desc_lines = wrap_text(
            it.description, Font.font_large.value, inner_max_w - 92, max_lines=3
        )

        h = card_pad_y * 2 + 10 + (len(title_lines) + len(desc_lines)) * 32
        card_heights.append(h)

    total_h = margin + header_h + 22
    if items:
        total_h += sum(card_heights) + gap * (len(items) - 1)
    total_h += margin

    img = Image.new("RGB", (width, int(total_h)), Theme.bg)
    draw = ImageDraw.Draw(img)

    # ----------------------------
    # Header: big date + weekday
    # ----------------------------
    header_top = margin
    # Left big date block
    date_x = margin
    date_y = header_top + 10

    # "02 / 11" as two big numbers with slash
    draw.text(
        (date_x, date_y),
        f"{data.month:02d} / {data.day:02d}",
        font=Font.font_extra_large.value,
        fill=Theme.text,
    )
    # Weekday under date
    draw.text(
        (date_x, date_y + 58),
        f"星期{WeekDay.get_by_value(today.weekday()).name_cn}",
        font=Font.font_extra_large.value,
        fill=Theme.subtext,
    )

    draw.text(
        (margin + 200, header_top + 30),
        "历史上的今天",
        font=Font.font_extra_large.value,
        fill=Theme.text,
    )

    # separator line
    sep_y = margin + header_h
    draw.line((margin, sep_y, width - margin, sep_y), fill=Theme.border, width=2)

    # Timeline
    list_top = sep_y + 22
    list_bottom = list_top + (
        sum(card_heights) + gap * (len(items) - 1) if items else 0
    )
    if items:
        draw.line(
            (timeline_x, list_top, timeline_x, list_bottom),
            fill=Theme.accent,
            width=6,
        )

    # ----------------------------
    # Cards
    # ----------------------------
    cy = list_top
    for idx, it in enumerate(items):
        et = HistoryTitle.get(it.event_type)

        h = card_heights[idx]
        card_x0 = content_left
        card_y0 = cy
        card_x1 = content_right
        card_y1 = cy + h

        # timeline dot
        dot_y = card_y0 + 36
        draw.ellipse(
            (timeline_x - 12, dot_y - 12, timeline_x + 12, dot_y + 12),
            fill=et.color if et else Theme.accent,
        )
        draw.ellipse(
            (timeline_x - 6, dot_y - 6, timeline_x + 6, dot_y + 6), fill=(255, 255, 255)
        )

        # card
        draw.rounded_rectangle(
            (card_x0, card_y0, card_x1, card_y1),
            radius=card_radius,
            fill=Theme.card,
            outline=Theme.border,
            width=2,
        )

        # badge top-right
        badge_text = et.value if et else "未知事件"
        badge_color = et.color if et else Theme.accent
        badge_w = int(draw.textlength(badge_text, font=Font.font_large.value)) + 26
        bx1 = card_x1 - 18
        bx0 = bx1 - badge_w
        by0 = card_y0 + 25
        by1 = by0 + 34
        draw.rounded_rectangle((bx0, by0, bx1, by1), radius=16, fill=badge_color)
        draw.text(
            (bx0 + 13, by0 + 6), badge_text, font=Font.font_large.value, fill=Theme.card
        )
        # year
        draw.text(
            (margin + 60, card_y0 + 25),
            it.year,
            font=Font.font_large.value,
            fill=badge_color,
            anchor="ra",
        )

        # right emoji icon column
        emoji = et.icon.resize((66, 66)) if et else None
        if emoji:
            # center vertically in card
            img.paste(
                Image.new("RGBA", emoji.size, badge_color),
                (card_x1 - card_pad_x - 60, card_y0 + (h // 2)),
                mask=emoji,
            )

        # title + desc, reserve emoji column width ~ 96
        text_x = card_x0 + card_pad_x
        text_max_w = (card_x1 - card_pad_x) - text_x - 96

        title_lines = wrap_text(
            it.title, Font.font_large.value, text_max_w, max_lines=2
        )
        ty = card_y0 + 16
        for i, line in enumerate(title_lines):
            draw.text(
                (text_x, ty + i * 38),
                line,
                font=Font.font_large.value,
                fill=Theme.text,
            )

        # desc spans (within reserved width)
        dy = ty + len(title_lines) * 38 + 6
        desc_lines = wrap_text(
            it.description, Font.font_large.value, text_max_w, max_lines=3
        )
        desc_x = card_x0 + card_pad_x
        for i, line in enumerate(desc_lines):
            draw.text(
                (desc_x, dy + i * 32),
                line,
                font=Font.font_large.value,
                fill=Theme.subtext,
            )

        cy = card_y1 + gap

    return img
