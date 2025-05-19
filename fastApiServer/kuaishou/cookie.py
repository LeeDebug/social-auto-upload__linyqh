from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import subprocess
import sys
import asyncio

router = APIRouter()

async def generate_ks_cookie(account_name: str):
    try:
        script_path = Path(__file__).parent.parent.parent / "examples/get_kuaishou_cookie.py"
        
        if not script_path.exists():
            raise HTTPException(
                status_code=500,
                detail=f"脚本路径不存在: {script_path}"
            )
            
        result = await asyncio.to_thread(
            subprocess.run,
            [sys.executable, str(script_path), account_name],
            capture_output=True,
            text=True,
            cwd=script_path.parent.parent
        )
        
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

@router.post("/login_without_cookie",
    summary="快手无Cookie登录接口",
    description="该接口用于生成快手账号的Cookie，通过传入快手账号名称（唯一标识）调用相关脚本生成对应的Cookie文件。")
async def create_cookie(account_name: str):
    """
    快手Cookie生成接口
    参数：
    - account_name: 快手账号名称（唯一标识）
    """
    result = await generate_ks_cookie(account_name)
    return JSONResponse(content=result)

@router.post("/kuaishou/kuaishou_video_upload", 
    summary="快手视频上传接口",
    description="该接口用于上传视频到快手平台，支持视频文件、标题、描述等参数。")
async def upload_kuaishou_video():
    return  {"status": "success"}
