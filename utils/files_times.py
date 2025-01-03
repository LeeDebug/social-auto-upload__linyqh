from datetime import datetime, timedelta
from pathlib import Path
from conf import BASE_DIR


def get_absolute_path(relative_path: str, base_dir: str = None) -> str:
    # Convert the relative path to an absolute path
    absolute_path = Path(BASE_DIR) / base_dir / relative_path
    return str(absolute_path)


def get_title_and_hashtags_from_content(content: str):
    print("[files_times.py] get_title_and_hashtags_from_content > content type: ", type(content))
    lines = content.split('\n')
    title = lines[0].strip() if lines else ''
    tags = [tag.strip() for tag in lines[1:] if tag.strip()]
    return title, tags


def get_title_and_hashtags(file_path):
    print("[files_times.py] get_title_and_hashtags > file_path: ", file_path)

    # 构造对应的元数据文件路径
    meta_file_path = Path(file_path).with_suffix('.txt')
    if not meta_file_path.exists():
        raise FileNotFoundError(f"元数据文件不存在：{meta_file_path}")

    encodings_to_try = ['utf-8', 'gbk', 'gb2312']  # 常见的编码列表
    for encoding in encodings_to_try:
        try:
            with open(meta_file_path, 'r', encoding=encoding) as file:
                content = file.read()
                print(f"[files_times.py] get_title_and_hashtags > content (using {encoding}): ",
                      content[:100])  # 打印前100个字符用于调试
                return get_title_and_hashtags_from_content(content)
        except UnicodeDecodeError:
            print(f"Failed to read metadata file with encoding {encoding}. Trying next one...")
            continue
        except Exception as e:
            print(f"An error occurred while reading the metadata file: {e}")
            break
    else:
        raise ValueError("Could not read the metadata file with any of the provided encodings.")


"""
Call Examples:
今天发布
    generate_schedule_time_any_day(5, 2, daily_times=[8, 14],
                                    start_date="0", start_time="08:00", timestamps=False)
明天发布
    generate_schedule_time_any_day(5, 2, daily_times=[9, 14],
                                    start_date="1", start_time="09:00", timestamps=False)
指定日期发布
    generate_schedule_time_any_day(5, 2, daily_times=[8, 14],
                                    start_date="2025-01-10", start_time="08:00", timestamps=False)
"""
def generate_schedule_time_any_day(total_videos, videos_per_day, daily_times=None, start_date=None, start_time="08:00",
                                   timestamps=False):
    """
    Generate a schedule for video uploads.

    Args:
    - total_videos: Total number of videos to be uploaded.
    - videos_per_day: Number of videos to be uploaded each day.
    - daily_times: List of hours (in 24-hour format) to upload videos. Default is [8, 12, 18, 22].
    - start_date: The date to start uploading videos, in '0', '1', '2' format. '0' means today, '1' means tomorrow, and so on, or in 'YYYY-MM-DD' format.
    - start_time: The start time of the first video upload in 'HH:MM' format. Defaults to "08:00".
    - timestamps: Whether to return timestamps (True) or datetime objects (False).

    Returns:
    - A list of scheduling times for the videos, either as timestamps or datetime objects.
    """

    if total_videos <= 0 or videos_per_day <= 0:
        raise ValueError("total_videos and videos_per_day must be positive integers")

    # Default upload times if not provided
    if daily_times is None:
        daily_times = [8, 12, 18, 22]

    if videos_per_day > len(daily_times):
        raise ValueError("videos_per_day cannot exceed the length of daily_times")

    # Parse the start_date
    if start_date is None:
        start_date = 0  # Default to today if not provided

    # If start_date is a string representing 0, 1, 2, 3, calculate the date accordingly
    if isinstance(start_date, str) and start_date.isdigit():
        start_date = int(start_date)  # Convert to integer

    # If start_date is a date string in 'YYYY-MM-DD' format, parse it
    if isinstance(start_date, str):
        try:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(
                "start_date must be a valid date string in 'YYYY-MM-DD' format or a digit string '0', '1', '2' etc.")

    # If start_date is an integer (0, 1, 2, etc.), calculate the date based on today
    elif isinstance(start_date, int):
        start_datetime = datetime.now() + timedelta(days=start_date)  # Today + start_date days
    else:
        raise ValueError("start_date must be either a digit string '0', '1', '2', or a date string 'YYYY-MM-DD'.")

    # Set the start time (combine start_date with start_time)
    start_datetime = start_datetime.replace(hour=int(start_time.split(":")[0]), minute=int(start_time.split(":")[1]),
                                            second=0, microsecond=0)

    # Generate the schedule
    schedule = []
    current_time = start_datetime

    for video in range(total_videos):
        day_offset = video // videos_per_day  # Which day the video will be uploaded
        daily_video_index = video % videos_per_day  # Which time of day to use from daily_times

        # Calculate the time for the current video
        hour = daily_times[daily_video_index]
        scheduled_time = current_time + timedelta(days=day_offset, hours=hour - current_time.hour,
                                                  minutes=-current_time.minute)

        schedule.append(scheduled_time)

    # Return timestamps or datetime objects
    if timestamps:
        schedule = [int(time.timestamp()) for time in schedule]

    return schedule
