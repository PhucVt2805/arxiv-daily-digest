from langchain_google_genai import GoogleGenerativeAIEmbeddings
from typing import List
from src.model import ArxivPaper
import asyncio
from qdrant_client.models import PointStruct
import hashlib
import uuid
import os

from src.utils.log_config import get_logger
from src.database import get_qdrant_client

logger = get_logger('VevtorProcessor')

class VectorProcessor:
    def __init__(self):
        self.API_KEY = os.getenv('GOOGLE_API_KEY')
        if not self.API_KEY:
            logger.error('GOOGLE_API_KEY has not been configured yet!')
            raise ValueError('GOOGLE_API_KEY missing')
        
        self.embedding_model = GoogleGenerativeAIEmbeddings(
            model='models/text-embedding-004',
            google_api_key=self.API_KEY,
            task_type='SEMANTIC_SIMILARITY'
        )

    async def process_and_index(self, papers: List[ArxivPaper]):
        """
        Import the list of articles -> Embed -> Upload to Qdrant
        """
        if not papers:
            logger.info("No papers to process.")
            return
        
        logger.info(f"🚀 Start vectorizing the {len(papers)} article with Gemini...")

        texts_to_embed = [f'Title: {p.title}\nSummary: {p.summary}' for p in papers]

        try:
            all_embeddings = []

            for i in range(0, len(texts_to_embed), 20):
                batch_texts = texts_to_embed[i:i+20]
                logger.debug(f'Embedding batch {i} --> {i+len(batch_texts)}')

                batch_embeddings = await self.embedding_model.aembed_documents(batch_texts)
                all_embeddings.extend(batch_embeddings)

                await asyncio.sleep(.5)

            points = []
            if all_embeddings:
                vector_size = len(all_embeddings[0])
                logger.info(f'Vector Dimension: {vector_size}')

            for i, paper in enumerate(papers):
                payload = {
                    "paper_id": paper.id,
                    "title": paper.title,
                    "published_date": paper.published_date.isoformat(),
                    "category": paper.prime_category,
                    "arxiv_url": paper.arxiv_url
                }

                points.append(PointStruct(
                    id=self._generate_uuid_from_str(paper.id),
                    vector=all_embeddings[i],
                    payload=payload
                ))

            qdrant_client = get_qdrant_client()
            await qdrant_client.upsert(
                collection_name="arxiv_vectors",
                points=points
            )
            
            logger.info(f"✅ The {len(points)} vectors have been successfully indexed into Qdrant.")
            
        except Exception as e:
            logger.error(f"❌ Vectorization process error: {e}", exc_info=True)

    def _generate_uuid_from_str(self, text: str) -> str:
        hash_value = hashlib.md5(text.encode()).hexdigest()
        return str(uuid.UUID(hash_value))