from pathlib import Path

from conf import BASE_DIR

Path(BASE_DIR / "cookies" / "weibo_uploader").mkdir(exist_ok=True)