"""
Question Type Interface

This module provides console-based interfaces for advanced question type
management, templates, and conversion tools.
"""

from typing import List, Dict, Any, Optional
import logging

from question_type_validator import QuestionTypeValidator
from question_scorer import QuestionScorer
from question_templates import QuestionTemplates
from question_type_converter import QuestionTypeConverter

logger = logging.getLogger(__name__)

class QuestionTypeInterface:
    """Console interface for advanced question type operations."""
    
    def __init__(self):
        """Initialize the question type interface."""
        self.validator = QuestionTypeValidator()
        self.scorer = QuestionScorer()
        self.templates = QuestionTemplates()
        self.converter = QuestionTypeConverter()
        self.logger = logging.getLogger(__name__)
    
    def display_question_type_menu(self) -> None:
        """Display the question type management menu."""
        print("\n" + "="*60)
        print("📝 QUESTION TYPE MANAGEMENT")
        print("="*60)
        print("1. View Question Types")
        print("2. Question Templates")
        print("3. Convert Question Type")
        print("4. Validate Question")
        print("5. Question Type Statistics")
        print("6. Scoring Information")
        print("0. Back to Main Menu")
        print("-"*60)
    
    def view_question_types(self) -> None:
        """Display information about all supported question types."""
        print("\n" + "="*60)
        print("📋 SUPPORTED QUESTION TYPES")
        print("="*60)
        
        type_info = self.validator.get_question_type_info()
        
        for question_type, info in type_info.items():
            print(f"\n🔹 {info['name'].upper()}")
            print(f"   Description: {info['description']}")
            print(f"   Min Answers: {info['min_answers']}")
            print(f"   Max Answers: {info['max_answers']}")
            print(f"   Correct Answers: {info['correct_answers']}")
            
            # Show scoring info
            scoring_info = self.scorer.get_scoring_info(question_type)
            print(f"   Scoring: {scoring_info['description']}")
            if scoring_info['partial_credit']:
                print(f"   Partial Credit: ✅ Yes")
            else:
                print(f"   Partial Credit: ❌ No")
    
    def display_templates_menu(self) -> None:
        """Display templates menu."""
        print("\n" + "="*60)
        print("📋 QUESTION TEMPLATES")
        print("="*60)
        print("1. View All Templates")
        print("2. View Template Examples")
        print("3. Subject-Specific Presets")
        print("4. Create from Template")
        print("0. Back")
        print("-"*60)
        
        choice = input("Select option: ").strip()
        
        if choice == '1':
            self._view_all_templates()
        elif choice == '2':
            self._view_template_examples()
        elif choice == '3':
            self._view_subject_presets()
        elif choice == '4':
            self._create_from_template()
        elif choice == '0':
            return
        else:
            print("❌ Invalid selection.")
    
    def _view_all_templates(self) -> None:
        """View all available templates."""
        print("\n" + "="*60)
        print("📋 ALL TEMPLATES")
        print("="*60)
        
        templates = self.templates.get_all_templates()
        
        for question_type, template_info in templates.items():
            print(f"\n🔹 {template_info['name']}")
            print(f"   Description: {template_info['description']}")
            print(f"   Sample Question: {template_info['template']['question_text']}")
            print(f"   Answer Options: {len(template_info['template']['answers'])}")
    
    def _view_template_examples(self) -> None:
        """View examples for a specific template."""
        print("\n" + "="*60)
        print("📋 TEMPLATE EXAMPLES")
        print("="*60)
        
        # Show available types
        templates = self.templates.get_all_templates()
        print("Available question types:")
        for i, question_type in enumerate(templates.keys(), 1):
            print(f"{i}. {templates[question_type]['name']}")
        
        try:
            choice = int(input("\nSelect question type (number): "))
            question_types = list(templates.keys())
            
            if 1 <= choice <= len(question_types):
                selected_type = question_types[choice - 1]
                examples = self.templates.get_examples(selected_type)
                
                print(f"\n📝 Examples for {templates[selected_type]['name']}:")
                print("-" * 50)
                
                for i, example in enumerate(examples, 1):
                    print(f"\nExample {i}:")
                    print(f"Question: {example['question_text']}")
                    print("Answers:")
                    for j, answer in enumerate(example['answers'], 1):
                        status = "✅" if answer['is_correct'] else "❌"
                        print(f"  {j}. {answer['text']} {status}")
            else:
                print("❌ Invalid selection.")
                
        except ValueError:
            print("❌ Invalid input.")
    
    def _view_subject_presets(self) -> None:
        """View subject-specific presets."""
        print("\n" + "="*60)
        print("📚 SUBJECT-SPECIFIC PRESETS")
        print("="*60)
        
        presets = self.templates.get_all_subject_presets()
        
        for subject, preset_info in presets.items():
            print(f"\n🔹 {preset_info['name']}")
            print(f"   Tags: {', '.join(preset_info['tags'])}")
            print(f"   Available Templates: {', '.join(preset_info['templates'].keys())}")
    
    def _create_from_template(self) -> None:
        """Create a question from a template."""
        print("\n" + "="*60)
        print("➕ CREATE FROM TEMPLATE")
        print("="*60)
        
        templates = self.templates.get_all_templates()
        print("Available templates:")
        for i, (question_type, template_info) in enumerate(templates.items(), 1):
            print(f"{i}. {template_info['name']}")
        
        try:
            choice = int(input("\nSelect template (number): "))
            question_types = list(templates.keys())
            
            if 1 <= choice <= len(question_types):
                selected_type = question_types[choice - 1]
                template = templates[selected_type]
                
                print(f"\n📝 Creating {template['name']} question:")
                print(f"Template: {template['template']['question_text']}")
                
                # Get custom question text
                custom_text = input("Enter your question text (or press Enter to use template): ").strip()
                if not custom_text:
                    custom_text = template['template']['question_text']
                
                # Show template answers
                print("\nTemplate answers:")
                for i, answer in enumerate(template['template']['answers'], 1):
                    status = "✅" if answer['is_correct'] else "❌"
                    print(f"  {i}. {answer['text']} {status}")
                
                print("\n✅ Question created from template!")
                print(f"Question: {custom_text}")
                print(f"Type: {selected_type}")
                print(f"Answers: {len(template['template']['answers'])} options")
                
            else:
                print("❌ Invalid selection.")
                
        except ValueError:
            print("❌ Invalid input.")
    
    def convert_question_type_interactive(self) -> None:
        """Interactive question type conversion."""
        print("\n" + "="*60)
        print("🔄 CONVERT QUESTION TYPE")
        print("="*60)
        
        # Get source question type
        print("Available question types:")
        type_info = self.validator.get_question_type_info()
        for i, (question_type, info) in enumerate(type_info.items(), 1):
            print(f"{i}. {info['name']}")
        
        try:
            source_choice = int(input("\nSelect source question type (number): "))
            question_types = list(type_info.keys())
            
            if 1 <= source_choice <= len(question_types):
                source_type = question_types[source_choice - 1]
                
                # Get conversion options
                conversion_options = self.converter.get_conversion_options(source_type)
                
                if not conversion_options:
                    print(f"❌ No conversion options available for {type_info[source_type]['name']}")
                    return
                
                print(f"\nConversion options for {type_info[source_type]['name']}:")
                for i, target_type in enumerate(conversion_options, 1):
                    target_info = type_info[target_type]
                    print(f"{i}. {target_info['name']}")
                
                target_choice = int(input("\nSelect target question type (number): "))
                
                if 1 <= target_choice <= len(conversion_options):
                    target_type = conversion_options[target_choice - 1]
                    
                    # Show conversion preview
                    print(f"\n🔄 Converting from {type_info[source_type]['name']} to {type_info[target_type]['name']}")
                    print("Note: This is a preview of the conversion process.")
                    print("In a real implementation, you would select an actual question to convert.")
                    
                else:
                    print("❌ Invalid target selection.")
            else:
                print("❌ Invalid source selection.")
                
        except ValueError:
            print("❌ Invalid input.")
    
    def validate_question_interactive(self) -> None:
        """Interactive question validation."""
        print("\n" + "="*60)
        print("✅ VALIDATE QUESTION")
        print("="*60)
        print("This feature validates question structure and provides improvement suggestions.")
        print("In a real implementation, you would input an actual question to validate.")
        
        # Show validation rules
        print("\n📋 Validation Rules:")
        type_info = self.validator.get_question_type_info()
        
        for question_type, info in type_info.items():
            print(f"\n{info['name']}:")
            print(f"  • {info['min_answers']}-{info['max_answers']} answers required")
            print(f"  • {info['correct_answers']} correct answer(s)")
            print(f"  • {info['description']}")
    
    def display_scoring_information(self) -> None:
        """Display scoring information for all question types."""
        print("\n" + "="*60)
        print("📊 SCORING INFORMATION")
        print("="*60)
        
        type_info = self.validator.get_question_type_info()
        
        for question_type, info in type_info.items():
            scoring_info = self.scorer.get_scoring_info(question_type)
            
            print(f"\n🔹 {info['name']}")
            print(f"   Max Points: {scoring_info['max_points']}")
            print(f"   Scoring Type: {scoring_info['scoring_type']}")
            print(f"   Partial Credit: {'Yes' if scoring_info['partial_credit'] else 'No'}")
            print(f"   Description: {scoring_info['description']}")
            
            if scoring_info['partial_credit']:
                print("   📝 Partial Credit Details:")
                print("      • Points awarded for each correct selection")
                print("      • Penalty for incorrect selections")
                print("      • Final score = (correct points) - (incorrect penalty)")
    
    def get_question_type_suggestions(self, subject: str = None) -> Dict[str, Any]:
        """
        Get suggestions for question types based on subject.
        
        Args:
            subject: Optional subject area
            
        Returns:
            Suggestions for question types
        """
        suggestions = {
            'recommended_types': [],
            'subject_specific': {},
            'general_tips': []
        }
        
        if subject:
            preset = self.templates.get_subject_preset(subject)
            if preset:
                suggestions['subject_specific'] = preset
                suggestions['recommended_types'] = list(preset['templates'].keys())
        
        # General recommendations
        suggestions['general_tips'] = [
            "Use multiple choice for factual knowledge",
            "Use true/false for simple statements",
            "Use select all for complex topics with multiple correct answers",
            "Consider question difficulty and learning objectives"
        ]
        
        return suggestions
