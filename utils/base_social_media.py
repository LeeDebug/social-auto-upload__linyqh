from pathlib import Path
from typing import List

from conf import BASE_DIR

SOCIAL_MEDIA_DOUYIN = "douyin"
SOCIAL_MEDIA_TENCENT = "tencent"
SOCIAL_MEDIA_TIKTOK = "tiktok"
SOCIAL_MEDIA_BILIBILI = "bilibili"
SOCIAL_MEDIA_KUAISHOU = "kuaishou"

# 添加平台名称映射
PLATFORM_MAP = {
    "小红书": "xhs",
    "哔哩哔哩": "bilibili",
    "抖音": "douyin",
    "快手": "kuaishou",
    "TikTok": "tiktok",
    "腾讯视频": "tencent"
}


def get_platform_key(display_name: str) -> str:
    """将显示名称转换为平台键值"""
    return PLATFORM_MAP.get(display_name, display_name.lower())


def get_supported_social_media():
    """返回支持的社交媒体平台列表"""
    return ["小红书", "哔哩哔哩", "抖音", "快手", "TikTok", "腾讯视频"]


def get_cli_action() -> List[str]:
    return ["upload", "login", "watch"]


async def set_init_script(context):
    stealth_js_path = Path(BASE_DIR / "utils/stealth.min.js")
    await context.add_init_script(path=stealth_js_path)
    return context
