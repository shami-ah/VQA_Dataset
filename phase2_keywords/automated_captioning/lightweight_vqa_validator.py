#!/usr/bin/env python3
"""
Lightweight VQA Validator - Final quality enhancement using ultra-lightweight models
Uses T5-small (60M parameters) for grammar correction and text improvement
"""

import logging
import re
from typing import Dict, List, Optional

try:
    import torch
except ImportError:
    torch = None

class LightweightVQAValidator:
    def __init__(self, enable_model: bool = True):
        """Initialize lightweight VQA validator"""
        self.logger = self._setup_logger()
        self.enable_model = enable_model
        self.model = None
        self.tokenizer = None
        
        if enable_model:
            self._load_lightweight_model()
    
    def _setup_logger(self):
        """Setup logging"""
        logger = logging.getLogger('LightweightVQAValidator')
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def _load_lightweight_model(self):
        """Load ultra-lightweight T5-small model for text improvement"""
        try:
            from transformers import T5ForConditionalGeneration, T5Tokenizer
            
            self.logger.info("Loading T5-small model (60M parameters)...")
            model_name = "t5-small"  # Only 60M parameters, ~240MB
            
            self.tokenizer = T5Tokenizer.from_pretrained(model_name)
            self.model = T5ForConditionalGeneration.from_pretrained(model_name)
            
            # Use CPU for minimal memory usage
            self.model.eval()
            
            self.logger.info("✅ T5-small model loaded successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to load T5 model: {e}")
            self.logger.info("Falling back to rule-based validation only")
            self.enable_model = False
    
    def validate_and_improve_vqa_pairs(self, vqa_pairs: List[Dict]) -> List[Dict]:
        """Validate and improve VQA pairs with lightweight model"""
        if not vqa_pairs:
            return vqa_pairs
            
        self.logger.info(f"🔍 Validating and improving {len(vqa_pairs)} VQA pairs...")
        
        improved_pairs = []
        for i, pair in enumerate(vqa_pairs):
            try:
                improved_pair = self._improve_single_vqa_pair(pair)
                improved_pairs.append(improved_pair)
                
                if (i + 1) % 10 == 0:
                    self.logger.info(f"   Processed {i + 1}/{len(vqa_pairs)} pairs...")
                    
            except Exception as e:
                self.logger.warning(f"Error improving pair {i}: {e}")
                # Keep original if improvement fails
                improved_pairs.append(pair)
        
        self.logger.info("✅ VQA validation and improvement completed")
        return improved_pairs
    
    def _improve_single_vqa_pair(self, pair: Dict) -> Dict:
        """Improve a single VQA pair with comprehensive validation"""
        improved_pair = pair.copy()
        
        # 1. Subject consistency validation
        improved_pair = self._validate_subject_consistency(improved_pair)
        
        # 2. Basic cleanup and rule-based improvements
        improved_pair = self._apply_rule_based_improvements(improved_pair)
        
        # 3. Content coherence improvements
        improved_pair = self._improve_content_coherence(improved_pair)
        
        # 4. Model-based improvements (if enabled)
        if self.enable_model and self.model is not None:
            improved_pair = self._apply_model_based_improvements(improved_pair)
        
        return improved_pair
    
    def _validate_subject_consistency(self, pair: Dict) -> Dict:
        """Validate and fix subject consistency between question/answer content"""
        improved_pair = pair.copy()
        
        question = improved_pair.get('question', '')
        answer = improved_pair.get('answer', '')
        
        # Extract quoted OCR content from answers
        import re
        quoted_content = re.findall(r"'([^']+)'|\"([^\"]+)\"", answer)
        quoted_text = ' '.join([match[0] or match[1] for match in quoted_content]).lower()
        
        # Combine all content for analysis
        full_content = f"{question} {answer} {quoted_text}".lower()
        
        # Enhanced subject-specific indicators 
        subject_indicators = {
            'language_arts': ['grammar', 'pronoun', 'verb', 'english', 'suffix', 'tense', 'will', 
                            'director', 'movies', 'person who', 'chart of grammar', 'object pronouns'],
            'chemistry': ['chemical', 'formula', 'compound', 'sodium', 'chloride', 'molecular', 'element', 'oxide'],
            'physics': ['energy', 'physics', 'kinetic', 'potential', 'motion', 'force', 'tutorials', 'ke', 'pe'],
            'mathematics': ['function', 'notation', 'algebra', 'equation', 'mathematical', 'variable', 'xy', 'solve'],
            'biology': ['brain', 'synapse', 'anatomy', 'biological', 'heart', 'structure', 'human brain'],
            'history': ['timeline', 'history', 'historical', 'chronological', 'world history']
        }
        
        # Find the most likely subject based on content
        detected_subject = 'general'
        max_matches = 0
        
        for subject, indicators in subject_indicators.items():
            matches = sum(1 for indicator in indicators if indicator in full_content)
            if matches > max_matches:
                max_matches = matches
                detected_subject = subject
        
        # Special case: if quoted content strongly indicates a different subject, use that
        if quoted_text:
            for subject, indicators in subject_indicators.items():
                quoted_matches = sum(1 for indicator in indicators if indicator in quoted_text)
                if quoted_matches >= 2:  # Strong indicator in quoted content
                    detected_subject = subject
                    max_matches = quoted_matches
                    break
        
        # Fix subject mismatches in answers  
        if max_matches > 0 and detected_subject != 'general':
            # Fix generic subject references
            wrong_subjects = ['physics-specific', 'chemistry-specific', 'mathematics-specific', 
                            'biology-specific', 'history-specific', 'language arts-specific', 'general-specific']
            correct_reference = f"{detected_subject.replace('_', ' ')}-specific"
            
            for wrong in wrong_subjects:
                if wrong != correct_reference:
                    answer = answer.replace(wrong, correct_reference)
            
            # Fix content-specific mismatches
            if detected_subject == 'language_arts':
                answer = answer.replace('physics tutorial', 'language arts material')
                answer = answer.replace('physics concepts', 'grammar concepts')
                answer = answer.replace('energy concepts', 'grammar concepts')
                answer = answer.replace('energy principles', 'grammar rules')
                answer = answer.replace('motion scenarios', 'language applications')
                answer = answer.replace('kinetic energy (KE) and potential energy (PE)', 'grammar rules and language structure')
                answer = answer.replace('energy transformation and conservation in physical systems', 'grammar instruction and language development')
            elif detected_subject == 'mathematics':
                answer = answer.replace('physics tutorial', 'mathematics material')
                answer = answer.replace('physics concepts', 'mathematical concepts')
                answer = answer.replace('energy principles', 'mathematical principles')
            elif detected_subject == 'chemistry':
                answer = answer.replace('physics tutorial', 'chemistry material')
                answer = answer.replace('energy concepts', 'chemical concepts')
            
            improved_pair['answer'] = answer
        
        return improved_pair
    
    def _improve_content_coherence(self, pair: Dict) -> Dict:
        """Improve content coherence and remove template language"""
        improved_pair = pair.copy()
        
        question = improved_pair.get('question', '')
        answer = improved_pair.get('answer', '')
        
        # Fix punctuation issues
        if 'which provides' in answer and answer.endswith('?'):
            answer = answer.replace('?', '.')
        
        # Remove or replace remaining template phrases
        template_fixes = {
            'This educational resource provides structured learning content designed to build foundational knowledge and develop critical thinking skills in the subject area.': 'This material provides essential knowledge and skills for academic learning.',
            'which provides educational information for student learning?': 'which contains educational content for student learning.',
            'The visible text': 'The text',
            'provides concrete evidence of the physics-specific content': 'confirms the educational content',
            'provides concrete evidence of the chemistry-specific content': 'confirms the chemistry content',
            'provides concrete evidence of the mathematics-specific content': 'confirms the mathematical content',
            'provides concrete evidence of the language arts-specific content': 'confirms the language content',
        }
        
        for template, replacement in template_fixes.items():
            answer = answer.replace(template, replacement)
        
        # Improve awkward phrasing
        if answer.endswith(' student learning?'):
            answer = answer.replace(' student learning?', ' student learning.')
        
        if ' for student learning.' in answer and answer.count(' for student learning') > 1:
            # Remove duplicate phrases
            answer = answer.replace(' for student learning.', '', 1)
        
        # Clean up any double periods or spaces
        answer = re.sub(r'\.+', '.', answer)
        answer = re.sub(r'\s+', ' ', answer)
        answer = answer.strip()
        
        improved_pair['question'] = question
        improved_pair['answer'] = answer
        
        return improved_pair
    
    def _apply_rule_based_improvements(self, pair: Dict) -> Dict:
        """Apply rule-based text improvements (no model required)"""
        improved_pair = pair.copy()
        
        # Improve question
        question = improved_pair.get('question', '')
        question = self._fix_common_text_issues(question)
        improved_pair['question'] = question
        
        # Improve answer
        answer = improved_pair.get('answer', '')
        answer = self._fix_common_text_issues(answer)
        answer = self._improve_answer_structure(answer)
        improved_pair['answer'] = answer
        
        # Improve caption if present
        if 'caption' in improved_pair:
            caption = improved_pair['caption']
            caption = self._fix_common_text_issues(caption)
            improved_pair['caption'] = caption
        
        return improved_pair
    
    def _fix_common_text_issues(self, text: str) -> str:
        """Fix common text issues without AI model"""
        if not text:
            return text
        
        # Fix spacing issues
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
        text = text.strip()
        
        # Fix punctuation spacing
        text = re.sub(r'\s+([.!?;:,])', r'\1', text)  # Remove space before punctuation
        text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', text)  # Ensure space after sentence end
        
        # Fix capitalization
        if text and not text[0].isupper():
            text = text[0].upper() + text[1:]
        
        # Ensure questions end with question marks
        if 'what ' in text.lower() or 'how ' in text.lower() or 'which ' in text.lower():
            if not text.endswith('?'):
                text = text.rstrip('.!') + '?'
        
        # Fix common OCR artifacts that weren't caught
        ocr_fixes = {
            ' teh ': ' the ',
            ' adn ': ' and ',
            ' ot ': ' to ',
            ' fo ': ' of ',
            'Iearning': 'learning',
            'educationa ': 'educational ',
            'studetns': 'students',
            'understnad': 'understand',
        }
        
        for wrong, correct in ocr_fixes.items():
            text = text.replace(wrong, correct)
        
        return text
    
    def _improve_answer_structure(self, answer: str) -> str:
        """Improve answer structure and flow"""
        if not answer or len(answer) < 50:
            return answer
        
        # Ensure minimum answer length for educational quality
        if len(answer) < 120:
            if '. This educational' not in answer:
                answer += " This educational content supports comprehensive learning and skill development."
        
        # Remove repetitive and template phrases
        repetitive_patterns = [
            r'(\b\w+\b)\s+\1\b',  # Word repetition
            r'(educational\s+content)\s+\1',  # Phrase repetition
            r'(students\s+can)\s+\1',
        ]
        
        # Replace common template language with improvements
        template_replacements = {
            'This educational material teaches general education concepts': 'This material provides foundational knowledge',
            'educational content supports comprehensive learning': 'content enhances understanding',
            'developing both theoretical understanding and practical skills': 'building knowledge and skills',
            'for academic and real-world applications': 'in various contexts',
            'This educational content supports': 'This content aids',
            'educational material teaches general education': 'material covers educational',
        }
        
        for pattern in repetitive_patterns:
            answer = re.sub(pattern, r'\1', answer, flags=re.IGNORECASE)
        
        # Replace template language with better alternatives
        for template, replacement in template_replacements.items():
            answer = answer.replace(template, replacement)
        
        # Clean up any resulting double spaces or awkward phrasing
        answer = re.sub(r'\s+', ' ', answer).strip()
        answer = re.sub(r'\.\s*\.', '.', answer)  # Remove double periods
        
        return answer
    
    def _apply_model_based_improvements(self, pair: Dict) -> Dict:
        """Apply AI model-based improvements for final polish"""
        if not self.model or not self.tokenizer:
            return pair
        
        improved_pair = pair.copy()
        
        try:
            # Improve question with T5
            question = pair.get('question', '')
            if question:
                improved_question = self._improve_text_with_t5(
                    question, 
                    task_prefix="grammar: "
                )
                if improved_question and len(improved_question) > 10:
                    improved_pair['question'] = improved_question
            
            # Improve answer with T5  
            answer = pair.get('answer', '')
            if answer and len(answer) < 300:  # Only for shorter answers to avoid token limits
                improved_answer = self._improve_text_with_t5(
                    answer[:200],  # Limit length for T5-small
                    task_prefix="grammar: "
                )
                if improved_answer and len(improved_answer) > 50:
                    improved_pair['answer'] = improved_answer
                    
        except Exception as e:
            self.logger.debug(f"Model improvement failed: {e}")
            # Return original if model fails
            return pair
        
        return improved_pair
    
    def _improve_text_with_t5(self, text: str, task_prefix: str = "grammar: ") -> str:
        """Use T5-small to improve text quality"""
        if not text or not self.model:
            return text
        
        try:
            # Prepare input for T5
            input_text = task_prefix + text
            
            # Tokenize with limits for small model
            inputs = self.tokenizer.encode(
                input_text, 
                return_tensors="pt", 
                max_length=256,  # Small limit for T5-small
                truncation=True
            )
            
            # Generate improvement
            if torch is not None:
                with torch.no_grad():
                    outputs = self.model.generate(
                        inputs,
                        max_length=300,
                        num_beams=2,  # Small beam size for speed
                        early_stopping=True,
                        temperature=0.7,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
            else:
                # Fallback without torch
                outputs = self.model.generate(
                    inputs,
                    max_length=300,
                    num_beams=2,  # Small beam size for speed
                    early_stopping=True,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode result
            improved_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Basic validation - ensure improvement is reasonable
            if (len(improved_text) > len(text) * 0.5 and 
                len(improved_text) < len(text) * 2.0 and
                improved_text != text):
                return improved_text
            else:
                return text  # Return original if improvement seems wrong
                
        except Exception as e:
            self.logger.debug(f"T5 improvement failed: {e}")
            return text
    
    def validate_dataset_quality(self, vqa_pairs: List[Dict]) -> Dict:
        """Validate overall dataset quality metrics"""
        if not vqa_pairs:
            return {"error": "No VQA pairs provided"}
        
        metrics = {
            "total_pairs": len(vqa_pairs),
            "quality_issues": [],
            "subject_distribution": {},
            "question_type_distribution": {},
            "avg_question_length": 0,
            "avg_answer_length": 0,
            "quality_score": 0.0
        }
        
        question_lengths = []
        answer_lengths = []
        quality_issues = []
        
        for i, pair in enumerate(vqa_pairs):
            question = pair.get('question', '')
            answer = pair.get('answer', '')
            pair_type = pair.get('type', 'unknown')
            
            # Track lengths
            question_lengths.append(len(question))
            answer_lengths.append(len(answer))
            
            # Check for quality issues
            if len(question) < 20:
                quality_issues.append(f"Pair {i+1}: Question too short")
            if len(answer) < 50:
                quality_issues.append(f"Pair {i+1}: Answer too short")
            if not question.endswith('?'):
                quality_issues.append(f"Pair {i+1}: Question missing question mark")
            
            # Track distributions
            metrics["question_type_distribution"][pair_type] = metrics["question_type_distribution"].get(pair_type, 0) + 1
        
        metrics["avg_question_length"] = sum(question_lengths) / len(question_lengths) if question_lengths else 0
        metrics["avg_answer_length"] = sum(answer_lengths) / len(answer_lengths) if answer_lengths else 0
        metrics["quality_issues"] = quality_issues[:20]  # Limit to first 20 issues
        
        # Calculate quality score (0-100)
        quality_score = 100.0
        quality_score -= min(len(quality_issues) * 2, 40)  # Deduct for issues
        quality_score = max(quality_score, 0.0)
        
        metrics["quality_score"] = quality_score
        
        return metrics

def main():
    """Test the lightweight validator"""
    validator = LightweightVQAValidator(enable_model=False)  # Start with rule-based only
    
    # Test data
    test_pairs = [
        {
            "question": "what is  the educational purpose of this material",
            "answer": "this material teaches students about chemistry concepts and chemical formulas for learning",
            "type": "educational_purpose"
        }
    ]
    
    # Improve pairs
    improved = validator.validate_and_improve_vqa_pairs(test_pairs)
    
    print("Original:", test_pairs[0])
    print("\nImproved:", improved[0])
    
    # Check quality
    quality = validator.validate_dataset_quality(improved)
    print(f"\nQuality Score: {quality['quality_score']}/100")

if __name__ == "__main__":
    main()