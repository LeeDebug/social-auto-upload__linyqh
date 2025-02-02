import time
from datetime import datetime
from pathlib import Path

# ! 如果要在根目录调用该文件，需要添加以下代码
import sys
# 获取当前文件的父目录（即 'src' 目录）的父目录（即项目根目录）
project_root = Path(__file__).parent.parent.resolve()
# 将项目根目录添加到 Python 的模块搜索路径中
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from uploader.bilibili_uploader.main import read_cookie_json_file, extract_keys_from_json, random_emoji, BilibiliUploader
from conf import BASE_DIR
from utils.constant import VideoZoneTypes
from utils.files_times import generate_schedule_time_any_day, get_title_and_hashtags

if __name__ == '__main__':
    # 以今天日期当做要发布的文件夹
    filepath = Path(BASE_DIR) / "videos" / "backups" / datetime.now().strftime("%Y-%m-%d")
    print("filepath: ", filepath)
    # how to get cookie, see the file of get_bilibili_cookie.py.
    account_file = Path(BASE_DIR / "cookies" / "bilibili_uploader" / "account.json")
    if not account_file.exists():
        print(f"{account_file.name} 配置文件不存在")
        exit()
    cookie_data = read_cookie_json_file(account_file)
    cookie_data = extract_keys_from_json(cookie_data)

    tid = VideoZoneTypes.SPORTS_FOOTBALL.value  # 设置分区id
    # 获取视频目录
    folder_path = Path(filepath)
    # 获取文件夹中的所有文件
    files = list(folder_path.glob("*.mp4"))
    file_num = len(files)
    if file_num == 0:
        raise ValueError("要发布的文件夹或视频不存在")

    timestamps = generate_schedule_time_any_day(file_num, 1,
                                                daily_times=[7], start_date="1", timestamps=True)

    for index, file in enumerate(files):
        title, tags = get_title_and_hashtags(str(file))
        # just avoid error, bilibili don't allow same title of video.
        title += random_emoji()
        tags_str = ' '.join(','.join([tag for tag in tags]).split()[:3])
        # 打印视频文件名、标题和 hashtag
        print(f"视频文件名：{file}")
        print(f"标题：{title}")
        print(f"Hashtag：{[tags_str]}")
        # I set desc same as title, do what u like.
        desc = title
        # bili_uploader = BilibiliUploader(cookie_data, file, title, desc, tid, [tags_str], timestamps[index])
        bili_uploader = BilibiliUploader(cookie_data, file, title, desc, tid, [tags_str], 0)
        bili_uploader.upload()

        # life is beautiful don't so rush. be kind be patience
        time.sleep(30)
