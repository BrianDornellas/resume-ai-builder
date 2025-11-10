"""
Resume template formatting module.
Provides different resume layouts: chronological and functional.
Returns resumes in Markdown format for better rendering.
"""


def format_resume_mock(name, education, experience, skills, template='chronological'):
    """
    Generate a mock resume in the specified template format.
    Used when AI API key is not configured.
    
    Args:
        name: Candidate's full name
        education: Education details
        experience: Work experience details
        skills: Technical and professional skills
        template: Template type ('chronological' or 'functional')
    
    Returns:
        Formatted resume in Markdown
    """
    if template == 'functional':
        return _format_functional_mock(name, education, experience, skills)
    else:  # chronological is default
        return _format_chronological_mock(name, education, experience, skills)


def _format_chronological_mock(name, education, experience, skills):
    """
    Generate a chronological resume format.
    Emphasizes work history in reverse chronological order.
    """
    resume = f"""# {name}

---

## 📚 Education

{education}

---

## 💼 Professional Experience

{experience}

---

## 🛠 Technical Skills

{skills}

---

*Mock resume generated using Chronological template. Add your OpenAI API key to enable AI-powered generation.*
"""
    return resume


def _format_functional_mock(name, education, experience, skills):
    """
    Generate a functional resume format.
    Emphasizes skills and competencies over chronological work history.
    """
    resume = f"""# {name}

---

## 🛠 Core Competencies & Skills

{skills}

---

## 💼 Relevant Experience

{experience}

---

## 📚 Education & Credentials

{education}

---

*Mock resume generated using Functional template. Add your OpenAI API key to enable AI-powered generation.*
"""
    return resume


def create_ai_prompt(name, education, experience, skills, template='chronological'):
    """
    Create an AI prompt based on the selected template.
    
    Args:
        name: Candidate's full name
        education: Education details
        experience: Work experience details
        skills: Technical and professional skills
        template: Template type ('chronological' or 'functional')
    
    Returns:
        Formatted prompt string for AI
    """
    if template == 'functional':
        return _create_functional_prompt(name, education, experience, skills)
    else:  # chronological is default
        return _create_chronological_prompt(name, education, experience, skills)


def _create_chronological_prompt(name, education, experience, skills):
    """Create prompt for chronological resume format."""
    prompt = f"""Generate a professional resume in Markdown format using a CHRONOLOGICAL layout.

**Candidate Information:**
- Name: {name}
- Education: {education}
- Experience: {experience}
- Skills: {skills}

**Requirements:**
1. Use Markdown formatting (headers, bold, lists, etc.)
2. Follow chronological format with sections in this order:
   - Name (as H1 header)
   - Professional Summary (brief, 2-3 sentences)
   - Professional Experience (reverse chronological order)
   - Education
   - Technical Skills
3. Use emojis sparingly for section headers
4. Make it ATS-friendly and professional
5. Include concrete achievements and metrics where applicable
6. Keep the total length reasonable for a resume

Please create a well-formatted, professional resume."""
    return prompt


def _create_functional_prompt(name, education, experience, skills):
    """Create prompt for functional resume format."""
    prompt = f"""Generate a professional resume in Markdown format using a FUNCTIONAL layout.

**Candidate Information:**
- Name: {name}
- Education: {education}
- Experience: {experience}
- Skills: {skills}

**Requirements:**
1. Use Markdown formatting (headers, bold, lists, etc.)
2. Follow functional format with sections in this order:
   - Name (as H1 header)
   - Professional Summary (brief, 2-3 sentences)
   - Core Competencies & Skills (grouped by category)
   - Relevant Experience (organized by skill areas, not chronologically)
   - Education & Credentials
3. Emphasize transferable skills and competencies
4. Use emojis sparingly for section headers
5. Make it ATS-friendly and professional
6. Group experiences by skill/competency area rather than by date
7. Keep the total length reasonable for a resume

Please create a well-formatted, professional resume."""
    return prompt
