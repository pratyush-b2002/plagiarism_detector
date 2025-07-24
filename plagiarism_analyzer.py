import os
import threading
from urllib.parse import urlsplit
from tkinter import filedialog
import customtkinter as ctk

import pdfplumber
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# External APIs and scraping
from serpapi import GoogleSearch
from playwright.sync_api import sync_playwright
from parsel import Selector

# Get your SerpApi API key from environment variable, fallback to empty string for safety
API_KEY = os.environ.get("SERPAPI_KEY", "a0a26b2cd238ae13987115ee5415ea400338bdc451ac53108883689fd3e03fd5")

# User-agent string for scraping ResearchGate
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
     "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"

# --- NLP core setup ---
vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=50000, stop_words='english')


def similarity_percent(doc_a, doc_b):
    tfidf = vectorizer.fit_transform([doc_a, doc_b])
    score = cosine_similarity(tfidf[0], tfidf[1])[0, 0]
    return round(score * 100, 2)


# --- Web fetching functions ---

def scholar_snippets(query, api_key, pages=3):
    params = {"engine": "google_scholar", "q": query, "api_key": api_key}
    docs = []
    for _ in range(pages):
        data = GoogleSearch(params).get_dict()
        docs.extend(r.get("snippet", "") for r in data.get("organic_results", []))
        if "next" not in data.get("pagination", {}):
            break
        next_url = data["pagination"]["next"]
        query_parts = dict(pair.split("=") for pair in urlsplit(next_url).query.split("&"))
        params.update(query_parts)
    return docs


def rg_snippets(term, pages=3):
    snippets = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent=UA)
            for n in range(1, pages + 1):
                url = f"https://www.researchgate.net/search/publication?q={term}&page={n}"
                page.goto(url, timeout=60000)
                sel = Selector(text=page.content())
                snippets += sel.css(".nova-legacy-c-card__body p::text").getall()
            browser.close()
    except Exception as e:
        print(f"Error scraping ResearchGate: {e}")
    return snippets


# --- GUI Application ---

ctk.set_appearance_mode("dark")  # "dark" or "light"
ctk.set_default_color_theme("dark-blue")  # Themes: ['blue', 'dark-blue', 'green']


class PlagApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NLP Plagiarism Analyzer")
        self.geometry("850x500")
        self.minsize(800, 450)

        # Tab view for two options
        tabview = ctk.CTkTabview(self)
        tabview.pack(fill="both", expand=True, padx=20, pady=20)

        self.local_tab = tabview.add("Compare Two Docs")
        self.web_tab = tabview.add("Scan Web")

        # --- Local Comparison Tab ---
        self.file_a = ctk.StringVar()
        self.file_b = ctk.StringVar()

        ctk.CTkButton(self.local_tab, text="Upload Document 1", corner_radius=20,
                      command=lambda: self.pick_file(self.file_a))\
            .grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        ctk.CTkEntry(self.local_tab, textvariable=self.file_a, state="readonly")\
            .grid(row=0, column=1, padx=15, pady=15, sticky="ew")

        ctk.CTkButton(self.local_tab, text="Upload Document 2", corner_radius=20,
                      command=lambda: self.pick_file(self.file_b))\
            .grid(row=1, column=0, padx=15, pady=15, sticky="ew")
        ctk.CTkEntry(self.local_tab, textvariable=self.file_b, state="readonly")\
            .grid(row=1, column=1, padx=15, pady=15, sticky="ew")

        self.local_result_label = ctk.CTkLabel(self.local_tab, text="", font=ctk.CTkFont(size=16))
        self.local_result_label.grid(row=3, column=0, columnspan=2, pady=10)

        self.local_compare_btn = ctk.CTkButton(self.local_tab, text="Compare", corner_radius=25,
                                              command=self.compare_local)
        self.local_compare_btn.grid(row=2, column=0, columnspan=2, pady=15, ipadx=10, ipady=8)

        self.local_tab.grid_columnconfigure(1, weight=1)

        # --- Web Scan Tab ---
        self.file_web = ctk.StringVar()
        self.query = ctk.StringVar()

        ctk.CTkButton(self.web_tab, text="Upload Document", corner_radius=20,
                      command=lambda: self.pick_file(self.file_web))\
            .grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        ctk.CTkEntry(self.web_tab, textvariable=self.file_web, state="readonly")\
            .grid(row=0, column=1, padx=15, pady=15, sticky="ew")

        ctk.CTkEntry(self.web_tab, textvariable=self.query, width=300,
                     placeholder_text="Enter keywords (e.g. paper title)")\
            .grid(row=1, column=0, columnspan=2, padx=15, pady=10, sticky="ew")

        self.web_result_label = ctk.CTkLabel(self.web_tab, text="", font=ctk.CTkFont(size=16))
        self.web_result_label.grid(row=3, column=0, columnspan=2, pady=10)

        self.web_scan_btn = ctk.CTkButton(self.web_tab, text="Scan Web", corner_radius=25,
                                          command=self.compare_web)
        self.web_scan_btn.grid(row=2, column=0, columnspan=2, pady=15, ipadx=10, ipady=8)

        self.web_tab.grid_columnconfigure(1, weight=1)

    def pick_file(self, var):
        filename = filedialog.askopenfilename(title="Select file",
                                              filetypes=[("Text files", "*.txt"), ("PDF files", "*.pdf"),
                                                         ("All files", "*.*")])
        if filename:
            var.set(filename)

    def read_file_text(self, filepath):
        try:
            if filepath.lower().endswith(".pdf"):
                with pdfplumber.open(filepath) as pdf:
                    text = ''.join(page.extract_text() or '' for page in pdf.pages)
            else:
                with open(filepath, encoding="utf-8", errors="ignore") as f:
                    text = f.read()
            return text
        except Exception as e:
            print(f"Error reading file {filepath}: {e}")
            return ""

    def compare_local(self):
        file_a_path = self.file_a.get()
        file_b_path = self.file_b.get()

        if not (file_a_path and file_b_path):
            self.local_result_label.configure(text="Please upload both documents.", text_color="red")
            return

        self.local_result_label.configure(text="Comparing...", text_color="orange")
        self.local_compare_btn.configure(state="disabled")

        def worker():
            doc_a = self.read_file_text(file_a_path)
            doc_b = self.read_file_text(file_b_path)
            if not doc_a or not doc_b:
                self.local_result_label.configure(text="Failed to read files.", text_color="red")
                self.local_compare_btn.configure(state="normal")
                return

            score = similarity_percent(doc_a, doc_b)

            color = "green" if score >= 80 else ("orange" if score >= 40 else "red")
            self.local_result_label.configure(text=f"Similarity: {score}%", text_color=color)
            self.local_compare_btn.configure(state="normal")

        threading.Thread(target=worker, daemon=True).start()

    def compare_web(self):
        file_path = self.file_web.get()
        query_text = self.query.get().strip()

        if not file_path:
            self.web_result_label.configure(text="Please upload a document.", text_color="red")
            return
        if not query_text:
            self.web_result_label.configure(text="Please enter keywords to search.", text_color="red")
            return

        self.web_result_label.configure(text="Scanning web...", text_color="orange")
        self.web_scan_btn.configure(state="disabled")

        def worker():
            doc = self.read_file_text(file_path)
            if not doc:
                self.web_result_label.configure(text="Failed to read document.", text_color="red")
                self.web_scan_btn.configure(state="normal")
                return

            try:
                snippets = []
                if API_KEY:
                    snippets += scholar_snippets(query_text, API_KEY, pages=3)
                else:
                    self.web_result_label.configure(
                        text="SerpApi API key missing or invalid, skipping Google Scholar.", text_color="orange")

                snippets += rg_snippets(query_text, pages=2)

                combined_text = "\n".join(snippets)
                if not combined_text.strip():
                    self.web_result_label.configure(text="No snippets found from web.", text_color="red")
                    self.web_scan_btn.configure(state="normal")
                    return

                score = similarity_percent(doc, combined_text)

                color = "green" if score >= 80 else ("orange" if score >= 40 else "red")
                self.web_result_label.configure(text=f"Highest web similarity: {score}%", text_color=color)
            except Exception as e:
                self.web_result_label.configure(
                    text=f"Error during web scan:\n{str(e)}", text_color="red")
            finally:
                self.web_scan_btn.configure(state="normal")

        threading.Thread(target=worker, daemon=True).start()


if __name__ == "__main__":
    app = PlagApp()
    app.mainloop()
