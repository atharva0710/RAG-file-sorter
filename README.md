# Content Alchemist

**RAG-based Intelligent Auto-tagger**  
Automatically organize and classify PDF and text files using AI-powered content analysis.

## Overview

Content Alchemist is a Python-based file organization system that monitors a designated folder for new files. When a PDF or TXT file is added, the system:

1. Extracts text content from the file
2. Analyzes the content using Google Gemini AI
3. Generates an intelligent, descriptive filename
4. Categorizes and moves the file to the appropriate folder
5. Stores metadata and summaries in a searchable SQLite database

## Features

- **Automated File Monitoring**: Uses watchdog library to detect new files in real-time
- **Intelligent Classification**: Leverages Google Gemini AI for content understanding
- **Dynamic Categories**: Supports predefined categories with automatic creation of new ones as needed
- **Smart Renaming**: Generates descriptive filenames in snake_case format with year prefixes
- **Searchable Archive**: Full-text search capabilities through an integrated dashboard
- **SQLite Logging**: Maintains a complete audit trail of all processed files

## Quick Start

### Prerequisites

- Python 3.9 or higher
- Google Gemini API key ([Get one here](https://aistudio.google.com/apikey))

### Installation

1. Clone the repository:

```bash
git clone https://github.com/atharva0710/RAG-file-sorter.git
cd RAG-file-sorter
```

2. Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

3. Configure your API key:

```bash
cp .env.example .env
# Edit .env and add your API key:
# GEMINI_API_KEY=your-actual-api-key-here
```

### Usage

#### Starting the File Watcher

The watcher monitors the input directory and processes files automatically:

```bash
python3 watcher.py
```

Leave this terminal running. The watcher will display:

```
Watching '/path/to/input_drop_zone' for new files...
Press Ctrl+C to stop.
```

#### Starting the Dashboard (Optional)

Launch the Streamlit dashboard in a separate terminal:

```bash
streamlit run main_dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`.

#### Processing Files

1. Copy or move any PDF or TXT file into the `input_drop_zone/` folder
2. The watcher will automatically:
   - Extract text content
   - Classify the document
   - Generate a descriptive filename
   - Move it to the appropriate category folder
   - Log the transaction to the database

Example output:

```
[watcher] New file detected: my_messy_file.pdf
[watcher] Classifying...
[watcher] Category : ML-Bio
[watcher] New name : 2026_protein_folding_research.pdf
[watcher] Summary  : This paper discusses protein folding using deep learning.
[organizer] Moved to /organized_storage/ML-Bio/2026_protein_folding_research.pdf
[logger] Saved record for '2026_protein_folding_research.pdf'
[watcher] Done!
```

## Project Structure

```
RAG_fileSorter/
├── input_drop_zone/          # Input directory for new files
├── organized_storage/         # Output directory with categorized files
│   ├── ML-Bio/
│   ├── Systems CS/
│   ├── Finance/
│   └── Personal/
├── watcher.py                 # File monitoring daemon
├── main_dashboard.py          # Streamlit web interface
├── processor.py               # Text extraction module
├── classifier.py              # AI classification engine
├── organizer.py               # File management utilities
├── db.py                      # SQLite database interface
├── test_pipeline.py           # Manual processing script
└── content_alchemist.db       # SQLite database (auto-created)
```

## Dashboard Features

The Streamlit dashboard provides two main interfaces:

### Recent Files Tab

- Displays the last 20 processed files in a table format
- Columns: Original Filename, New Filename, Category, Summary, Timestamp

### Query Tab

- Full-text search across file summaries
- Example queries:
  - "What papers are about Biology?"
  - "Show me finance documents"
  - "transformer protein"

## Configuration

### Adding Categories

Edit the `VALID_CATEGORIES` list in `classifier.py`:

```python
VALID_CATEGORIES = [
    "Systems CS",
    "ML-Bio",
    "Personal",
    "Finance",
    "History",        # Add custom categories
    "Philosophy",
]
```

**Note**: The system can also dynamically create new categories. If a file doesn't fit existing categories, the AI will suggest an appropriate new category name.

### Changing the AI Model

Modify the `MODEL_NAME` variable in `classifier.py`:

```python
MODEL_NAME = "gemini-flash-latest"  # or "gemini-2.0-flash", etc.
```

### Data Storage Locations

- Organized files: `organized_storage/` directory
- Database: `content_alchemist.db` (SQLite file in project root)

## Manual Processing

Process files without the watcher daemon:

```bash
# Using the test script
python3 test_pipeline.py

# Direct classification
python3 classifier.py path/to/your/file.pdf
```

## Troubleshooting

### Missing Dependencies

```bash
python3 -m pip install -r requirements.txt
```

### API Rate Limiting

If you encounter "429 quota exceeded" errors, you've reached the Gemini API rate limit. Wait a few minutes or upgrade your API plan.

### Files Not Processing

- Verify the file format is `.pdf` or `.txt` (unsupported formats move to `_unsupported/`)
- Check the watcher terminal for error messages
- Ensure files aren't locked by other programs

### Empty Dashboard

- Confirm at least one file has been processed
- Verify `content_alchemist.db` exists in the project root

## Example Workflow

**Scenario**: Organizing 100 research papers with inconsistent naming

1. Start the watcher: `python3 watcher.py`
2. Start the dashboard: `streamlit run main_dashboard.py`
3. Copy all PDFs into `input_drop_zone/`
4. Wait 2-3 minutes for processing
5. Results:
   - Files sorted into appropriate category folders
   - Descriptive, standardized filenames
   - Searchable summaries in the dashboard

## Technical Details

This project demonstrates:

- **File System Monitoring**: Real-time file detection with `watchdog`
- **PDF Processing**: Text extraction using `PyPDF2`
- **LLM Integration**: Structured prompting with Google Gemini API
- **JSON Response Parsing**: Reliable extraction of AI-generated metadata
- **Database Operations**: SQLite for persistent storage and search
- **Web Interfaces**: Streamlit for rapid dashboard development
- **File I/O**: Cross-platform file operations with Python's `os` and `shutil`

## Extension Ideas

- Support additional file formats (`.docx`, `.epub`, `.html`)
- Enhanced metadata extraction (authors, publication dates, citations)
- Duplicate detection and deduplication
- Email or webhook notifications
- Cloud storage integration (Google Drive, Dropbox, S3)
- OCR support for scanned documents
- Batch processing mode for large archives

## Support

If you encounter issues:

1. Check the watcher terminal for detailed error messages
2. Verify your `.env` file contains a valid API key
3. Inspect `organized_storage/_unclassified/` and `_unsupported/` directories
4. Review the database: `sqlite3 content_alchemist.db` then `SELECT * FROM files;`

## License

MIT License - see LICENSE file for details

## Author

Atharva Mandhaniya  
GitHub: [@atharva0710](https://github.com/atharva0710)
