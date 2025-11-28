"""
Utility functions for parsing and processing quiz data.
"""

import re
from typing import Dict, List, Optional


def parse_quiz_text(quiz_text: str) -> Dict:
    """
    Parse quiz text from Gemini into structured format.
    
    Expected format:
    1. Question text?
    A) Option 1
    B) Option 2
    C) Option 3
    D) Option 4
    Correct Answer: B
    
    Returns:
        Dictionary with structured quiz data
    """
    questions = []
    lines = quiz_text.strip().split('\n')
    
    current_question = None
    current_options = {}
    current_correct = None
    question_number = 0
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check for question number
        question_match = re.match(r'^(\d+)\.\s*(.+)', line)
        if question_match:
            # Save previous question if exists
            if current_question and current_options:
                questions.append({
                    'questionId': f'q{question_number}',
                    'questionText': current_question,
                    'options': current_options.copy(),
                    'correctAnswer': current_correct
                })
            
            question_number = int(question_match.group(1))
            current_question = question_match.group(2).rstrip('?')
            current_options = {}
            current_correct = None
            continue
        
        # Check for option (A, B, C, D)
        option_match = re.match(r'^([A-D])\)\s*(.+)', line)
        if option_match:
            option_letter = option_match.group(1)
            option_text = option_match.group(2)
            current_options[option_letter] = option_text
            continue
        
        # Check for correct answer
        correct_match = re.search(r'[Cc]orrect\s+[Aa]nswer:\s*([A-D])', line)
        if correct_match:
            current_correct = correct_match.group(1)
            continue
    
    # Save last question
    if current_question and current_options:
        questions.append({
            'questionId': f'q{question_number}',
            'questionText': current_question,
            'options': current_options.copy(),
            'correctAnswer': current_correct
        })
    
    return {
        'questions': questions,
        'numberOfQuestions': len(questions)
    }


def calculate_quiz_score(quiz_data: Dict, student_answers: Dict[str, str]) -> Dict:
    """
    Calculate quiz score based on student answers.
    
    Args:
        quiz_data: Structured quiz data with questions and correct answers
        student_answers: Dictionary of questionId -> answer (e.g., {"q1": "B", "q2": "A"})
        
    Returns:
        Dictionary with score, correct answers, total questions, and percentage
    """
    questions = quiz_data.get('questions', [])
    total_questions = len(questions)
    correct_count = 0
    
    answer_details = []
    
    for question in questions:
        question_id = question.get('questionId')
        correct_answer = question.get('correctAnswer')
        student_answer = student_answers.get(question_id, '').upper().strip()
        
        is_correct = student_answer == correct_answer
        
        if is_correct:
            correct_count += 1
        
        answer_details.append({
            'questionId': question_id,
            'questionText': question.get('questionText'),
            'studentAnswer': student_answer,
            'correctAnswer': correct_answer,
            'isCorrect': is_correct
        })
    
    score_percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
    
    return {
        'score': round(score_percentage, 2),
        'correctAnswers': correct_count,
        'totalQuestions': total_questions,
        'percentage': round(score_percentage, 2),
        'answerDetails': answer_details
    }

