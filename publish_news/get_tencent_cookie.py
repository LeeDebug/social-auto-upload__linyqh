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
from uploader.tencent_uploader.main import weixin_setup

if __name__ == '__main__':
    account_file = Path(BASE_DIR / "cookies" / "tencent_uploader" / "account-159.json")
    cookie_setup = asyncio.run(weixin_setup(str(account_file), handle=True))
