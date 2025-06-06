
overall_summary = performance_data['overall_summary']
subject_summary = performance_data['subject_summary']
chapter_details = performance_data['chapter_details']

# Initialize the new performance data structure
new_performance_data = {
    "overall_summary": {
        "total_score": f"{overall_summary['total_marks_scored']}/{overall_summary['total_marks_possible']}",
        "questions_attempted": f"{overall_summary['final_attempted']}/{overall_summary['total_questions_in_test']}",
        "correct_answers": overall_summary['final_correct'],
        "overall_accuracy": f"{round(overall_summary['overall_accuracy_percent'], 1)}%",
        "time_taken": f"{overall_summary['time_taken_minutes']} minutes"
    },
    "subject_summary": {
        subject: {
            "score": f"{data['marks_scored']}/{data['total_marks_possible']}",
            "questions_attempted": f"{data['attempted']}/{data['total_questions']}",
            "correct": data['correct'],
            "incorrect": data['incorrect'],
            "accuracy": f"{round(data['accuracy_percent'], 1)}%",
            "avg_time_per_question": f"{round(data['avg_time_per_attempted_q_seconds'], 1)} seconds"
        }
        for subject, data in subject_summary.items()
    },
    "difficulty_summary": {},
    "chapter_concepts": {
        subject: {
            chapter: {
                "total_questions": chapter_data['questions_total'],
                "attempted": chapter_data['answered'],
                "correct": chapter_data['correct'],
                "accuracy": f"{round(chapter_data['accuracy_on_answered_percent'], 1)}%",
                "avg_time": f"{round(chapter_data['avg_time_per_answered_q_seconds'], 1)} seconds",
                "strong_concepts": [],
                "weak_concepts": []
            }
            for chapter, chapter_data in chapters.items()
        }
        for subject, chapters in chapter_details.items()
    }
}

# Process difficulty_summary from debug_counts
difficulty_stats = {
    "Easy": {"total": 0, "attempted": 0, "correct": 0, "incorrect": 0, "time_sum": 0},
    "Medium": {"total": 0, "attempted": 0, "correct": 0, "incorrect": 0, "time_sum": 0},
    "Tough": {"total": 0, "attempted": 0, "correct": 0, "incorrect": 0, "time_sum": 0}
}

for (subject, chapter), questions in debug_counts.items():
    for q in questions:
        level = q['level'].capitalize()
        difficulty_stats[level]["total"] += 1
        if q['status'] == 'answered':
            difficulty_stats[level]["attempted"] += 1
            difficulty_stats[level]["time_sum"] += q['time_taken']
            if q.get('correct', False):
                difficulty_stats[level]["correct"] += 1
            else:
                difficulty_stats[level]["incorrect"] += 1

for level, stats in difficulty_stats.items():
    accuracy = (stats['correct'] / stats['attempted'] * 100) if stats['attempted'] > 0 else 0
    avg_time = (stats['time_sum'] / stats['attempted']) if stats['attempted'] > 0 else 0
    new_performance_data["difficulty_summary"][level] = {
        "total": stats['total'],
        "attempted": stats['attempted'],
        "correct": stats['correct'],
        "incorrect": stats['incorrect'],
        "accuracy": f"{round(accuracy, 1)}%",
        "avg_time": f"{round(avg_time, 1)} seconds"
    }

# Process strong and weak concepts from concept_stats
for subject, chapters in new_performance_data["chapter_concepts"].items():
    for chapter, chapter_data in chapters.items():
        concepts = concept_stats.get((subject, chapter), {})
        for concept, stats in concepts.items():
            accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            concept_entry = {"concept": concept, "accuracy": f"{round(accuracy, 1)}%"}
            if accuracy >= 75:
                new_performance_data["chapter_concepts"][subject][chapter]["strong_concepts"].append(concept_entry)
            else:
                new_performance_data["chapter_concepts"][subject][chapter]["weak_concepts"].append(concept_entry)

# The resulting new_performance_data matches your desired structure