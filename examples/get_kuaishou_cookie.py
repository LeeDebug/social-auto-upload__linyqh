import asyncio
import sys
from pathlib import Path

from conf import BASE_DIR
from uploader.ks_uploader.main import ks_setup

if __name__ == '__main__':
    # 接收命令行参数
    account_name = sys.argv[1] if len(sys.argv) > 1 else "default_account"
    
    # 动态生成账户文件路径
    account_file = Path(BASE_DIR / "cookies" / "ks_uploader" / f"{account_name}.json")
    account_file.parent.mkdir(exist_ok=True)
    
    # 执行原有逻辑
    cookie_setup = asyncio.run(ks_setup(str(account_file), handle=True))
