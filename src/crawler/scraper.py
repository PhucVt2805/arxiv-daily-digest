import arxiv
from ast import List
from src.model import ArxivPaper
from typing import Literal, List
from src.utils.log_config import get_logger
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timezone, timedelta

logger = get_logger("Crawler") 

class ArxivScraper:
    def __init__(self):
        self.client = arxiv.Client(
                page_size = 100,
                delay_seconds = 3,
                num_retries = 3
            )

    def get_paper(
            self,
            topics: List[Literal["AI", "AR", "CC", "CE", "CL", "CR", "CV", "CY", "DB", "DC", "DL", "DM", "DS", "ET", "GR", "GT", "HC", "IR", "IT", "LO", "LG", "MA", "MM", "MS", "NA", "NE", "NI", "OS", "PF", "PL", "RO", "SC", "SD", "SE", "SI", "SY"]] = "AI",
            days_back: int = 3
        ) -> list[ArxivPaper]:
        """Get recent papers from arXiv based on topic and date.
        
        Args:
            topic (Literal): The research area to filter papers. Defaults to "AI".
                includes:
                    AI: Artificial Intelligence
                    AR: Hardware Architecture
                    CC: Computational Complexity
                    CE: Computational Engineering, Finance, and Science
                    CL: Computation and Language
                    CR: Cryptography and Security
                    CV: Computer Vision and Pattern Recognition
                    CY: Computers and Society
                    DB: Databases
                    DC: Distributed, Parallel, and Cluster Computing
                    DL: Digital Libraries
                    DM: Discrete Mathematics
                    DS: Data Structures and Algorithms
                    ET: Emerging Technologies
                    GR: Graphics
                    GT: Computer Science and Game Theory
                    HC: Human-Computer Interaction
                    IR: Information Retrieval
                    IT: Information Theory
                    LO: Logic in Computer Science
                    LG: Machine Learning
                    MA: Multiagent Systems
                    MM: Multimedia
                    MS: Mathematical Software
                    NA: Numerical Analysis
                    NE: Neural and Evolutionary Computing
                    NI: Networking and Internet Architecture
                    OS: Operating Systems
                    PF: Performance
                    PL: Programming Languages
                    RO: Robotics
                    SC: Symbolic Computation
                    SD: Sound
                    SE: Software Engineering
                    SI: Social and Information Networks
                    SY: Systems and Control

            date_str (str): The date string in "dd/mm/yyyy" format to filter papers published after this date. Defaults to 3 days before today.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing paper details.
        """
        
        logger.info(f'Calling the Arxiv API for topics: {topics} in the past {days_back}...')
        today = datetime.now(timezone.utc).date()

        query = " OR ".join([f"cat:cs.{t}" for t in topics])
        search = arxiv.Search(
            query = query,
            max_results = 200,
            sort_by = arxiv.SortCriterion.LastUpdatedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        results_list = []

        seen_ids = set()

        try:
            for result in self.client.results(search):
                print(result.entry_id)
                if result.updated.date() > today - timedelta(days=days_back):  
                    break
                short_id = result.entry_id.split('/')[-1]


                if short_id in seen_ids:
                    continue
                seen_ids.add(short_id)

                paper = ArxivPaper(
                    _id = result.entry_id.split('/')[-1],
                    title = result.title.replace('\n', ' '),
                    author = [str(a) for a in result.authors],
                    arxiv_url = result.entry_id,
                    pdf_url=result.pdf_url,
                    published_date=result.published,
                    updated_date=result.updated,
                    summary = result.summary.replace('\n', ' '),
                    prime_category = result.primary_category,
                    categories = result.categories
                )
                results_list.append(paper)
                
        except Exception as e:
            logger.error(f'Error fetching papers: {e}')
        
        logger.info(f'Found {len(results_list)} papers updated in the last {days_back} days in topics: {topics}')

        return results_list
    
    async def save_to_db(self, papers: List[ArxivPaper]) -> int:
        """An asynchronous function to save to MongoDB via Beanie.
        Returns the number of new posts added."""
        if not papers:
            logger.info("No new papers to save.")
            return 0
        
        new_count = 0
        logger.info('Start saving to the database...')

        for paper in papers:
            try:
                await paper.insert()
                new_count += 1
            except DuplicateKeyError:
                pass
            except Exception as e:
                logger.error(f'Error saving paper ID {paper.id}: {e}')

        logger.info(f'Saved {new_count} new papers to the Mongodb.')
        return new_count