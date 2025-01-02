from datetime import datetime, timedelta
from pathlib import Path
import os
import re

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


def generate_schedule_time_any_day(total_videos, videos_per_day, start_time_today, daily_times=None, timestamps=False):
    """
    Generate a schedule for video uploads, starting from a specific time today.

    Args:
    - total_videos (int): Total number of videos to be uploaded.
    - videos_per_day (int): Number of videos to be uploaded each day.
    - start_time_today (str or datetime): The starting time today, either as a 'HH:MM' formatted string or a datetime object.
    - daily_times (list, optional): List of specific times (hours) in a day to publish videos. Defaults to evenly spaced times.
    - timestamps (bool, optional): Whether to return Unix timestamps instead of datetime objects. Defaults to False.

    Returns:
    - list: List of scheduling times as either datetime objects or Unix timestamps.

    Raises:
    - ValueError: If videos_per_day is not positive or exceeds the length of daily_times.
    - ValueError: If start_time_today is not a valid datetime or string in 'HH:MM' format.
    """
    # Validate videos_per_day
    if videos_per_day <= 0:
        raise ValueError("videos_per_day should be a positive integer")

    # Parse start_time_today if it's a string in 'HH:MM' format
    if isinstance(start_time_today, str):
        try:
            start_hour, start_minute = map(int, start_time_today.split(':'))
            now = datetime.now()
            start_time_today = now.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
        except ValueError:
            raise ValueError("start_time_today should be a datetime object or a string in 'HH:MM' format")

    # Validate start_time_today type
    if not isinstance(start_time_today, datetime):
        raise ValueError("start_time_today should be a datetime object or a valid 'HH:MM' formatted string")

    # Generate default daily_times if not provided
    if daily_times is None:
        daily_times = [i for i in range(0, 24, 24 // videos_per_day)]

    # Validate daily_times length
    if videos_per_day > len(daily_times):
        raise ValueError("videos_per_day should not exceed the length of daily_times")

    # Initialize the schedule list
    schedule = []

    # Generate schedule for each video
    for video in range(total_videos):
        # Determine which day the video will be published
        day_offset = video // videos_per_day

        # Determine the time slot for this video
        daily_video_index = video % videos_per_day
        scheduled_time = start_time_today + timedelta(
            days=day_offset,  # Add day offset
            hours=daily_times[daily_video_index] - start_time_today.hour  # Adjust hour difference
        )

        # Append the scheduled time
        schedule.append(scheduled_time)

    # Convert to Unix timestamps if requested
    if timestamps:
        schedule = [int(time.timestamp()) for time in schedule]

    return schedule

