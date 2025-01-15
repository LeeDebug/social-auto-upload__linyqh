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
# from tk_uploader.main import tiktok_setup, TiktokVideo
from uploader.tk_uploader.main_chrome import tiktok_setup, TiktokVideo
from utils.files_times import generate_schedule_time_any_day, get_title_and_hashtags


if __name__ == '__main__':
    # 以今天日期当做要发布的文件夹
    filepath = Path(BASE_DIR) / "videos" / "backups" / datetime.now().strftime("%Y-%m-%d")
    account_file = Path(BASE_DIR / "cookies" / "tk_uploader" / "account.json")
    folder_path = Path(filepath)
    # get video files from folder
    files = list(folder_path.glob("*.mp4"))
    file_num = len(files)
    if file_num == 0:
        raise ValueError("要发布的文件夹或视频不存在")

    publish_datetimes = generate_schedule_time_any_day(file_num, 1,
                                                daily_times=[7], start_date="1")
    cookie_setup = asyncio.run(tiktok_setup(account_file, handle=True))

    for index, file in enumerate(files):
        title, tags = get_title_and_hashtags(str(file))
        thumbnail_path = file.with_suffix('.png')
        print(f"video_file_name：{file}")
        print(f"video_title：{title}")
        print(f"video_hashtag：{tags}")
        if thumbnail_path.exists():
            print(f"thumbnail_file_name：{thumbnail_path}")
            # app = TiktokVideo(title, file, tags, publish_datetimes[index], account_file, thumbnail_path)
            app = TiktokVideo(title, file, tags, 0, account_file, thumbnail_path)
        else:
#             app = TiktokVideo(title, file, tags, publish_datetimes[index], account_file)
            app = TiktokVideo(title, file, tags, 0, account_file)
        asyncio.run(app.main(), debug=False)
