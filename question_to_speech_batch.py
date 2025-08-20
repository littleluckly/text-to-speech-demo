import re
import json
import os
import time
from pathlib import Path
import asyncio
from typing import Dict, List, Any
import sys

# Import the MarkdownQuestionParser class from the original file
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from question_to_speech import MarkdownQuestionParser

class BatchMarkdownQuestionParser(MarkdownQuestionParser):
    def __init__(self, input_file: str, output_dir: str = "questions", batch_size: int = 5, interval: int = 60, start_from: int = 1):
        super().__init__(input_file, output_dir)
        self.batch_size = batch_size  # Number of questions to process in each batch
        self.interval = interval  # Interval between batches in seconds
        self.start_from = start_from  # Start processing from this question number
        self.status_file = Path(output_dir) / "batch_status.json"
    
    def load_status(self) -> int:
        """Load the last processed question number from status file"""
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    status = json.load(f)
                    return status.get('last_processed', self.start_from)
            except Exception as e:
                print(f"Error loading status file: {e}")
        return self.start_from
    
    def save_status(self, last_processed: int):
        """Save the last processed question number to status file"""
        status = {
            'last_processed': last_processed,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'input_file': self.input_file,
            'output_dir': str(self.output_dir)
        }
        
        try:
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(status, f, ensure_ascii=False, indent=2)
            print(f"Status saved: last processed question {last_processed}")
        except Exception as e:
            print(f"Error saving status file: {e}")
    
    async def parse_and_generate_batch(self):
        """Process questions in batches with intervals to prevent API rate limiting"""
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
        
        total_questions = len(question_blocks)
        print(f"Found {total_questions} question blocks in total")
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Load last processed question number
        start_index = self.load_status() - 1  # Convert to 0-based index
        start_index = max(0, start_index)  # Ensure it's not negative
        
        print(f"Starting from question {start_index + 1}/{total_questions}")
        print(f"Batch size: {self.batch_size}, Interval between batches: {self.interval} seconds")
        
        # Process questions in batches
        while start_index < total_questions:
            end_index = min(start_index + self.batch_size, total_questions)
            current_batch = question_blocks[start_index:end_index]
            
            print(f"\n=== Processing batch {start_index//self.batch_size + 1} ===")
            print(f"Processing questions {start_index + 1} to {end_index}/{total_questions}")
            
            # Process each question in the current batch
            for i, block in enumerate(current_batch):
                question_num = start_index + i + 1
                try:
                    # Check if this question has already been processed
                    question_dir = self.output_dir / f"q_{question_num:04d}"
                    if question_dir.exists() and (question_dir / "meta.json").exists():
                        print(f"Skipping question {question_num}, already processed.")
                        continue
                    
                    question_data = self.parse_question_block(block)
                    if question_data:
                        await self.create_question_directory(question_data, question_num)
                        # Save status after each successful question processing
                        self.save_status(question_num)
                    else:
                        print(f"Skipping invalid block {question_num}")
                except Exception as e:
                    print(f"✗ Error processing question {question_num}: {e}")
                    # Save status even if there's an error to avoid reprocessing
                    self.save_status(question_num)
                    # You might want to break here if you don't want to continue after an error
                    # break
            
            # Update start_index for next batch
            start_index = end_index
            
            # If there are more questions to process, wait for the interval
            if start_index < total_questions:
                print(f"\nWaiting for {self.interval} seconds before next batch...")
                await asyncio.sleep(self.interval)
        
        print(f"\n✓ Successfully processed all questions")
        print(f"Output directory: {self.output_dir.absolute()}")
        
        # Clean up status file if all questions are processed
        if self.status_file.exists():
            try:
                os.remove(self.status_file)
                print("Status file removed as all processing is complete.")
            except Exception as e:
                print(f"Error removing status file: {e}")

async def main():
    # Check for command line arguments
    if len(sys.argv) < 3:
        print("Usage: python3 question_to_speech_batch.py <input_markdown_file> <output_directory> [options]")
        print("Options:")
        print("  --batch-size <number>    Number of questions to process in each batch (default: 5)")
        print("  --interval <seconds>     Interval between batches in seconds (default: 60)")
        print("  --start-from <number>    Start processing from this question number (default: 1)")
        print("Example: python3 question_to_speech_batch.py vue_questions.md format-output --batch-size 3 --interval 90")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    # Default values
    batch_size = 5
    interval = 60
    start_from = 1
    
    # Parse optional arguments
    for i in range(3, len(sys.argv)):
        if sys.argv[i] == '--batch-size' and i + 1 < len(sys.argv):
            try:
                batch_size = int(sys.argv[i + 1])
                if batch_size < 1:
                    print("Batch size must be at least 1")
                    sys.exit(1)
            except ValueError:
                print("Invalid batch size")
                sys.exit(1)
        elif sys.argv[i] == '--interval' and i + 1 < len(sys.argv):
            try:
                interval = int(sys.argv[i + 1])
                if interval < 0:
                    print("Interval must be non-negative")
                    sys.exit(1)
            except ValueError:
                print("Invalid interval")
                sys.exit(1)
        elif sys.argv[i] == '--start-from' and i + 1 < len(sys.argv):
            try:
                start_from = int(sys.argv[i + 1])
                if start_from < 1:
                    print("Start from must be at least 1")
                    sys.exit(1)
            except ValueError:
                print("Invalid start from value")
                sys.exit(1)
    
    if not os.path.exists(input_file):
        print(f"✗ Error: Input file '{input_file}' does not exist.")
        sys.exit(1)
    
    # Create parser and run batch processing
    parser = BatchMarkdownQuestionParser(
        input_file, 
        output_dir, 
        batch_size=batch_size, 
        interval=interval, 
        start_from=start_from
    )
    await parser.parse_and_generate_batch()

if __name__ == "__main__":
    asyncio.run(main())