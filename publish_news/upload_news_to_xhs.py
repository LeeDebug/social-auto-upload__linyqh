import configparser
from datetime import datetime
from pathlib import Path
from time import sleep

from xhs import XhsClient

# ! 如果要在根目录调用该文件，需要添加以下代码
import sys
# 获取当前文件的父目录（即 'src' 目录）的父目录（即项目根目录）
project_root = Path(__file__).parent.parent.resolve()
# 将项目根目录添加到 Python 的模块搜索路径中
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from conf import BASE_DIR
from utils.files_times import generate_schedule_time_any_day, get_title_and_hashtags
from uploader.xhs_uploader.main import sign_local, beauty_print
from utils.log import xhs_logger

config = configparser.RawConfigParser()
config.read(Path(BASE_DIR / "cookies" / "xhs_uploader" / "accounts-159.ini"))


if __name__ == '__main__':
    # 以今天日期当做要发布的文件夹
    filepath = Path(BASE_DIR) / "videos" / "backups" / (datetime.now().strftime("%Y-%m-%d") + "_news")
    # 获取视频目录
    folder_path = Path(filepath)
    # 获取文件夹中的所有文件
    files = list(folder_path.glob("*.mp4"))
    file_num = len(files)
    if file_num == 0:
        raise ValueError("要发布的文件夹或视频不存在")

    cookies = config['account1']['cookies']
    xhs_client = XhsClient(cookies, sign=sign_local, timeout=60)
    # auth cookie
    # 注意：该校验cookie方式可能并没那么准确
    try:
        xhs_client.get_video_first_frame_image_id("3214")
    except:
        xhs_logger.info("cookie 失效")
        exit()

    publish_datetimes = generate_schedule_time_any_day(file_num, 10,
                                                daily_times=[6,6,7,7,7,7,8,8,8,8], start_date="1")

    for index, file in enumerate(files):
        xhs_logger.info(f"开始发布第 {index+1} 个视频")
        title, tags = get_title_and_hashtags(str(file))
        # 加入到标题 补充标题（xhs 可以填1000字不写白不写）
        tags_str = ' '.join(['#' + tag for tag in tags])
        hash_tags_str = ''
        hash_tags = []

        # 打印视频文件名、标题和 hashtag
        xhs_logger.info(f"视频文件名：{file}")
        xhs_logger.info(f"标题：{title}")
        xhs_logger.info(f"Hashtag：{tags}")

        topics = []
        # 获取hashtag
        for i in tags[:3]:
            topic_official = xhs_client.get_suggest_topic(i)
            if topic_official:
                topic_official[0]['type'] = 'topic'
                topic_one = topic_official[0]
                hash_tag_name = topic_one['name']
                hash_tags.append(hash_tag_name)
                topics.append(topic_one)
        xhs_logger.info("topics: ", topics)

        hash_tags_str = ' ' + ' '.join(['#' + tag + '[话题]#' for tag in hash_tags])

        note = xhs_client.create_video_note(title=title[:20], video_path=str(file),
                                            desc=title + tags_str + hash_tags_str,
                                            topics=topics,
                                            is_private=False,
                                            )
                                            # post_time = publish_datetimes[index].strftime("%Y-%m-%d %H:%M:%S"))

        beauty_print(note)

        xhs_logger.info(f"第 {index+1} 个视频发布结束")
        # 强制休眠 120s，避免风控（必要）
        sleep(120)

