"""
Model Factory Methods

This module provides factory methods for creating test data and model instances
for testing and development purposes.
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import random
import string

from .question import Question
from .tag import Tag
from .quiz_session import QuizSession

class ModelFactory:
    """Factory class for creating model instances for testing."""
    
    @staticmethod
    def create_sample_answers(question_type: str, num_options: int = 4) -> List[Dict[str, Any]]:
        """
        Create sample answer options for a question.
        
        Args:
            question_type: Type of question
            num_options: Number of answer options to create
            
        Returns:
            List of answer dictionaries
        """
        answers = []
        
        if question_type == "true_false":
            answers = [
                {"id": "answer_1", "text": "True", "is_correct": True},
                {"id": "answer_2", "text": "False", "is_correct": False}
            ]
        else:
            # Create multiple choice or select all answers
            correct_indices = []
            
            if question_type == "multiple_choice":
                # Exactly one correct answer
                correct_indices = [random.randint(0, num_options - 1)]
            elif question_type == "select_all":
                # Multiple correct answers (at least 1, at most num_options-1)
                num_correct = random.randint(1, num_options - 1)
                correct_indices = random.sample(range(num_options), num_correct)
            
            for i in range(num_options):
                answer = {
                    "id": f"answer_{i+1}",
                    "text": f"Option {chr(65 + i)}",  # A, B, C, D, etc.
                    "is_correct": i in correct_indices
                }
                answers.append(answer)
        
        return answers
    
    @staticmethod
    def create_question(
        question_text: Optional[str] = None,
        question_type: Optional[str] = None,
        answers: Optional[List[Dict[str, Any]]] = None,
        tags: Optional[List[str]] = None,
        question_id: Optional[str] = None
    ) -> Question:
        """
        Create a Question instance with sample data.
        
        Args:
            question_text: Question text (generated if not provided)
            question_type: Question type (random if not provided)
            answers: Answer options (generated if not provided)
            tags: Tag names (generated if not provided)
            question_id: Question ID (generated if not provided)
            
        Returns:
            Question instance
        """
        # Default question types
        question_types = ["multiple_choice", "true_false", "select_all"]
        
        # Generate question text if not provided
        if not question_text:
            question_texts = [
                "What is the capital of France?",
                "Which programming language is known for its simplicity?",
                "What is 2 + 2?",
                "The sun rises in the east.",
                "Which of the following are programming languages?",
                "What is the largest planet in our solar system?",
                "Python is a compiled language.",
                "Which of the following are data structures?"
            ]
            question_text = random.choice(question_texts)
        
        # Select question type if not provided
        if not question_type:
            question_type = random.choice(question_types)
        
        # Generate answers if not provided
        if not answers:
            num_options = 4 if question_type != "true_false" else 2
            answers = ModelFactory.create_sample_answers(question_type, num_options)
        
        # Generate tags if not provided
        if not tags:
            sample_tags = ["general", "programming", "science", "math", "geography", "history"]
            num_tags = random.randint(1, 3)
            tags = random.sample(sample_tags, num_tags)
        
        return Question(
            question_text=question_text,
            question_type=question_type,
            answers=answers,
            tags=tags,
            question_id=question_id
        )
    
    @staticmethod
    def create_tag(
        name: Optional[str] = None,
        description: Optional[str] = None,
        color: Optional[str] = None,
        tag_id: Optional[str] = None
    ) -> Tag:
        """
        Create a Tag instance with sample data.
        
        Args:
            name: Tag name (generated if not provided)
            description: Tag description (generated if not provided)
            color: Tag color (generated if not provided)
            tag_id: Tag ID (generated if not provided)
            
        Returns:
            Tag instance
        """
        # Generate tag name if not provided
        if not name:
            tag_names = [
                "programming", "science", "math", "geography", "history",
                "literature", "art", "music", "sports", "technology",
                "biology", "chemistry", "physics", "computer-science"
            ]
            name = random.choice(tag_names)
        
        # Generate description if not provided
        if not description:
            descriptions = {
                "programming": "Programming and software development questions",
                "science": "General science questions",
                "math": "Mathematics and arithmetic questions",
                "geography": "Geography and world knowledge questions",
                "history": "Historical facts and events",
                "literature": "Literature and language questions",
                "art": "Art and creative questions",
                "music": "Music theory and history",
                "sports": "Sports and athletics",
                "technology": "Technology and innovation",
                "biology": "Biology and life sciences",
                "chemistry": "Chemistry and chemical processes",
                "physics": "Physics and natural laws",
                "computer-science": "Computer science concepts"
            }
            description = descriptions.get(name, f"Questions related to {name}")
        
        # Generate color if not provided
        if not color:
            colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF", "#FFA500", "#800080"]
            color = random.choice(colors)
        
        return Tag(
            name=name,
            description=description,
            color=color,
            tag_id=tag_id
        )
    
    @staticmethod
    def create_quiz_session(
        questions: Optional[List[Dict[str, Any]]] = None,
        session_id: Optional[str] = None,
        num_questions: int = 5
    ) -> QuizSession:
        """
        Create a QuizSession instance with sample data.
        
        Args:
            questions: List of questions (generated if not provided)
            session_id: Session ID (generated if not provided)
            num_questions: Number of questions to generate if not provided
            
        Returns:
            QuizSession instance
        """
        # Generate questions if not provided
        if not questions:
            questions = []
            for _ in range(num_questions):
                question = ModelFactory.create_question()
                questions.append(question.to_dict())
        
        return QuizSession(
            questions=questions,
            session_id=session_id
        )
    
    @staticmethod
    def create_question_bank(num_questions: int = 20) -> List[Question]:
        """
        Create a bank of sample questions for testing.
        
        Args:
            num_questions: Number of questions to create
            
        Returns:
            List of Question instances
        """
        questions = []
        
        for i in range(num_questions):
            question = ModelFactory.create_question()
            questions.append(question)
        
        return questions
    
    @staticmethod
    def create_tag_collection(num_tags: int = 10) -> List[Tag]:
        """
        Create a collection of sample tags for testing.
        
        Args:
            num_tags: Number of tags to create
            
        Returns:
            List of Tag instances
        """
        tags = []
        used_names = set()
        
        for _ in range(num_tags):
            # Ensure unique tag names
            while True:
                tag = ModelFactory.create_tag()
                if tag.name not in used_names:
                    used_names.add(tag.name)
                    tags.append(tag)
                    break
        
        return tags
    
    @staticmethod
    def create_completed_quiz_session(
        num_questions: int = 5,
        score_percentage: float = 75.0
    ) -> QuizSession:
        """
        Create a completed quiz session with specified score.
        
        Args:
            num_questions: Number of questions in the quiz
            score_percentage: Target score percentage
            
        Returns:
            Completed QuizSession instance
        """
        # Create questions
        questions = []
        for _ in range(num_questions):
            question = ModelFactory.create_question()
            questions.append(question.to_dict())
        
        # Create session
        session = QuizSession(questions=questions)
        
        # Add answers to achieve target score
        target_correct = int((score_percentage / 100) * num_questions)
        correct_count = 0
        
        for i, question_dict in enumerate(questions):
            question = Question.from_dict(question_dict)
            correct_answers = question.get_correct_answers()
            
            # Determine if this answer should be correct
            should_be_correct = correct_count < target_correct
            
            if should_be_correct:
                # Select correct answer
                selected_answer = correct_answers[0] if correct_answers else "answer_1"
                is_correct = True
                correct_count += 1
            else:
                # Select incorrect answer
                all_answers = [answer['id'] for answer in question.answers]
                incorrect_answers = [aid for aid in all_answers if aid not in correct_answers]
                selected_answer = incorrect_answers[0] if incorrect_answers else "answer_1"
                is_correct = False
            
            session.add_answer(question.id, selected_answer, is_correct)
        
        return session
    
    @staticmethod
    def create_random_string(length: int = 10) -> str:
        """
        Create a random string for testing.
        
        Args:
            length: Length of the string
            
        Returns:
            Random string
        """
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    @staticmethod
    def create_sample_question_data() -> Dict[str, Any]:
        """
        Create sample question data for testing serialization.
        
        Returns:
            Dictionary with sample question data
        """
        return {
            "id": str(uuid.uuid4()),
            "question_text": "What is the capital of France?",
            "question_type": "multiple_choice",
            "answers": [
                {"id": "answer_1", "text": "Paris", "is_correct": True},
                {"id": "answer_2", "text": "London", "is_correct": False},
                {"id": "answer_3", "text": "Berlin", "is_correct": False},
                {"id": "answer_4", "text": "Madrid", "is_correct": False}
            ],
            "tags": ["geography", "europe"],
            "created_at": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "usage_count": 0
        }
    
    @staticmethod
    def create_sample_tag_data() -> Dict[str, Any]:
        """
        Create sample tag data for testing serialization.
        
        Returns:
            Dictionary with sample tag data
        """
        return {
            "id": str(uuid.uuid4()),
            "name": "geography",
            "description": "Geography and world knowledge questions",
            "color": "#00FF00",
            "question_count": 5,
            "created_at": datetime.now().isoformat(),
            "created_by": "system"
        }
