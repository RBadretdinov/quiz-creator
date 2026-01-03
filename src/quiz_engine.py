"""
Quiz Engine Module

This module contains the core quiz logic including question randomization,
answer validation, scoring calculation, and quiz session management.
Enhanced with Phase 1.4 features: partial credit, session recovery, analytics, and export.
"""

import random
import uuid
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import logging

from question_scorer import QuestionScorer

logger = logging.getLogger(__name__)

class QuizEngine:
    """Core quiz engine for managing quiz sessions and logic."""
    
    def __init__(self, session_storage_path: str = "data/quiz_sessions.json"):
        """Initialize the quiz engine with session persistence."""
        self.active_sessions: Dict[str, Dict] = {}
        self.session_storage_path = session_storage_path
        self.question_scorer = QuestionScorer()
        self.analytics_data: Dict[str, Any] = {
            'total_quizzes_taken': 0,
            'average_score': 0.0,
            'average_completion_time': 0.0,
            'question_difficulty_stats': {},
            'user_performance_history': []
        }
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(session_storage_path), exist_ok=True)
        
        # Load existing sessions and analytics
        self._load_sessions()
        self._load_analytics()
        
        logger.info("Quiz engine initialized with session persistence and analytics")
    
    def randomize_questions(self, questions: List[Dict]) -> List[Dict]:
        """
        Randomize the order of questions using Fisher-Yates shuffle.
        
        Args:
            questions: List of question dictionaries
            
        Returns:
            List of questions in randomized order
        """
        if not questions:
            return []
        
        return self._fisher_yates_shuffle(questions)
    
    def _fisher_yates_shuffle(self, questions: List[Dict]) -> List[Dict]:
        """Standard Fisher-Yates shuffle implementation."""
        randomized = questions.copy()
        random.shuffle(randomized)
        logger.debug(f"Fisher-Yates shuffled {len(randomized)} questions")
        return randomized
    
    
    def randomize_answers(self, question: Dict) -> Dict:
        """
        Randomize the order of answer options for a question.
        
        Args:
            question: Question dictionary with answers array
            
        Returns:
            Question with randomized answer order
        """
        if 'answers' not in question or not question['answers']:
            return question
        
        question_copy = question.copy()
        answers = question_copy['answers'].copy()
        random.shuffle(answers)
        question_copy['answers'] = answers
        
        logger.debug(f"Randomized answers for question: {question.get('id', 'unknown')}")
        return question_copy
    
    def create_randomized_quiz(self, question_bank: List[Dict], question_count: int) -> List[Dict]:
        """
        Create a new quiz with randomized questions and answers.
        
        Args:
            question_bank: Source questions
            question_count: Number of questions to include
            
        Returns:
            List of randomized questions with randomized answers
        """
        if not question_bank:
            return []
        
        # Select random questions
        selected_questions = random.sample(question_bank, min(question_count, len(question_bank)))
        
        # Randomize question order
        randomized_questions = self.randomize_questions(selected_questions)
        
        # Randomize answers for each question
        final_quiz = [self.randomize_answers(q) for q in randomized_questions]
        
        logger.info(f"Created randomized quiz with {len(final_quiz)} questions")
        return final_quiz
    
    def start_quiz(self, questions: List[Dict], resume_session_id: Optional[str] = None) -> str:
        """
        Initialize a new quiz session or resume an existing one.
        
        Args:
            questions: List of questions for the quiz
            resume_session_id: Optional session ID to resume
            
        Returns:
            Session ID for the quiz session
        """
        if resume_session_id and resume_session_id in self.active_sessions:
            logger.info(f"Resuming quiz session: {resume_session_id}")
            return resume_session_id
        
        # Validate questions list
        if not questions or len(questions) == 0:
            logger.error("Cannot start quiz with empty questions list")
            return None
        
        session_id = str(uuid.uuid4())
        
        session = {
            'id': session_id,
            'questions': questions,
            'current_question_index': 0,
            'answers': [],
            'score': 0,
            'start_time': datetime.now(),
            'end_time': None,
            'is_complete': False,
            'is_paused': False,
            'pause_count': 0,
            'total_pause_time': timedelta(0),
            'last_activity': datetime.now(),
            'metadata': {
                'question_count': len(questions),
                'tags_used': self._extract_tags_from_questions(questions)
            }
        }
        
        self.active_sessions[session_id] = session
        self._save_session(session)
        logger.info(f"Started new quiz session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Get a quiz session by ID.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session dictionary or None if not found
        """
        return self.active_sessions.get(session_id)
    
    def pause_quiz(self, session_id: str) -> bool:
        """
        Pause an active quiz session.
        
        Args:
            session_id: Session to pause
            
        Returns:
            True if successfully paused
        """
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        if session['is_complete'] or session['is_paused']:
            return False
        
        session['is_paused'] = True
        session['pause_start_time'] = datetime.now()
        session['pause_count'] += 1
        
        self._save_session(session)
        logger.info(f"Paused quiz session: {session_id}")
        return True
    
    def resume_quiz(self, session_id: str) -> bool:
        """
        Resume a paused quiz session.
        
        Args:
            session_id: Session to resume
            
        Returns:
            True if successfully resumed
        """
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        if not session['is_paused']:
            return False
        
        # Calculate pause duration
        if 'pause_start_time' in session:
            pause_duration = datetime.now() - session['pause_start_time']
            session['total_pause_time'] += pause_duration
            del session['pause_start_time']
        
        session['is_paused'] = False
        session['last_activity'] = datetime.now()
        
        self._save_session(session)
        logger.info(f"Resumed quiz session: {session_id}")
        return True
    
    def get_available_sessions(self) -> List[Dict]:
        """
        Get list of sessions that can be resumed.
        
        Returns:
            List of session metadata
        """
        available = []
        for session_id, session in self.active_sessions.items():
            if not session['is_complete']:
                available.append({
                    'id': session_id,
                    'progress': session['current_question_index'] / len(session['questions']),
                    'start_time': session['start_time'],
                    'is_paused': session['is_paused'],
                    'question_count': len(session['questions'])
                })
        return available
    
    def submit_answer(self, session_id: str, question_id: str, selected_answers: Any) -> Dict:
        """
        Process user's answer submission with enhanced validation and partial credit.
        
        Args:
            session_id: Unique session identifier
            question_id: Question being answered
            selected_answers: User's selected answer(s)
            
        Returns:
            Answer result with correctness, partial credit, and detailed feedback
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        question = self._find_question_by_id(session['questions'], question_id)
        
        if not question:
            raise ValueError(f"Question {question_id} not found")
        
        # Convert answer IDs to indices if needed
        answer_indices = self._convert_answers_to_indices(question, selected_answers)
        
        # Use new scoring system
        scoring_result = self.question_scorer.calculate_score(
            question['question_type'],
            question['answers'],
            answer_indices
        )
        
        # Record answer with detailed information
        answer_record = {
            'question_id': question_id,
            'selected_answers': selected_answers,
            'is_correct': scoring_result['is_correct'],
            'partial_credit': scoring_result.get('details', {}).get('partial_credit', 0),
            'score_earned': scoring_result['points_earned'],
            'max_points': scoring_result['max_points'],
            'feedback': scoring_result['feedback'],
            'timestamp': datetime.now(),
            'response_time': self._calculate_response_time(session, question_id),
            'validation_details': scoring_result.get('details', {})
        }
        
        session['answers'].append(answer_record)
        session['last_activity'] = datetime.now()
        
        # Update analytics
        self._update_question_analytics(question_id, scoring_result)
        
        # Move to next question
        session['current_question_index'] += 1
        
        # Check if quiz is complete
        if session['current_question_index'] >= len(session['questions']):
            session['is_complete'] = True
            session['end_time'] = datetime.now()
            score_info = self.calculate_score(session)
            session['score'] = score_info['percentage']  # Store percentage as float for backward compatibility
            self._update_session_analytics(session)
        
        # Save session state
        self._save_session(session)
        
        logger.debug(f"Answer submitted for session {session_id}, question {question_id}")
        
        # Format feedback message to match test expectations
        feedback = scoring_result['feedback']
        if scoring_result['is_correct']:
            feedback = "Correct! Well done!"
        else:
            # Get correct answer text(s)
            correct_answer_texts = []
            for answer in question.get('answers', []):
                if answer.get('is_correct'):
                    correct_answer_texts.append(answer.get('text', answer.get('id', '')))
            
            if correct_answer_texts:
                if len(correct_answer_texts) == 1:
                    feedback = f"Incorrect. The correct answer is {correct_answer_texts[0]}."
                else:
                    feedback = f"Incorrect. The correct answers are {', '.join(correct_answer_texts)}."
            else:
                feedback = "Incorrect."
        
        return {
            'is_correct': scoring_result['is_correct'],
            'partial_credit': scoring_result.get('details', {}).get('partial_credit', 0),
            'score_earned': scoring_result['points_earned'],
            'max_points': scoring_result['max_points'],
            'correct_answers': self._get_correct_answers(question),
            'feedback': feedback,
            'explanation': question.get('explanation', ''),
            'response_time': answer_record['response_time']
        }
    
    def calculate_score(self, session: Dict) -> Dict[str, Any]:
        """
        Calculate comprehensive quiz score and statistics.
        
        Args:
            session: Completed quiz session
            
        Returns:
            Detailed score information including partial credit
        """
        if not session['answers']:
            return {
                'total_score': 0.0,
                'percentage': 0.0,
                'correct_count': 0,
                'total_questions': 0,
                'partial_credit_earned': 0.0,
                'average_response_time': 0.0,
                'difficulty_breakdown': {}
            }
        
        total_score = 0.0
        correct_count = 0
        total_response_time = 0.0
        
        for answer in session['answers']:
            # Add score earned (including partial credit)
            total_score += answer.get('score_earned', 1.0 if answer['is_correct'] else 0.0)
            
            if answer['is_correct']:
                correct_count += 1
            
            # Track response time
            if 'response_time' in answer:
                total_response_time += answer['response_time']
        
        total_questions = len(session['answers'])
        percentage = (total_score / total_questions) * 100 if total_questions > 0 else 0.0
        average_response_time = total_response_time / total_questions if total_questions > 0 else 0.0
        
        # Calculate completion time
        completion_time = None
        if session.get('end_time') and session.get('start_time'):
            completion_time = session['end_time'] - session['start_time'] - session.get('total_pause_time', timedelta(0))
        
        score_info = {
            'total_score': total_score,
            'percentage': percentage,
            'correct_count': correct_count,
            'total_questions': total_questions,
            'partial_credit_earned': total_score - correct_count,
            'average_response_time': average_response_time,
            'completion_time': completion_time,
            'pause_count': session.get('pause_count', 0),
            'total_pause_time': session.get('total_pause_time', timedelta(0))
        }
        
        logger.info(f"Calculated comprehensive score: {percentage:.1f}% ({correct_count}/{total_questions})")
        return score_info
    
    def _find_question_by_id(self, questions: List[Dict], question_id: str) -> Optional[Dict]:
        """Find a question by its ID."""
        for question in questions:
            if question.get('id') == question_id:
                return question
        return None
    
    def _convert_answers_to_indices(self, question: Dict, selected_answers: Any) -> List[int]:
        """
        Convert answer IDs to indices (0-based) for scoring.
        
        Args:
            question: Question dictionary with answers
            selected_answers: Answer ID(s) or list of answer IDs
            
        Returns:
            List of 0-based indices
        """
        # If already a list of integers, return as-is
        if isinstance(selected_answers, list) and all(isinstance(x, int) for x in selected_answers):
            return selected_answers
        
        # Convert single value to list
        if not isinstance(selected_answers, list):
            selected_answers = [selected_answers]
        
        # Create mapping from answer ID to index
        answer_map = {}
        for i, answer in enumerate(question.get('answers', [])):
            answer_id = answer.get('id')
            if answer_id:
                answer_map[answer_id] = i
        
        # Convert answer IDs to indices
        indices = []
        for answer_id in selected_answers:
            if isinstance(answer_id, int):
                indices.append(answer_id)
            elif answer_id in answer_map:
                indices.append(answer_map[answer_id])
        
        return indices
    
    def _validate_answer(self, question: Dict, selected_answers: Any) -> bool:
        """Validate user's answer against correct answers."""
        correct_answers = self._get_correct_answers(question)
        
        if question.get('question_type') == 'select_all':
            # For select all questions, check if all correct answers are selected
            return set(selected_answers) == set(correct_answers)
        else:
            # For single choice questions
            return selected_answers in correct_answers
    
    def _get_correct_answers(self, question: Dict) -> List[str]:
        """Get list of correct answer IDs for a question."""
        correct_answers = []
        for answer in question.get('answers', []):
            if answer.get('is_correct'):
                correct_answers.append(answer.get('id'))
        return correct_answers
    
    def _generate_feedback(self, is_correct: bool) -> str:
        """Generate immediate feedback for user answers."""
        if is_correct:
            return "Correct! Well done!"
        else:
            return "Incorrect. The correct answer has been highlighted."
    
    def _validate_answer_enhanced(self, question: Dict, selected_answers: Any) -> Dict[str, Any]:
        """Enhanced answer validation with partial credit support."""
        question_type = question.get('question_type', 'multiple_choice')
        correct_answers = self._get_correct_answers(question)
        
        if question_type == 'select_all':
            return self._validate_select_all_answer(question, selected_answers, correct_answers)
        elif question_type == 'true_false':
            return self._validate_true_false_answer(question, selected_answers, correct_answers)
        else:
            return self._validate_multiple_choice_answer(question, selected_answers, correct_answers)
    
    def _validate_select_all_answer(self, question: Dict, selected_answers: List[str], correct_answers: List[str]) -> Dict[str, Any]:
        """Validate select-all-that-apply questions with partial credit."""
        if not isinstance(selected_answers, list):
            selected_answers = [selected_answers]
        
        selected_set = set(selected_answers)
        correct_set = set(correct_answers)
        
        # Calculate partial credit
        correct_selections = len(selected_set & correct_set)
        incorrect_selections = len(selected_set - correct_set)
        missed_selections = len(correct_set - selected_set)
        
        total_correct = len(correct_set)
        
        # Partial credit calculation
        if correct_selections == total_correct and incorrect_selections == 0:
            # Perfect answer
            is_correct = True
            partial_credit = 0.0
            score_earned = 1.0
            feedback = "Perfect! You selected all correct answers."
        elif correct_selections > 0 and incorrect_selections == 0:
            # Partial credit for correct selections only
            is_correct = False
            partial_credit = correct_selections / total_correct
            score_earned = partial_credit
            feedback = f"Partial credit! You got {correct_selections}/{total_correct} correct answers."
        elif correct_selections > 0:
            # Some correct, some incorrect
            is_correct = False
            partial_credit = max(0, (correct_selections - incorrect_selections) / total_correct)
            score_earned = partial_credit
            feedback = f"Mixed results. {correct_selections} correct, {incorrect_selections} incorrect."
        else:
            # All incorrect
            is_correct = False
            partial_credit = 0.0
            score_earned = 0.0
            feedback = "Incorrect. None of your selections were correct."
        
        return {
            'is_correct': is_correct,
            'partial_credit': partial_credit,
            'score_earned': score_earned,
            'feedback': feedback,
            'details': {
                'correct_selections': correct_selections,
                'incorrect_selections': incorrect_selections,
                'missed_selections': missed_selections,
                'total_correct': total_correct
            }
        }
    
    def _validate_true_false_answer(self, question: Dict, selected_answer: str, correct_answers: List[str]) -> Dict[str, Any]:
        """Validate true/false questions."""
        is_correct = selected_answer in correct_answers
        score_earned = 1.0 if is_correct else 0.0
        
        feedback = "Correct!" if is_correct else "Incorrect."
        
        return {
            'is_correct': is_correct,
            'partial_credit': 0.0,
            'score_earned': score_earned,
            'feedback': feedback,
            'details': {'selected': selected_answer, 'correct': correct_answers[0]}
        }
    
    def _validate_multiple_choice_answer(self, question: Dict, selected_answer: str, correct_answers: List[str]) -> Dict[str, Any]:
        """Validate multiple choice questions."""
        is_correct = selected_answer in correct_answers
        score_earned = 1.0 if is_correct else 0.0
        
        feedback = "Correct!" if is_correct else "Incorrect."
        
        return {
            'is_correct': is_correct,
            'partial_credit': 0.0,
            'score_earned': score_earned,
            'feedback': feedback,
            'details': {'selected': selected_answer, 'correct': correct_answers}
        }
    
    def _calculate_response_time(self, session: Dict, question_id: str) -> float:
        """Calculate response time for a question (simplified implementation)."""
        # In a real implementation, you'd track when the question was displayed
        # For now, return a random response time for demonstration
        import random
        return random.uniform(5.0, 30.0)  # 5-30 seconds
    
    def _update_question_analytics(self, question_id: str, validation_result: Dict[str, Any]):
        """Update analytics for individual questions."""
        if question_id not in self.analytics_data['question_difficulty_stats']:
            self.analytics_data['question_difficulty_stats'][question_id] = {
                'total_attempts': 0,
                'correct_attempts': 0,
                'accuracy': 0.0,
                'average_score': 0.0,
                'response_times': []
            }
        
        stats = self.analytics_data['question_difficulty_stats'][question_id]
        stats['total_attempts'] += 1
        if validation_result['is_correct']:
            stats['correct_attempts'] += 1
        
        stats['accuracy'] = stats['correct_attempts'] / stats['total_attempts']
        stats['average_score'] = (stats['average_score'] * (stats['total_attempts'] - 1) + validation_result['points_earned']) / stats['total_attempts']
        
        if 'response_time' in validation_result:
            stats['response_times'].append(validation_result['response_time'])
            # Keep only last 100 response times
            if len(stats['response_times']) > 100:
                stats['response_times'] = stats['response_times'][-100:]
    
    def _update_session_analytics(self, session: Dict):
        """Update overall session analytics."""
        self.analytics_data['total_quizzes_taken'] += 1
        
        # Get score (handle both float and dict formats)
        if isinstance(session.get('score'), dict):
            new_score = session['score']['percentage']
        else:
            new_score = session.get('score', 0.0)
        
        # Update average score
        current_avg = self.analytics_data['average_score']
        total_quizzes = self.analytics_data['total_quizzes_taken']
        self.analytics_data['average_score'] = (current_avg * (total_quizzes - 1) + new_score) / total_quizzes
        
        # Calculate completion time from session
        completion_time_seconds = None
        if session.get('end_time') and session.get('start_time'):
            completion_time = session['end_time'] - session['start_time'] - session.get('total_pause_time', timedelta(0))
            completion_time_seconds = completion_time.total_seconds()
            
            # Update average completion time
            current_avg_time = self.analytics_data['average_completion_time']
            self.analytics_data['average_completion_time'] = (current_avg_time * (total_quizzes - 1) + completion_time_seconds) / total_quizzes
        
        # Store session in performance history
        self.analytics_data['user_performance_history'].append({
            'session_id': session['id'],
            'score': new_score,
            'completion_time': completion_time_seconds,
            'timestamp': session['end_time'],
            'question_count': len(session['questions'])
        })
        
        # Keep only last 100 sessions in history
        if len(self.analytics_data['user_performance_history']) > 100:
            self.analytics_data['user_performance_history'] = self.analytics_data['user_performance_history'][-100:]
    
    
    def _extract_tags_from_questions(self, questions: List[Dict]) -> List[str]:
        """Extract all unique tags from questions."""
        tags = set()
        for question in questions:
            question_tags = question.get('tags', [])
            if isinstance(question_tags, list):
                tags.update(question_tags)
        return list(tags)
    
    def _save_session(self, session: Dict):
        """Save session to persistent storage."""
        try:
            # Convert datetime objects to strings for JSON serialization
            session_copy = session.copy()
            
            # Handle datetime fields
            datetime_fields = ['start_time', 'end_time', 'last_activity', 'pause_start_time']
            for field in datetime_fields:
                if field in session_copy and session_copy[field] is not None:
                    if isinstance(session_copy[field], datetime):
                        session_copy[field] = session_copy[field].isoformat()
            
            # Convert timedelta to seconds
            if 'total_pause_time' in session_copy and isinstance(session_copy['total_pause_time'], timedelta):
                session_copy['total_pause_time'] = session_copy['total_pause_time'].total_seconds()
            
            # Handle score field which might contain timedelta objects
            if 'score' in session_copy and isinstance(session_copy['score'], dict):
                score_copy = session_copy['score'].copy()
                if 'completion_time' in score_copy and isinstance(score_copy['completion_time'], timedelta):
                    score_copy['completion_time'] = score_copy['completion_time'].total_seconds()
                if 'total_pause_time' in score_copy and isinstance(score_copy['total_pause_time'], timedelta):
                    score_copy['total_pause_time'] = score_copy['total_pause_time'].total_seconds()
                session_copy['score'] = score_copy
            
            # Convert answer timestamps
            for answer in session_copy.get('answers', []):
                if 'timestamp' in answer and answer['timestamp'] is not None:
                    if isinstance(answer['timestamp'], datetime):
                        answer['timestamp'] = answer['timestamp'].isoformat()
            
            # Load existing sessions
            sessions = self._load_sessions_data()
            sessions[session['id']] = session_copy
            
            # Save to file
            with open(self.session_storage_path, 'w') as f:
                json.dump(sessions, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save session {session['id']}: {e}")
    
    def _load_sessions(self):
        """Load sessions from persistent storage."""
        try:
            sessions_data = self._load_sessions_data()
            for session_id, session_data in sessions_data.items():
                # Convert string timestamps back to datetime objects
                datetime_fields = ['start_time', 'end_time', 'last_activity', 'pause_start_time']
                for field in datetime_fields:
                    if field in session_data and session_data[field] is not None:
                        if isinstance(session_data[field], str):
                            session_data[field] = datetime.fromisoformat(session_data[field])
                
                # Convert pause time back to timedelta
                if 'total_pause_time' in session_data and isinstance(session_data['total_pause_time'], (int, float)):
                    session_data['total_pause_time'] = timedelta(seconds=session_data['total_pause_time'])
                
                # Handle score field which might contain timedelta objects
                if 'score' in session_data and isinstance(session_data['score'], dict):
                    score_data = session_data['score']
                    if 'completion_time' in score_data and isinstance(score_data['completion_time'], (int, float)):
                        score_data['completion_time'] = timedelta(seconds=score_data['completion_time'])
                    if 'total_pause_time' in score_data and isinstance(score_data['total_pause_time'], (int, float)):
                        score_data['total_pause_time'] = timedelta(seconds=score_data['total_pause_time'])
                
                # Convert answer timestamps
                for answer in session_data.get('answers', []):
                    if 'timestamp' in answer and answer['timestamp'] is not None:
                        if isinstance(answer['timestamp'], str):
                            answer['timestamp'] = datetime.fromisoformat(answer['timestamp'])
                
                self.active_sessions[session_id] = session_data
                
        except Exception as e:
            logger.error(f"Failed to load sessions: {e}")
    
    def _load_sessions_data(self) -> Dict:
        """Load raw sessions data from file."""
        try:
            if os.path.exists(self.session_storage_path):
                with open(self.session_storage_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load sessions data: {e}")
        return {}
    
    def _load_analytics(self):
        """Load analytics data from persistent storage."""
        try:
            analytics_path = "data/analytics.json"
            if os.path.exists(analytics_path):
                with open(analytics_path, 'r') as f:
                    self.analytics_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load analytics: {e}")
    
    def _save_analytics(self):
        """Save analytics data to persistent storage."""
        try:
            analytics_path = "data/analytics.json"
            os.makedirs(os.path.dirname(analytics_path), exist_ok=True)
            
            # Convert datetime objects to strings
            analytics_copy = self.analytics_data.copy()
            for session in analytics_copy.get('user_performance_history', []):
                if 'timestamp' in session and session['timestamp'] is not None:
                    if isinstance(session['timestamp'], datetime):
                        session['timestamp'] = session['timestamp'].isoformat()
            
            with open(analytics_path, 'w') as f:
                json.dump(analytics_copy, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save analytics: {e}")
    
    def get_quiz_statistics(self) -> Dict[str, Any]:
        """Get comprehensive quiz statistics and analytics."""
        self._save_analytics()  # Save current analytics
        return self.analytics_data.copy()
    
    def export_quiz_session(self, session_id: str, format: str = "json") -> str:
        """
        Export quiz session data in various formats.
        
        Args:
            session_id: Session to export
            format: Export format ("json", "csv", "html")
            
        Returns:
            Exported data as string
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        
        if format == "json":
            return json.dumps(session, indent=2, default=str)
        elif format == "csv":
            return self._export_session_csv(session)
        elif format == "html":
            return self._export_session_html(session)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_session_csv(self, session: Dict) -> str:
        """Export session as CSV format."""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Question ID', 'Selected Answer', 'Correct', 'Score Earned', 'Response Time'])
        
        # Write answer data
        for answer in session.get('answers', []):
            writer.writerow([
                answer.get('question_id', ''),
                str(answer.get('selected_answers', '')),
                answer.get('is_correct', False),
                answer.get('score_earned', 0.0),
                answer.get('response_time', 0.0)
            ])
        
        return output.getvalue()
    
    def _export_session_html(self, session: Dict) -> str:
        """Export session as HTML format."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Quiz Session Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .score {{ font-size: 24px; font-weight: bold; color: #2e7d32; }}
                .question {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .correct {{ background-color: #e8f5e8; }}
                .incorrect {{ background-color: #ffeaea; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Quiz Session Report</h1>
                <p><strong>Session ID:</strong> {session.get('id', 'N/A')}</p>
                <p><strong>Start Time:</strong> {session.get('start_time', 'N/A')}</p>
                <p><strong>End Time:</strong> {session.get('end_time', 'N/A')}</p>
                <div class="score">Score: {session.get('score', {}).get('percentage', 0):.1f}%</div>
            </div>
        """
        
        for answer in session.get('answers', []):
            css_class = "correct" if answer.get('is_correct') else "incorrect"
            html += f"""
            <div class="question {css_class}">
                <h3>Question: {answer.get('question_id', 'N/A')}</h3>
                <p><strong>Your Answer:</strong> {answer.get('selected_answers', 'N/A')}</p>
                <p><strong>Correct:</strong> {answer.get('is_correct', False)}</p>
                <p><strong>Score Earned:</strong> {answer.get('score_earned', 0.0)}</p>
                <p><strong>Response Time:</strong> {answer.get('response_time', 0.0):.1f} seconds</p>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html
