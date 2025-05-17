from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import asyncio
import uvicorn

app = FastAPI(title="自媒体自动化服务接口", description="提供自媒体自动化服务的相关接口")

# 原cookie生成逻辑封装
async def generate_ks_cookie(account_name: str):
    try:
        import subprocess
        from pathlib import Path
        import sys
        
        # 修正为从项目根目录开始的路径（原路径多了一层fastApiServer）
        script_path = Path(__file__).parent.parent / "examples/get_kuaishou_cookie.py"
        
        # 添加路径存在性检查
        if not script_path.exists():
            raise HTTPException(
                status_code=500,
                detail=f"脚本路径不存在: {script_path}"
            )
            
        # 使用绝对路径调用
        result = subprocess.run(
            [sys.executable, str(script_path), account_name],  # 使用当前python解释器
            capture_output=True,
            text=True,
            cwd=script_path.parent.parent  # 设置工作目录为项目根目录
        )
        
        # 错误处理
        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"脚本执行失败: {result.stderr}"
            )
            
        return {
            "status": "success",
            "cookie_path": f"cookies/ks_uploader/{account_name}.json"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ks/cookie")
async def create_cookie(account_name: str):
    """
    快手Cookie生成接口
    参数：
    - account_name: 快手账号名称（唯一标识）
    """
    result = await generate_ks_cookie(account_name)
    return JSONResponse(content=result)

# 检测服务状态
@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    # 新增项目根目录判断
    if not Path("../uploader").exists():
        raise Exception("请确保在项目根目录运行此文件")
    uvicorn.run(app, host="0.0.0.0", port=8000)