from pathlib import Path
from typing import Any, Coroutine, List, Optional, TypeVar
from PIL import ImageDraw, ImageFont

T = TypeVar("T")
NUM_TO_STRING = {
    1: "一",
    2: "二",
    3: "三",
    4: "四",
    5: "五",
    6: "六",
    7: "七",
    8: "八",
    9: "九",
    10: "十",
    11: "十一",
    12: "十二",
    13: "十三",
    14: "十四",
    15: "十五",
    16: "十六",
    17: "十七",
    18: "十八",
    19: "十九",
    20: "二十",
    21: "二十一",
    22: "二十二",
    23: "二十三",
    24: "二十四",
    25: "二十五",
    26: "二十六",
    27: "二十七",
    28: "二十八",
    29: "二十九",
    30: "三十",
    31: "三十一",
    32: "三十二",  # 以防万一
}


def num_to_string(num: int) -> str:
    """将数字转换为中文字符串"""
    return NUM_TO_STRING[num] if num in NUM_TO_STRING else str(num)


async def safe_call(coro: Coroutine[Any, Any, T]) -> Optional[T]:
    """安全调用协程，捕获异常并返回None"""
    try:
        return await coro
    except Exception:
        return None


def clear_old_file(path: Path):
    """清理旧文件"""
    for f in path.iterdir():
        if f.is_file():
            f.unlink()


def wrap_text(
    text: str, font: ImageFont.ImageFont, max_width: int, max_lines: int = None
) -> List[str]:
    # 按字符累积（对中英文混排更稳）
    lines = []
    cur = ""
    for ch in text:
        if ch == "\n":
            lines.append(cur)
            cur = ""
            continue
        test = cur + ch
        if font.getlength(test) <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    if max_lines is not None:
        lines = lines[:max_lines]
    return lines


def ellipsize(text: str, font: ImageFont.ImageFont, max_width: int) -> str:
    if font.getlength(text) <= max_width:
        return text
    ell = "…"
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi) // 2
        cand = text[:mid] + ell
        if font.getlength(cand) <= max_width:
            lo = mid + 1
        else:
            hi = mid
    return text[: max(0, lo - 1)] + ell
