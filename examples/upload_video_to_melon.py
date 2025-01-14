import asyncio
from datetime import datetime
from pathlib import Path

# ! 如果要在根目录调用该文件，需要添加以下代码
import sys
# 获取当前文件的父目录（即 'src' 目录）的父目录（即项目根目录）
project_root = Path(__file__).parent.parent.resolve()
# 将项目根目录添加到 Python 的模块搜索路径中
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from conf import BASE_DIR
from uploader.melon_uploader.main import melon_setup, MelonVideo
from utils.files_times import generate_schedule_time_any_day, get_title_and_hashtags


if __name__ == '__main__':
    # 以今天日期当做要发布的文件夹
    # filepath = Path(BASE_DIR) / "videos" / "backups" / datetime.now().strftime("%Y-%m-%d")
    account_file = Path(BASE_DIR / "cookies" / "melon_uploader" / "account.json")
    cookie_setup = asyncio.run(melon_setup(account_file, handle=False))

    app = MelonVideo(account_file)
    asyncio.run(app.main(), debug=False)
