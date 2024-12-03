from fastapi import APIRouter, BackgroundTasks
from services.crawl_service import start_crawl_service, get_crawl_status_service
import configuration as cf
router = APIRouter()

@router.post("/start-crawl", summary="啟動爬蟲任務")
async def start_crawl(url: str = None, num_threads: int = 3, background_tasks: BackgroundTasks = BackgroundTasks()):
    """
    啟動爬蟲並將其作為後台任務執行
    """

    target_url = url or cf.get_url()
    return start_crawl_service(target_url, num_threads, background_tasks)

@router.get("/crawl-status", summary="獲取爬蟲任務狀態")
async def get_crawl_status():
    """
    查詢當前爬蟲任務的執行情況
    """
    return get_crawl_status_service()
