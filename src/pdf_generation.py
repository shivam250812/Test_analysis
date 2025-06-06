import json
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os
import tempfile
import time
import re
import unicodedata 

import matplotlib.pyplot as plt

# --- Load JSON Data ---
def load_json_data(file_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"JSON file not found: {file_path}")
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return None

# --- Process Data ---
def process_data(json_data):
    if not json_data or not isinstance(json_data, list):
        print("Invalid JSON data")
        return None

    processed_data = {
        "overall_summary": {},
        "subject_summary": defaultdict(dict),
        "chapter_details": defaultdict(dict)
    }
    chapter_stats = defaultdict(lambda: {
        "questions_total": 0,
        "answered": 0,
        "correct": 0,
        "incorrect": 0,
        "marked_review": 0,
        "not_answered": 0,
        "total_time_seconds": 0,
        "difficulty_counts": defaultdict(int),
        "difficulty_stats": defaultdict(lambda: {"correct": 0, "incorrect": 0, "unattempted": 0})
    })

    concept_stats = defaultdict(lambda: defaultdict(lambda: {"total": 0, "correct": 0, "incorrect": 0}))

    section_subject_map = {
        "Physics Single Correct": "Physics",
        "Physics Numerical": "Physics",
        "Chemistry Single Correct": "Chemistry",
        "Chemistry Numerical": "Chemistry",
        "Mathematics Single Correct": "Mathematics",
        "Mathematics Numerical": "Mathematics"
    }

    subject_map = {
        "607018ee404ae53194e73d92": "Physics",
        "607018ee404ae53194e73d90": "Chemistry",
        "607018ee404ae53194e73d91": "Mathematics"
    }

    debug_counts = defaultdict(list)

    data = json_data[0]
    processed_data["overall_summary"] = {
        "total_marks_scored": data.get("totalMarkScored", 0),
        "total_marks_possible": data.get("totalMarks", 300),
        "total_time_taken_seconds": data.get("totalTimeTaken", 0),
        "total_questions_in_test": data.get("test", {}).get("totalQuestions", 0),
        "final_attempted": data.get("totalAttempted", 0),
        "final_correct": data.get("totalCorrect", 0),
        "overall_accuracy_percent": data.get("accuracy", 0),
        "time_taken_minutes": data.get("totalTimeTaken", 0) / 60.0
    }

    for subject in data.get("subjects", []):
        subject_id = subject.get("subjectId", {}).get("$oid", "")
        subject_name = subject_map.get(subject_id, "Unknown")
        processed_data["subject_summary"][subject_name] = {
            "marks_scored": subject.get("totalMarkScored", 0),
            "total_marks_possible": subject.get("totalMarks", 100),
            "time_seconds": subject.get("totalTimeTaken", 0),
            "attempted": subject.get("totalAttempted", 0),
            "correct": subject.get("totalCorrect", 0),
            "incorrect": subject.get("totalAttempted", 0) - subject.get("totalCorrect", 0),
            "accuracy_percent": subject.get("accuracy", 0),
            "avg_time_per_attempted_q_seconds": (subject.get("totalTimeTaken", 0) / subject.get("totalAttempted", 0)) if subject.get("totalAttempted", 0) > 0 else 0
        }

    for section in data.get("sections", []):
        section_title = section.get("sectionId", {}).get("title", "")
        subject = section_subject_map.get(section_title, "Unknown")

        for question in section.get("questions", []):
            chapter = question.get("questionId", {}).get("chapters", [{}])[0].get("title", "Unknown")
            status = question.get("status", "notAnswered")
            time_taken = question.get("timeTaken", 0)
            level = question.get("questionId", {}).get("level", "unknown")
            concepts = [concept.get("title", "Unknown") for concept in question.get("questionId", {}).get("concepts", [])]

            if (subject == "Physics" and chapter not in ["Electrostatics", "Capacitance"]) or \
               (subject == "Chemistry" and chapter not in ["Solutions", "Electrochemistry"]) or \
               (subject == "Mathematics" and chapter not in ["Functions", "Sets and Relations"]):
                continue

            chapter_stats[(subject, chapter)]["questions_total"] += 1
            chapter_stats[(subject, chapter)]["total_time_seconds"] += time_taken
            chapter_stats[(subject, chapter)]["difficulty_counts"][level] += 1

            debug_info = {
                "status": status,
                "time_taken": time_taken,
                "level": level,
                "concepts": concepts
            }

            if status == "answered":
                chapter_stats[(subject, chapter)]["answered"] += 1
                is_correct = False
                marked_options = question.get("markedOptions", [])
                input_value = question.get("inputValue", {})

                if marked_options:
                    is_correct = any(opt.get("isCorrect", False) for opt in marked_options)
                elif input_value.get("value") is not None:
                    is_correct = input_value.get("isCorrect", False)

                if is_correct:
                    chapter_stats[(subject, chapter)]["correct"] += 1
                    chapter_stats[(subject, chapter)]["difficulty_stats"][level]["correct"] += 1
                    debug_info["correct"] = True
                else:
                    chapter_stats[(subject, chapter)]["incorrect"] += 1
                    chapter_stats[(subject, chapter)]["difficulty_stats"][level]["incorrect"] += 1
                    debug_info["correct"] = False

                for concept in concepts:
                    concept_stats[(subject, chapter)][concept]["total"] += 1
                    if is_correct:
                        concept_stats[(subject, chapter)][concept]["correct"] += 1
                    else:
                        concept_stats[(subject, chapter)][concept]["incorrect"] += 1
            elif status == "markedReview":
                chapter_stats[(subject, chapter)]["marked_review"] += 1
                chapter_stats[(subject, chapter)]["difficulty_stats"][level]["unattempted"] += 1
            elif status == "notAnswered":
                chapter_stats[(subject, chapter)]["not_answered"] += 1
                chapter_stats[(subject, chapter)]["difficulty_stats"][level]["unattempted"] += 1

            debug_counts[(subject, chapter)].append(debug_info)

    for (subject, chapter), stats in chapter_stats.items():
        stats["accuracy_on_answered_percent"] = (stats["correct"] / stats["answered"] * 100) if stats["answered"] > 0 else 0.0
        stats["avg_time_per_answered_q_seconds"] = (stats["total_time_seconds"] / stats["answered"]) if stats["answered"] > 0 else 0.0
        processed_data["chapter_details"][subject][chapter] = stats

    subject_questions = defaultdict(int)
    for subject in processed_data["chapter_details"]:
        subject_questions[subject] = sum(chapter["questions_total"] for chapter in processed_data["chapter_details"][subject].values())
        processed_data["subject_summary"][subject]["total_questions"] = subject_questions[subject]

    processed_data["overall_summary"]["total_questions_calculated"] = sum(subject_questions.values())

    return processed_data

# --- Function to Extract Data for Charts ---
def extract_chart_data(processed_data):
    chart_data = {}
    difficulty_levels = ['easy', 'medium', 'tough']

    for subject in processed_data["chapter_details"]:
        chart_data[subject] = {
            'Easy': {'correct': 0, 'incorrect': 0, 'unattempted': 0, 'total': 0},
            'Medium': {'correct': 0, 'incorrect': 0, 'unattempted': 0, 'total': 0},
            'Tough': {'correct': 0, 'incorrect': 0, 'unattempted': 0, 'total': 0}
        }
        for chapter, stats in processed_data["chapter_details"][subject].items():
            for level in difficulty_levels:
                level_key = level.capitalize()
                chart_data[subject][level_key]['correct'] += stats["difficulty_stats"][level]["correct"]
                chart_data[subject][level_key]['incorrect'] += stats["difficulty_stats"][level]["incorrect"]
                chart_data[subject][level_key]['unattempted'] += stats["difficulty_stats"][level]["unattempted"]
                chart_data[subject][level_key]['total'] += stats["difficulty_counts"][level]

    return chart_data

# --- Function to Plot Bar Chart for a Subject and Save as Image ---
def plot_subject_chart(subject, subject_data, temp_image_path):
    difficulty_levels = ['Easy', 'Medium', 'Tough']
    correct = [subject_data[level]['correct'] for level in difficulty_levels]
    incorrect = [subject_data[level]['incorrect'] for level in difficulty_levels]
    unattempted = [subject_data[level]['unattempted'] for level in difficulty_levels]
    totals = [subject_data[level]['total'] for level in difficulty_levels]

    colors = {'Correct': '#36A2EB', 'Incorrect': '#FF6384', 'Unattempted': '#FFCE56'}

    x = np.arange(len(difficulty_levels))
    width = 0.25

    fig, ax = plt.subplots(figsize=(5, 3))  # Smaller size for grid layout

    bar1 = ax.bar(x - width, correct, width, label='Correct', color=colors['Correct'])
    bar2 = ax.bar(x, incorrect, width, label='Incorrect', color=colors['Incorrect'])
    bar3 = ax.bar(x + width, unattempted, width, label='Unattempted', color=colors['Unattempted'])

    for bar in [bar1, bar2, bar3]:
        for b in bar:
            height = b.get_height()
            ax.text(b.get_x() + b.get_width() / 2., height, f'{int(height)}',
                    ha='center', va='bottom', color='black', fontsize=8)

    ax.set_xlabel('Difficulty', fontsize=8)
    ax.set_ylabel('Questions', fontsize=8)
    ax.set_title(f'{subject} Performance', fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(difficulty_levels, fontsize=8)
    ax.legend(fontsize=6)

    ax.set_ylim(0, max(totals) + 2)

    try:
        plt.tight_layout()
        plt.savefig(temp_image_path, format='png', dpi=300, bbox_inches='tight')
        plt.close(fig)
        time.sleep(0.2)
        if not os.path.exists(temp_image_path):
            raise FileNotFoundError(f"Failed to save image at {temp_image_path}")
        if not os.access(temp_image_path, os.R_OK):
            raise PermissionError(f"Cannot read image at {temp_image_path}")
        print(f"Chart saved successfully for {subject} at {temp_image_path}")
    except Exception as e:
        print(f"Error saving chart image for {subject}: {e}")
        plt.close(fig)
        return None, None

    description = f"Total questions - Easy: {totals[0]}, Medium: {totals[1]}, Tough: {totals[2]}"
    return temp_image_path, description

# --- Function to Clean Document Content ---
def clean_document_content(content):
    cleaned_content = content.replace('*', '')
    lines = cleaned_content.split('\n')
    output_lines = []
    in_table = False
    table_data = []
    table_count = 0

    for line in lines:
        line = line.strip()
        if not line:
            if in_table and table_data:
                table_data = [row for row in table_data if not all(cell.strip().startswith('-') and len(cell.strip()) > 1 for cell in row)]
                if table_data:
                    table_count += 1
                    output_lines.append({'type': 'table', 'data': table_data, 'table_type': 'subject' if table_count == 1 else 'difficulty'})
                table_data = []
                in_table = False
            continue
        if line.startswith('|'):
            in_table = True
            table_data.append([cell.strip() for cell in line.split('|')[1:-1]])
            continue
        if in_table and not line.startswith('|'):
            in_table = False
            if table_data:
                table_data = [row for row in table_data if not all(cell.strip().startswith('-') and len(cell.strip()) > 1 for cell in row)]
                if table_data:
                    table_count += 1
                    output_lines.append({'type': 'table', 'data': table_data, 'table_type': 'subject' if table_count == 1 else 'difficulty'})
                table_data = []
            output_lines.append({'type': 'text', 'content': line})
        else:
            output_lines.append({'type': 'text', 'content': line})

    if table_data:
        table_data = [row for row in table_data if not all(cell.strip().startswith('-') and len(cell.strip()) > 1 for cell in row)]
        if table_data:
            table_count += 1
            output_lines.append({'type': 'table', 'data': table_data, 'table_type': 'difficulty'})

    return output_lines

def create_styled_pdf(cleaned_content, chart_data, output_filename='feedback_report.pdf'):
    doc = SimpleDocTemplate(output_filename, pagesize=letter, rightMargin=0.75*inch, leftMargin=0.75*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    
    main_title_style = ParagraphStyle(
        name='MainTitleStyle',
        fontSize=18,
        leading=22,
        spaceAfter=10,
        fontName='Helvetica-Bold',
        textColor=colors.navy,
        alignment=1  # Center
    )
    
    section_title_style = ParagraphStyle(
        name='SectionTitleStyle',
        fontSize=14,
        leading=16,
        spaceAfter=6,
        fontName='Helvetica-Bold',
        textColor=colors.darkblue,
        alignment=0  # Left
    )
    
    subheading_style = ParagraphStyle(
        name='SubheadingStyle',
        fontSize=10,
        leading=12,
        spaceAfter=4,
        fontName='Helvetica-Oblique',
        textColor=colors.darkslategray
    )
    
    body_style = ParagraphStyle(
        name='BodyStyle',
        fontSize=8,
        leading=10,
        spaceAfter=3,
        fontName='Times-Roman',
        textColor=colors.black
    )
    
    list_style = ParagraphStyle(
        name='ListStyle',
        fontSize=8,
        leading=10,
        spaceAfter=3,
        fontName='Times-Roman',
        textColor=colors.black,
        leftIndent=16,
        bulletFontName='Times-Roman',
        bulletFontSize=8,
        bulletIndent=8
    )
    
    story = []
    temp_files = []  # Track temporary files for cleanup
    current_section = None
    in_performance_breakdown = False
    table_count = 0  # Track number of tables in Performance Breakdown
    page_width = letter[0] - 1.5*inch  # Available width after margins
    charts_added = False  # Flag to prevent duplicate charts

    # Add main title
    story.append(Paragraph("Test Performance Report", main_title_style))
    story.append(Spacer(1, 0.08*inch))

    def add_chart(subject, image_path, description):
        nonlocal story, temp_files
        try:
            from PIL import Image as PILImage
            with PILImage.open(image_path) as img:
                img_width, img_height = img.size
                aspect_ratio = img_height / img_width
                target_width = min(page_width, 5.5*inch)
                target_height = target_width * aspect_ratio
                if target_height > 3.5*inch:
                    target_height = 3.5*inch
                    target_width = target_height / aspect_ratio
            story.append(Spacer(1, 0.05*inch))
            story.append(Paragraph(f"{subject} Performance Chart", subheading_style))
            img = Image(image_path, width=target_width, height=target_height)
            img.hAlign = 'CENTER'
            story.append(img)
            story.append(Paragraph(description, body_style))
            story.append(Spacer(1, 0.05*inch))
            temp_files.append(image_path)
            print(f"Added chart for {subject} to PDF")
        except Exception as e:
            print(f"Error embedding image for {subject}: {e}")

    for item in cleaned_content:
        if item['type'] == 'text':
            content = item['content']
            if content in ['Overall Performance', 'Motivating Introduction', 'Performance Breakdown', 
                          'Time vs. Accuracy Insights', 'Chapter-wise Concept Analysis', 'Actionable Suggestions']:
                if in_performance_breakdown and table_count >= 2 and not charts_added:
                    # Add Physics and Chemistry charts on page 2
                    story.append(PageBreak())
                    for subject in ['Physics', 'Chemistry']:
                        if subject in chart_data:
                            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                            temp_image_path = temp_file.name
                            temp_file.close()
                            print(f"Generating chart for {subject} at {temp_image_path}")
                            image_path, description = plot_subject_chart(subject, chart_data[subject], temp_image_path)
                            if image_path and os.path.exists(image_path):
                                add_chart(subject, image_path, description)
                    # Add Mathematics chart on page 3
                    story.append(PageBreak())
                    if chart_data.get('Mathematics'):
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                        temp_image_path = temp_file.name
                        temp_file.close()
                        print(f"Generating chart for Mathematics at {temp_image_path}")
                        image_path, description = plot_subject_chart('Mathematics', chart_data['Mathematics'], temp_image_path)
                        if image_path and os.path.exists(image_path):
                            add_chart('Mathematics', image_path, description)
                    charts_added = True
                story.append(Paragraph(content, section_title_style))
                current_section = content
                in_performance_breakdown = (content == 'Performance Breakdown')
                table_count = 0  # Reset table count for new section
                continue
            if content in ['Physics:', 'Chemistry:', 'Mathematics:']:
                story.append(Paragraph(content[:-1], subheading_style))
                continue
            if content.startswith('Electrostatics:') or content.startswith('Capacitance:') or \
               content.startswith('Solutions:') or content.startswith('Electrochemistry:') or \
               content.startswith('Functions:') or content.startswith('Sets and Relations:'):
                story.append(Paragraph(f"• {content}", list_style))
                continue
            if current_section == 'Time vs. Accuracy Insights':
                try:
                    cleaned_content = re.sub(r'^\s*[-•]|\$\s*\\cdot\s*\d*\s*', '', content).strip()
                    cleaned_content = re.sub(r'\s+', ' ', cleaned_content.replace('\n', ' ')).strip()
                    sentences = re.split(r'(?<!\d)\.(?!\d)', cleaned_content)
                    sentences = [s.strip() for s in sentences if s.strip()]
                    for sentence in sentences:
                        if sentence and sentence != '.':
                            story.append(Paragraph(f"• {sentence}.", list_style))
                except re.error as e:
                    print(f"Regex error in bullet point processing: {e}")
                    cleaned_fallback = re.sub(r'\s+', ' ', content.replace('\n', ' ')).strip()
                    sentences = re.split(r'(?<!\d)\.(?!\d)', cleaned_fallback)
                    sentences = [s.strip() for s in sentences if s.strip()]
                    for sentence in sentences:
                        if sentence and sentence != '.':
                            story.append(Paragraph(f"• {sentence}.", list_style))
                continue
            if current_section == 'Actionable Suggestions':
                # Enhanced cleaning
                cleaned_content = unicodedata.normalize('NFKD', content)  # Normalize Unicode
                cleaned_content = re.sub(r'[^\x20-\x7E]', '', cleaned_content)  # Keep only printable ASCII characters
                cleaned_content = re.sub(r'^\s*[-•]|\$\s*\\cdot\s*\d*\s*', '', cleaned_content).strip()
                sections = re.split(r'\s*\d+\s*(?=\n)', cleaned_content)
                sections = [s.strip() for s in sections if s.strip()]
                section_number = 1
                for section in sections:
                    section_cleaned = re.sub(r'\s+', ' ', section.replace('\n', ' ')).strip()
                    if section_cleaned:
                        sentences = re.split(r'(?<!\d)\.(?!\d)', section_cleaned)
                        sentences = [s.strip() for s in sentences if s.strip()]
                        if sentences:
                            paragraph_text = '. '.join(sentences)
                            if not paragraph_text.endswith('.'):
                                paragraph_text += '.'
                            print(f"Actionable Suggestion {section_number}: {paragraph_text}")  # Debug logging
                            story.append(Paragraph(paragraph_text, body_style))
                            story.append(Spacer(1, 0.03*inch))
                    section_number += 1
                continue
            story.append(Paragraph(content.replace('%', '%'), body_style))
            story.append(Spacer(1, 0.03*inch))
        
        elif item['type'] == 'table' and in_performance_breakdown:
            table_title = "Subject Performance" if item['table_type'] == 'subject' else "Difficulty Performance"
            story.append(Paragraph(table_title, subheading_style))
            col_count = len(item['data'][0])
            col_width = (page_width - 0.3*inch) / col_count
            if item['table_type'] == 'difficulty':
                item['data'][0] = [col.replace('Avg Time (seconds)', 'Avg Time(s)') for col in item['data'][0]]
            table = Table(item['data'], colWidths=[col_width] * col_count)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(table)
            story.append(Spacer(1, 0.05*inch))
            table_count += 1

    # Build the PDF
    try:
        doc.build(story)
        print(f"PDF generated: {output_filename}")
    except Exception as e:
        print(f"Error building PDF: {e}")
    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    print(f"Removed temporary file {temp_file}")
            except Exception as e:
                print(f"Error removing temporary file {temp_file}: {e}")

# --- Main Execution ---
file_path = "/content/sample_submission_analysis_1.json"
text_file_path = "/content/feedback_output.txt"
pdf_path = "feedback2_report.pdf"

if not os.path.exists(text_file_path):
    print(f"Text file not found: {text_file_path}")
    exit(1)

json_data = load_json_data(file_path)
if json_data:
    processed_data = process_data(json_data)
    if processed_data:
        chart_data = extract_chart_data(processed_data)
        try:
            with open(text_file_path, "r") as file:
                document_content = file.read()
            print(f"Successfully loaded text file: {text_file_path}")
            cleaned_content = clean_document_content(document_content)
            create_styled_pdf(cleaned_content, chart_data, pdf_path)
        except Exception as e:
            print(f"Error processing text file: {e}")
else:
    print("Failed to load JSON file")