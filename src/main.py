from src.database import init_database
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.crawler.scraper import ArxivScraper
from src.utils.log_config import setup_logging, get_logger

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
        papers = scraper.get_paper(topics=["AI", "CL", "CV", "CL"], days_back=3)
        if papers:
            inserted_count = await scraper.save_to_db(papers)
            logger.info(f"📊 Startup report: Updated {inserted_count} with new articles.")
        else:
            logger.info("⚠️ No articles were found during this period.")
    except Exception as e:
        logger.error(f"❌ Pipeline Crawler Error: {e}", exc_info=True)

    logger.info("✅ The system is ready to receive requests!")
    
    yield

    logger.info("🛑 Server is off...")

app = FastAPI(lifespan=lifespan)
@app.get("/")
def read_root():
    return {"status": "running", "service": "Arxiv Agent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('src.main:app', host='0.0.0.0', port=8000, reload=True)