#!/usr/bin/env python3
"""
starter_pdf_tool.py
A basic starter PDF generator tool in Python using fpdf2.

Features:
- Create a PDF from text (via --text, a .txt file, or stdin)
- Optional title/author
- Page header & footer with page numbers
- Adjustable font, size, margins, alignment, and line spacing
- Optional Unicode support via a provided TTF font

Usage examples:
  # From direct text
  python starter_pdf_tool.py --text "Hello, world!" -o hello.pdf --title "Demo" --author "Sammy"

  # From a .txt file
  python starter_pdf_tool.py --input notes.txt -o notes.pdf --title "My Notes"

  # Pipe from stdin
  echo "Piped content" | python starter_pdf_tool.py -o piped.pdf

  # Use a TTF font for Unicode (e.g., NotoSans)
  python starter_pdf_tool.py --text "नमस्ते, 你好, مرحبا!" -o unicode.pdf --ttf /path/to/NotoSans-Regular.ttf

Install dependency first:
  pip install fpdf2
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

try:
    from fpdf import FPDF  # pip install fpdf2
except ModuleNotFoundError as e:
    print("This tool requires the 'fpdf2' package. Install it with:\n  pip install fpdf2", file=sys.stderr)
    raise


class PDF(FPDF):
    def __init__(self, title: str = "", author: str = "", line_height: float = 6.0, align: str = "L", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.doc_title = title
        self.doc_author = author
        self.line_height = line_height
        self.align = align

    # Header on every page
    def header(self):
        if self.doc_title:
            self.set_font("", "B", 12)
            self.cell(0, 10, txt=self.doc_title, new_x="LMARGIN", new_y="NEXT", align="C")
            self.ln(2)

    # Footer on every page
    def footer(self):
        self.set_y(-15)
        self.set_font(size=10)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def read_text(input_path: Optional[Path], text_arg: Optional[str]) -> str:
    """Resolve input text from --input, --text, or stdin."""
    if input_path:
        return Path(input_path).read_text(encoding="utf-8")
    if text_arg is not None:
        return text_arg
    if not sys.stdin.isatty():  # has piped data
        return sys.stdin.read()
    return ""

def add_text_to_pdf(pdf: PDF, content: str, font_name: str, font_size: int, align: str):
    pdf.set_font(font_name, size=font_size)
    # Split on double newlines for naive paragraph handling
    paragraphs = content.split("\n\n")
    for para in paragraphs:
        lines = para.splitlines()
        if not lines:
            pdf.ln(pdf.line_height)
            continue
        # Join back into a single paragraph with newline handling
        block = "\n".join(lines)
        pdf.multi_cell(w=0, h=pdf.line_height, txt=block, align=align)
        pdf.ln(pdf.line_height / 2)

def main():
    parser = argparse.ArgumentParser(description="Basic starter PDF generator using fpdf2.")
    src = parser.add_argument_group("Source")
    src.add_argument("--input", "-i", type=Path, help="Path to a .txt file to convert.")
    src.add_argument("--text", "-t", type=str, help="Raw text to put in the PDF. If omitted, reads from stdin if available.")

    out = parser.add_argument_group("Output")
    out.add_argument("--output", "-o", type=Path, required=True, help="Output PDF file path, e.g., out.pdf")
    out.add_argument("--title", type=str, default="", help="Document title (also displayed in header).")
    out.add_argument("--author", type=str, default="", help="Document author metadata.")

    fmt = parser.add_argu_
