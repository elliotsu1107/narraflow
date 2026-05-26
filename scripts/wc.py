#!/usr/bin/env python3
"""
文脉 Narraflow — 章节字数统计工具

用法:
  python wc.py <文件路径>          # 统计正文字数
  python wc.py <文件路径> --all    # 统计全文（含要点、细纲）

输出:
  正文总字数, 目标字数（从文件名或参数读取）
"""

import re
import sys
from pathlib import Path


def strip_frontmatter(text: str) -> str:
    """移除 YAML frontmatter（--- 之间的内容）"""
    return re.sub(r'^---[\s\S]*?---\n*', '', text)


def extract_section(text: str, section_title: str) -> str:
    """提取指定标题下的内容，到下一个标题或文件结尾"""
    pattern = rf'^##\s*{re.escape(section_title)}\s*$(.*?)(?=^##\s|\Z)'
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return ''


def count_chars(text: str) -> int:
    """统计有效字数：中文字符 + 英文单词数"""
    # 移除代码块
    text = re.sub(r'```[\s\S]*?```', '', text)
    # 移除行内代码
    text = re.sub(r'`[^`]+`', '', text)
    # 移除图片和链接（保留文字）
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'\[([^\]]*)\]\(.*?\)', r'\1', text)
    # 移除 markdown 标记（粗体、斜体等）
    text = re.sub(r'[*_~]{1,2}([^*_~]+)[*_~]{1,2}', r'\1', text)
    # 移除注释
    text = re.sub(r'<!--[\s\S]*?-->', '', text)
    # 移除分隔线
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
    # 移除引用标记
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
    # 移除列表标记
    text = re.sub(r'^[\s]*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    # 移除表格
    text = re.sub(r'\|[^|]*\|', '', text)
    text = re.sub(r'^[\s\-:|]+$', '', text, flags=re.MULTILINE)

    # 中文字符
    chinese_chars = len(re.findall(r'[一-鿿㐀-䶿豈-﫿]', text))
    # 英文单词
    english_words = len(re.findall(r'[a-zA-Z]+', text))

    return chinese_chars + english_words


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) < 2:
        print("用法: python wc.py <文件路径> [--all]")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"文件不存在: {filepath}")
        sys.exit(1)

    count_all = '--all' in sys.argv

    raw = filepath.read_text(encoding='utf-8')
    body = strip_frontmatter(raw)

    if count_all:
        total = count_chars(body)
        print(f"全文总字数: {total}")
        return

    # 统计正文部分
    main_text = extract_section(body, '正文')
    if not main_text:
        # 如果没有 ## 正文 标记，统计全部
        main_text = body

    total = count_chars(main_text)
    print(f"正文总字数: {total}")


if __name__ == '__main__':
    main()
