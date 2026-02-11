# 🧪 Content Alchemist — User Guide

**RAG-based Intelligent Auto-tagger**  
Automatically organize your messy PDFs and text files using AI.

---

## 📖 What Does This Do?

Content Alchemist watches a folder on your computer. When you drop a file (PDF or TXT) into it:

1. **Reads** the file and extracts text
2. **Understands** the content using Google Gemini AI
3. **Renames** the file intelligently (e.g., `2026_genetic_encoding_analysis.pdf`)
4. **Moves** it to the correct category folder (e.g., `ML-Bio`, `Systems CS`, `Finance`, `Personal`)
5. **Saves** a summary to a database so you can search later

---

## 🚀 Quick Start (5 Steps)

### Step 1: Install Dependencies

Open your terminal in the project folder and run:

```bash
cd /Users/atharvamandhaniya/Desktop/Python/RAG_fileSorter
python3 -m pip install -r requirements.txt
```

This installs all the libraries you need (PyPDF2, Streamlit, watchdog, etc.).

---

### Step 2: Add Your API Key

You already have a `.env` file with your Gemini API key. If you need to change it:

```bash
# Open the .env file
nano .env

# It should look like this:
GEMINI_API_KEY=your-actual-api-key-here
```

Save and exit (`Ctrl+X`, then `Y`, then `Enter`).

---

### Step 3: Start the Watcher

The watcher is the "brain" that monitors your drop zone. Start it:

```bash
python3 watcher.py
```

You'll see:

```
👁  Watching '/Users/atharvamandhaniya/Desktop/Python/RAG_fileSorter/input_drop_zone' for new files...
   Drop a PDF or TXT file in there and watch the magic.
   Press Ctrl+C to stop.
```

**Leave this terminal running.** Open a new terminal for the next step.

---

### Step 4: Start the Dashboard (Optional)

The dashboard lets you browse and search your organized files. In a **new terminal**:

```bash
cd /Users/atharvamandhaniya/Desktop/Python/RAG_fileSorter
streamlit run main_dashboard.py
```

Your browser will open automatically to `http://localhost:8501`.

---

### Step 5: Drop a File and Watch

1. Find any PDF or TXT file on your computer (research paper, article, notes, etc.)
2. **Copy or move it** into the `input_drop_zone/` folder
3. Watch the terminal where `watcher.py` is running

You'll see something like:

```
============================================================
[watcher] New file detected: my_messy_file.pdf
============================================================
[watcher] Classifying...
[watcher] Category : ML-Bio
[watcher] New name : 2026_protein_folding_research.pdf
[watcher] Summary  : This paper discusses protein folding using deep learning.
[organizer] Moved → /Users/.../organized_storage/ML-Bio/2026_protein_folding_research.pdf
[logger] Saved record for '2026_protein_folding_research.pdf' in category 'ML-Bio'
[watcher] ✅ Done!
```

4. Check the `organized_storage/` folder — your file is now there, renamed and organized!

---

## 📂 Folder Structure

```
RAG_fileSorter/
├── input_drop_zone/          ← Drop files here
├── organized_storage/         ← Organized files appear here
│   ├── ML-Bio/
│   ├── Systems CS/
│   ├── Finance/
│   └── Personal/
├── watcher.py                 ← The automation script
├── main_dashboard.py          ← The Streamlit UI
├── processor.py               ← Extracts text from PDFs/TXT
├── classifier.py              ← Talks to Gemini AI
├── organizer.py               ← Moves and renames files
├── db.py                      ← SQLite logger
└── content_alchemist.db       ← Database (auto-created)
```

---

## 🎯 Using the Dashboard

Once you run `streamlit run main_dashboard.py`, you'll see two tabs:

### 📋 Recent Tab

- Shows a table of the **last 20 processed files**
- Columns: Original Filename, New Filename, Category, Summary, Processed At

### 🔍 Query Tab

- Type questions like:
  - _"What papers are about Biology?"_
  - _"Show me finance documents"_
  - _"transformer protein"_
- The app searches the **summary** column and shows matching files

---

## 🛠️ Common Tasks

### How do I add more categories?

Edit `classifier.py` and change the `VALID_CATEGORIES` list:

```python
VALID_CATEGORIES = [
    "Systems CS",
    "ML-Bio",
    "Personal",
    "Finance",
    "History",        # Add new ones here
    "Philosophy",
]
```

### How do I change the AI model?

Edit `classifier.py` and change the `MODEL_NAME`:

```python
MODEL_NAME = "gemini-flash-latest"  # or "gemini-2.0-flash", etc.
```

### How do I stop the watcher?

Press `Ctrl+C` in the terminal where `watcher.py` is running.

### Where is my data stored?

- **Files**: `organized_storage/` folder
- **Database**: `content_alchemist.db` (SQLite file in the project root)

### Can I process files manually (without the watcher)?

Yes! Use the test script:

```bash
python3 test_pipeline.py
```

Or run the classifier directly:

```bash
python3 classifier.py path/to/your/file.pdf
```

---

## 🐛 Troubleshooting

### "No module named 'PyPDF2'"

Run: `python3 -m pip install -r requirements.txt`

### "API call failed: 429 quota exceeded"

You've hit the Gemini API rate limit. Wait a few minutes or upgrade your API plan.

### "File not moved / still in drop zone"

- Check the watcher terminal for error messages
- Make sure the file is a `.pdf` or `.txt` (other formats go to `_unsupported/`)
- Make sure the file isn't locked or being used by another program

### Dashboard shows "No files found"

- Make sure you've processed at least one file with the watcher
- Check that `content_alchemist.db` exists in the project folder

---

## 📊 Example Workflow

**Scenario**: You have 100 research papers with names like `paper_final_v3.pdf`, `draft.pdf`, etc.

1. Start the watcher: `python3 watcher.py`
2. Start the dashboard: `streamlit run main_dashboard.py`
3. Drag all 100 PDFs into `input_drop_zone/`
4. Wait 2-3 minutes (depending on file size and API speed)
5. Check `organized_storage/` — all files are now:
   - Sorted into category folders
   - Renamed with descriptive names
   - Searchable via the dashboard

---

## 🎓 What You Learned

By building this project, you now understand:

- **File watching** with Python's `watchdog` library
- **PDF text extraction** with PyPDF2
- **LLM integration** with Google Gemini API
- **Structured prompts** to get JSON responses from AI
- **SQLite databases** for logging and search
- **Streamlit dashboards** for building UIs without JavaScript
- **File operations** (moving, renaming, folder creation)

---

## 🚀 Next Steps

Want to extend this project? Try:

1. **Add more file types**: Support `.docx`, `.epub`, etc.
2. **Smarter summaries**: Ask the LLM to extract key findings, authors, dates
3. **Duplicate detection**: Check if a file already exists before processing
4. **Email notifications**: Get notified when files are processed
5. **Cloud storage**: Auto-upload organized files to Google Drive or Dropbox

---

## 📞 Need Help?

If something isn't working, check:

1. The terminal where `watcher.py` is running (error messages appear there)
2. Your `.env` file (make sure the API key is correct)
3. The `organized_storage/` folder (files might be in `_unclassified/` or `_unsupported/`)

Happy organizing! 🧪✨
