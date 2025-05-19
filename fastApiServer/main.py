# 从 fastapi 库中导入 FastAPI 类，用于创建 FastAPI 应用实例
from fastapi import FastAPI
# 从 pathlib 模块中导入 Path 类，用于处理文件路径和目录操作
from pathlib import Path
# 导入 uvicorn 库，它是一个 ASGI 服务器，用于运行 FastAPI 应用
import uvicorn

# 新增路由导入，从 kuaishou.cookie 模块中导入名为 router 的路由对象，并将其重命名为 ks_router
from kuaishou.cookie import router as ks_router

# 创建一个 FastAPI 应用实例，设置应用的标题和描述信息
app = FastAPI(title="自媒体自动化服务接口", description="提供自媒体自动化服务的相关接口")

# 挂载快手路由，将 ks_router 路由对象挂载到应用中，设置路由前缀为 /kuaishou，标签为 快手服务
app.include_router(ks_router, prefix="/kuaishou", tags=["快手服务"])

# 定义一个 GET 请求的路由，路径为 /health，标签为 基础服务，用于检测服务状态
@app.get("/health", tags=["基础服务"])
# 定义处理 /health 路由请求的函数
def health_check():
    # 返回一个包含服务状态信息的字典
    return {"status": "ok"}

# 判断当前脚本是否作为主程序运行
if __name__ == "__main__":
    # 检查上级目录下的 uploader 目录是否存在
    if not Path("../uploader").exists():
        # 如果 uploader 目录不存在，抛出异常提示用户确保在项目根目录运行此文件
        raise Exception("请确保在项目根目录运行此文件")
    # 使用 uvicorn 运行 FastAPI 应用，指定主机地址为 0.0.0.0，端口号为 8000，并开启实时热更新功能
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
