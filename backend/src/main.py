from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import List

from src.database import init_database
from src.crawler.scraper import ArxivScraper
from src.utils.log_config import setup_logging, get_logger
from src.processor import VectorProcessor
from src.model import ArxivPaper

logger = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    global logger
    logger = get_logger("MainApp")

    logger.info("🚀 The server is starting up...")

    try:
        await init_database()
    except Exception as e:
        logger.critical(f"Failed to initialize the database: {e}")
        raise e
    logger.info("🔄 Activate the Crawler Pipeline to start...")

    try:
        scraper = ArxivScraper()
        processor = VectorProcessor()

        papers = scraper.get_paper(topics=["AI", "CL", "CV", "CL"], days_back=3)
        new_papers = await scraper.save_to_db(papers)

        if new_papers:
            await processor.process_and_index(new_papers)
            logger.info(f"📊 Pipeline complete: {len(new_papers)} new post is ready for chat.")
        else:
            logger.info("⚠️ There are no new posts to process.")
            
    except Exception as e:
        logger.error(f"❌ Pipeline error: {e}", exc_info=True)
    logger.info("✅ The system is ready to receive requests!")
    
    yield

    logger.info("🛑 Server is off...")

app = FastAPI(lifespan=lifespan)
@app.get("/")
def read_root():
    return {"status": "running", "service": "Arxiv Agent"}

@app.get("/news/latest")
async def get_latest_news():
    papers = await ArxivPaper.find_all().sort("-published_date").limit(20).to_list()
    return papers

from fastapi.responses import StreamingResponse
import asyncio

@app.post("/chat/stream")
async def chat_stream(body: dict):
    async def fake_generator():
        mock_text = f"Tôi đã nhận câu hỏi: '{body['message']}' về bài báo {body['paper_id']}. \n\nĐây là câu trả lời giả lập từ Backend..."
        for word in mock_text.split():
            yield word + " "
            await asyncio.sleep(0.1)
            
    return StreamingResponse(fake_generator(), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('src.main:app', host='0.0.0.0', port=8000, reload=True)