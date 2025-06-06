import requests
import json
import os
import requests
import json
import os
from dotenv import load_dotenv # Import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Gemini API configuration
API_KEY = os.getenv("GEMINI_API_KEY") # Now it will read from the .env file
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# Performance data from prepare_llm_context_comprehensive output
new_new_performance_data = {
    "overall_summary": {
        "total_score": "133/300",
        "questions_attempted": "47/75",
        "correct_answers": 36,
        "overall_accuracy": "76.6%",
        "time_taken": "83.3 minutes"
    },
    "subject_summary": {
        "Physics": {
            "score": "44/100",
            "questions_attempted": "16/25",
            "correct": 12,
            "incorrect": 4,
            "accuracy": "75.0%",
            "avg_time_per_question": "186.5 seconds"
        },
        "Chemistry": {
            "score": "60/100",
            "questions_attempted": "20/25",
            "correct": 16,
            "incorrect": 4,
            "accuracy": "80.0%",
            "avg_time_per_question": "69.8 seconds"
        },
        "Mathematics": {
            "score": "29/100",
            "questions_attempted": "11/25",
            "correct": 8,
            "incorrect": 3,
            "accuracy": "72.7%",
            "avg_time_per_question": "56.1 seconds"
        }
    },
    "difficulty_summary": {
        "Easy": {
            "total": 25,
            "attempted": 19,
            "correct": 14,
            "incorrect": 5,
            "accuracy": "73.7%",
            "avg_time": "138.3 seconds"
        },
        "Medium": {
            "total": 30,
            "attempted": 18,
            "correct": 14,
            "incorrect": 4,
            "accuracy": "77.8%",
            "avg_time": "77.8 seconds"
        },
        "Tough": {
            "total": 20,
            "attempted": 10,
            "correct": 8,
            "incorrect": 2,
            "accuracy": "80.0%",
            "avg_time": "97.0 seconds"
        }
    },
    "chapter_concepts": {
        "Physics": {
            "Capacitance": {
                "total_questions": 10,
                "attempted": 8,
                "correct": 6,
                "accuracy": "75.0%",
                "avg_time": "62.5 seconds",
                "strong_concepts": [
                    {"concept": "Charging of Capacitors", "accuracy": "100.0%"},
                    {"concept": "Series and Parallel Combinations of Capacitor", "accuracy": "100.0%"},
                    {"concept": "Induced charge on dielectric", "accuracy": "100.0%"},
                    {"concept": "Energy stored in capacitor", "accuracy": "100.0%"}
                ],
                "weak_concepts": [
                    {"concept": "Multiple dielectric slabs in capacitor", "accuracy": "0.0%"},
                    {"concept": "Force on plates of capacitor", "accuracy": "0.0%"}
                ]
            },
            "Electrostatics": {
                "total_questions": 15,
                "attempted": 12,
                "correct": 10,
                "accuracy": "83.3%",
                "avg_time": "74.8 seconds",
                "strong_concepts": [
                    {"concept": "Electric Field and Force due to Dipole", "accuracy": "100.0%"},
                    {"concept": "Properties of Electric Dipole", "accuracy": "100.0%"},
                    {"concept": "Electric Field due to continuous charge distribution", "accuracy": "100.0%"},
                    {"concept": "Electric flux", "accuracy": "100.0%"},
                    {"concept": "Gauss theorem", "accuracy": "100.0%"},
                    {"concept": "Electric potential due to point charge", "accuracy": "100.0%"},
                    {"concept": "Electric field by group of charges", "accuracy": "100.0%"}
                ],
                "weak_concepts": [
                    {"concept": "Coulombs Law", "accuracy": "0.0%"},
                    {"concept": "Charged Particle in electric field", "accuracy": "50.0%"}
                ]
            }
        },
        "Chemistry": {
            "Electrochemistry": {
                "total_questions": 13,
                "attempted": 1,
                "correct": 1,
                "accuracy": "100.0%",
                "avg_time": "122.0 seconds",
                "strong_concepts": [
                    {"concept": "Factors which enhance corrosion", "accuracy": "100.0%"}
                ],
                "weak_concepts": []
            },
            "Solutions": {
                "total_questions": 12,
                "attempted": 10,
                "correct": 7,
                "accuracy": "70.0%",
                "avg_time": "49.5 seconds",
                "strong_concepts": [
                    {"concept": "Henry's law", "accuracy": "100.0%"},
                    {"concept": "Azeotropic solutions", "accuracy": "100.0%"},
                    {"concept": "Elevation in boiling point", "accuracy": "100.0%"},
                    {"concept": "Vapour pressure of solution containing volatile solute and volatile solvent", "accuracy": "100.0%"}
                ],
                "weak_concepts": [
                    {"concept": "Osmotic pressure", "accuracy": "33.3%"},
                    {"concept": "Depression in freezing point", "accuracy": "0.0%"}
                ]
            }
        },
        "Mathematics": {
            "Functions": {
                "total_questions": 18,
                "attempted": 10,
                "correct": 7,
                "accuracy": "70.0%",
                "avg_time": "177.1 seconds",
                "strong_concepts": [
                    {"concept": "Questions on determining odd and even functions", "accuracy": "100.0%"},
                    {"concept": "domain of modulus functions", "accuracy": "100.0%"},
                    {"concept": "questions based on functional equations", "accuracy": "100.0%"},
                    {"concept": "range involving modulus functions", "accuracy": "100.0%"}
                ],
                "weak_concepts": [
                    {"concept": "finding fog and gof", "accuracy": "50.0%"},
                    {"concept": "period of normal functions", "accuracy": "0.0%"}
                ]
            },
            "Sets and Relations": {
                "total_questions": 7,
                "attempted": 6,
                "correct": 5,
                "accuracy": "83.3%",
                "avg_time": "202.2 seconds",
                "strong_concepts": [
                    {"concept": "Questions on number of relations and sets", "accuracy": "100.0%"},
                    {"concept": "Questions on Venn Diagram", "accuracy": "100.0%"}
                ],
                "weak_concepts": [
                    {"concept": "Questions on Symmetric Transitive and Reflexive Properties", "accuracy": "50.0%"}
                ]
            }
        }
    }
}

# API prompt for generating feedback
prompt = f"""
You are an expert tutor providing personalized feedback for a student's test performance. Based on the following data, generate a detailed, human-like feedback report that is motivating, encouraging, and actionable. The report should include:

1. An 'Overall Performance' section summarizing the total score, questions attempted, correct answers, accuracy, and time taken.
2. A personalized, motivating introduction (highlight specific achievements like strong concepts, acknowledge challenges like low attempt rates, avoid generic phrases).
3. A performance breakdown by difficulty level (Easy, Medium, Tough) across subjects (Physics, Chemistry, Mathematics), presented concisely.
4. Time vs. accuracy insights, explaining how time allocation impacts performance and identifying patterns (e.g., spending too long on easy questions).
5. A chapter-wise concept analysis, listing strong (≥80% accuracy) and weak (≤60% accuracy) concepts for each chapter in Physics (Electrostatics, Capacitance), Chemistry (Solutions, Electrochemistry), and Mathematics (Functions, Sets and Relations).
6. 2–3 actionable suggestions for improvement, focusing on specific weaknesses and leveraging strengths.

Use a friendly, supportive tone and keep the response clear and concise. Avoid technical jargon. Here is the performance data:

Overall Summary:
- Total Score: {new_new_performance_data['overall_summary']['total_score']}
- Questions Attempted: {new_new_performance_data['overall_summary']['questions_attempted']}
- Correct Answers: {new_new_performance_data['overall_summary']['correct_answers']}
- Overall Accuracy: {new_new_performance_data['overall_summary']['overall_accuracy']}
- Time Taken: {new_new_performance_data['overall_summary']['time_taken']}

Subject-wise Summary:
- Physics: Score: {new_new_performance_data['subject_summary']['Physics']['score']}, Attempted: {new_new_performance_data['subject_summary']['Physics']['questions_attempted']}, Correct: {new_new_performance_data['subject_summary']['Physics']['correct']}, Incorrect: {new_new_performance_data['subject_summary']['Physics']['incorrect']}, Accuracy: {new_new_performance_data['subject_summary']['Physics']['accuracy']}, Avg Time/Question: {new_new_performance_data['subject_summary']['Physics']['avg_time_per_question']}
- Chemistry: Score: {new_new_performance_data['subject_summary']['Chemistry']['score']}, Attempted: {new_new_performance_data['subject_summary']['Chemistry']['questions_attempted']}, Correct: {new_new_performance_data['subject_summary']['Chemistry']['correct']}, Incorrect: {new_new_performance_data['subject_summary']['Chemistry']['incorrect']}, Accuracy: {new_new_performance_data['subject_summary']['Chemistry']['accuracy']}, Avg Time/Question: {new_new_performance_data['subject_summary']['Chemistry']['avg_time_per_question']}
- Mathematics: Score: {new_new_performance_data['subject_summary']['Mathematics']['score']}, Attempted: {new_new_performance_data['subject_summary']['Mathematics']['questions_attempted']}, Correct: {new_new_performance_data['subject_summary']['Mathematics']['correct']}, Incorrect: {new_new_performance_data['subject_summary']['Mathematics']['incorrect']}, Accuracy: {new_new_performance_data['subject_summary']['Mathematics']['accuracy']}, Avg Time/Question: {new_new_performance_data['subject_summary']['Mathematics']['avg_time_per_question']}

Difficulty-wise Summary:
- Easy: Total: {new_new_performance_data['difficulty_summary']['Easy']['total']}, Attempted: {new_new_performance_data['difficulty_summary']['Easy']['attempted']}, Correct: {new_new_performance_data['difficulty_summary']['Easy']['correct']}, Incorrect: {new_new_performance_data['difficulty_summary']['Easy']['incorrect']}, Accuracy: {new_new_performance_data['difficulty_summary']['Easy']['accuracy']}, Avg Time: {new_new_performance_data['difficulty_summary']['Easy']['avg_time']}
- Medium: Total: {new_new_performance_data['difficulty_summary']['Medium']['total']}, Attempted: {new_new_performance_data['difficulty_summary']['Medium']['attempted']}, Correct: {new_new_performance_data['difficulty_summary']['Medium']['correct']}, Incorrect: {new_new_performance_data['difficulty_summary']['Medium']['incorrect']}, Accuracy: {new_new_performance_data['difficulty_summary']['Medium']['accuracy']}, Avg Time: {new_new_performance_data['difficulty_summary']['Medium']['avg_time']}
- Tough: Total: {new_new_performance_data['difficulty_summary']['Tough']['total']}, Attempted: {new_new_performance_data['difficulty_summary']['Tough']['attempted']}, Correct: {new_new_performance_data['difficulty_summary']['Tough']['correct']}, Incorrect: {new_new_performance_data['difficulty_summary']['Tough']['incorrect']}, Accuracy: {new_new_performance_data['difficulty_summary']['Tough']['accuracy']}, Avg Time: {new_new_performance_data['difficulty_summary']['Tough']['avg_time']}

Chapter-wise Concepts:
- Physics (Capacitance): Total: {new_new_performance_data['chapter_concepts']['Physics']['Capacitance']['total_questions']}, Attempted: {new_new_performance_data['chapter_concepts']['Physics']['Capacitance']['attempted']}, Correct: {new_new_performance_data['chapter_concepts']['Physics']['Capacitance']['correct']}, Accuracy: {new_new_performance_data['chapter_concepts']['Physics']['Capacitance']['accuracy']}, Avg Time: {new_new_performance_data['chapter_concepts']['Physics']['Capacitance']['avg_time']}
  Strong Concepts: {', '.join([f"{c['concept']} ({c['accuracy']})" for c in new_new_performance_data['chapter_concepts']['Physics']['Capacitance']['strong_concepts']])}
  Weak Concepts: {', '.join([f"{c['concept']} ({c['accuracy']})" for c in new_new_performance_data['chapter_concepts']['Physics']['Capacitance']['weak_concepts']])}
- Physics (Electrostatics): Total: {new_new_performance_data['chapter_concepts']['Physics']['Electrostatics']['total_questions']}, Attempted: {new_new_performance_data['chapter_concepts']['Physics']['Electrostatics']['attempted']}, Correct: {new_new_performance_data['chapter_concepts']['Physics']['Electrostatics']['correct']}, Accuracy: {new_new_performance_data['chapter_concepts']['Physics']['Electrostatics']['accuracy']}, Avg Time: {new_new_performance_data['chapter_concepts']['Physics']['Electrostatics']['avg_time']}
  Strong Concepts: {', '.join([f"{c['concept']} ({c['accuracy']})" for c in new_new_performance_data['chapter_concepts']['Physics']['Electrostatics']['strong_concepts']])}
  Weak Concepts: {', '.join([f"{c['concept']} ({c['accuracy']})" for c in new_new_performance_data['chapter_concepts']['Physics']['Electrostatics']['weak_concepts']])}
- Chemistry (Electrochemistry): Total: {new_new_performance_data['chapter_concepts']['Chemistry']['Electrochemistry']['total_questions']}, Attempted: {new_new_performance_data['chapter_concepts']['Chemistry']['Electrochemistry']['attempted']}, Correct: {new_new_performance_data['chapter_concepts']['Chemistry']['Electrochemistry']['correct']}, Accuracy: {new_new_performance_data['chapter_concepts']['Chemistry']['Electrochemistry']['accuracy']}, Avg Time: {new_new_performance_data['chemistry_chapter_concepts']['Electrochemistry']['avg_time']}
  Strong Concepts: {', '.join([f"{c['concept']} ({c['accuracy']})" for c in new_new_performance_data['chapter_concepts']['Chemistry']['Electrochemistry']['strong_concepts']])}
  Weak Concepts: {', '.join([f"{c['concept']} ({c['accuracy']})" for c in new_new_performance_data['chapter_concepts']['Chemistry']['Electrochemistry']['weak_concepts']])}
- Chemistry (Solutions): Total: {new_new_performance_data['chapter_concepts']['Chemistry']['Solutions']['total_questions']}, Attempted: {new_new_performance_data['chapter_concepts']['Chemistry']['Solutions']['attempted']}, Correct: {new_new_performance_data['chapter_concepts']['Chemistry']['Solutions']['correct']}, Accuracy: {new_new_performance_data['chapter_concepts']['Chemistry']['Solutions']['accuracy']}, Avg Time: {new_new_performance_data['chapter_concepts']['Chemistry']['Solutions']['avg_time']}
  Strong Concepts: {', '.join([f"{c['concept']} ({c['accuracy']})" for c in new_new_performance_data['chapter_concepts']['Chemistry']['Solutions']['strong_concepts']])}
  Weak Concepts: {', '.join([f"{c['concept']} ({c['accuracy']})" for c in new_new_performance_data['chapter_concepts']['Chemistry']['Solutions']['weak_concepts']])}
- Mathematics (Functions): Total: {new_new_performance_data['chapter_concepts']['Mathematics']['Functions']['total_questions']}, Attempted: {new_new_performance_data['chapter_concepts']['Mathematics']['Functions']['attempted']}, Correct: {new_new_performance_data['chapter_concepts']['Mathematics']['Functions']['correct']}, Accuracy: {new_new_performance_data['chapter_concepts']['Mathematics']['Functions']['accuracy']}, Avg Time: {new_new_performance_data['chapter_concepts']['Mathematics']['Functions']['avg_time']}
  Strong Concepts: {', '.join([f"{c['concept']} ({c['accuracy']})" for c in new_new_performance_data['chapter_concepts']['Mathematics']['Functions']['strong_concepts']])}
  Weak Concepts: {', '.join([f"{c['concept']} ({c['accuracy']})" for c in new_new_performance_data['chapter_concepts']['Mathematics']['Functions']['weak_concepts']])}
- Mathematics (Sets and Relations): Total: {new_new_performance_data['chapter_concepts']['Mathematics']['Sets and Relations']['total_questions']}, Attempted: {new_new_performance_data['chapter_concepts']['Mathematics']['Sets and Relations']['attempted']}, Correct: {new_new_performance_data['chapter_concepts']['Mathematics']['Sets and Relations']['correct']}, Accuracy: {new_new_performance_data['chapter_concepts']['Mathematics']['Sets and Relations']['accuracy']}, Avg Time: {new_new_performance_data['chapter_concepts']['Mathematics']['Sets and Relations']['avg_time']}
  Strong Concepts: {', '.join([f"{c['concept']} ({c['accuracy']})" for c in new_new_performance_data['chapter_concepts']['Mathematics']['Sets and Relations']['strong_concepts']])}
  Weak Concepts: {', '.join([f"{c['concept']} ({c['accuracy']})" for c in new_new_performance_data['chapter_concepts']['Mathematics']['Sets and Relations']['weak_concepts']])}

Format the response in clear sections with headers: 'Overall Performance', 'Motivating Introduction', 'Performance Breakdown', 'Time vs. Accuracy Insights', 'Chapter-wise Concept Analysis', and 'Actionable Suggestions'. Ensure the response is under 2000 tokens to stay within free tier limits.
"""

# API request
headers = {
    "Content-Type": "application/json"
}

payload = {
    "contents": [
        {
            "parts": [
                {"text": prompt}
            ],
            "role": "user"
        }
    ]
}

try:
    response = requests.post(f"{API_URL}?key={API_KEY}", headers=headers, json=payload)
    response.raise_for_status()
    feedback = response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    print("Generated Feedback:")
    print(feedback)
except requests.RequestException as e:
    print(f"Error calling Gemini API: {e}")
    feedback = "Failed to generate feedback due to API error."

# Save feedback for PDF generation
with open("feedback_output.txt", "w") as f:
    f.write(feedback)

# Performance data from prepare_llm_context_comprehensive output
new_new_performance_data = {
    "overall_summary": {
        "total_score": "133/300",
        "questions_attempted": "47/75",
        "correct_answers": 36,
        "overall_accuracy": "76.6%",
        "time_taken": "83.3 minutes"
    },
    "subject_summary": {
        "Physics": {
            "score": "44/100",
            "questions_attempted": "16/25",
            "correct": 12,
            "incorrect": 4,
            "accuracy": "75.0%",
            "avg_time_per_question": "186.5 seconds"
        },
        "Chemistry": {
            "score": "60/100",
            "questions_attempted": "20/25",
            "correct": 16,
            "incorrect": 4,
            "accuracy": "80.0%",
            "avg_time_per_question": "69.8 seconds"
        },
        "Mathematics": {
            "score": "29/100",
            "questions_attempted": "11/25",
            "correct": 8,
            "incorrect": 3,
            "accuracy": "72.7%",
            "avg_time_per_question": "56.1 seconds"
        }
    },
    "difficulty_summary": {
        "Easy": {
            "total": 25,
            "attempted": 19,
            "correct": 14,
            "incorrect": 5,
            "accuracy": "73.7%",
            "avg_time": "138.3 seconds"
        },
        "Medium": {
            "total": 30,
            "attempted": 18,
            "correct": 14,
            "incorrect": 4,
            "accuracy": "77.8%",
            "avg_time": "77.8 seconds"
        },
        "Tough": {
            "total": 20,
            "attempted": 10,
            "correct": 8,
            "incorrect": 2,
            "accuracy": "80.0%",
            "avg_time": "97.0 seconds"
        }
    },
    "chapter_concepts": {
        "Physics": {
            "Capacitance": {
                "total_questions": 10,
                "attempted": 8,
                "correct": 6,
                "accuracy": "75.0%",
                "avg_time": "62.5 seconds",
                "strong_concepts": [
                    {"concept": "Charging of Capacitors", "accuracy": "100.0%"},
                    {"concept": "Series and Parallel Combinations of Capacitor", "accuracy": "100.0%"},
                    {"concept": "Induced charge on dielectric", "accuracy": "100.0%"},
                    {"concept": "Energy stored in capacitor", "accuracy": "100.0%"}
                ],
                "weak_concepts": [
                    {"concept": "Multiple dielectric slabs in capacitor", "accuracy": "0.0%"},
                    {"concept": "Force on plates of capacitor", "accuracy": "0.0%"}
                ]
            },
            "Electrostatics": {
                "total_questions": 15,
                "attempted": 12,
                "correct": 10,
                "accuracy": "83.3%",
                "avg_time": "74.8 seconds",
                "strong_concepts": [
                    {"concept": "Electric Field and Force due to Dipole", "accuracy": "100.0%"},
                    {"concept": "Properties of Electric Dipole", "accuracy": "100.0%"},
                    {"concept": "Electric Field due to continuous charge distribution", "accuracy": "100.0%"},
                    {"concept": "Electric flux", "accuracy": "100.0%"},
                    {"concept": "Gauss theorem", "accuracy": "100.0%"},
                    {"concept": "Electric potential due to point charge", "accuracy": "100.0%"},
                    {"concept": "Electric field by group of charges", "accuracy": "100.0%"}
                ],
                "weak_concepts": [
                    {"concept": "Coulombs Law", "accuracy": "0.0%"},
                    {"concept": "Charged Particle in electric field", "accuracy": "50.0%"}
                ]
            }
        },
        "Chemistry": {
            "Electrochemistry": {
                "total_questions": 13,
                "attempted": 1,
                "correct": 1,
                "accuracy": "100.0%",
                "avg_time": "122.0 seconds",
                "strong_concepts": [
                    {"concept": "Factors which enhance corrosion", "accuracy": "100.0%"}
                ],
                "weak_concepts": []
            },
            "Solutions": {
                "total_questions": 12,
                "attempted": 10,
                "correct": 7,
                "accuracy": "70.0%",
                "avg_time": "49.5 seconds",
                "strong_concepts": [
                    {"concept": "Henry's law", "accuracy": "100.0%"},
                    {"concept": "Azeotropic solutions", "accuracy": "100.0%"},
                    {"concept": "Elevation in boiling point", "accuracy": "100.0%"},
                    {"concept": "Vapour pressure of solution containing volatile solute and volatile solvent", "accuracy": "100.0%"}
                ],
                "weak_concepts": [
                    {"concept": "Osmotic pressure", "accuracy": "33.3%"},
                    {"concept": "Depression in freezing point", "accuracy": "0.0%"}
                ]
            }
        },
        "Mathematics": {
            "Functions": {
                "total_questions": 18,
                "attempted": 10,
                "correct": 7,
                "accuracy": "70.0%",
                "avg_time": "177.1 seconds",
                "strong_concepts": [
                    {"concept": "Questions on determining odd and even functions", "accuracy": "100.0%"},
                    {"concept": "domain of modulus functions", "accuracy": "100.0%"},
                    {"concept": "questions based on functional equations", "accuracy": "100.0%"},
                    {"concept": "range involving modulus functions", "accuracy": "100.0%"}
                ],
                "weak_concepts": [
                    {"concept": "finding fog and gof", "accuracy": "50.0%"},
                    {"concept": "period of normal functions", "accuracy": "0.0%"}
                ]
            },
            "Sets and Relations": {
                "total_questions": 7,
                "attempted": 6,
                "correct": 5,
                "accuracy": "83.3%",
                "avg_time": "202.2 seconds",
                "strong_concepts": [
                    {"concept": "Questions on number of relations and sets", "accuracy": "100.0%"},
                    {"concept": "Questions on Venn Diagram", "accuracy": "100.0%"}
                ],
                "weak_concepts": [
                    {"concept": "Questions on Symmetric Transitive and Reflexive Properties", "accuracy": "50.0%"}
                ]
            }
        }
    }
}

# API prompt for generating feedback
prompt = f"""
You are an expert tutor providing personalized feedback for a student's test performance. Based on the following data, generate a detailed, human-like feedback report that is motivating, encouraging, and actionable. The report should include:

1. An 'Overall Performance' section summarizing the total score, questions attempted, correct answers, accuracy, and time taken.
2. A personalized, motivating introduction (highlight specific achievements like strong concepts, acknowledge challenges like low attempt rates, avoid generic phrases).
3. A performance breakdown by difficulty level (Easy, Medium, Tough) across subjects (Physics, Chemistry, Mathematics), presented concisely.
4. Time vs. accuracy insights, explaining how time allocation impacts performance and identifying patterns (e.g., spending too long on easy questions).
5. A chapter-wise concept analysis, listing strong (≥80% accuracy) and weak (≤60% accuracy) concepts for each chapter in Physics (Electrostatics, Capacitance), Chemistry (Solutions, Electrochemistry), and Mathematics (Functions, Sets and Relations).
6. 2–3 actionable suggestions for improvement, focusing on specific weaknesses and leveraging strengths.

Use a friendly, supportive tone and keep the response clear and concise. Avoid technical jargon. Here is the performance data:

Overall Summary:
- Total Score: {new_performance_data['overall_summary']['total_score']}
- Questions Attempted: {new_performance_data['overall_summary']['questions_attempted']}
- Correct Answers: {new_performance_data['overall_summary']['correct_answers']}
- Overall Accuracy: {new_performance_data['overall_summary']['overall_accuracy']}
- Time Taken: {new_performance_data['overall_summary']['time_taken']}

Subject-wise Summary:
- Physics: Score: {new_performance_data['subject_summary']['Physics']['score']}, Attempted: {new_performance_data['subject_summary']['Physics']['questions_attempted']}, Correct: {new_performance_data['subject_summary']['Physics']['correct']}, Incorrect: {new_performance_data['subject_summary']['Physics']['incorrect']}, Accuracy: {new_performance_data['subject_summary']['Physics']['accuracy']}, Avg Time/Question: {new_performance_data['subject_summary']['Physics']['avg_time_per_question']}
- Chemistry: Score: {new_performance_data['subject_summary']['Chemistry']['score']}, Attempted: {new_performance_data['subject_summary']['Chemistry']['questions_attempted']}, Correct: {new_performance_data['subject_summary']['Chemistry']['correct']}, Incorrect: {new_performance_data['subject_summary']['Chemistry']['incorrect']}, Accuracy: {new_performance_data['subject_summary']['Chemistry']['accuracy']}, Avg Time/Question: {new_performance_data['subject_summary']['Chemistry']['avg_time_per_question']}
- Mathematics: Score: {new_performance_data['subject_summary']['Mathematics']['score']}, Attempted: {new_performance_data['subject_summary']['Mathematics']['questions_attempted']}, Correct: {new_performance_data['subject_summary']['Mathematics']['correct']}, Incorrect: {new_performance_data['subject_summary']['Mathematics']['incorrect']}, Accuracy: {new_performance_data['subject_summary']['Mathematics']['accuracy']}, Avg Time/Question: {new_performance_data['subject_summary']['Mathematics']['avg_time_per_question']}

Difficulty-wise Summary:
- Easy: Total: {new_performance_data['difficulty_summary']['Easy']['total']}, Attempted: {new_performance_data['difficulty_summary']['Easy']['attempted']}, Correct: {new_performance_data['difficulty_summary']['Easy']['correct']}, Incorrect: {new_performance_data['difficulty_summary']['Easy']['incorrect']}, Accuracy: {new_performance_data['difficulty_summary']['Easy']['accuracy']}, Avg Time: {new_performance_data['difficulty_summary']['Easy']['avg_time']}
- Medium: Total: {new_performance_data['difficulty_summary']['Medium']['total']}, Attempted: {new_performance_data['difficulty_summary']['Medium']['attempted']}, Correct: {new_performance_data['difficulty_summary']['Medium']['correct']}, Incorrect: {new_performance_data['difficulty_summary']['Medium']['incorrect']}, Accuracy: {new_performance_data['difficulty_summary']['Medium']['accuracy']}, Avg Time: {new_performance_data['difficulty_summary']['Medium']['avg_time']}
- Tough: Total: {new_performance_data['difficulty_summary']['Tough']['total']}, Attempted: {new_performance_data['difficulty_summary']['Tough']['attempted']}, Correct: {new_performance_data['difficulty_summary']['Tough']['correct']}, Incorrect: {new_performance_data['difficulty_summary']['Tough']['incorrect']}, Accuracy: {new_performance_data['difficulty_summary']['Tough']['accuracy']}, Avg Time: {new_performance_data['difficulty_summary']['Tough']['avg_time']}

Chapter-wise Concepts:
- Physics (Capacitance): Total: {new_performance_data['chapter_concepts']['Physics']['Capacitance']['total_questions']}, Attempted: {new_performance_data['chapter_concepts']['Physics']['Capacitance']['attempted']}, Correct: {new_performance_data['chapter_concepts']['Physics']['Capacitance']['correct']}, Accuracy: {new_performance_data['chapter_concepts']['Physics']['Capacitance']['accuracy']}, Avg Time: {new_performance_data['chapter_concepts']['Physics']['Capacitance']['avg_time']}
  Strong Concepts: {', '.join([f"{c['concept']} ({c['accuracy']})" for c in new_performance_data['chapter_concepts']['Physics']['Capacitance']['strong_concepts']])}
  Weak Concepts: {', '.join([f"{c['concept']} ({c['accuracy']})" for c in new_performance_data['chapter_concepts']['Physics']['Capacitance']['weak_concepts']])}
- Physics (Electrostatics): Total: {new_performance_data['chapter_concepts']['Physics']['Electrostatics']['total_questions']}, Attempted: {new_performance_data['chapter_concepts']['Physics']['Electrostatics']['attempted']}, Correct: {new_performance_data['chapter_concepts']['Physics']['Electrostatics']['correct']}, Accuracy: {new_performance_data['chapter_concepts']['Physics']['Electrostatics']['accuracy']}, Avg Time: {new_performance_data['chapter_concepts']['Physics']['Electrostatics']['avg_time']}
  Strong Concepts: {', '.join([f"{c['concept']} ({c['accuracy']})" for c in new_performance_data['chapter_concepts']['Physics']['Electrostatics']['strong_concepts']])}
  Weak Concepts: {', '.join([f"{c['concept']} ({c['accuracy']})" for c in new_performance_data['chapter_concepts']['Physics']['Electrostatics']['weak_concepts']])}
- Chemistry (Electrochemistry): Total: {new_performance_data['chapter_concepts']['Chemistry']['Electrochemistry']['total_questions']}, Attempted: {new_performance_data['chapter_concepts']['Chemistry']['Electrochemistry']['attempted']}, Correct: {new_performance_data['chapter_concepts']['Chemistry']['Electrochemistry']['correct']}, Accuracy: {new_performance_data['chapter_concepts']['Chemistry']['Electrochemistry']['accuracy']}, Avg Time: {new_performance_data['chapter_concepts']['Chemistry']['Electrochemistry']['avg_time']}
  Strong Concepts: {', '.join([f"{c['concept']} ({c['accuracy']})" for c in new_performance_data['chapter_concepts']['Chemistry']['Electrochemistry']['strong_concepts']])}
  Weak Concepts: {', '.join([f"{c['concept']} ({c['accuracy']})" for c in new_performance_data['chapter_concepts']['Chemistry']['Electrochemistry']['weak_concepts']])}
- Chemistry (Solutions): Total: {new_performance_data['chapter_concepts']['Chemistry']['Solutions']['total_questions']}, Attempted: {new_performance_data['chapter_concepts']['Chemistry']['Solutions']['attempted']}, Correct: {new_performance_data['chapter_concepts']['Chemistry']['Solutions']['correct']}, Accuracy: {new_performance_data['chapter_concepts']['Chemistry']['Solutions']['accuracy']}, Avg Time: {new_performance_data['chapter_concepts']['Chemistry']['Solutions']['avg_time']}
  Strong Concepts: {', '.join([f"{c['concept']} ({c['accuracy']})" for c in new_performance_data['chapter_concepts']['Chemistry']['Solutions']['strong_concepts']])}
  Weak Concepts: {', '.join([f"{c['concept']} ({c['accuracy']})" for c in new_performance_data['chapter_concepts']['Chemistry']['Solutions']['weak_concepts']])}
- Mathematics (Functions): Total: {new_performance_data['chapter_concepts']['Mathematics']['Functions']['total_questions']}, Attempted: {new_performance_data['chapter_concepts']['Mathematics']['Functions']['attempted']}, Correct: {new_performance_data['chapter_concepts']['Mathematics']['Functions']['correct']}, Accuracy: {new_performance_data['chapter_concepts']['Mathematics']['Functions']['accuracy']}, Avg Time: {new_performance_data['chapter_concepts']['Mathematics']['Functions']['avg_time']}
  Strong Concepts: {', '.join([f"{c['concept']} ({c['accuracy']})" for c in new_performance_data['chapter_concepts']['Mathematics']['Functions']['strong_concepts']])}
  Weak Concepts: {', '.join([f"{c['concept']} ({c['accuracy']})" for c in new_performance_data['chapter_concepts']['Mathematics']['Functions']['weak_concepts']])}
- Mathematics (Sets and Relations): Total: {new_performance_data['chapter_concepts']['Mathematics']['Sets and Relations']['total_questions']}, Attempted: {new_performance_data['chapter_concepts']['Mathematics']['Sets and Relations']['attempted']}, Correct: {new_performance_data['chapter_concepts']['Mathematics']['Sets and Relations']['correct']}, Accuracy: {new_performance_data['chapter_concepts']['Mathematics']['Sets and Relations']['accuracy']}, Avg Time: {new_performance_data['chapter_concepts']['Mathematics']['Sets and Relations']['avg_time']}
  Strong Concepts: {', '.join([f"{c['concept']} ({c['accuracy']})" for c in new_performance_data['chapter_concepts']['Mathematics']['Sets and Relations']['strong_concepts']])}
  Weak Concepts: {', '.join([f"{c['concept']} ({c['accuracy']})" for c in new_performance_data['chapter_concepts']['Mathematics']['Sets and Relations']['weak_concepts']])}

Format the response in clear sections with headers: 'Overall Performance', 'Motivating Introduction', 'Performance Breakdown', 'Time vs. Accuracy Insights', 'Chapter-wise Concept Analysis', and 'Actionable Suggestions'. Ensure the response is under 2000 tokens to stay within free tier limits.
"""

# API request
headers = {
    "Content-Type": "application/json"
}

payload = {
    "contents": [
        {
            "parts": [
                {"text": prompt}
            ],
            "role": "user"
        }
    ]
}

try:
    response = requests.post(f"{API_URL}?key={API_KEY}", headers=headers, json=payload)
    response.raise_for_status()
    feedback = response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    print("Generated Feedback:")
    print(feedback)
except requests.RequestException as e:
    print(f"Error calling Gemini API: {e}")
    feedback = "Failed to generate feedback due to API error."

# Save feedback for PDF generation
with open("feedback_output.txt", "w") as f:
    f.write(feedback)