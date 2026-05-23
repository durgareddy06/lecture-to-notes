import io
import re
from fpdf import FPDF


class SmartNotesPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_fill_color(102, 126, 234)
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, "  Lecture Smart Notes", fill=True, ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def export_to_pdf(markdown_text: str, source_filename: str = "") -> bytes:
    pdf = SmartNotesPDF()
    pdf.set_margins(20, 25, 20)   # left, top, right margins
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    lines = markdown_text.split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(2)
            continue

        try:
            # H1
            if line.startswith("# "):
                text = _clean(line[2:])
                if not text:
                    continue
                pdf.set_font("Helvetica", "B", 15)
                pdf.set_fill_color(240, 242, 255)
                pdf.multi_cell(0, 9, text, fill=True)
                pdf.ln(2)

            # H2
            elif line.startswith("## "):
                text = _clean(line[3:])
                if not text:
                    continue
                pdf.set_font("Helvetica", "B", 12)
                pdf.set_text_color(102, 126, 234)
                pdf.multi_cell(0, 8, text)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(1)

            # H3
            elif line.startswith("### "):
                text = _clean(line[4:])
                if not text:
                    continue
                pdf.set_font("Helvetica", "B", 11)
                pdf.set_text_color(50, 50, 120)
                pdf.multi_cell(0, 7, text)
                pdf.set_text_color(0, 0, 0)

            # Bullets
            elif line.startswith(("- ", "* ", "+ ")):
                text = _clean(line[2:])
                if not text:
                    continue
                pdf.set_font("Helvetica", "", 10)
                pdf.multi_cell(0, 6, f"  - {text}")

            # Divider
            elif set(line) <= {"-", " "} and len(line) > 2:
                pdf.set_draw_color(180, 180, 200)
                pdf.line(15, pdf.get_y(), 195, pdf.get_y())
                pdf.ln(3)

            # Table row
            elif line.startswith("|") and line.endswith("|"):
                cells = [c.strip() for c in line.split("|") if c.strip()]
                if cells and not all(set(c) <= {"-", " "} for c in cells):
                    row_text = " | ".join(cells)
                    row_text = _clean(row_text)
                    if row_text:
                        pdf.set_font("Courier", "", 9)
                        pdf.multi_cell(0, 6, row_text)

            # Normal text
            else:
                text = _clean(line)
                if text:
                    pdf.set_font("Helvetica", "", 10)
                    pdf.multi_cell(0, 6, text)

        except Exception as e:
            # Skip any line that causes error — dont crash full PDF
            print(f"[PDF] Skipping line due to error: {e}")
            continue

    return bytes(pdf.output())


def _clean(text: str) -> str:
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*',     r'\1', text)
    text = re.sub(r'`(.*?)`',       r'\1', text)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    text = re.sub(r'#{1,6}\s*',     '',    text)

    replacements = {
        '\u2022': '-',
        '\u2019': "'",
        '\u2018': "'",
        '\u201c': '"',
        '\u201d': '"',
        '\u2013': '-',
        '\u2014': '--',
        '\u2026': '...',
        '\u2192': '->',
        '\u2190': '<-',
        '\u00e9': 'e',
        '\u00e0': 'a',
        '\u00e8': 'e',
        '\u00ea': 'e',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)

    text = text.encode('latin-1', errors='ignore').decode('latin-1')
    return text.strip()