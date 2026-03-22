# PDF to Anki Flashcard Generator

A tool that converts PDF documents into Anki flashcards using AI models for question generation.

**Primary Usage:** Run `python ui.py` to launch the web interface. This is the intended way to use the application for all users.

## Quick Start

1. **Install Python** (if not already installed)
   - Download from python.org
   - Version 3.8 or higher required

2. **Clone or Download this repository**
   ```bash
   git clone https://github.com/ArnavGandre/PDF-to-Anki.git
   cd PDF-to-Anki
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements_ui.txt
   ```

4. **Get an API key** (choose one):
   - **Groq** (recommended): https://console.groq.com/keys (free tier available)
   - **Google Gemini**: https://ai.google.dev/

5. **Launch the application**
   ```bash
   python ui.py
   ```

6. **Use the interface**
   - Upload your PDF file
   - Enter your API key
   - Choose processing options
   - Click "Generate Flashcards"
   - Download the resulting Anki deck

## Code Explanation

### Core Processing Files

#### ui.py (Primary User Interface)
Gradio-based web application providing the main user interface for the PDF-to-Anki converter.

**Components:**
- Web interface with file upload
- API key input field
- Model selection dropdown
- Processing mode toggle (API/Local)
- Chunk sensitivity slider
- Generate button and download link

**Purpose:** This is the main way users interact with the application. Provides user-friendly access to all processing features through a web browser interface.

#### main.py (Internal Processing Engine)
Backend processing engine that handles the core PDF-to-Anki conversion logic. Not intended for direct user execution.

**Functions:**
- `run_pipeline()`: Main pipeline function that coordinates all processing steps
- `extract_text_from_pdf()`: Extracts raw text from PDF files using pdfplumber

**Workflow:**
1. Extracts text from PDF
2. Breaks text into sentences
3. Groups sentences into semantic chunks
4. Processes each chunk with AI models
5. Sanitizes and formats outputs
6. Creates Anki deck file

**Note:** This file is called internally by ui.py and is not meant to be run or modified by end users.

#### sentence_extract.py
Handles text preprocessing by splitting raw PDF text into individual sentences.

**Functions:**
- `extract_sentences(text)`: Splits text into sentences using regex patterns, cleans whitespace and formatting artifacts

**Purpose:** Converts continuous text blocks into structured sentence arrays for further processing.

#### chunker.py
Implements semantic text chunking using sentence embeddings to group related sentences.

**Functions:**
- `semantic_chunk(sentences, sens)`: Uses sentence-transformers to create embeddings, calculates similarity scores between consecutive sentences, and groups them into coherent chunks based on a sensitivity threshold

**Purpose:** Ensures that related information stays together in processing units, improving AI model performance.

#### json_maker.py
Creates structured JSON data files for processing state management.

**Functions:**
- `json_data(chunks, filename)`: Converts chunk arrays into JSON format with processing metadata

**Purpose:** Provides persistent storage for processing state and chunk data.

#### api_inference.py
Handles external AI API calls for flashcard generation.

**Functions:**
- `api_inference(chunk, model_name, model_type, model_key)`: Makes API calls to Groq or Google Gemini services with retry logic and rate limiting

**Purpose:** Interfaces with cloud AI models to generate question-answer pairs from text chunks.

#### local_inference.py
Manages local AI model inference for offline processing.

**Functions:**
- `load_model(model_name, model_path=None)`: Loads HuggingFace transformers models into memory
- `local_inference(chunk, model_name, model_path=None)`: Processes text chunks using local models

**Purpose:** Enables offline processing using TinyLlama or Phi-3 models.

#### sanitize_output.py
Parses and cleans AI-generated outputs into structured flashcard format.

**Functions:**
- `sanitize_output(text)`: Uses regex patterns to extract question-answer pairs from raw AI responses

**Purpose:** Converts unstructured AI outputs into clean, importable flashcard data.

#### anki_maker.py
Creates Anki deck files from processed flashcard data.

**Functions:**
- `anki_maker(pairs, deck_name, output_filename)`: Uses genanki library to create .apkg files

**Purpose:** Generates final Anki-compatible deck files for import.

### User Interface Files

#### ui.py
PyQt5-based desktop application providing a graphical user interface.

**Components:**
- Tabbed interface with input, settings, and processing sections
- File browser for PDF selection
- API configuration panels
- Real-time progress tracking
- Flashcard preview
- Deck download functionality

**Purpose:** Provides user-friendly access to all processing features without command-line interaction.

### Utility Scripts

#### script.py
Alternative processing script with page-by-page PDF processing and incremental Anki deck building.

**Functions:**
- `load_or_create_qa_file()`: Manages persistent QA data storage
- `generate_questions()`: Local model inference for question generation
- `extract_questions_and_answers()`: Output parsing and formatting
- `add_new_cards_to_deck()`: Incremental Anki deck updates

**Purpose:** Provides an alternative processing approach with more granular control and resumable processing.

### Configuration Files

#### requirements.txt
Python package dependencies for the project.

#### requirements_ui.txt
Additional dependencies specifically for the desktop UI.

### Data Files

#### data.json / data_ui.json
Processing state and chunk data storage.

#### output.json / output_ui.json
Final flashcard data in JSON format.

#### output.apkg / output_ui.apkg
Anki deck files ready for import.

## API Configuration

### Groq API (Recommended)
- Models: llama-3.3-70b-versatile, llama-3.1-8b-instant, mixtral-8x7b-32768
- Free tier available
- Fast response times
- Good for production use

### Google Gemini API
- Models: gemini-1.5-flash, gemini-1.5-pro, gemini-2.0-flash (or any other models you have access to)
- Pay-per-use pricing
- Advanced capabilities
- Higher quality outputs

### Local Models
- TinyLlama: Fast, lightweight (1.1B parameters)
- Phi-3: Better quality, moderate speed (3.8B parameters)
- No API costs
- Requires GPU for best performance

## Processing Parameters

### Chunk Sensitivity
- Range: 5-50 (default: 15)
- Lower values: Smaller, more focused chunks
- Higher values: Larger, broader chunks
- Affects AI model context and output quality

### Chunk Size
- Controls semantic grouping of sentences
- Smaller chunks: More precise flashcards
- Larger chunks: Better context preservation

## Output Formats

### JSON Output (output.json)
```json
{
  "pairs": [
    {
      "front": "Question text",
      "back": "Answer text"
    }
  ]
}
```

### Anki Deck (.apkg)
- Standard Anki import format
- Contains all flashcards with Q&A structure
- Ready for import into Anki desktop/mobile

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Verify API key is correct and active
   - Check account has sufficient credits
   - Ensure correct API provider selected

2. **Model Loading Errors**
   - For local models: Ensure sufficient RAM/VRAM
   - For API models: Check internet connection
   - Verify model names are correct

3. **PDF Processing Errors**
   - Ensure PDF is text-based (not image-only)
   - Check PDF is not password-protected
   - Verify file path is correct

4. **Memory Issues**
   - Reduce chunk sensitivity for large PDFs
   - Use API mode instead of local models
   - Process smaller PDF sections

### Performance Optimization

- Use Groq API for fastest processing
- Adjust chunk sensitivity based on content type
- Process in smaller batches for large documents
- Use local models only if you have sufficient hardware

## Dependencies

### Core Dependencies
- sentence-transformers: Text embedding generation
- transformers: HuggingFace model interface
- torch: PyTorch machine learning framework
- pdfplumber: PDF text extraction
- genanki: Anki deck creation
- groq: Groq API client
- google-genai: Google Gemini API client

### UI Dependencies
- gradio: Web UI framework (alternative)

## License

See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Stuff to add if you are contributing:

1. Progress bar
2. More models support
3. A way to preview the flashcards in the app itself.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review existing issues on GitHub
3. Create a new issue with detailed information
4. Include error messages and system information
