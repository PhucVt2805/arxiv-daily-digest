from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, date, timezone

class ArxivPaper(BaseModel):
    id: str = Field(alias="_id")
    title: str
    author: List[str]
    arxiv_url: str
    pdf_url: str
    published_date: datetime
    updated_date: datetime
    summary: str
    prime_category: str
    categories: List[str]
    crawled_at: date = Field(default_factory=lambda: datetime.now(timezone.utc).date())

class BaseNewsScraper(ABC):
    @abstractmethod
    def fetch_raw_html(self, url: str) -> str:
        """Download content from url""" 
        pass


    @abstractmethod
    def parse_content(self, raw_html: str) -> List[ArxivPaper]:
        """Convert raw HTML to clean list of ArxivPaper objects"""
        pass

class BaseVectorStore(ABC):
    """
    Interface to store and search vectors (RAG).
    """
    @abstractmethod
    def add_documents(self, documents: List[ArxivPaper]):
        """Save documents to vector db"""
        pass

    @abstractmethod
    def similarity_search(self, query: str, k: int = 3) -> List[ArxivPaper]:
        """Search for related content based on query"""
        pass

class BaseLLMService(ABC):
    """
    Interface wrap LLMs 
    """
    @abstractmethod
    def generate_response(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Generate text response from LLM"""
        pass
    
    @abstractmethod
    def generate_structured_output(self, prompt: str, schema: BaseModel) -> BaseModel:
        """It is mandatory to return JSON according to the Schema definition. (Function Calling)"""
        pass

class BaseAgentNode(ABC):
    """
    Standard interface for Nodes in LangGraph.
    Each Node must have clear logic for handling state.
    """
    @abstractmethod
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Receive current state, process logic, and return updated state.
        """
        pass