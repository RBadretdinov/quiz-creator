"""
Question Quality Analyzer

This module provides analysis and scoring of question quality,
including clarity, effectiveness, and improvement suggestions.
"""

from typing import List, Dict, Any, Optional, Tuple
import re
import logging

logger = logging.getLogger(__name__)

class QuestionQualityAnalyzer:
    """Analyzes question quality and provides improvement suggestions."""
    
    def __init__(self):
        """Initialize the quality analyzer."""
        self.quality_weights = {
            'clarity': 0.3,
            'difficulty_balance': 0.2,
            'answer_quality': 0.25,
            'tagging': 0.15,
            'structure': 0.1
        }
    
    def analyze_question_quality(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the quality of a question.
        
        Args:
            question: Question to analyze
            
        Returns:
            Quality analysis results
        """
        analysis = {
            'overall_score': 0.0,
            'scores': {},
            'suggestions': [],
            'strengths': [],
            'weaknesses': []
        }
        
        # Analyze different aspects
        clarity_score = self._analyze_clarity(question)
        difficulty_score = self._analyze_difficulty_balance(question)
        answer_score = self._analyze_answer_quality(question)
        tagging_score = self._analyze_tagging(question)
        structure_score = self._analyze_structure(question)
        
        # Store individual scores
        analysis['scores'] = {
            'clarity': clarity_score,
            'difficulty_balance': difficulty_score,
            'answer_quality': answer_score,
            'tagging': tagging_score,
            'structure': structure_score
        }
        
        # Calculate overall score
        overall_score = (
            clarity_score * self.quality_weights['clarity'] +
            difficulty_score * self.quality_weights['difficulty_balance'] +
            answer_score * self.quality_weights['answer_quality'] +
            tagging_score * self.quality_weights['tagging'] +
            structure_score * self.quality_weights['structure']
        )
        
        analysis['overall_score'] = round(overall_score, 2)
        
        # Generate suggestions and identify strengths/weaknesses
        analysis['suggestions'] = self._generate_suggestions(question, analysis['scores'])
        analysis['strengths'] = self._identify_strengths(analysis['scores'])
        analysis['weaknesses'] = self._identify_weaknesses(analysis['scores'])
        
        return analysis
    
    def _analyze_clarity(self, question: Dict[str, Any]) -> float:
        """Analyze question clarity."""
        score = 0.0
        question_text = question.get('question_text', '')
        
        # Length analysis (optimal: 20-100 characters)
        text_length = len(question_text)
        if 20 <= text_length <= 100:
            score += 0.3
        elif 10 <= text_length < 20 or 100 < text_length <= 150:
            score += 0.2
        else:
            score += 0.1
        
        # Grammar and punctuation
        if question_text.endswith('?'):
            score += 0.2
        else:
            score += 0.1
        
        # Check for common clarity issues
        clarity_issues = 0
        
        # Check for double negatives
        if re.search(r'\b(not|no|never|none|nothing)\b.*\b(not|no|never|none|nothing)\b', question_text.lower()):
            clarity_issues += 1
        
        # Check for ambiguous pronouns
        if re.search(r'\b(it|this|that|they|them)\b', question_text.lower()):
            clarity_issues += 1
        
        # Check for overly complex sentences
        if len(question_text.split('.')) > 2:
            clarity_issues += 1
        
        # Check for jargon or technical terms without context
        technical_terms = ['algorithm', 'paradigm', 'methodology', 'framework', 'architecture']
        if any(term in question_text.lower() for term in technical_terms):
            clarity_issues += 1
        
        # Deduct points for clarity issues
        clarity_penalty = min(clarity_issues * 0.1, 0.3)
        score += 0.3 - clarity_penalty
        
        return min(score, 1.0)
    
    def _analyze_difficulty_balance(self, question: Dict[str, Any]) -> float:
        """Analyze difficulty balance of the question."""
        score = 0.0
        answers = question.get('answers', [])
        question_type = question.get('question_type', '')
        
        if not answers:
            return 0.0
        
        # Analyze answer distribution
        correct_answers = [a for a in answers if a.get('is_correct', False)]
        incorrect_answers = [a for a in answers if not a.get('is_correct', False)]
        
        # Check for appropriate number of correct answers
        if question_type == 'multiple_choice' or question_type == 'true_false':
            if len(correct_answers) == 1:
                score += 0.4
            else:
                score += 0.1
        elif question_type == 'select_all':
            if 1 <= len(correct_answers) <= len(answers) - 1:
                score += 0.4
            else:
                score += 0.1
        
        # Analyze answer length balance
        answer_lengths = [len(a.get('text', '')) for a in answers]
        if answer_lengths:
            length_variance = max(answer_lengths) - min(answer_lengths)
            if length_variance <= 20:  # Balanced lengths
                score += 0.3
            elif length_variance <= 50:
                score += 0.2
            else:
                score += 0.1
        
        # Check for obviously wrong answers
        obviously_wrong = 0
        for answer in incorrect_answers:
            answer_text = answer.get('text', '').lower()
            if any(phrase in answer_text for phrase in ['none of the above', 'all of the above', 'cannot be determined']):
                obviously_wrong += 1
        
        if obviously_wrong == 0:
            score += 0.3
        elif obviously_wrong == 1:
            score += 0.2
        else:
            score += 0.1
        
        return min(score, 1.0)
    
    def _analyze_answer_quality(self, question: Dict[str, Any]) -> float:
        """Analyze the quality of answers."""
        score = 0.0
        answers = question.get('answers', [])
        
        if not answers:
            return 0.0
        
        # Check answer count
        answer_count = len(answers)
        if 3 <= answer_count <= 5:
            score += 0.3
        elif answer_count == 2 or answer_count == 6:
            score += 0.2
        else:
            score += 0.1
        
        # Analyze individual answer quality
        answer_scores = []
        for answer in answers:
            answer_score = 0.0
            answer_text = answer.get('text', '')
            
            # Length check (optimal: 10-50 characters)
            if 10 <= len(answer_text) <= 50:
                answer_score += 0.3
            elif 5 <= len(answer_text) < 10 or 50 < len(answer_text) <= 100:
                answer_score += 0.2
            else:
                answer_score += 0.1
            
            # Check for empty or very short answers
            if len(answer_text.strip()) < 3:
                answer_score = 0.0
            
            # Check for repetitive answers
            if answer_text.lower() in [a.get('text', '').lower() for a in answers if a != answer]:
                answer_score *= 0.5
            
            answer_scores.append(answer_score)
        
        # Average answer quality
        if answer_scores:
            avg_answer_score = sum(answer_scores) / len(answer_scores)
            score += avg_answer_score * 0.7
        
        return min(score, 1.0)
    
    def _analyze_tagging(self, question: Dict[str, Any]) -> float:
        """Analyze question tagging quality."""
        score = 0.0
        tags = question.get('tags', [])
        
        # Check tag count (optimal: 2-5 tags)
        tag_count = len(tags)
        if 2 <= tag_count <= 5:
            score += 0.4
        elif tag_count == 1 or 6 <= tag_count <= 8:
            score += 0.3
        elif tag_count == 0:
            score += 0.0
        else:
            score += 0.2
        
        # Check tag quality
        if tags:
            # Check for descriptive tags
            descriptive_tags = 0
            for tag in tags:
                if len(tag) >= 3 and not tag.isdigit():
                    descriptive_tags += 1
            
            if descriptive_tags >= len(tags) * 0.8:
                score += 0.3
            elif descriptive_tags >= len(tags) * 0.5:
                score += 0.2
            else:
                score += 0.1
            
            # Check for tag diversity
            unique_tag_words = set()
            for tag in tags:
                unique_tag_words.update(tag.lower().split())
            
            if len(unique_tag_words) >= len(tags):
                score += 0.3
            else:
                score += 0.2
        
        return min(score, 1.0)
    
    def _analyze_structure(self, question: Dict[str, Any]) -> float:
        """Analyze question structure."""
        score = 0.0
        question_text = question.get('question_text', '')
        question_type = question.get('question_type', '')
        
        # Check question format
        if question_type == 'true_false':
            if 'true' in question_text.lower() and 'false' in question_text.lower():
                score += 0.2
            else:
                score += 0.1
        else:
            score += 0.2
        
        # Check for proper capitalization
        if question_text and question_text[0].isupper():
            score += 0.2
        else:
            score += 0.1
        
        # Check for proper punctuation
        if question_text.endswith(('?', '.', '!')):
            score += 0.2
        else:
            score += 0.1
        
        # Check for consistent formatting
        if not re.search(r'[A-Z]{2,}', question_text):  # No excessive caps
            score += 0.2
        else:
            score += 0.1
        
        # Check for appropriate question type structure
        if question_type == 'select_all':
            if 'select all' in question_text.lower() or 'all that apply' in question_text.lower():
                score += 0.2
            else:
                score += 0.1
        else:
            score += 0.2
        
        return min(score, 1.0)
    
    def _generate_suggestions(self, question: Dict[str, Any], scores: Dict[str, float]) -> List[str]:
        """Generate improvement suggestions based on scores."""
        suggestions = []
        
        # Clarity suggestions
        if scores['clarity'] < 0.7:
            suggestions.append("Consider simplifying the question text for better clarity")
            if len(question.get('question_text', '')) > 100:
                suggestions.append("Question text is quite long - consider breaking it into shorter sentences")
            if not question.get('question_text', '').endswith('?'):
                suggestions.append("Add a question mark at the end of the question")
        
        # Difficulty balance suggestions
        if scores['difficulty_balance'] < 0.7:
            answers = question.get('answers', [])
            correct_count = sum(1 for a in answers if a.get('is_correct', False))
            
            if question.get('question_type') == 'multiple_choice' and correct_count != 1:
                suggestions.append("Multiple choice questions should have exactly one correct answer")
            elif question.get('question_type') == 'select_all' and correct_count == 0:
                suggestions.append("Select all questions should have at least one correct answer")
            
            # Check answer length balance
            answer_lengths = [len(a.get('text', '')) for a in answers]
            if answer_lengths and max(answer_lengths) - min(answer_lengths) > 50:
                suggestions.append("Consider balancing the length of answer options")
        
        # Answer quality suggestions
        if scores['answer_quality'] < 0.7:
            answers = question.get('answers', [])
            if len(answers) < 3:
                suggestions.append("Consider adding more answer options (3-5 is optimal)")
            elif len(answers) > 5:
                suggestions.append("Consider reducing the number of answer options")
            
            # Check for very short answers
            short_answers = [a for a in answers if len(a.get('text', '')) < 5]
            if short_answers:
                suggestions.append("Some answers are very short - consider making them more descriptive")
        
        # Tagging suggestions
        if scores['tagging'] < 0.7:
            tags = question.get('tags', [])
            if len(tags) < 2:
                suggestions.append("Add more descriptive tags to help categorize the question")
            elif len(tags) > 8:
                suggestions.append("Consider reducing the number of tags (2-5 is optimal)")
            
            # Check for non-descriptive tags
            if any(tag.isdigit() or len(tag) < 3 for tag in tags):
                suggestions.append("Use more descriptive tag names")
        
        # Structure suggestions
        if scores['structure'] < 0.7:
            question_text = question.get('question_text', '')
            if not question_text[0].isupper():
                suggestions.append("Start the question with a capital letter")
            if not question_text.endswith('?'):
                suggestions.append("End the question with a question mark")
            
            if question.get('question_type') == 'select_all':
                if 'select all' not in question_text.lower() and 'all that apply' not in question_text.lower():
                    suggestions.append("Consider adding 'Select all that apply' to the question text")
        
        return suggestions
    
    def _identify_strengths(self, scores: Dict[str, float]) -> List[str]:
        """Identify question strengths."""
        strengths = []
        
        if scores['clarity'] >= 0.8:
            strengths.append("Clear and well-written question text")
        
        if scores['difficulty_balance'] >= 0.8:
            strengths.append("Well-balanced difficulty with appropriate answer distribution")
        
        if scores['answer_quality'] >= 0.8:
            strengths.append("High-quality answer options")
        
        if scores['tagging'] >= 0.8:
            strengths.append("Excellent tagging and categorization")
        
        if scores['structure'] >= 0.8:
            strengths.append("Proper question structure and formatting")
        
        return strengths
    
    def _identify_weaknesses(self, scores: Dict[str, float]) -> List[str]:
        """Identify question weaknesses."""
        weaknesses = []
        
        if scores['clarity'] < 0.5:
            weaknesses.append("Question text needs improvement for clarity")
        
        if scores['difficulty_balance'] < 0.5:
            weaknesses.append("Answer distribution needs balancing")
        
        if scores['answer_quality'] < 0.5:
            weaknesses.append("Answer options need improvement")
        
        if scores['tagging'] < 0.5:
            weaknesses.append("Tagging needs improvement")
        
        if scores['structure'] < 0.5:
            weaknesses.append("Question structure needs improvement")
        
        return weaknesses
    
    def get_quality_grade(self, overall_score: float) -> str:
        """Convert numeric score to letter grade."""
        if overall_score >= 0.9:
            return 'A'
        elif overall_score >= 0.8:
            return 'B'
        elif overall_score >= 0.7:
            return 'C'
        elif overall_score >= 0.6:
            return 'D'
        else:
            return 'F'
    
    def analyze_question_bank_quality(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze the overall quality of a question bank.
        
        Args:
            questions: List of questions to analyze
            
        Returns:
            Question bank quality analysis
        """
        if not questions:
            return {'error': 'No questions provided'}
        
        analyses = []
        for question in questions:
            analysis = self.analyze_question_quality(question)
            analyses.append(analysis)
        
        # Calculate statistics
        overall_scores = [a['overall_score'] for a in analyses]
        avg_score = sum(overall_scores) / len(overall_scores)
        
        # Grade distribution
        grade_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
        for score in overall_scores:
            grade = self.get_quality_grade(score)
            grade_counts[grade] += 1
        
        # Component averages
        component_averages = {}
        for component in ['clarity', 'difficulty_balance', 'answer_quality', 'tagging', 'structure']:
            component_scores = [a['scores'][component] for a in analyses]
            component_averages[component] = sum(component_scores) / len(component_scores)
        
        # Common suggestions
        all_suggestions = []
        for analysis in analyses:
            all_suggestions.extend(analysis['suggestions'])
        
        # Count suggestion frequency
        suggestion_counts = {}
        for suggestion in all_suggestions:
            suggestion_counts[suggestion] = suggestion_counts.get(suggestion, 0) + 1
        
        # Get most common suggestions
        common_suggestions = sorted(suggestion_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_questions': len(questions),
            'average_quality_score': round(avg_score, 2),
            'grade_distribution': grade_counts,
            'component_averages': {k: round(v, 2) for k, v in component_averages.items()},
            'common_suggestions': common_suggestions,
            'high_quality_questions': len([s for s in overall_scores if s >= 0.8]),
            'low_quality_questions': len([s for s in overall_scores if s < 0.6])
        }
