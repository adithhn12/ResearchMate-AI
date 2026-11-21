import io
import os
from typing import Dict, Any
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

class ExportService:
    @staticmethod
    def generate_docx(review_data: Dict[str, Any]) -> io.BytesIO:
        """
        Generate an elegant, professional academic DOCX file from literature review data.
        """
        doc = Document()

        # Set page margins (1 inch)
        for section in doc.sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)

        # Title
        title_text = review_data.get("title", "Literature Review")
        title_p = doc.add_paragraph()
        title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_run = title_p.add_run(title_text)
        title_run.font.size = Pt(22)
        title_run.font.bold = True
        title_run.font.color.rgb = RGBColor(15, 23, 42)  # Navy #0f172a

        # Subtitle
        sub_p = doc.add_paragraph()
        sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        sub_run = sub_p.add_run("Generated with ResearchMate AI — Academic Literature Review")
        sub_run.font.size = Pt(10)
        sub_run.font.italic = True
        sub_run.font.color.rgb = RGBColor(100, 116, 139)

        doc.add_paragraph()  # Blank line

        # Sections
        sections = [
            ("1. Introduction", review_data.get("introduction")),
            ("2. Background and Related Work", review_data.get("background_related_work")),
            ("3. Thematic Literature Analysis", review_data.get("thematic_analysis")),
            ("4. Comparison of Existing Approaches", review_data.get("comparison_existing_approaches")),
            ("5. Research Limitations", review_data.get("research_limitations")),
            ("6. Research Gaps & Open Opportunities", review_data.get("research_gaps")),
            ("7. Conclusion", review_data.get("conclusion")),
            ("8. References", review_data.get("references"))
        ]

        for sec_title, sec_content in sections:
            if not sec_content:
                continue

            h = doc.add_heading(level=1)
            h_run = h.add_run(sec_title)
            h_run.font.size = Pt(14)
            h_run.font.bold = True
            h_run.font.color.rgb = RGBColor(30, 58, 138)  # Deep Blue #1e3a8a

            # Split paragraphs
            paragraphs = sec_content.strip().split("\n\n")
            for p_text in paragraphs:
                if not p_text.strip():
                    continue
                p = doc.add_paragraph()
                p.paragraph_format.line_spacing = 1.15
                p.paragraph_format.space_after = Pt(6)
                
                # Check for bullet points
                if p_text.strip().startswith("- ") or p_text.strip().startswith("* "):
                    for line in p_text.strip().split("\n"):
                        clean_line = line.lstrip("- *").strip()
                        bp = doc.add_paragraph(clean_line, style="List Bullet")
                        bp.paragraph_format.space_after = Pt(3)
                else:
                    run = p.add_run(p_text.strip())
                    run.font.size = Pt(11)
                    run.font.color.rgb = RGBColor(30, 41, 59)

        file_stream = io.BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream

    @staticmethod
    def generate_pdf(review_data: Dict[str, Any]) -> io.BytesIO:
        """
        Generate a publication-ready PDF using ReportLab.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=54,
            leftMargin=54,
            topMargin=54,
            bottomMargin=54
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#0f172a'),
            alignment=1,
            spaceAfter=8
        )

        sub_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#64748b'),
            alignment=1,
            spaceAfter=18
        )

        h1_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=18,
            textColor=colors.HexColor('#1e3a8a'),
            spaceBefore=14,
            spaceAfter=6,
            keepWithNext=True
        )

        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=15,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=8
        )

        bullet_style = ParagraphStyle(
            'Bullet',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor('#334155'),
            leftIndent=15,
            spaceAfter=4
        )

        story = []

        # Title and Subtitle
        title_text = review_data.get("title", "Literature Review")
        story.append(Paragraph(title_text, title_style))
        story.append(Paragraph("Generated by ResearchMate AI — AI-Powered Academic Assistant", sub_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceAfter=14))

        sections = [
            ("1. Introduction", review_data.get("introduction")),
            ("2. Background and Related Work", review_data.get("background_related_work")),
            ("3. Thematic Literature Analysis", review_data.get("thematic_analysis")),
            ("4. Comparison of Existing Approaches", review_data.get("comparison_existing_approaches")),
            ("5. Research Limitations", review_data.get("research_limitations")),
            ("6. Research Gaps & Open Opportunities", review_data.get("research_gaps")),
            ("7. Conclusion", review_data.get("conclusion")),
            ("8. References", review_data.get("references"))
        ]

        for sec_title, sec_content in sections:
            if not sec_content:
                continue

            story.append(Paragraph(sec_title, h1_style))
            paragraphs = sec_content.strip().split("\n\n")
            for p_text in paragraphs:
                if not p_text.strip():
                    continue

                # Check bullet lines
                if p_text.strip().startswith("- ") or p_text.strip().startswith("* "):
                    for line in p_text.strip().split("\n"):
                        clean_line = line.lstrip("- *").strip()
                        # escape XML special chars
                        clean_line = clean_line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                        story.append(Paragraph(f"• {clean_line}", bullet_style))
                else:
                    clean_text = p_text.strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    story.append(Paragraph(clean_text, body_style))

            story.append(Spacer(1, 6))

        doc.build(story)
        buffer.seek(0)
        return buffer

export_service = ExportService()
