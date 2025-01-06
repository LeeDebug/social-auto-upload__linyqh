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
from uploader.tencent_uploader.main import weixin_setup, TencentVideo
from utils.constant import TencentZoneTypes
from utils.files_times import generate_schedule_time_any_day, get_title_and_hashtags


if __name__ == '__main__':
    # 以今天日期当做要发布的文件夹
    filepath = Path(BASE_DIR) / "videos" / "backups" / (datetime.now().strftime("%Y-%m-%d") + "_news")
    account_file = Path(BASE_DIR / "cookies" / "tencent_uploader" / "account-159.json")
    # 获取视频目录
    folder_path = Path(filepath)
    # 获取文件夹中的所有文件
    files = list(folder_path.glob("*.mp4"))
    file_num = len(files)
    if file_num == 0:
        raise ValueError("要发布的文件夹或视频不存在")

    publish_datetimes = generate_schedule_time_any_day(file_num, 10,
                                                daily_times=[6,6,7,7,7,7,8,8,8,8], start_date="1")
    cookie_setup = asyncio.run(weixin_setup(account_file, handle=True))
    category = TencentZoneTypes.LIFESTYLE.value  # 标记原创需要否则不需要传

    for index, file in enumerate(files):
        title, tags = get_title_and_hashtags(str(file))
        # 打印视频文件名、标题和 hashtag
        print(f"视频文件名：{file}")
        print(f"标题：{title}")
        print(f"Hashtag：{tags}")
        app = TencentVideo(title, file, tags, publish_datetimes[index], account_file, category)
        asyncio.run(app.main(), debug=False)
