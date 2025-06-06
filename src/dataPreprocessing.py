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
        return None

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
            "total_marks_possible": subject.get("totalMarks", 100),  # Fixed: Use 100 as default
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
                "concepts": concepts
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

    # Debug: Print question counts
    print("\n=== Debug: Question Counts per Chapter ===")
    for (subject, chapter), questions in debug_counts.items():
        print(f"\n{subject} - {chapter}:")
        for i, q in enumerate(questions, 1):
            print(f"  Q{i}: Status={q['status']}, Time={q['time_taken']}s, Level={q['level']}, Correct={q.get('correct', 'N/A')}, Concepts={q['concepts']}")

    # Print concept analysis
    print("\n=== Concept Analysis for All Chapters ===")
    for (subject, chapter), concepts in concept_stats.items():
        print(f"\n{subject} - {chapter}:")
        for concept, stats in concepts.items():
            print(f"  {concept}:")
            print(f"    Total Questions: {stats['total']}")
            print(f"    Correct: {stats['correct']}")
            print(f"    Incorrect: {stats['incorrect']}")

    return processed_data

# --- Main Execution ---
file_path = "/content/sample_submission_analysis_1.json"
json_data = load_json_data(file_path)
if json_data:
    result = process_data(json_data)
    if result:
        import pprint
        print("\n=== Overall Summary ===")
        pprint.pprint(result["overall_summary"])
        print("\n=== Subject Summary ===")
        pprint.pprint(dict(result["subject_summary"]))
        print("\n=== Corrected Chapter Details ===")
        pprint.pprint(dict(result["chapter_details"]))
else:
    print("Failed to load JSON file")