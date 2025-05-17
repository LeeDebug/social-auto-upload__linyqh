from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pathlib import Path
import uvicorn

# 删除原有的 generate_ks_cookie 函数和 @app.post("/api/ks/cookie") 路由

# 新增路由导入
from kuaishou.cookie import router as ks_router

app = FastAPI(title="自媒体自动化服务接口", description="提供自媒体自动化服务的相关接口")

# 挂载快手路由
app.include_router(ks_router, prefix="/api/ks", tags=["Kuaishou"])

# 检测服务状态
@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    if not Path("../uploader").exists():
        raise Exception("请确保在项目根目录运行此文件")
    uvicorn.run(app, host="0.0.0.0", port=8000)
