Plagiarism Analyzer – Installation & Usage Guide
A modern desktop tool for checking document similarity and potential plagiarism, built with Python, NLP techniques (TF-IDF, Cosine Similarity), and a sleek, intuitive UI powered by CustomTkinter.

Features
Upload and compare two documents (PDF or TXT) for similarity score (%).

Scan web sources (Google Scholar, ResearchGate) for similarity against popular research papers.

Modern, rounded & dark/light themed UI (CustomTkinter).

Fast & offline analysis with optional online research matching.

Requirements
OS: Windows, macOS, or Linux

Python: Version 3.10 or later (recommended)

Internet Connection: Required for “Scan Web” feature

1. Setup Instructions
1.1. Clone or Download the Project

   git clone https://github.com/yourusername/plagiarism-analyzer.git
   cd plagiarism-analyzer

OR
Download and extract the ZIP file, then open the folder in your terminal.
1.2. Create and Activate a Virtual Environment

python -m venv .venv
# Activate venv (Windows)
.\.venv\Scripts\activate
# Activate venv (macOS/Linux)
source .venv/bin/activate

1.3. Install the Required Packages

pip install --upgrade pip
pip install -r requirements.txt
If there is no requirements.txt, install directly:


pip install scikit-learn numpy customtkinter pdfplumber google-search-results playwright parsel
python -m playwright install chromium
2. API Keys (for Web Searching)
Google Scholar queries use SerpApi.

Register and get a free API key from serpapi.com.

Set your API key with (replace key as needed):
# On Windows:
set SERPAPI_KEY=your_actual_serpapi_key_here
# On macOS/Linux:
export SERPAPI_KEY=your_actual_serpapi_key_here
Or edit your .env or main Python script if preferred.

3. Running the Application

python plagiarism_analyzer.py
4. Using the App
4.1. Compare Two Documents
Choose the "Compare Two Docs" tab.

Upload your first and second document (TXT or PDF).

Press Compare.

View the similarity score shown as a percentage.

4.2. Scan Web for Similarity
Open the "Scan Web" tab.

Upload your document (TXT or PDF).

Enter keywords or paper title to search the web.

Press Scan Web.

The app finds research snippets and computes the top similarity score.

5. Packaging as an Executable (Optional for Non-Technical Users)
To bundle as a standalone Windows .exe (no Python needed):

pip install pyinstaller
pyinstaller --onefile --noconsole plagiarism_analyzer.py
Output will be in the /dist folder.

Share the .exe with other users.

6. Troubleshooting & Tips
If PDF files don't extract text, ensure they aren't scanned images or encrypted.

Error messages (e.g., "Failed to read file") often mean the app cannot extract usable machine text.

For best results, use plain, text-based PDFs or TXT files.

7. License
This project is open-source. See the LICENSE file for details.
