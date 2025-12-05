# pdf_generator.py

import io
import markdown2
from bs4 import BeautifulSoup

from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

# Frontend expects this list
PDF_TEMPLATES = ["classic", "modern"]


def _build_styles(template: str):
    """
    Build style objects depending on the selected template.
    Classic = serif / conservative
    Modern  = sans-serif / subtle accent color
    """
    styles = getSampleStyleSheet()

    # Base body text
    base = styles["Normal"]
    base.fontSize = 11
    base.leading = 14

    if template == "modern":
        # Modern: sans-serif, slightly more airy, subtle gray text
        base.fontName = "Helvetica"
        base.textColor = colors.HexColor("#222222")

        heading1 = ParagraphStyle(
            "Heading1",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0D47A1"),  # strong blue accent
            spaceBefore=0,
            spaceAfter=6,
        )

        heading2 = ParagraphStyle(
            "Heading2",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#1565C0"),
            spaceBefore=10,
            spaceAfter=4,
        )

        bullet_style = ParagraphStyle(
            "Bullet",
            parent=base,
            leftIndent=16,
            bulletIndent=8,
            spaceBefore=2,
            spaceAfter=2,
        )

    else:
        # Classic: serif font, neutral black text, conservative spacing
        base.fontName = "Times-Roman"
        base.textColor = colors.black

        heading1 = ParagraphStyle(
            "Heading1",
            parent=styles["Heading1"],
            fontName="Times-Bold",
            fontSize=20,
            leading=24,
            textColor=colors.black,
            spaceBefore=0,
            spaceAfter=8,
        )

        heading2 = ParagraphStyle(
            "Heading2",
            parent=styles["Heading2"],
            fontName="Times-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.black,
            spaceBefore=8,
            spaceAfter=4,
        )

        bullet_style = ParagraphStyle(
            "Bullet",
            parent=base,
            leftIndent=14,
            bulletIndent=6,
            spaceBefore=1,
            spaceAfter=1,
        )

    return base, heading1, heading2, bullet_style


def _markdown_to_flowables(md_text: str, template: str):
    """
    Convert markdown into a list of ReportLab flowables.
    Supports headings, paragraphs, and bullet lists,
    with template-specific styling.
    """
    base, heading1, heading2, bullet_style = _build_styles(template)

    flow = []

    # Convert markdown → HTML
    html = markdown2.markdown(
        md_text,
        extras=["fenced-code-blocks", "strike", "underline", "cuddled-lists"],
    )

    soup = BeautifulSoup(html, "html.parser")

    first_h1_seen = False

    for elem in soup.children:
        # Skip pure whitespace text nodes
        if isinstance(elem, str):
            text = elem.strip()
            if text:
                flow.append(Paragraph(text, base))
                flow.append(Spacer(1, 4))
            continue

        name = elem.name

        if name == "h1":
            text = elem.get_text(strip=True)
            if not text:
                continue

            # For modern: treat the first H1 as the "name" header with a rule under it
            if template == "modern" and not first_h1_seen:
                first_h1_seen = True
                flow.append(Paragraph(text, heading1))
                # subtle horizontal rule
                flow.append(
                    HRFlowable(
                        width="100%",
                        thickness=0.8,
                        color=colors.HexColor("#B0BEC5"),
                        spaceBefore=4,
                        spaceAfter=10,
                    )
                )
            else:
                # Subsequent H1s are just normal section headings
                flow.append(Paragraph(text, heading1))
                flow.append(Spacer(1, 6))

        elif name in ("h2", "h3"):
            txt = elem.get_text(strip=True)
            if txt:
                # Optional: uppercase section titles for modern template
                if template == "modern":
                    txt = txt.upper()
                flow.append(Paragraph(txt, heading2))
                flow.append(Spacer(1, 4))

        elif name == "ul":
            for li in elem.find_all("li"):
                txt = li.get_text(strip=True)
                if txt:
                    flow.append(Paragraph(f"• {txt}", bullet_style))
            flow.append(Spacer(1, 4))

        elif name == "p":
            txt = elem.get_text(strip=True)
            if txt:
                flow.append(Paragraph(txt, base))
                flow.append(Spacer(1, 4))

        else:
            # Fallback: treat unknown tags as simple paragraphs
            txt = elem.get_text(strip=True)
            if txt:
                flow.append(Paragraph(txt, base))
                flow.append(Spacer(1, 4))

    if not flow:
        flow.append(Paragraph(" ", base))

    return flow


def generate_pdf(content: str, template: str = "classic") -> bytes:
    """
    Generate a PDF (as bytes) from markdown content.
    Uses different styling based on template: 'classic' or 'modern'.
    """
    if not isinstance(content, str) or not content.strip():
        raise ValueError("PDF content is empty")

    buffer = io.BytesIO()

    # You can tweak margins per template if you want to
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    flowables = _markdown_to_flowables(content, template)

    doc.build(flowables)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    if not pdf_bytes:
        raise ValueError("Failed to generate PDF bytes")

    return pdf_bytes
