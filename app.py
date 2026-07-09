import streamlit as st
import requests
import json
import os
import time
from git import Repo
import shutil
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(
    page_title="AI Code Intelligence System",
    layout="wide"
)

st.title("🤖 AI Code Intelligence System")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:7b"


# ---------------- LANGUAGE DETECTION ---------------- #
def detect_language(filename):
    ext = os.path.splitext(filename)[1].lower()
    mapping = {
        ".py": "Python",
        ".java": "Java",
        ".cpp": "C++",
        ".cc": "C++",
        ".cxx": "C++",
        ".c": "C",
        ".sql": "SQL"
    }
    return mapping.get(ext, "Unknown")


# ---------------- AI ANALYSIS ---------------- #
def call_ai(code, language):
    prompt = f"""
You are an expert software engineer and code reviewer.

Analyze the following {language} code.

Return ONLY valid JSON.

{{
  "summary": "Explain what the code does",
  "bugs": [],
  "improvements": [],
  "best_practices": [],
  "severity": "Low",
  "complexity": "Low",
  "score": 0,
  "fixed_code": ""
}}

Rules:
- Do NOT use placeholder text.
- Base all answers on the actual code.
- bugs must be a list.
- improvements must be a list.
- best_practices must be a list.
- severity must be Low, Medium, or High.
- complexity must be Low, Medium, or High.
- score must be between 0 and 10.
- fixed_code must contain an improved version of the code.

Code:
{code[:3000]}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "format": "json",
                "stream": False
            },
            timeout=180
        )
        response.raise_for_status()

        raw = response.json().get("response", "{}")

        with st.expander("🔍 Raw AI Output"):
            st.code(raw)

        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            return {
                "summary": raw,
                "bugs": [],
                "improvements": [],
                "best_practices": [],
                "severity": "Unknown",
                "complexity": "Unknown",
                "score": 5,
                "fixed_code": ""
            }

        return {
            "summary": result.get("summary", "No summary available"),
            "bugs": result.get("bugs", []),
            "improvements": result.get("improvements", []),
            "best_practices": result.get("best_practices", []),
            "severity": result.get("severity", "Unknown"),
            "complexity": result.get("complexity", "Unknown"),
            "score": result.get("score", 5),
            "fixed_code": result.get("fixed_code", "")
        }

    except Exception as e:
        return {
            "summary": f"Analysis failed: {str(e)}",
            "bugs": [],
            "improvements": [],
            "best_practices": [],
            "severity": "Unknown",
            "complexity": "Unknown",
            "score": 5,
            "fixed_code": ""
        }


# ---------------- PDF GENERATION ---------------- #
def create_pdf(result, language):
    pdf_file = "analysis_report.pdf"
    doc = SimpleDocTemplate(pdf_file)
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("AI Code Analysis Report", styles["Title"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph(f"<b>Language:</b> {language}", styles["Normal"]))
    content.append(Paragraph(f"<b>Score:</b> {result.get('score', 5)}/10", styles["Normal"]))
    content.append(Paragraph(f"<b>Severity:</b> {result.get('severity', 'Unknown')}", styles["Normal"]))
    content.append(Paragraph(f"<b>Complexity:</b> {result.get('complexity', 'Unknown')}", styles["Normal"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph("<b>Summary</b>", styles["Heading2"]))
    content.append(Paragraph(result.get("summary", ""), styles["Normal"]))
    content.append(Spacer(1, 10))

    content.append(Paragraph("<b>Bugs</b>", styles["Heading2"]))
    for bug in result.get("bugs", []):
        content.append(Paragraph(f"• {bug}", styles["Normal"]))

    content.append(Paragraph("<b>Improvements</b>", styles["Heading2"]))
    for imp in result.get("improvements", []):
        content.append(Paragraph(f"• {imp}", styles["Normal"]))

    content.append(Paragraph("<b>Best Practices</b>", styles["Heading2"]))
    for bp in result.get("best_practices", []):
        content.append(Paragraph(f"• {bp}", styles["Normal"]))

    doc.build(content)
    return pdf_file


# ---------------- RESULT DISPLAY ---------------- #
def show_result(result, language):
    try:
        score = float(result.get("score", 5))
    except:
        score = 5
    score = max(0, min(score, 10))

    severity = str(result.get("severity", "Unknown")).strip()
    complexity = str(result.get("complexity", "Unknown")).strip()

    if severity not in ["Low", "Medium", "High"]:
        severity = "Unknown"
    if complexity not in ["Low", "Medium", "High"]:
        complexity = "Unknown"

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Score", f"{score}/10")
    col2.metric("Severity", severity)
    col3.metric("Complexity", complexity)
    col4.metric("Language", language)

    st.divider()
    st.subheader("🧠 Summary")
    st.write(result.get("summary", ""))

    st.subheader("🐞 Bugs")
    bugs = result.get("bugs", [])
    if bugs:
        for bug in bugs:
            st.error(bug)
    else:
        st.success("No major bugs detected")

    st.subheader("💡 Improvements")
    improvements = result.get("improvements", [])
    if improvements:
        for imp in improvements:
            st.info(imp)
    else:
        st.success("No improvements suggested")

    st.subheader("📚 Best Practices")
    best_practices = result.get("best_practices", [])
    if best_practices:
        for bp in best_practices:
            st.success(bp)
    else:
        st.info("No best-practice recommendations.")

    st.subheader("🛠 Suggested Fixed Code")
    fixed_code = result.get("fixed_code", "")
    if fixed_code:
        lang_map = {
            "Python": "python",
            "Java": "java",
            "C++": "cpp",
            "C": "c",
            "SQL": "sql"
        }
        st.code(
            fixed_code,
            language=lang_map.get(language, "text")
        )
    else:
        st.info("No fixed code generated.")


# ---------------- TABS ---------------- #
tab1, tab2 = st.tabs(["📄 Upload Code", "🔗 GitHub Repository"])


# ====================================================
# FILE ANALYZER
# ====================================================
with tab1:
    uploaded_file = st.file_uploader(
        "Upload code file",
        type=["py", "java", "cpp", "c", "sql"]
    )

    if uploaded_file:
        code = uploaded_file.read().decode("utf-8", errors="ignore")
        language = detect_language(uploaded_file.name)

        st.subheader("📄 Code Preview")
        st.code(code)
        st.info(f"Detected Language: {language}")

        if st.button("Analyze Code"):
            with st.spinner("Analyzing..."):
                result = call_ai(code, language)
            show_result(result, language)

            # PDF download button
            pdf_path = create_pdf(result, language)
            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_file,
                    file_name="AI_Code_Report.pdf",
                    mime="application/pdf"
                )


# ====================================================
# GITHUB ANALYZER
# ====================================================
with tab2:
    repo_url = st.text_input("Enter GitHub Repository URL")

    if st.button("Analyze Repository") and repo_url:
        repo_path = f"repo_{int(time.time())}"

        try:
            with st.spinner("Cloning repository..."):
                Repo.clone_from(repo_url, repo_path)
            st.success("Repository cloned successfully")
        except Exception as e:
            st.error(f"Clone failed: {e}")
            st.stop()

        files = []
        for root, _, file_list in os.walk(repo_path):
            for file in file_list:
                if file.endswith((".py", ".java", ".cpp", ".c", ".sql")):
                    files.append(os.path.join(root, file))

        if not files:
            st.warning("No supported code files found")
            st.stop()

        limit = min(8, len(files))
        st.info(f"Analyzing {limit} file(s) for speed.")
        scores = []
        progress = st.progress(0)
        for idx, file in enumerate(files[:limit]):
            progress.progress((idx + 1) / limit)

            try:
                with open(file, "r", encoding="utf-8", errors="ignore") as f:
                    code = f.read()

                language = detect_language(file)
                result = call_ai(code, language)

                st.subheader(f"📄 {os.path.basename(file)}")
                show_result(result, language)

                try:
                    scores.append(float(result.get("score", 5)))
                except Exception:
                    scores.append(5)

            except Exception as e:
                st.error(f"Error reading {file}: {e}")

        st.divider()

        avg_score = sum(scores) / len(scores) if scores else 0

        st.subheader("📊 Repository Score")

        if avg_score >= 8:
            st.success(f"Excellent Project 🚀 ({avg_score:.1f}/10)")
        elif avg_score >= 5:
            st.warning(f"Moderate Project ⚠️ ({avg_score:.1f}/10)")
        else:
            st.error(f"Needs Improvement ❌ ({avg_score:.1f}/10)")

        st.info(f"Analyzed {len(scores)} file(s) successfully.")

        if os.path.exists(repo_path):
            shutil.rmtree(repo_path, ignore_errors=True)