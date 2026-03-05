import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from ..models.schemas import ResearchReport

class FileWriter:
    @staticmethod
    def write_markdown(report: ResearchReport, path: str) -> str:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        lines = [
            f"# {report.title}",
            f"\n*Generated at {report.generated_at} | Word Count: {report.word_count}*\n",
            "## Executive Summary",
            report.executive_summary,
            ""
        ]
        
        for section in report.sections:
            lines.append(f"## {section.heading}")
            lines.append(section.content)
            lines.append("")
            
        lines.append("## Sources")
        for src in report.sources:
            lines.append(f"{src.number}. [{src.title}]({src.url}) - retrieved {src.accessed_at}")
            
        content = "\n".join(lines)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return path

    @staticmethod
    def write_pdf(report: ResearchReport, path: str) -> str:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        doc = SimpleDocTemplate(path, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=24, spaceAfter=20)
        heading_style = styles['Heading2']
        body_style = styles['Normal']
        
        story = []
        
        # Title
        story.append(Paragraph(report.title, title_style))
        story.append(Spacer(1, 12))
        
        # Exec Summary
        story.append(Paragraph("Executive Summary", heading_style))
        story.append(Paragraph(report.executive_summary, body_style))
        story.append(Spacer(1, 12))
        
        # Sections
        for section in report.sections:
            story.append(Paragraph(section.heading, heading_style))
            # Split content by double newlines for separate paragraphs
            for p_text in section.content.split("\n\n"):
                if p_text.strip():
                    # Replace markdown bold with reportlab bold
                    p_text_clean = p_text.replace("**", "<b>", 1).replace("**", "</b>", 1) if p_text.count("**") >= 2 else p_text
                    story.append(Paragraph(p_text_clean, body_style))
            story.append(Spacer(1, 12))
            
        # Sources
        story.append(Paragraph("Sources", heading_style))
        for src in report.sources:
            src_text = f"[{src.number}] {src.title} - {src.url}"
            story.append(Paragraph(src_text, body_style))
            
        doc.build(story)
        return path
