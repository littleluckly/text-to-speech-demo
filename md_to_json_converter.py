#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
import uuid
from pathlib import Path
import argparse

class MdToJsonConverter:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # 用于记录转换失败的文件
        self.failed_files = []
    
    def clean_meta_json(self, meta_content):
        """清理meta元数据中的特殊字符"""
        # 替换HTML实体和特殊字符
        meta_content = meta_content.replace('&#x20;', ' ').replace('\\[', '[').replace('\\]', ']')
        # 移除可能的代码块标记
        meta_content = meta_content.strip('```')
        return meta_content
    
    def parse_md_file(self, md_file_path):
        """解析单个md文件并返回JSON数据"""
        try:
            with open(md_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取文件名作为问题标题（默认值）
            file_name = md_file_path.stem
            question_markdown = file_name
            
            # 1. 检查文件中是否有一号标题
            first_heading_match = re.search(r'^#\s+(.*?)$', content, re.MULTILINE)
            if first_heading_match:
                question_markdown = first_heading_match.group(1).strip()
            
            # 2. 提取meta元数据
            meta_match = re.search(r'##\s+meta\s+元数据\s*\n+```\s*\n(.*?)\n```', content, re.DOTALL)
            meta_data = {}
            if meta_match:
                meta_content = self.clean_meta_json(meta_match.group(1))
                try:
                    meta_data = json.loads(meta_content)
                except json.JSONDecodeError:
                    print(f"警告: {md_file_path} 中的meta元数据格式不正确")
            
            # 3. 提取answer_simple_markdown（答案 1）
            answer_simple_match = re.search(r'##\s+答案\s+1[\s：:].*?\n+([\s\S]+?)(?=\n##\s+答案\s+2|\Z)', content, re.DOTALL)
            answer_simple_markdown = answer_simple_match.group(1).strip() if answer_simple_match else ''
            
            # 4. 提取answer_detail_markdown（答案 2）
            answer_detail_match = re.search(r'##\s+答案\s+2[\s：:].*?\n+([\s\S]+?)(?=\n##\s+答案\s+3|\Z)', content, re.DOTALL)
            answer_detail_markdown = answer_detail_match.group(1).strip() if answer_detail_match else ''
            
            # 5. 提取answer_analysis_markdown（答案 3，如果存在）
            answer_analysis_match = re.search(r'##\s+答案\s+3[\s：:].*?\n+([\s\S]+)', content, re.DOTALL)
            answer_analysis_markdown = answer_analysis_match.group(1).strip() if answer_analysis_match else answer_detail_markdown
            
            # 6. 生成audioKey（不需要拼接文件名称）
            audio_key = f"q{str(uuid.uuid4())[:8]}"
            
            # 构建最终的JSON数据
            json_data = {
                "audioKey": audio_key,
                **meta_data,  # 合并meta元数据
                "question_markdown": question_markdown,
                "answer_simple_markdown": answer_simple_markdown,
                "answer_detail_markdown": answer_detail_markdown,
                "answer_analysis_markdown": answer_analysis_markdown,
                "files": {
                    "audio_answer_simple": f"{audio_key}_audio_answer_simple.mp3",
                    "audio_answer_detail": f"{audio_key}_audio_answer_detail.mp3",
                    "audio_answer_analysis": f"{audio_key}_audio_answer_analysis.mp3",
                    "audio_question": f"{audio_key}_audio_question.mp3"
                }
            }
            
            return json_data
        except Exception as e:
            print(f"处理文件 {md_file_path} 时出错: {str(e)}")
            return None
    
    def convert_file(self, md_file_path):
        """转换单个md文件"""
        md_file = Path(md_file_path)
        print(f"处理文件: {md_file.name}")
        
        # 解析md文件
        json_data = self.parse_md_file(md_file)
        if json_data:
            # 生成输出文件名
            output_filename = f"{md_file.stem}.json"
            output_path = self.output_dir / output_filename
            
            # 写入JSON文件
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                print(f"成功生成JSON文件: {output_path}")
                return True
            except Exception as e:
                error_msg = f"写入JSON文件 {output_path} 时出错: {str(e)}"
                print(error_msg)
                self.failed_files.append((md_file.name, error_msg))
                return False
        else:
            error_msg = f"解析文件 {md_file.name} 失败"
            print(error_msg)
            self.failed_files.append((md_file.name, error_msg))
            return False
    
    def convert_directory(self, input_dir, max_count=None):
        """转换目录中的md文件"""
        # 获取输入目录中的所有md文件
        md_files = list(Path(input_dir).glob('*.md'))
        total_files = len(md_files)
        
        # 如果指定了最大转换数量，则限制文件列表
        if max_count is not None and max_count > 0:
            md_files = md_files[:max_count]
            total_files = len(md_files)
            print(f"找到 {total_files} 个Markdown文件，将处理前 {max_count} 个文件")
        else:
            print(f"找到 {total_files} 个Markdown文件需要处理")
        
        success_count = 0
        
        for idx, md_file in enumerate(md_files, 1):
            print(f"处理文件 {idx}/{total_files}: {md_file.name}")
            
            # 解析md文件
            if self.convert_file(md_file):
                success_count += 1
        
        # 输出转换报告
        self.print_conversion_report(success_count, total_files)
    
    def print_conversion_report(self, success_count, total_count):
        """输出转换报告"""
        print("\n===== 转换报告 =====")
        print(f"总文件数: {total_count}")
        print(f"成功转换: {success_count}")
        print(f"失败转换: {len(self.failed_files)}")
        
        if self.failed_files:
            print("\n失败文件列表:")
            for file_name, error_msg in self.failed_files:
                print(f"- {file_name}: {error_msg}")
        print("==================")

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='将Markdown文件转换为指定格式的JSON文件')
    parser.add_argument('-i', '--input', default='questions', help='输入目录或文件路径')
    parser.add_argument('-o', '--output', default='questions-json', help='输出目录，默认为questions-json')
    parser.add_argument('-n', '--number', type=int, default=None, help='指定转换文件数量，不指定则转换所有文件')
    args = parser.parse_args()
    
    # 创建转换器实例
    converter = MdToJsonConverter(args.output)
    
    # 判断输入是文件还是目录
    input_path = Path(args.input)
    if input_path.is_file() and input_path.suffix == '.md':
        # 处理单个文件
        success = converter.convert_file(input_path)
        print("\n===== 转换报告 =====")
        print(f"总文件数: 1")
        print(f"成功转换: {1 if success else 0}")
        print(f"失败转换: {0 if success else 1}")
        if converter.failed_files:
            print("\n失败文件列表:")
            for file_name, error_msg in converter.failed_files:
                print(f"- {file_name}: {error_msg}")
        print("==================")
    else:
        # 处理目录
        converter.convert_directory(args.input, args.number)