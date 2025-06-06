# Test_analysis
# 🎓 Student Performance Feedback System

An AI-powered system to analyze student test data, generate insightful feedback, and produce a styled PDF report with performance breakdowns and actionable suggestions.

---

## 📑 Table of Contents

- [Objective](#objective)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [API(s) Used](#apis-used)
- [Prompt Logic](#prompt-logic)
- [Report Structure](#report-structure)
- [Installation](#installation)
- [Usage](#usage)
- [PDF Report](#pdf-report)
- [Code Quality](#code-quality)
- [Bonus Features](#bonus-features)
- [Submission](#submission)
- [Notes](#notes)

---

## 🎯 Objective

The goal is to build a system that:
- Analyzes test data provided in JSON format.
- Generates insightful, encouraging, and personalized feedback for students.
- Leverages modern LLM APIs (e.g., OpenAI, Claude, Gemini) for feedback generation.
- Produces a styled PDF report with performance breakdowns, tables, and actionable suggestions.
- Demonstrates skills in prompt engineering, data interpretation, and automation.

---

## 🛠 Tech Stack

- **Language:** Python  
- **Libraries:** 
  - `reportlab` – PDF generation and styling  
  - `json` – Test data parsing  
  - `collections.defaultdict` – Efficient aggregation  
  - `re`, `unicodedata` – Text preprocessing  
  - `matplotlib`, `seaborn`, `pandas` – Charts & data analysis  
  - `google-generativeai`, `python-dotenv` – For LLM feedback integration  

- **Environment:** Jupyter Notebook / Google Colab compatible

---

## ✨ Features

### 🔍 Data Processing
- Parses JSON test data: accuracy, time, difficulty, concept mapping
- Aggregates subject-wise (Physics, Chemistry, Mathematics)
- Breaks down chapter-wise and concept-level performance

### 💬 AI-Generated Feedback
- Personalized motivational intro
- Subject & difficulty performance tables
- Time vs. accuracy insights
- Chapter-wise concept strengths & weaknesses
- 3 actionable recommendations tailored to performance

### 📄 PDF Generation
- Styled PDF (e.g., `feedback3_report.pdf`) with:
  - Clean layout
  - Highlighted insights
  - Tables and bullet lists
  - Color-coded suggestions

---

## 🔌 API(s) Used

While the project includes dependencies for Google Generative AI, current integration assumes:
- **`feedback_output.txt`** contains LLM-generated feedback.
- Direct API call functionality (via Gemini or similar) can be added for full automation.

---

## 🧠 Prompt Logic

A structured prompt to an LLM would include:

**Input Context:**
- Overall stats (e.g., 133/300 marks, 76.6% accuracy)
- Subject-wise accuracy and time
- Chapter-wise and concept-level breakdowns
- Time vs. accuracy analysis

**Prompt Example:**
```text
"Congratulations on completing your test with 76.6% accuracy! You performed strongly in Chemistry with 80% accuracy. Let’s review subject strengths and areas of improvement."
