
# 📘  EduVoice – AI Agent for PDF-to-Audio Accessibility
___

Making Reading Accessible for Everyone

5 day Agentic AI Competition for ** Slater_ Team**

EduVoice is an AI-powered agent designed to convert PDFs into high-quality voice recordings, enabling blind and visually impaired learners to access written content easily and independently.

## 🚨 Problem Statement
___


Millions of blind and visually impaired people struggle with one core challenge:

Most educational material is locked inside PDFs — inaccessible without assistance.

Not all PDFs are screen-reader friendly. Many contain:

Two-column layouts

Images with text

Dense academic formatting

Unlabelled headings

Complex diagrams

Traditional screen readers fail or read content in the wrong order, making learning exhausting or impossible.

EduNarrator aims to solve this by giving visually impaired learners a way to “hear” any PDF, effortlessly.

## 🎯 Solution Overview
___


EduVoice is an agentic AI system that:

- Reads any PDF

- Extracts and cleans the text

- Understands the structure

- Converts the content into natural, human-sounding speech

- Outputs a single MP3 that can be listened to anywhere

It allows blind learners to:

- Study books and notes

- Review lecture slides

- Revise through audio

- Access inaccessible PDFs

Learn independently without waiting for assistance

## 🧠 How It Works (Agent Architecture)
___


EduNarrator consists of five cooperating AI agents:

1️⃣ PDF Reader Agent

Extracts text accurately from PDF pages using intelligent parsing, even with multi-column layouts.

2️⃣ Cleaner Agent

Removes page numbers, headers, footers, fixed formatting issues, and merges broken lines.

3️⃣ Chunker Agent

Splits text into manageable, speaker-friendly segments.

4️⃣ Narrator Agent (TTS)

Uses advanced text-to-speech models (OpenAI / Google / ElevenLabs) to generate natural human-like audio.

5️⃣ Audio Merge Agent

Combines all generated audio chunks into a final MP3 file.

## 🧩 Features
___


✔️ Accessibility-First Design

Built for blind and low-vision users based on real accessibility challenges.

✔️ Reads Any PDF

Academic papers, textbooks, notes, assignments, slides — all supported.

✔️ High-Quality Voice Output

Select from multiple voices and speaking styles.

✔️ Optional Educational Enhancements

Audio summaries

Simplified explanations

Section-wise playback

Multi-language voice output

✔️ Fast & Lightweight

Optimized for rapid conversions.

## 🚀 Tech Stack

- Python – backend orchestration

- React – frontend UI

- PDFBox – PDF extraction

- FFmpeg – audio merging

## 📦 System Dependencies

**IMPORTANT**: Before running EduVoice, you must install and configure the following system dependencies. These tools must be available in your system's PATH:

### 1. Tesseract OCR

Required for Optical Character Recognition (OCR) when processing scanned PDFs or PDFs with embedded images containing text.

**Windows:**
1. Download the installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer (recommended: `tesseract-ocr-w64-setup-5.x.x.exe`)
3. During installation, **check the option to add Tesseract to your PATH**
4. Verify installation by running in PowerShell/Command Prompt:
   ```bash
   tesseract --version
   ```

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

### 2. Poppler

Required for converting PDF pages to images (used by the `pdf2image` library for OCR processing).

**Windows:**
1. Download Poppler for Windows from: https://github.com/oschwartz10612/poppler-windows/releases/
2. Extract the ZIP file to a folder (e.g., `C:\poppler`)
3. Add the `bin` folder to your system PATH:
   - Open System Properties → Environment Variables
   - Add `C:\poppler\Library\bin` to your PATH (or wherever you extracted it)
4. Verify installation by running:
   ```bash
   pdftoppm -h
   ```

**macOS:**
```bash
brew install poppler
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install poppler-utils
```

### 3. FFmpeg

Required for merging audio chunks into the final MP3 output file (used by `pydub` library).

**Windows:**
1. Download FFmpeg from: https://ffmpeg.org/download.html#build-windows
   - Or use a build from: https://www.gyan.dev/ffmpeg/builds/
2. Extract the ZIP file to a folder (e.g., `C:\ffmpeg`)
3. Add the `bin` folder to your system PATH:
   - Open System Properties → Environment Variables
   - Add `C:\ffmpeg\bin` to your PATH
4. Verify installation by running:
   ```bash
   ffmpeg -version
   ```

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

### Verifying Installation

After installing all dependencies, verify they are accessible from the command line:

```bash
# Check Tesseract
tesseract --version

# Check Poppler (pdftoppm should be available)
pdftoppm -h

# Check FFmpeg
ffmpeg -version
```

If any of these commands fail with "command not found" or similar errors, the tool is not in your PATH and the application will fail at runtime. Make sure to restart your terminal/IDE after modifying PATH variables.

## ⚙️ Installation & Setup

### Prerequisites

- Python 3.8 or higher
- All system dependencies installed (see above)
- Google Gemini API key (for AI features)

### Python Package Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd EduVoice
   ```

2. Create a virtual environment (recommended):
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your API key:
   - Create a `config.py` file in the root directory
   - Add your Gemini API key:
     ```python
     GEMINI_API_KEY = "your-api-key-here"
     ```

### Running the Application

Start the Streamlit application:

```bash
streamlit run Home.py
```

The application will be available at `http://localhost:8501`

## 🛡️ License
___

MIT License

💙 Motivation

EduVoice was built with one goal:

Make education accessible to everyone, regardless of visual ability.

No student should be left out because a PDF is unreadable.
