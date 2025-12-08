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
<<<<<<< HEAD
    if not isinstance(content, str) or not content.strip():
        raise ValueError("PDF content is empty")

    buffer = io.BytesIO()

    # You can tweak margins per template if you want to
=======
    if template not in PDF_TEMPLATES:
        raise ValueError(f"Unknown template: {template}. Available: {PDF_TEMPLATES}")
    
    # Clean up any literal placeholder markers that might be in the content from previous processing
    # Handle all marker formats for backward compatibility
    content = content.replace('§§§BOLDSTART§§§', '**').replace('§§§BOLDEND§§§', '**')
    content = content.replace('<<<BOLD_START>>>', '**').replace('<<<BOLD_END>>>', '**')
    content = content.replace('__BOLD_START__', '**').replace('__BOLD_END__', '**')
    content = content.replace('BOLD_START', '').replace('BOLD_END', '')
    # Also handle escaped versions that might appear
    content = content.replace('&lt;&lt;&lt;BOLD_START&gt;&gt;&gt;', '**').replace('&lt;&lt;&lt;BOLD_END&gt;&gt;&gt;', '**')
    
    buffer = BytesIO()
>>>>>>> 22a27ef8ed00107ca62be6acd41d0f0aba76e2e5
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

<<<<<<< HEAD
    return pdf_bytes
=======

def _parse_content(
    content: str,
    title_style: ParagraphStyle,
    section_style: ParagraphStyle,
    body_style: ParagraphStyle,
    bullet_style: ParagraphStyle,
    use_hr: bool = False,
) -> list:
    """
    Parse content (plain text or Markdown-like) into a ReportLab story.
    
    Handles:
    - Lines starting with '# ' as titles
    - Lines starting with '## ' or '### ' as section headers
    - Lines starting with '- ' or '* ' as bullet points
    - '---' as horizontal rules
    - Other lines as body text
    - Cleans up Markdown artifacts
    """
    story = []
    lines = content.strip().split('\n')
    first_title = True
    
    for line in lines:
        line = line.rstrip()
        
        # Skip empty lines but add small spacing
        if not line:
            story.append(Spacer(1, 6))
            continue
        
        # Skip HTML comments
        if line.strip().startswith('<!--') or line.strip().endswith('-->'):
            continue
        
        # Horizontal rule
        if line.strip() == '---' or line.strip() == '___' or line.strip() == '***':
            if use_hr:
                story.append(Spacer(1, 4))
                story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
                story.append(Spacer(1, 4))
            else:
                story.append(Spacer(1, 8))
            continue
        
        # Title (H1)
        if line.startswith('# '):
            text = _clean_markdown(_strip_emoji(line[2:].strip()))
            if first_title:
                story.append(Paragraph(text, title_style))
                first_title = False
            else:
                story.append(Paragraph(text, section_style))
            continue
        
        # Section header (H2 or H3)
        if line.startswith('## ') or line.startswith('### '):
            header_text = line.lstrip('#').strip()
            text = _clean_markdown(_strip_emoji(header_text))
            story.append(Paragraph(text, section_style))
            continue
        
        # Bullet point (handle various bullet styles)
        if line.lstrip().startswith('- ') or line.lstrip().startswith('* ') or line.lstrip().startswith('• '):
            # Remove leading whitespace and bullet marker
            text_content = line.lstrip()
            for prefix in ['- ', '* ', '• ']:
                if text_content.startswith(prefix):
                    text_content = text_content[len(prefix):]
                    break
            text = _clean_markdown(text_content.strip())
            story.append(Paragraph(f"• {text}", bullet_style))
            continue
        
        # Regular body text - convert bold, clean markdown
        text = _clean_markdown(line)
        story.append(Paragraph(text, body_style))
    
    return story


def _clean_markdown(text: str) -> str:
    """
    Clean markdown artifacts and prepare text for PDF rendering.
    Handles bold conversion and XML escaping properly.
    """
    # Normalize Unicode characters first
    text = _normalize_unicode(text)
    
    # Handle bold conversion (before escaping)
    text = _convert_bold(text)
    
    # Escape XML characters
    text = _escape_xml(text)
    
    # Re-add bold tags after escaping (§ doesn't need escaping)
    text = text.replace('§§§BOLDSTART§§§', '<b>').replace('§§§BOLDEND§§§', '</b>')
    
    # Clean up common Markdown artifacts that might have been missed
    # Remove stray asterisks that aren't part of bold
    text = re.sub(r'(?<!\*)\*(?!\*)', '', text)
    
    return text


def _strip_emoji(text: str) -> str:
    """Remove common emoji characters from text."""
    emoji_chars = ['📚', '💼', '🛠', '📋', '🎓', '🏆', '📧', '📱', '🌐', '👤']
    for emoji in emoji_chars:
        text = text.replace(emoji, '')
    return text.strip()


def _escape_xml(text: str) -> str:
    """Escape XML special characters for ReportLab Paragraph."""
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text


def _convert_bold(text: str) -> str:
    """
    Convert **text** to placeholder markers for bold (to be converted after escaping).
    Uses markers that won't be affected by XML escaping.
    """
    # Use markers without < > characters to avoid XML escaping issues
    # Replace **text** with placeholder markers (non-greedy to handle multiple instances)
    text = re.sub(r'\*\*(.+?)\*\*', r'§§§BOLDSTART§§§\1§§§BOLDEND§§§', text)
    
    # Also handle __text__ for bold (less common but valid markdown)
    # Use word boundaries and non-greedy match to be more specific
    text = re.sub(r'\b__(.+?)__\b', r'§§§BOLDSTART§§§\1§§§BOLDEND§§§', text)
    
    return text


def _normalize_unicode(text: str) -> str:
    """
    Normalize Unicode characters to their closest ASCII equivalents for better PDF compatibility.
    """
    # Replace common Unicode characters with ASCII equivalents
    replacements = {
        '\u2013': '-',  # en-dash
        '\u2014': '--', # em-dash
        '\u2018': "'",  # left single quote
        '\u2019': "'",  # right single quote
        '\u201c': '"',  # left double quote
        '\u201d': '"',  # right double quote
        '\u2022': '•',  # bullet (keep this one)
        '\u25a0': '',   # black square ■ - remove it
        '\u2026': '...', # ellipsis
    }
    
    for unicode_char, ascii_char in replacements.items():
        text = text.replace(unicode_char, ascii_char)
    
    return text
>>>>>>> 22a27ef8ed00107ca62be6acd41d0f0aba76e2e5
