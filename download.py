import asyncio
from pathlib import Path
from typing import Optional
import httpx
from .constant import FilePath


async def download_image(
    client: httpx.AsyncClient, url: str, cache_path: Optional[Path] = None
) -> Optional[bytes]:
    try:
        r = await client.get(url, timeout=15.0)
        r.raise_for_status()
        if cache_path:
            cache_path.write_bytes(r.content)
        return r.content
    except Exception as e:
        print(f"下载图片失败: {url} -> {e}")
        return None


async def download_image_with_retries(
    client: httpx.AsyncClient,
    url: str,
    sem: asyncio.Semaphore,
    cache_path: Optional[Path] = None,
) -> Optional[bytes]:
    if not url:
        return None
    if (FilePath.bangumi_cache.value / Path(url.split("/")[-1])).exists():
        return (FilePath.bangumi_cache.value / Path(url.split("/")[-1])).read_bytes()

    async with sem:
        try:
            for _ in range(3):  # 最多重试3次
                return await download_image(client, url, cache_path)
        except Exception as e:
            print(f"下载图片失败: {url} -> {e}")
            return None
