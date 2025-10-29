# HCI Web Scraper - AI Agent Instructions

## Project Overview
Academic literature scraper targeting HCI/XR research across multiple databases (ACM, IEEE, Springer, ScienceDirect). Built on Scrapy with SQLite storage and Selenium for JavaScript-heavy sites.

## Architecture & Data Flow

### Three-Spider Architecture
1. **Results Spiders**: Search database APIs/sites, extract pagination and DOI lists
2. **Issues Spiders**: Scrape individual paper metadata using DOI/URL lists from database
3. **Pages Spiders**: Download full paper content when available

### Key Components
- `HCIScrapy/config.py`: Defines search queries, database mappings, and inclusion criteria
- `HCIScrapy/database.py`: SQLite operations with upsert patterns for deduplication
- `HCIScrapy/pipelines.py`: Query generation and data processing pipelines
- `HCIScrapy/spiders/`: Database-specific scrapers with different strategies

## Database-Specific Patterns

### Spider Naming Convention
- `{DB}IssuesSpider.py`: Metadata extraction (uses `documents` attribute from DB)
- `{DB}PagesSpider.py`: Full content download
- `{DB}ResultsSpider.py`: Search result pagination

### Search Query Architecture
Each database requires different query formatting in `QueryPipeline`:
```python
# ACM: Field-based searches
'Title:(term) OR Abstract:(term)'

# IEEE: Quoted field syntax  
'"Document Title":term OR "Abstract":term'

# Springer/SD: Simple boolean
'"term1" OR "term2" AND "term3"'
```

## Critical Workflows

### Running Spiders
```bash
# From HCIScrapy directory
cd HCIScrapy
scrapy crawl ieee_issues  # Run specific spider
python run_spider.py      # Run with custom configuration
```

### Environment Setup
```bash
cd HCIScrapy
setup.bat  # Windows dependency installation
```

### Configuration Management
- Search terms defined in `SEARCH_QUERY` arrays in `config.py`
- Trial management via `TRIAL` constant
- Database switching via `STORAGE_TEST` flag
- Connection strings support both SQLite and SQL Server

## Development Patterns

### Spider Attributes
All spiders must define:
```python
name = "spider_name"           # Scrapy identifier
db = "DATABASE_NAME"           # From config constants
stype = "Issues|Pages|Results" # Processing type
url_field = "doi|url"          # Database field for URL construction
use_selenium = True|False      # Selenium requirement
```

### Database Integration
- Use `DatabaseManager.upsert_issue()` for conflict resolution
- All spiders expect `self.documents` list populated by pipeline
- Selenium spiders use `js` meta field for JavaScript execution

### Error Handling
- Spiders continue processing even with individual failures
- Random delays prevent rate limiting: `time.sleep(random.uniform(1, 2))`
- Headers rotation implemented per database requirements

## Testing & Analysis
- `analysis.py`: Term frequency analysis across scraped documents
- Test flags in `config.py` control pipeline behavior
- CSV exports to `output_file.csv` for analysis

When modifying spiders, always consider rate limiting, field mapping differences between databases, and the three-phase scraping workflow.