from datetime import datetime
import asyncio
from pathlib import Path

# ! 如果要在根目录调用该文件，需要添加以下代码
import sys
from time import sleep

# 获取当前文件的父目录（即 'src' 目录）的父目录（即项目根目录）
project_root = Path(__file__).parent.parent.resolve()
# 将项目根目录添加到 Python 的模块搜索路径中
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from conf import BASE_DIR
from uploader.douyin_uploader.main import douyin_setup, DouYinVideo
from utils.files_times import generate_schedule_time_any_day, get_title_and_hashtags


if __name__ == '__main__':
    # 以今天日期当做要发布的文件夹
    filepath = Path(BASE_DIR) / "videos" / "backups" / (datetime.now().strftime("%Y-%m-%d") + "_news")
    account_file = Path(BASE_DIR / "cookies" / "douyin_uploader" / "account-159.json")
    # 获取视频目录
    folder_path = Path(filepath)
    # 获取文件夹中的所有文件
    files = list(folder_path.glob("*.mp4"))
    file_num = len(files)
    if file_num == 0:
        raise ValueError("要发布的文件夹或视频不存在")

    publish_datetimes = generate_schedule_time_any_day(file_num, 10,
                                                daily_times=[6,6,7,7,7,7,8,8,8,8], start_date="1")
    cookie_setup = asyncio.run(douyin_setup(account_file, handle=False))

    for index, file in enumerate(files):
        print(f"开始发布第 {index} 个视频")
        # 获取视频文件对应的元数据文件路径
        meta_file_path = file.with_suffix('.txt')

        # 如果存在元数据文件，则从中获取标题和标签
        if meta_file_path.exists():
            title, tags = get_title_and_hashtags(str(meta_file_path))
        else:
            # 如果没有元数据文件，可以提供默认值或者抛出异常
            title, tags = "默认标题", ["#默认标签"]

        thumbnail_path = file.with_suffix('.png') if file.with_suffix('.png').exists() else None
        print(f"视频文件名：{file}")
        print(f"标题：{title}")
        print(f"Hashtag：{tags}")

        # app = DouYinVideo(title, file, tags, publish_datetimes[index], account_file, thumbnail_path=thumbnail_path)
        app = DouYinVideo(title, file, tags, 0, account_file, thumbnail_path=thumbnail_path)
        asyncio.run(app.main(), debug=False)

        sleep(120)
        print(f"第 {index} 个视频发布结束")
