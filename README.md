# 🤖 AI Code Intelligence System

An AI-powered code review application built with Streamlit that analyzes source code and GitHub repositories using a local Large Language Model (Qwen2.5-Coder via Ollama).

## Features

- 📄 Upload and analyze source code files
- 🔗 Analyze public GitHub repositories
- 🐞 Detect potential bugs
- 💡 Suggest code improvements
- 📚 Recommend best practices
- 🛠 Generate improved code
- 📊 Repository quality score
- 📄 Download PDF analysis reports
- 🌐 Multi-language support

## Supported Languages

- Python
- Java
- C
- C++
- SQL

## Technologies Used

- Python
- Streamlit
- Ollama
- Qwen2.5-Coder
- GitPython
- ReportLab
- Requests

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd AI_Code_Review_Assistant
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start Ollama and pull the model:

```bash
ollama pull qwen2.5-coder:7b
```

Run the application:

```bash
streamlit run app.py
```

## Project Structure

```
AI_Code_Review_Assistant/
│── app.py
│── requirements.txt
│── README.md
│── .gitignore
```

## Future Improvements

- Support more programming languages
- Export reports in multiple formats
- Security vulnerability detection
- Repository-wide insights dashboard
- Code complexity visualization

## Author

Tripti