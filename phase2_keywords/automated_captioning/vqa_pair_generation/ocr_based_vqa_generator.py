#!/usr/bin/env python3
"""
OCR-Based VQA Generator - Creates specific, training-worthy VQA pairs
Uses actual OCR text to generate precise questions about formulas, equations, text, numbers, etc.
"""

import os
import json
import logging
import random
import re
from typing import Dict, List, Optional, Tuple
import time
from datetime import datetime

class OCRBasedVQAGenerator:
    def __init__(self, language: str = "english"):
        """Initialize OCR-based VQA generator for specific, training-worthy Q&A pairs"""
        self.language = language
        self.logger = self._setup_logger()
        
        # Pattern recognition for different content types
        self.patterns = {
            'math_equation': r'([a-zA-Z]\s*[=]\s*[^=\n]+)|(\d+\s*[+\-×÷]\s*\d+)|([xy]\s*[+\-=]\s*\d+)',
            'chemical_formula': r'(H₂O|CO₂|NaCl|CaCO₃|H₂SO₄|NH₃|CH₄|O₂|N₂|Ca\(OH\)₂)',
            'chemistry_elements': r'\b([A-Z][a-z]?\d*[₀-₉]*)\b',  # Separate pattern for elements
            'numbers': r'\d+\.?\d*',
            'words': r'\b[A-Za-z]{2,}\b',
            'greeting_words': r'\b(Hello|Hi|Hey|Goodbye|Bye|Thanks?|Please|Welcome|Good\s+morning|Good\s+afternoon|Good\s+evening)\b',
            'grammar_terms': r'\b(noun|verb|adjective|adverb|sentence|grammar|tense|plural|singular)\b',
            'units': r'(kg|gram|meter|cm|mm|°C|°F|mph|km/h|Hz|MHz)',
            'symbols': r'[+\-×÷=<>≤≥≠∑∫√π∞α β γ δ ε]',
            'fractions': r'\d+/\d+',
            'percentages': r'\d+%',
            'dates': r'\d{4}|\d{1,2}/\d{1,2}/\d{2,4}'
        }
        
        self.logger.info(f"🎯 OCR-Based VQA Generator initialized for {language}")
    
    def _setup_logger(self):
        """Setup logging"""
        logger = logging.getLogger('OCRBasedVQA')
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def _extract_content_elements(self, ocr_text: str) -> Dict:
        """Extract specific elements from OCR text for question generation"""
        if not ocr_text:
            return {}
            
        elements = {}
        text = ocr_text.strip()
        
        # Extract mathematical equations
        equations = re.findall(self.patterns['math_equation'], text, re.IGNORECASE)
        elements['equations'] = [eq for eq_tuple in equations for eq in eq_tuple if eq.strip()]
        
        # Extract chemical formulas (known compounds)
        formulas = re.findall(self.patterns['chemical_formula'], text, re.IGNORECASE)
        elements['chemical_formulas'] = [f for f in formulas if f.strip()]
        
        # Extract greeting words
        greetings = re.findall(self.patterns['greeting_words'], text, re.IGNORECASE)
        elements['greetings'] = [g for g in greetings if g.strip()]
        
        # Extract grammar terms
        grammar_terms = re.findall(self.patterns['grammar_terms'], text, re.IGNORECASE)
        elements['grammar_terms'] = [g for g in grammar_terms if g.strip()]
        
        # Extract numbers
        elements['numbers'] = re.findall(self.patterns['numbers'], text)
        
        # Extract words (educational terms)
        words = re.findall(self.patterns['words'], text)
        elements['words'] = [w for w in words if len(w) > 3][:10]  # Top 10 meaningful words
        
        # Extract units
        elements['units'] = re.findall(self.patterns['units'], text, re.IGNORECASE)
        
        # Extract mathematical symbols
        elements['symbols'] = list(set(re.findall(self.patterns['symbols'], text)))
        
        # Extract fractions
        elements['fractions'] = re.findall(self.patterns['fractions'], text)
        
        # Extract percentages
        elements['percentages'] = re.findall(self.patterns['percentages'], text)
        
        # Extract dates
        elements['dates'] = re.findall(self.patterns['dates'], text)
        
        # Get lines for specific text reading
        elements['lines'] = [line.strip() for line in text.split('\n') if line.strip() and len(line.strip()) > 5][:5]
        
        # Get individual sentences
        elements['sentences'] = [s.strip() + '.' for s in re.split(r'[.!?]+', text) if s.strip() and len(s.strip()) > 10][:3]
        
        return elements
    
    def _generate_specific_questions(self, elements: Dict, caption: str = "") -> List[Dict]:
        """Generate specific questions based on extracted OCR elements"""
        questions = []
        
        # Mathematical equation questions
        if elements.get('equations'):
            for eq in elements['equations'][:2]:  # Max 2 equation questions
                eq = eq.strip()
                if len(eq) > 3:
                    questions.append({
                        'question': f"What is the mathematical equation shown in the image?",
                        'answer': eq,
                        'type': 'formula_recognition',
                        'confidence': 0.95
                    })
                    
                    # If it contains variables, ask about them
                    variables = re.findall(r'\b[xy]\b', eq.lower())
                    if variables:
                        questions.append({
                            'question': f"What variable needs to be solved in this equation?",
                            'answer': variables[0],
                            'type': 'variable_identification',
                            'confidence': 0.90
                        })
        
        # Greeting recognition questions (for language learning content)
        if elements.get('greetings'):
            greeting_list = elements['greetings'][:3]  # Take up to 3 greetings
            if len(greeting_list) == 1:
                questions.append({
                    'question': f"What greeting is shown in the image?",
                    'answer': greeting_list[0],
                    'type': 'greeting_recognition',
                    'confidence': 0.95
                })
            elif len(greeting_list) > 1:
                questions.append({
                    'question': f"What greetings are visible in the image?",
                    'answer': ", ".join(greeting_list),
                    'type': 'greeting_recognition',
                    'confidence': 0.90
                })
                
                # Ask about specific greeting
                questions.append({
                    'question': f"Which greeting word comes first in the image?",
                    'answer': greeting_list[0],
                    'type': 'greeting_order',
                    'confidence': 0.85
                })
        
        # Grammar terms recognition
        if elements.get('grammar_terms'):
            grammar_list = elements['grammar_terms'][:2]
            for term in grammar_list:
                questions.append({
                    'question': f"What grammar concept is mentioned in the image?",
                    'answer': term,
                    'type': 'grammar_recognition',
                    'confidence': 0.90
                })

        # Chemical formula questions
        if elements.get('chemical_formulas'):
            for formula in elements['chemical_formulas'][:2]:
                formula = formula.strip()
                if len(formula) > 1:
                    questions.append({
                        'question': f"What chemical formula is displayed in the image?",
                        'answer': formula,
                        'type': 'chemical_recognition',
                        'confidence': 0.90
                    })
        
        # Number counting questions
        if elements.get('numbers'):
            unique_numbers = list(set(elements['numbers']))[:3]
            if len(unique_numbers) > 1:
                questions.append({
                    'question': f"How many different numerical values are shown in the image?",
                    'answer': str(len(unique_numbers)),
                    'type': 'counting',
                    'confidence': 0.85
                })
            
            # Ask about specific numbers
            for num in unique_numbers[:2]:
                if float(num) != int(float(num)):  # Decimal number
                    questions.append({
                        'question': f"What decimal number is visible in the image?",
                        'answer': num,
                        'type': 'number_recognition',
                        'confidence': 0.88
                    })
                elif int(float(num)) > 10:  # Significant integer
                    questions.append({
                        'question': f"What is the largest number shown in the image?",
                        'answer': num,
                        'type': 'number_recognition',
                        'confidence': 0.85
                    })
        
        # Word/text recognition questions
        if elements.get('words'):
            # Ask about specific educational terms
            educational_words = [w for w in elements['words'] 
                               if w.lower() in ['equation', 'formula', 'solution', 'problem', 'answer', 'calculate', 'solve', 'function', 'graph', 'theorem', 'proof', 'example', 'definition', 'theory', 'principle']]
            
            if educational_words:
                questions.append({
                    'question': f"What educational term is prominently displayed in the text?",
                    'answer': educational_words[0],
                    'type': 'text_recognition',
                    'confidence': 0.85
                })
        
        # Unit recognition questions
        if elements.get('units'):
            for unit in elements['units'][:1]:
                questions.append({
                    'question': f"What unit of measurement is shown in the image?",
                    'answer': unit,
                    'type': 'unit_recognition',
                    'confidence': 0.85
                })
        
        # Symbol recognition questions
        if elements.get('symbols'):
            for symbol in elements['symbols'][:1]:
                questions.append({
                    'question': f"What mathematical symbol is used in this image?",
                    'answer': symbol,
                    'type': 'symbol_recognition',
                    'confidence': 0.80
                })
        
        # Fraction questions
        if elements.get('fractions'):
            for frac in elements['fractions'][:1]:
                questions.append({
                    'question': f"What fraction is displayed in the image?",
                    'answer': frac,
                    'type': 'fraction_recognition',
                    'confidence': 0.88
                })
        
        # Percentage questions
        if elements.get('percentages'):
            for perc in elements['percentages'][:1]:
                questions.append({
                    'question': f"What percentage is shown in the image?",
                    'answer': perc,
                    'type': 'percentage_recognition',
                    'confidence': 0.85
                })
        
        # Direct text reading questions
        if elements.get('lines'):
            line = elements['lines'][0]  # First meaningful line
            if len(line) < 50:  # Not too long
                questions.append({
                    'question': f"What is the first line of text visible in the image?",
                    'answer': line,
                    'type': 'text_reading',
                    'confidence': 0.90
                })
        
        # Sentence comprehension
        if elements.get('sentences'):
            sentence = elements['sentences'][0]
            questions.append({
                'question': f"What complete sentence or statement is shown in the image?",
                'answer': sentence,
                'type': 'sentence_recognition',
                'confidence': 0.85
            })
        
        return questions
    
    def _add_fallback_questions(self, elements: Dict, caption: str) -> List[Dict]:
        """Add fallback questions when OCR content is limited"""
        fallback_questions = []
        
        # Caption-based questions
        if caption and len(caption) > 20:
            if 'math' in caption.lower() or 'equation' in caption.lower():
                fallback_questions.append({
                    'question': "What subject area does this educational content focus on?",
                    'answer': "Mathematics",
                    'type': 'subject_identification',
                    'confidence': 0.75
                })
            elif 'science' in caption.lower() or 'chemistry' in caption.lower():
                fallback_questions.append({
                    'question': "What subject area does this educational content focus on?",
                    'answer': "Science",
                    'type': 'subject_identification',
                    'confidence': 0.75
                })
        
        # Object counting from caption
        if 'formula' in caption.lower():
            fallback_questions.append({
                'question': "What type of educational content is primarily shown?",
                'answer': "Mathematical or scientific formulas",
                'type': 'content_type_identification',
                'confidence': 0.70
            })
        
        # Generic educational questions
        fallback_questions.append({
            'question': "What would students primarily learn from this image?",
            'answer': "Educational concepts through visual examples and clear explanations",
            'type': 'learning_objective',
            'confidence': 0.65
        })
        
        return fallback_questions
    
    def generate_vqa_pairs(self, image_data: Dict) -> List[Dict]:
        """
        Generate exactly 5 specific VQA pairs using OCR content
        
        Args:
            image_data: Dict containing image_path, ocr_text, caption
            
        Returns:
            List of 5 VQA pairs with specific, training-worthy content
        """
        ocr_text = image_data.get('ocr_text', '').strip()
        caption = image_data.get('caption', '').strip()
        image_path = image_data.get('image_path', '')
        
        self.logger.debug(f"Generating VQA for: {os.path.basename(image_path)}")
        self.logger.debug(f"OCR text length: {len(ocr_text)}")
        
        # Extract specific content elements from OCR
        elements = self._extract_content_elements(ocr_text)
        
        # Generate specific questions based on OCR content
        specific_questions = self._generate_specific_questions(elements, caption)
        
        # Add fallback questions if needed
        fallback_questions = self._add_fallback_questions(elements, caption)
        
        # Combine and select exactly 5 questions
        all_questions = specific_questions + fallback_questions
        
        # Prioritize specific questions over fallback
        final_questions = []
        
        # First, take up to 4 specific questions (high confidence)
        high_confidence_q = [q for q in specific_questions if q['confidence'] >= 0.85]
        final_questions.extend(high_confidence_q[:4])
        
        # Then fill remaining slots with other specific questions
        remaining_specific = [q for q in specific_questions if q not in final_questions]
        final_questions.extend(remaining_specific[:5-len(final_questions)])
        
        # Fill any remaining slots with fallback questions
        remaining_fallback = [q for q in fallback_questions if q not in final_questions]
        final_questions.extend(remaining_fallback[:5-len(final_questions)])
        
        # Ensure exactly 5 questions
        if len(final_questions) < 5:
            # Add more generic questions to reach 5
            generic_questions = [
                {
                    'question': "What type of educational material is shown in this image?",
                    'answer': "Educational content with text and visual elements",
                    'type': 'general_identification',
                    'confidence': 0.60
                },
                {
                    'question': "How would this image help students in their learning?",
                    'answer': "By providing visual examples and clear information presentation",
                    'type': 'educational_value',
                    'confidence': 0.55
                }
            ]
            final_questions.extend(generic_questions[:5-len(final_questions)])
        
        # Take exactly 5 questions
        final_questions = final_questions[:5]
        
        # Format as VQA pairs with metadata
        vqa_pairs = []
        for i, q in enumerate(final_questions):
            vqa_pair = {
                'question': q['question'],
                'answer': q['answer'],
                'type': q['type'],
                'confidence': q.get('confidence', 0.70),
                'uses_ocr': q['type'] in ['formula_recognition', 'text_reading', 'number_recognition', 'chemical_recognition', 'variable_identification', 'greeting_recognition', 'greeting_order', 'grammar_recognition'],
                'question_id': f"{os.path.basename(image_path).split('.')[0]}_q{i+1}",
                'generation_method': 'ocr_based',
                'timestamp': datetime.now().isoformat()
            }
            vqa_pairs.append(vqa_pair)
        
        self.logger.info(f"✅ Generated {len(vqa_pairs)} VQA pairs for {os.path.basename(image_path)}")
        self.logger.info(f"   OCR-based questions: {sum(1 for q in vqa_pairs if q['uses_ocr'])}/5")
        
        return vqa_pairs
    
    def batch_generate_vqa_pairs(self, image_data_list: List[Dict]) -> List[Dict]:
        """Generate VQA pairs for multiple images"""
        self.logger.info(f"🔄 Processing {len(image_data_list)} images for VQA generation...")
        
        all_vqa_pairs = []
        ocr_based_count = 0
        
        for i, image_data in enumerate(image_data_list):
            try:
                vqa_pairs = self.generate_vqa_pairs(image_data)
                
                # Add to combined results with image metadata
                for pair in vqa_pairs:
                    pair.update({
                        'image_id': os.path.basename(image_data.get('image_path', '')).split('.')[0],
                        'image_path': image_data.get('image_path', ''),
                        'image_width': image_data.get('width'),
                        'image_height': image_data.get('height'),
                        'image_format': image_data.get('format'),
                        'ocr_text': image_data.get('ocr_text', ''),
                        'caption': image_data.get('caption', '')
                    })
                
                all_vqa_pairs.extend(vqa_pairs)
                
                # Count OCR-based questions
                ocr_based_count += sum(1 for q in vqa_pairs if q.get('uses_ocr', False))
                
                if (i + 1) % 10 == 0:
                    self.logger.info(f"   Processed {i + 1}/{len(image_data_list)} images...")
                    
            except Exception as e:
                self.logger.error(f"Error processing {image_data.get('image_path', 'unknown')}: {e}")
        
        self.logger.info(f"🎯 VQA Generation Complete!")
        self.logger.info(f"   Total VQA pairs: {len(all_vqa_pairs)}")
        self.logger.info(f"   OCR-based questions: {ocr_based_count}/{len(all_vqa_pairs)} ({ocr_based_count/len(all_vqa_pairs)*100:.1f}%)")
        self.logger.info(f"   Average per image: {len(all_vqa_pairs)/len(image_data_list):.1f}")
        
        return all_vqa_pairs

def main():
    """Test the OCR-based VQA generator"""
    generator = OCRBasedVQAGenerator("english")
    
    # Test with sample data
    test_data = [
        {
            'image_path': '/test/math_problem.jpg',
            'ocr_text': 'Solve for x: 2x + 5 = 13\nStep 1: Subtract 5 from both sides\n2x = 8\nStep 2: Divide by 2\nx = 4',
            'caption': 'Educational math worksheet showing algebra problem'
        },
        {
            'image_path': '/test/chemistry.jpg', 
            'ocr_text': 'Chemical Formula: H₂O (water)\nMolar mass: 18.015 g/mol\nBoiling point: 100°C',
            'caption': 'Chemistry educational content showing water molecule'
        }
    ]
    
    # Generate VQA pairs
    vqa_pairs = generator.batch_generate_vqa_pairs(test_data)
    
    # Print results
    print("\n" + "="*60)
    print("SAMPLE VQA PAIRS GENERATED:")
    print("="*60)
    for pair in vqa_pairs[:10]:  # Show first 10
        print(f"Q: {pair['question']}")
        print(f"A: {pair['answer']}")
        print(f"Type: {pair['type']} | OCR-based: {pair['uses_ocr']}")
        print("-" * 40)

if __name__ == "__main__":
    main()