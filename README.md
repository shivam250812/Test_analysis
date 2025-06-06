# Test_analysis
# 🎓 Student Performance Feedback System

This project is an AI-powered Student Performance Feedback System designed to analyze test data from a JSON file, process performance metrics, and generate a styled PDF report with insightful, encouraging, and constructive feedback. The system processes subject-wise and chapter-wise performance, identifies strengths and weaknesses, and provides actionable suggestions to help students improve.

---

## 🎯 Objective

The goal is to build a system that:

-Analyzes test data provided in JSON format.
-Generates insightful, encouraging, and personalized feedback for students.
-Leverages modern LLM APIs (e.g., OpenAI, Claude, Gemini) for feedback generation.
-Produces a styled PDF report with performance breakdowns, tables, and actionable suggestions.
-Demonstrates skills in prompt engineering, data interpretation, and automation.

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
- Use gemini-pro API for feedback

---

## 🧠 Prompt Logic

A structured prompt to an LLM would include:

**Input Context:**
- Overall stats (e.g., 133/300 marks, 76.6% accuracy)
- Subject-wise accuracy and time
- Chapter-wise and concept-level breakdowns
- Time vs. accuracy analysis

---

## 🗂️ Report Structure

The generated PDF report (`feedback3_report.pdf`) includes the following structured sections:

1. **Main Title**
   - "Test Performance Report" centered, bold, navy blue

2. **Motivating Introduction**
   - Personalized message based on test performance

3. **Performance Breakdown**
   - **Subject-wise Table:** Marks, accuracy, time per subject  
   - **Difficulty Table:** Easy, medium, tough performance comparison  

4. **Time vs. Accuracy Insights**
   - Bullet points highlighting trends and anomalies in time management  

5. **Chapter-wise Concept Analysis**
   - Conceptual strengths (e.g., 3/3 correct) and weaknesses (e.g., 0/1 incorrect)  

6. **Actionable Suggestions**
   - Three well-highlighted and tailored recommendations
   - Presented in light yellow tables with blue borders

7. **Visual Styling**
   - Navy blue titles, Times-Roman for body, yellow highlights for key advice

---

## 📘 PDF Report

📄 **Download Report:** [https://drive.google.com/file/d/1MpGxVjs0D6h1p3m_GH8PWgbN62mVCpgJ/view?usp=drive_link]  
📌 File Name: `feedback3_report.pdf`  
✅ Includes:
- Subject & difficulty tables  
- Accuracy vs. time insights  
- Concept breakdown  
- Highlighted suggestions section  

---


