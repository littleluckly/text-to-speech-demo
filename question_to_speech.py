import os
import re
import json
from pathlib import Path
import markdown
from bs4 import BeautifulSoup
import edge_tts
import asyncio
from typing import Dict, List, Any

class MarkdownQuestionParser:
    def __init__(self, input_file: str, output_dir: str = "questions"):
        self.input_file = input_file
        self.output_dir = Path(output_dir)
        self.voice = "zh-CN-YunyangNeural"  # Chinese male voice
        
    def clean_markdown_text(self, text: str) -> str:
        """Remove markdown formatting and return clean text"""
        # Remove markdown headers
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        
        # Remove bold and italic formatting
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Italic
        text = re.sub(r'__([^_]+)__', r'\1', text)      # Bold alternative
        text = re.sub(r'_([^_]+)_', r'\1', text)        # Italic alternative
        
        # Remove links but keep text
        text = re.sub(r'\[([^\]]+)\]$$[^)]+$$', r'\1', text)
        
        # Remove images
        text = re.sub(r'!\[([^\]]*)\]$$[^)]+$$', '', text)
        
        # Remove emojis (basic emoji patterns)
        text = re.sub(r'[\U0001F600-\U0001F64F]', '', text)  # Emoticons
        text = re.sub(r'[\U0001F300-\U0001F5FF]', '', text)  # Symbols & pictographs
        text = re.sub(r'[\U0001F680-\U0001F6FF]', '', text)  # Transport & map
        text = re.sub(r'[\U0001F1E0-\U0001F1FF]', '', text)  # Flags
        
        # Remove special markdown symbols
        text = re.sub(r'[✅📘]', '', text)
        
        # Clean up extra whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = text.strip()
        
        return text
    
    def parse_frontmatter(self, content: str) -> tuple[Dict[str, Any], str]:
        """Parse YAML frontmatter and return metadata and remaining content"""
        frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(frontmatter_pattern, content, re.DOTALL)
        
        if match:
            frontmatter_text = match.group(1)
            remaining_content = content[match.end():]
            
            # Parse YAML-like frontmatter manually
            metadata = {}
            for line in frontmatter_text.split('\n'):
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Handle arrays
                    if value.startswith('[') and value.endswith(']'):
                        # Parse array
                        array_content = value[1:-1]
                        metadata[key] = [item.strip() for item in array_content.split(',')]
                    else:
                        metadata[key] = value
            
            return metadata, remaining_content
        
        return {}, content
    
    def parse_question_block(self, block: str) -> Dict[str, Any]:
        """Parse a single question block"""
        # Parse frontmatter
        metadata, content = self.parse_frontmatter(block)
        
        # Find question section
        question_match = re.search(r'## \*\*题目：\*\* (.+?)(?=\n## \*\*✅ 精简答案：\*\*)', content, re.DOTALL)
        if not question_match:
            return None
        
        question_text = question_match.group(1).strip()
        
        # Find simple answer section
        simple_answer_match = re.search(r'## \*\*✅ 精简答案：\*\* (.+?)(?=\n\*\*📘 详细解析：\*\*)', content, re.DOTALL)
        if not simple_answer_match:
            return None
        
        simple_answer = simple_answer_match.group(1).strip()
        
        # Find detailed analysis section
        analysis_match = re.search(r'\*\*📘 详细解析：\*\*\s*\n\n(.+)', content, re.DOTALL)
        detailed_analysis = ""
        if analysis_match:
            detailed_analysis = analysis_match.group(1).strip()
        
        return {
            'metadata': metadata,
            'question': self.clean_markdown_text(question_text),
            'simple_answer': self.clean_markdown_text(simple_answer),
            'detailed_analysis': self.clean_markdown_text(detailed_analysis)
        }
    
    def preprocess_text_for_speech(self, text: str) -> str:
        """Preprocess text to improve speech readability with proper pauses"""
        # Remove markdown code blocks (\`\`\`xxx\`\`\`)
        text = re.sub(r'\`\`\`[^`]*\`\`\`', '', text, flags=re.DOTALL)
        
        # Remove inline code (`code`)
        text = re.sub(r'`([^`]+)`', '', text)
        
        # Remove markdown list symbols (-, *, +)
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
        
        # Remove numbered list symbols (1. 2. etc.)
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
        
        # Remove remaining markdown symbols
        text = re.sub(r'[#*_~`]', '', text)
        
        # Replace arrows and special symbols with pauses
        text = re.sub(r'→', '，然后', text)  # Replace → with "then"
        text = re.sub(r'←', '，返回', text)  # Replace ← with "return"
        text = re.sub(r'↑', '，向上', text)  # Replace ↑ with "up"
        text = re.sub(r'↓', '，向下', text)  # Replace ↓ with "down"
        
        # Add pauses between lifecycle methods and technical terms
        lifecycle_methods = [
            'beforeCreate', 'created', 'beforeMount', 'mounted',
            'beforeUpdate', 'updated', 'beforeDestroy', 'destroyed',
            'beforeUnmount', 'unmounted', 'activated', 'deactivated'
        ]
        
        for method in lifecycle_methods:
            # Add pause after each lifecycle method
            text = re.sub(rf'\b{method}\b', f'{method}，', text)
        
        # Add pauses between code elements separated by spaces
        text = re.sub(r'(\w+)\s+(\w+)\s+(\w+)', r'\1，\2，\3', text)
        
        # Add pauses around parentheses and brackets
        text = re.sub(r'\(', '，开括号，', text)
        text = re.sub(r'\)', '，闭括号，', text)
        text = re.sub(r'\[', '，开方括号，', text)
        text = re.sub(r'\]', '，闭方括号，', text)
        text = re.sub(r'\{', '，开花括号，', text)
        text = re.sub(r'\}', '，闭花括号，', text)
        
        # Add pauses around equals signs and operators
        text = re.sub(r'=', '，等于，', text)
        text = re.sub(r'\+', '，加，', text)
        text = re.sub(r'\*', '，乘，', text)
        text = re.sub(r'/', '，除，', text)
        
        # Add pauses between camelCase words
        text = re.sub(r'([a-z])([A-Z])', r'\1，\2', text)
        
        # Add pauses around dots in method calls
        text = re.sub(r'\.', '，点，', text)
        
        # Clean up multiple consecutive commas
        text = re.sub(r'，+', '，', text)
        
        # Ensure proper spacing around Chinese punctuation
        text = re.sub(r'，\s*，', '，', text)
        text = re.sub(r'，\s*$', '。', text)  # End with period instead of comma
        
        return text.strip()
    
    async def generate_audio(self, text: str, output_path: Path):
        """Generate audio file from text using edge_tts 7.x"""
        try:
            # Preprocess text for better speech readability
            processed_text = self.preprocess_text_for_speech(text)
            
            # Additional cleaning for TTS
            clean_text = re.sub(r'[^\w\s\u4e00-\u9fff，。！？；：]', ' ', processed_text)
            clean_text = re.sub(r'\s+', ' ', clean_text)  # Normalize whitespace
            clean_text = clean_text.strip()
            
            if not clean_text:
                print(f"Skipping empty text for {output_path}")
                return
            
            voices_manager = await edge_tts.VoicesManager.create()
            
            # List of preferred Mandarin Chinese voices in order of preference
            preferred_voices = [
                "zh-CN-YunyangNeural",
                "zh-CN-YunjianNeural", 
                "zh-CN-YunxiNeural",
                "zh-CN-YunhaoNeural",
                "zh-CN-YunzeNeural"
            ]
            
            selected_voice = None
            all_voices = voices_manager.find()
            
            print(f"Looking for voice from preferred list...")
            
            # Try to find one of our preferred voices
            for voice in preferred_voices:
                matching_voices = [v for v in all_voices if v["Name"] == voice]
                if matching_voices:
                    selected_voice = voice
                    print(f"✓ Found preferred voice: {selected_voice}")
                    break
                else:
                    print(f"✗ Voice not available: {voice}")
            
            # If none of the preferred voices are found, look for any zh-CN voice
            if not selected_voice:
                print("No preferred voices found, looking for any zh-CN voice...")
                zh_cn_voices = [v for v in all_voices if v["Locale"].startswith("zh-CN")]
                if zh_cn_voices:
                    selected_voice = zh_cn_voices[0]["Name"]
                    print(f"✓ Using fallback zh-CN voice: {selected_voice}")
                    print(f"  Available zh-CN voices: {[v['Name'] for v in zh_cn_voices[:3]]}")
                else:
                    print("⚠️  No zh-CN voices found! This might cause issues.")
                    # List what voices are actually available
                    available_locales = list(set([v["Locale"] for v in all_voices]))
                    print(f"Available locales: {available_locales[:10]}")
                    selected_voice = "zh-CN-YunyangNeural"  # Default fallback
            
            # Create TTS communication with edge-tts 7.x
            communicate = edge_tts.Communicate(clean_text, selected_voice)
            
            # Save audio to file
            await communicate.save(str(output_path))
            print(f"✓ Generated audio: {output_path.name}")
        except Exception as e:
            print(f"✗ Error generating audio for {output_path}: {e}")
    
    async def create_question_directory(self, question_data: Dict[str, Any], question_num: int):
        """Create directory structure and files for a single question"""
        # Create question directory
        question_dir = self.output_dir / f"q_{question_num:04d}"
        question_dir.mkdir(parents=True, exist_ok=True)
        
        # Write question.md
        question_file = question_dir / "question.md"
        with open(question_file, 'w', encoding='utf-8') as f:
            f.write(question_data['question'])
        
        # Write answer_simple.md
        simple_answer_file = question_dir / "answer_simple.md"
        with open(simple_answer_file, 'w', encoding='utf-8') as f:
            f.write(question_data['simple_answer'])
        
        # Write answer_analysis.md
        analysis_file = question_dir / "answer_analysis.md"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            f.write(question_data['detailed_analysis'])
        
        # Generate audio files
        audio_simple_file = question_dir / "audio_simple.mp3"
        audio_question_file = question_dir / "audio_question.mp3"
        audio_analysis_file = question_dir / "audio_analysis.mp3"
        
        await self.generate_audio(question_data['simple_answer'], audio_simple_file)
        await self.generate_audio(question_data['question'], audio_question_file)
        await self.generate_audio(question_data['detailed_analysis'], audio_analysis_file)
        
        # Create meta.json
        meta_data = {
            'id': question_data['metadata'].get('id', question_num),
            'type': question_data['metadata'].get('type', 'unknown'),
            'difficulty': question_data['metadata'].get('difficulty', 'medium'),
            'tags': question_data['metadata'].get('tags', []),
            'question_length': len(question_data['question']),
            'simple_answer_length': len(question_data['simple_answer']),
            'detailed_analysis_length': len(question_data['detailed_analysis']),
            'created_at': None,  # You can add timestamp if needed
            'files': {
                'question': 'question.md',
                'simple_answer': 'answer_simple.md',
                'detailed_analysis': 'answer_analysis.md',
                'audio_simple': 'audio_simple.mp3',
                'audio_question': 'audio_question.mp3',
                'audio_analysis': 'audio_analysis.mp3'
            }
        }
        
        meta_file = question_dir / "meta.json"
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(meta_data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Created question directory: {question_dir}")
    
    async def parse_and_generate(self):
        """Main method to parse markdown file and generate question directories"""
        print(f"Reading markdown file: {self.input_file}")
        
        # Read the input file
        with open(self.input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split content into question blocks - each block starts with YAML frontmatter
        # First, split by --- that separates questions
        parts = content.split('\n---\n')
        
        question_blocks = []
        for i, part in enumerate(parts):
            if i == 0:
                # First part might not have leading ---
                if part.strip().startswith('---'):
                    question_blocks.append(part.strip())
                else:
                    question_blocks.append('---\n' + part.strip())
            else:
                # Add back the --- separator for proper YAML parsing
                question_blocks.append('---\n' + part.strip())
        
        # Filter out empty blocks
        question_blocks = [block for block in question_blocks if block.strip() and '题目' in block]
        
        print(f"Found {len(question_blocks)} question blocks")
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Process each question block
        question_count = 0
        for i, block in enumerate(question_blocks):
            try:
                question_data = self.parse_question_block(block)
                if question_data:
                    question_count += 1
                    await self.create_question_directory(question_data, question_count)
                else:
                    print(f"Skipping invalid block {i+1}")
            except Exception as e:
                print(f"✗ Error processing block {i+1}: {e}")
        
        print(f"\n✓ Successfully processed {question_count} questions")
        print(f"Output directory: {self.output_dir.absolute()}")
    
    async def list_available_voices(self):
        """List all available Chinese voices"""
        try:
            voices_manager = await edge_tts.VoicesManager.create()
            all_voices = voices_manager.find()
            
            # Filter Chinese voices
            chinese_voices = [v for v in all_voices if v["Locale"].startswith("zh")]
            
            print("\n=== Available Chinese Voices ===")
            for voice in chinese_voices:
                print(f"Name: {voice['Name']}")
                print(f"  Locale: {voice['Locale']}")
                print(f"  Gender: {voice['Gender']}")
                print(f"  Display Name: {voice['FriendlyName']}")
                print()
            
            print(f"Total Chinese voices found: {len(chinese_voices)}")
            return chinese_voices
        except Exception as e:
            print(f"✗ Error listing voices: {e}")
            return []

async def main():
    import sys
    
    # Check for voice listing command
    if len(sys.argv) == 2 and sys.argv[1] == "--list-voices":
        parser = MarkdownQuestionParser("", "")
        await parser.list_available_voices()
        return
    
    if len(sys.argv) != 3:
        print("Usage: python3 question_to_speech.py <input_markdown_file> <output_directory>")
        print("       python3 question_to_speech.py --list-voices")
        print("Example: python3 question_to_speech.py vue_questions.md format-output")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"✗ Error: Input file '{input_file}' does not exist.")
        sys.exit(1)
    
    # Create parser and run
    parser = MarkdownQuestionParser(input_file, output_dir)
    await parser.parse_and_generate()

if __name__ == "__main__":
    asyncio.run(main())
