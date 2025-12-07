"""
PDF generation module for resumes and cover letters.
Provides two templates: 'classic' and 'modern'.
"""

import re
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable


# Available PDF templates
PDF_TEMPLATES = ["classic", "modern"]


def generate_pdf(content: str, template: str = "classic") -> bytes:
    """
    Generate a PDF from content using the specified template.
    
    Args:
        content: Plain text or Markdown-like content for the document.
        template: Template name ('classic' or 'modern').
    
    Returns:
        PDF as bytes.
    
    Raises:
        ValueError: If template is not recognized.
    """
    if template not in PDF_TEMPLATES:
        raise ValueError(f"Unknown template: {template}. Available: {PDF_TEMPLATES}")
    
    # Clean up any literal placeholder markers that might be in the content
    content = content.replace('__BOLD_START__', '**').replace('__BOLD_END__', '**')
    content = content.replace('BOLD_START', '').replace('BOLD_END', '')
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )
    
    if template == "modern":
        story = _build_modern_story(content)
    else:
        story = _build_classic_story(content)
    
    doc.build(story)
    return buffer.getvalue()


def _build_classic_story(content: str) -> list:
    """
    Build a classic-styled PDF story.
    Traditional, conservative layout with serif fonts.
    """
    styles = getSampleStyleSheet()
    
    # Classic styles
    title_style = ParagraphStyle(
        'ClassicTitle',
        parent=styles['Heading1'],
        fontName='Times-Bold',
        fontSize=18,
        spaceAfter=6,
        textColor=colors.black,
    )
    
    section_style = ParagraphStyle(
        'ClassicSection',
        parent=styles['Heading2'],
        fontName='Times-Bold',
        fontSize=12,
        spaceBefore=12,
        spaceAfter=6,
        textColor=colors.black,
    )
    
    body_style = ParagraphStyle(
        'ClassicBody',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=10,
        leading=14,
        spaceAfter=4,
    )
    
    bullet_style = ParagraphStyle(
        'ClassicBullet',
        parent=body_style,
        leftIndent=20,
        bulletIndent=10,
    )
    
    return _parse_content(content, title_style, section_style, body_style, bullet_style, use_hr=True)


def _build_modern_story(content: str) -> list:
    """
    Build a modern-styled PDF story.
    Clean, contemporary layout with sans-serif fonts and accent colors.
    """
    styles = getSampleStyleSheet()
    
    # Modern styles with accent color
    accent_color = colors.HexColor('#2563EB')  # Blue accent
    
    title_style = ParagraphStyle(
        'ModernTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        spaceAfter=8,
        textColor=accent_color,
    )
    
    section_style = ParagraphStyle(
        'ModernSection',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        spaceBefore=14,
        spaceAfter=6,
        textColor=accent_color,
    )
    
    body_style = ParagraphStyle(
        'ModernBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        spaceAfter=4,
    )
    
    bullet_style = ParagraphStyle(
        'ModernBullet',
        parent=body_style,
        leftIndent=20,
        bulletIndent=10,
    )
    
    return _parse_content(content, title_style, section_style, body_style, bullet_style, use_hr=False)


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
    
    # Re-add bold tags after escaping
    text = text.replace('<<<BOLD_START>>>', '<b>').replace('<<<BOLD_END>>>', '</b>')
    
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
    Also handles other common Markdown formatting.
    """
    # Replace **text** with placeholder markers (non-greedy to handle multiple instances)
    text = re.sub(r'\*\*(.+?)\*\*', r'<<<BOLD_START>>>\1<<<BOLD_END>>>', text)
    # Also handle __text__ for bold (less common but valid) - use non-greedy match
    # But be careful not to match our placeholders
    text = re.sub(r'(?<!<)__(.+?)__(?!>)', r'<<<BOLD_START>>>\1<<<BOLD_END>>>', text)
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
