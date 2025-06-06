import json
from collections import defaultdict

# --- Load JSON Data ---
def load_json_data(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return None

# --- Process Data ---
def process_data(json_data):
    if not json_data or not isinstance(json_data, list):
        print("Invalid JSON data")
        return None, None, None

    # Initialize data structure
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
        "difficulty_counts": defaultdict(int)
    })

    # Initialize concept stats per chapter
    concept_stats = defaultdict(lambda: defaultdict(lambda: {"total": 0, "correct": 0, "incorrect": 0}))

    # Map sections to subjects
    section_subject_map = {
        "Physics Single Correct": "Physics",
        "Physics Numerical": "Physics",
        "Chemistry Single Correct": "Chemistry",
        "Chemistry Numerical": "Chemistry",
        "Mathematics Single Correct": "Mathematics",
        "Mathematics Numerical": "Mathematics"
    }

    # Subject ID to name mapping
    subject_map = {
        "607018ee404ae53194e73d92": "Physics",
        "607018ee404ae53194e73d90": "Chemistry",
        "607018ee404ae53194e73d91": "Mathematics"
    }

    # Debug: Track questions per chapter
    debug_counts = defaultdict(list)

    # Process overall summary
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

    # Process subject summary
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

    # Process sections and questions
    for section in data.get("sections", []):
        section_title = section.get("sectionId", {}).get("title", "")
        subject = section_subject_map.get(section_title, "Unknown")

        for question in section.get("questions", []):
            chapter = question.get("questionId", {}).get("chapters", [{}])[0].get("title", "Unknown")
            status = question.get("status", "notAnswered")
            time_taken = question.get("timeTaken", 0)
            level = question.get("questionId", {}).get("level", "unknown")
            concepts = [concept.get("title", "Unknown") for concept in question.get("questionId", {}).get("concepts", [])]

            # Filter for specified chapters
            if (subject == "Physics" and chapter not in ["Electrostatics", "Capacitance"]) or \
               (subject == "Chemistry" and chapter not in ["Solutions", "Electrochemistry"]) or \
               (subject == "Mathematics" and chapter not in ["Functions", "Sets and Relations"]):
                continue

            # Update chapter stats
            chapter_stats[(subject, chapter)]["questions_total"] += 1
            chapter_stats[(subject, chapter)]["total_time_seconds"] += time_taken
            chapter_stats[(subject, chapter)]["difficulty_counts"][level] += 1

            # Debug: Log question details
            debug_info = {
                "status": status,
                "time_taken": time_taken,
                "level": level,
                "concepts": concepts,
                "subject": subject  # Include subject for subject-wise difficulty analysis
            }

            if status == "answered":
                chapter_stats[(subject, chapter)]["answered"] += 1
                # Check correctness
                is_correct = False
                marked_options = question.get("markedOptions", [])
                input_value = question.get("inputValue", {})

                if marked_options:
                    is_correct = any(opt.get("isCorrect", False) for opt in marked_options)
                elif input_value.get("value") is not None:
                    is_correct = input_value.get("isCorrect", False)

                if is_correct:
                    chapter_stats[(subject, chapter)]["correct"] += 1
                    debug_info["correct"] = True
                else:
                    chapter_stats[(subject, chapter)]["incorrect"] += 1
                    debug_info["correct"] = False

                # Update concept stats
                for concept in concepts:
                    concept_stats[(subject, chapter)][concept]["total"] += 1
                    if is_correct:
                        concept_stats[(subject, chapter)][concept]["correct"] += 1
                    else:
                        concept_stats[(subject, chapter)][concept]["incorrect"] += 1
            elif status == "markedReview":
                chapter_stats[(subject, chapter)]["marked_review"] += 1
            elif status == "notAnswered":
                chapter_stats[(subject, chapter)]["not_answered"] += 1

            debug_counts[(subject, chapter)].append(debug_info)

    # Calculate chapter stats
    for (subject, chapter), stats in chapter_stats.items():
        stats["accuracy_on_answered_percent"] = (stats["correct"] / stats["answered"] * 100) if stats["answered"] > 0 else 0.0
        stats["avg_time_per_answered_q_seconds"] = (stats["total_time_seconds"] / stats["answered"]) if stats["answered"] > 0 else 0.0
        processed_data["chapter_details"][subject][chapter] = stats

    # Calculate total questions per subject
    subject_questions = defaultdict(int)
    for subject in processed_data["chapter_details"]:
        subject_questions[subject] = sum(chapter["questions_total"] for chapter in processed_data["chapter_details"][subject].values())
        processed_data["subject_summary"][subject]["total_questions"] = subject_questions[subject]

    # Calculate total questions in paper
    processed_data["overall_summary"]["total_questions_calculated"] = sum(subject_questions.values())

    return processed_data, concept_stats, debug_counts

# --- Prepare Comprehensive LLM Context ---
def prepare_comprehensive_llm_context(processed_data, concept_stats, debug_counts):
    """
    Prepare comprehensive test data including detailed difficulty-wise breakdown
    """

    context = f"""# Test Performance Analysis Report

## Overall Test Summary
- **Total Score**: {processed_data['overall_summary']['total_marks_scored']}/{processed_data['overall_summary']['total_marks_possible']} marks
- **Questions Attempted**: {processed_data['overall_summary']['final_attempted']}/{processed_data['overall_summary']['total_questions_in_test']}
- **Correct Answers**: {processed_data['overall_summary']['final_correct']}
- **Overall Accuracy**: {processed_data['overall_summary']['overall_accuracy_percent']:.1f}%
- **Time Taken**: {processed_data['overall_summary']['time_taken_minutes']:.1f} minutes

## Subject-wise Performance

"""

    # Add subject summaries
    for subject, stats in processed_data['subject_summary'].items():
        context += f"""### {subject}
- Score: {stats['marks_scored']}/{stats['total_marks_possible']} marks
- Questions: {stats['attempted']}/{stats['total_questions']} attempted
- Correct: {stats['correct']} | Incorrect: {stats['incorrect']}
- Accuracy: {stats['accuracy_percent']:.1f}%
- Avg Time/Question: {stats['avg_time_per_attempted_q_seconds']:.1f} seconds

"""

    # Calculate overall difficulty-wise analysis
    context += "## Overall Difficulty-wise Analysis\n\n"

    difficulty_stats = {
        'easy': {'total': 0, 'answered': 0, 'correct': 0, 'incorrect': 0,
                 'marked_review': 0, 'not_answered': 0, 'total_time': 0},
        'medium': {'total': 0, 'answered': 0, 'correct': 0, 'incorrect': 0,
                   'marked_review': 0, 'not_answered': 0, 'total_time': 0},
        'tough': {'total': 0, 'answered': 0, 'correct': 0, 'incorrect': 0,
                  'marked_review': 0, 'not_answered': 0, 'total_time': 0}
    }

    # Process debug_counts for overall difficulty analysis
    for (subject, chapter), questions in debug_counts.items():
        for q in questions:
            level = q['level']
            if level in difficulty_stats:
                difficulty_stats[level]['total'] += 1
                difficulty_stats[level]['total_time'] += q['time_taken']

                if q['status'] == 'answered':
                    difficulty_stats[level]['answered'] += 1
                    if q.get('correct', False):
                        difficulty_stats[level]['correct'] += 1
                    else:
                        difficulty_stats[level]['incorrect'] += 1
                elif q['status'] == 'markedReview':
                    difficulty_stats[level]['marked_review'] += 1
                elif q['status'] == 'notAnswered':
                    difficulty_stats[level]['not_answered'] += 1

    # Display overall difficulty-wise stats
    for difficulty, stats in difficulty_stats.items():
        if stats['total'] > 0:
            accuracy = (stats['correct'] / stats['answered'] * 100) if stats['answered'] > 0 else 0
            avg_time = stats['total_time'] / stats['answered'] if stats['answered'] > 0 else 0

            context += f"""### {difficulty.capitalize()} Level Questions
- Total Questions: {stats['total']}
- Attempted: {stats['answered']} | Correct: {stats['correct']} | Incorrect: {stats['incorrect']}
- Not Attempted: {stats['not_answered']} | Marked for Review: {stats['marked_review']}
- Accuracy: {accuracy:.1f}%
- Average Time per Attempted Question: {avg_time:.1f} seconds
- Total Time Spent: {stats['total_time']} seconds

"""

    # Add subject-wise difficulty analysis
    context += "## Subject-wise Difficulty Analysis\n\n"

    # Initialize subject-wise difficulty stats
    subject_difficulty_stats = defaultdict(lambda: {
        'easy': {'total': 0, 'answered': 0, 'correct': 0, 'incorrect': 0,
                 'marked_review': 0, 'not_answered': 0, 'total_time': 0},
        'medium': {'total': 0, 'answered': 0, 'correct': 0, 'incorrect': 0,
                   'marked_review': 0, 'not_answered': 0, 'total_time': 0},
        'tough': {'total': 0, 'answered': 0, 'correct': 0, 'incorrect': 0,
                  'marked_review': 0, 'not_answered': 0, 'total_time': 0}
    })

    # Process debug_counts for subject-wise difficulty analysis
    for (subject, chapter), questions in debug_counts.items():
        for q in questions:
            level = q['level']
            subj = q['subject']
            if level in subject_difficulty_stats[subj]:
                subject_difficulty_stats[subj][level]['total'] += 1
                subject_difficulty_stats[subj][level]['total_time'] += q['time_taken']

                if q['status'] == 'answered':
                    subject_difficulty_stats[subj][level]['answered'] += 1
                    if q.get('correct', False):
                        subject_difficulty_stats[subj][level]['correct'] += 1
                    else:
                        subject_difficulty_stats[subj][level]['incorrect'] += 1
                elif q['status'] == 'markedReview':
                    subject_difficulty_stats[subj][level]['marked_review'] += 1
                elif q['status'] == 'notAnswered':
                    subject_difficulty_stats[subj][level]['not_answered'] += 1

    # Display subject-wise difficulty stats
    for subj in subject_difficulty_stats:
        context += f"### {subj}\n\n"
        for difficulty, stats in subject_difficulty_stats[subj].items():
            if stats['total'] > 0:
                accuracy = (stats['correct'] / stats['answered'] * 100) if stats['answered'] > 0 else 0
                avg_time = stats['total_time'] / stats['answered'] if stats['answered'] > 0 else 0

                context += f"#### {difficulty.capitalize()} Level Questions\n"
                context += f"- Total Questions: {stats['total']}\n"
                context += f"- Attempted: {stats['answered']} | Correct: {stats['correct']} | Incorrect: {stats['incorrect']}\n"
                context += f"- Not Attempted: {stats['not_answered']} | Marked for Review: {stats['marked_review']}\n"
                context += f"- Accuracy: {accuracy:.1f}%\n"
                context += f"- Average Time per Attempted Question: {avg_time:.1f} seconds\n"
                context += f"- Total Time Spent: {stats['total_time']} seconds\n\n"
        context += "\n"

    # Add chapter-wise details with concept analysis
    context += "## Chapter-wise Analysis with Concepts\n\n"

    for subject, chapters in processed_data['chapter_details'].items():
        context += f"### {subject}\n\n"
        for chapter, stats in chapters.items():
            context += f"""**{chapter}**
- Total Questions: {stats['questions_total']}
- Attempted: {stats['answered']} | Not Attempted: {stats['not_answered']} | Marked for Review: {stats['marked_review']}
- Performance: {stats['correct']} correct, {stats['incorrect']} incorrect
- Accuracy: {stats['accuracy_on_answered_percent']:.1f}%
- Avg Time/Answered: {stats['avg_time_per_answered_q_seconds']:.1f} seconds
- Difficulty Distribution: Easy({stats['difficulty_counts']['easy']}), Medium({stats['difficulty_counts']['medium']}), Tough({stats['difficulty_counts']['tough']})

"""

            # Add concept analysis for this chapter
            chapter_concepts = concept_stats.get((subject, chapter), {})
            if chapter_concepts:
                strong_concepts = []
                weak_concepts = []
                moderate_concepts = []

                for concept, cstats in chapter_concepts.items():
                    if cstats['total'] > 0:
                        accuracy = (cstats['correct'] / cstats['total']) * 100
                        concept_info = f"  - {concept}: {cstats['correct']}/{cstats['total']} ({accuracy:.1f}%)"

                        if accuracy >= 80:
                            strong_concepts.append(concept_info)
                        elif accuracy <= 60:
                            weak_concepts.append(concept_info)
                        else:
                            moderate_concepts.append(concept_info)

                if strong_concepts:
                    context += "**Strong Concepts (≥80% accuracy):**\n"
                    context += "\n".join(strong_concepts) + "\n\n"

                if moderate_concepts:
                    context += "**Moderate Concepts (60-80% accuracy):**\n"
                    context += "\n".join(moderate_concepts) + "\n\n"

                if weak_concepts:
                    context += "**Weak Concepts (≤60% accuracy):**\n"
                    context += "\n".join(weak_concepts) + "\n\n"
            else:
                context += "*No concepts attempted in this chapter*\n\n"

    # Add overall insights
    context += """## Key Insights

### Overall Concept Performance:
"""

    # Aggregate all concepts across subjects
    all_strong_concepts = []
    all_weak_concepts = []

    for (subject, chapter), concepts in concept_stats.items():
        for concept, cstats in concepts.items():
            if cstats['total'] > 0:
                accuracy = (cstats['correct'] / cstats['total']) * 100
                if accuracy >= 80:
                    all_strong_concepts.append(f"- {subject} ({chapter}): {concept} - {accuracy:.1f}%")
                elif accuracy <= 60:
                    all_weak_concepts.append(f"- {subject} ({chapter}): {concept} - {accuracy:.1f}%")

    context += "\n**Strong Concepts Across All Subjects:**\n"
    context += "\n".join(all_strong_concepts) if all_strong_concepts else "- No concepts with ≥80% accuracy\n"

    context += "\n\n**Weak Concepts Needing Improvement:**\n"
    context += "\n".join(all_weak_concepts) if all_weak_concepts else "- No concepts with ≤60% accuracy\n"

    return context

# --- Main Execution ---
def main():
    file_path = "/content/sample_submission_analysis_1.json"
    json_data = load_json_data(file_path)
    if json_data:
        processed_data, concept_stats, debug_counts = process_data(json_data)
        if processed_data:
            llm_context = prepare_comprehensive_llm_context(processed_data, concept_stats, debug_counts)
            print("=== Comprehensive LLM Context ===")
            print(llm_context)
        else:
            print("Failed to process JSON data")
    else:
        print("Failed to load JSON file")

if __name__ == "__main__":
    main()