<div align="center">
  <h1>🔬 Arxiv CS Research Agent</h1>
  <p>
    <b>An Autonomous AI Agent powered by LangGraph & Google Gemini</b><br />
    <i>Automated Daily News, Deep Paper Analysis, and RAG-based Chat for Computer Science Researchers.</i>
  </p>
  <p>
    <img
      src="https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python&logoColor=white"
      alt="Python"
    />
    <img
      src="https://img.shields.io/badge/Framework-LangGraph-orange?style=for-the-badge"
      alt="LangGraph"
    />
    <img
      src="https://img.shields.io/badge/LLM-Google%20Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white"
      alt="Gemini"
    />
    <img
      src="https://img.shields.io/badge/Docker-Microservices-2496ED?style=for-the-badge&logo=docker&logoColor=white"
      alt="Docker"
    />
    <img
      src="https://img.shields.io/badge/Database-Mongo%20%2B%20Qdrant-green?style=for-the-badge"
      alt="DB"
    />
  </p>
</div>

<hr />
<h2>📑 Table of Contents</h2>
<ul>
  <li><a href="#about">About the Project</a></li>
  <li><a href="#architecture">System Architecture</a></li>
  <li><a href="#features">Key Features</a></li>
  <li><a href="#tech-stack">Tech Stack</a></li>
  <li><a href="#getting-started">Getting Started</a></li>
  <li><a href="#project-structure">Project Structure</a></li>
</ul>
<hr />

<h2 id="about">💡 About the Project</h2>
<p>
  The <b>Arxiv CS Research Agent</b> is a solution designed to tackle
  "Information Overload" in the Computer Science research field. Instead of
  manually scrolling through hundreds of new abstracts on arXiv daily, this
  system acts as a personal research assistant.
</p>
<p>
  It utilizes a <b>Microservices Architecture</b> to separate concerns between
  data ingestion (Backend) and user interaction (Frontend). At its core, it
  leverages <b>LangGraph</b> to orchestrate a ReAct (Reasoning + Acting) Agent
  capable of deciding when to search the web for general knowledge or download
  and analyze a full PDF for deep technical details.
</p>

<hr />

<h2 id="architecture">🏗 System Architecture</h2>

<p>
  The system follows a <b>Polyglot Persistence</b> pattern and is containerized
  using Docker Compose.
</p>

<ol>
  <li>
    <h3>Frontend Service</h3>
    <p>
      Built with <b>Streamlit</b>. Provides a dual-mode interface: "Daily News"
      for quick updates and "Research Mode" for deep diving into historical
      topics using keywords and date filters.
    </p>
  </li>

  <li>
    <h3>Backend Service</h3>
    <p>
      Built with <b>FastAPI</b>. Handles crawling logic, vectorization, and
      hosts the LangGraph Agent. Manages communication with external APIs
      (Arxiv, Google Gemini).
    </p>
  </li>

  <li><h3>Data Layer</h3></li>
  <ol style="list-style-type: lower-latin">
    <li>
      <b>MongoDB:</b> Stores paper metadata (titles, authors, summary) and the
      <i>Deep Analysis</i> (AI-generated summaries) of full PDFs.
    </li>
    <li>
      <b>Qdrant:</b> Stores vector embeddings (768d) for Semantic Search and RAG
      (Retrieval-Augmented Generation).
    </li>
  </ol>
</ol>

<hr />

<h2 id="features">✨ Key Features</h2>
<ol>
<li><h3>Intelligent Data Ingestion</h3></li>
<ol style="list-style-type: lower-latin">
  <li>
    <b>Smart Deduplication:</b> Checks existing records to avoid processing the
    same paper twice.
  </li>
  <li>
    <b>Flexible Crawling:</b> Supports fetching by Topic (e.g.
    <code>cs.CV</code>, <code>cs.AI</code>), Keyword (e.g. "YOLO", "LLM") and
    Date Range.
  </li>
  <li>
    <b>Research Mode:</b> Ability to scrape historical data from specific start
    dates (e.g. "Papers about Transformers since 2017").
  </li>
</ol>

<li><h3>Deep Analysis Strategy (Token Optimization)</h3></li>
<p>
  Instead of feeding raw PDFs into the chat context (which consumes massive
  tokens and introduces noise), the system employs a
  <b>Pre-processing Agent</b>:
</p>
<ol style="list-style-type: lower-latin">
  <li>Downloads the PDF via <b>PyMuPDF</b>.</li>
  <li>
    Uses <b>LLM</b> to extract core contributions, methodology,
    experiments, and limitations.
  </li>
  <li>Saves this <b>Structured Analysis</b> into MongoDB.</li>
  <li>
    The Chat Agent uses this structured analysis for future queries, reducing
    token costs by <b>~90%</b>.
  </li>
</ol>

<li><h3>LangGraph ReAct Agent</h3></li>
<p>
  The chat bot is not a simple chain, it's a reasoning engine that selects tools
  dynamically:
</p>
<ol style="list-style-type: lower-latin">
  <li><b>Chat:</b> Handles general conversation based on the <b>Abstract</b>.</li>
  <li>
    <b>Tool "web_search":</b> Used to retrieve <b>external information</b> beyond the scope of the paper (powered by <b>DuckDuckGo</b>).
  </li>
  <li>
    <b>Tool "read_full_paper":</b> Triggers the PDF <b>download and
      analysis</b> pipeline when the user asks about <b>specific details</b> (Math, Formulas,
      Architectures).
    </li>
  </ol>
</ol>

<hr />

<h2 id="demo">📸 Demo Applications</h2>

<h3>1. Research Mode (Deep Dive)</h3>
<p>
  <i>Allows users to search for historical papers using specific keywords (e.g., "YOLO", "Transformers") combined with date filters to retrieve foundational research.</i>
</p>
<img src="demo/ResearchMode.png" alt="Research Mode Interface" width="50%" style="border-radius: 10px; box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);" />
<br><br>

<h3>2. News Mode (Daily Updates)</h3>
<p>
  <i>Designed for daily catch-ups. Users can filter new papers by specific arXiv categories (e.g., Computer Vision, AI) updated within the last few days.</i>
</p>
<img src="demo/NewsMode.png" alt="News Mode Interface" width="50%" style="border-radius: 10px; box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);" />
<br><br>

<h3>3. Search Results & Chat Entry</h3>
<p>
  <i>Displays fetched papers with advanced sorting (Date/Category). Users can expand abstracts for a quick preview or click "Chat" to start the RAG pipeline.</i>
</p>
<img src="demo/ListOfPaper.png" alt="List of Papers Interface" width="50%" style="border-radius: 10px; box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);" />


<hr />

<h2 id="tech-stack">🛠 Tech Stack</h2>

<ul>
  <li><b>Language:</b> <a href="https://www.python.org/">Python</a> 3.10</li>
  <li>
    <b>Package Manager:</b>
    <a href="https://docs.astral.sh/uv/">uv</a> (Ultra-fast Python package installer)
  </li>
  <li><b>Containerization:</b> <a href="https://www.docker.com/">Docker</a> & Docker Compose</li>
  <li><b>Backend:</b> <a href="https://fastapi.tiangolo.com/">FastAPI</a>, <a href="https://beanie-odm.dev/">Beanie</a> (ODM), <a href="https://www.mongodb.com/docs/drivers/motor/">Motor</a> (Async Mongo Driver)</li>
  <li><b>Frontend:</b> <a href="https://streamlit.io/">Streamlit</a></li>
  <li>
    <b>AI & LLM:</b> <a href="https://www.langchain.com/">LangChain</a>, <a href="https://www.langchain.com/langgraph">LangGraph</a>, <a href="https://aistudio.google.com/">Google Gemini</a>
  </li>
  <li><b>Database:</b> <a href="https://www.mongodb.com/">MongoDB</a> (Document Store), <a href="https://qdrant.tech/">Qdrant</a> (Vector Engine)</li>
</ul>

<hr />

<h2 id="getting-started">🚀 Getting Started</h2>

<h3>Prerequisites</h3>
<ul>
  <li>Docker installed.</li>
  <li>Google AI Studio API Key.</li>
</ul>

<h3>Installation</h3>
<ol>
<li><h4>Clone the repository:</h4></li>
<pre><code>git clone https://github.com/PhucVt2805/arxiv-research-agent.git</pre></code>
<pre><code>cd arxiv-research-agent</code></pre>

<li><h4>Configure Environment Variables:</h4></li>
<p>Create a <code>.env</code> file in the root directory:</p>
<pre><code>MONGO_USER=YOUR_USERNAME
MONGO_PASS=YOUR_PASSWORD
VECTOR_SIZE=768
GOOGLE_API_KEY=YOUR_API_KEY
</code></pre>

<li><h4>Build and Run:</h4></li>
<pre><code>docker-compose up --build</code></pre>

<li><h4>Access the Application:</h4></li>
<ol style="list-style-type: lower-latin">
  <li>
    <b>Frontend (UI):</b>
    <a href="http://localhost:8501">http://localhost:8501</a>
  </li>
  <li>
    <b>Backend:</b>
    <a href="http://localhost:8000">http://localhost:8000</a>
  </li>
  <li>
    <b>Qdrant (Dashboard):</b>
    <a href="http://localhost:6333/dashboard">http://localhost:6333/dashboard</a>
  </li>
</ol>

</ol>

<hr />

<h2 id="project-structure">📂 Project Structure</h2>
  <pre><code>arxiv-cs-research-agent/
├── docker-compose.yml                # Service Orchestration
├── .env                              # Environment Config
├── pyproject.toml                    # Dependencies (Root)
├── README.md                         # Project Overview
├── uv.lock                           # Package Installer Lock
│
├── backend/                          # [Microservice] API & Worker
│   ├── pyproject.toml                # Dependencies
│   ├── Dockerfile                    # Multi-stage build
│   └── src/
│       ├── database.py               # DB Connections
│       ├── main.py                   # FastAPI Entrypoint
│       ├── models.py                 # Beanie ODM Models
│       ├── processor.py              # Vector Embeddings
│       ├── crawler/                  # Arxiv Scraper
│       ├── utils/                    # Log Config
│       └── agent/                    # LangGraph Logic
│           ├── graph.py              # ReAct Graph Definition
│           ├── tools.py              # Search & PDF Tools
│           └── paper_processor.py    # Paper Analysis
│
└── frontend/                         # [Microservice] User Interface
    ├── Dockerfile                    # Multi-stage build
    ├── pyproject.toml                # Dependencies
    └── src/
        └── main.py                   # Streamlit Application
</code></pre>

<hr />

<div align="center">
  <p>Built with ❤️ by a dedicated AI Engineer.</p>
  <p><i>If you find this project useful, please give it a star! ⭐️</i></p>
</div>