import asyncio
from pathlib import Path

# ! 如果要在根目录调用该文件，需要添加以下代码
import sys
# 获取当前文件的父目录（即 'src' 目录）的父目录（即项目根目录）
project_root = Path(__file__).parent.parent.resolve()
# 将项目根目录添加到 Python 的模块搜索路径中
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from conf import BASE_DIR
from uploader.melon_uploader.main import melon_setup

if __name__ == '__main__':
    print("BASE_DIR: ", BASE_DIR)
    account_file = Path(BASE_DIR / "cookies" / "melon_uploader" / "account.json")
    print("account_file: ", account_file)
    cookie_setup = asyncio.run(melon_setup(str(account_file), handle=True))
