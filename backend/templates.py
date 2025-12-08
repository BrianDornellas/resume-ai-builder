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

## Education

{education}

---

## Professional Experience

{experience}

---

## Technical Skills

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

## Core Competencies & Skills

{skills}

---

## Relevant Experience

{experience}

---

## Education & Credentials

{education}

---

*Mock resume generated using Functional template. Add your OpenAI API key to enable AI-powered generation.*
"""
    return resume


def create_ai_prompt(name, education, experience, skills, template='chronological'):
    """
    Create an AI prompt based on the selected template. Do not include emojis in the output.
    
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
3. Do not include emojis in the output.
4. Make it ATS-friendly and professional
5. Include concrete achievements and metrics where applicable
6. Keep the total length reasonable for a resume

Please create a well-formatted, professional resume."""
    return prompt


def _create_functional_prompt(name, education, experience, skills):
    """Create prompt for a functional resume format."""
    prompt = f"""Generate a professional resume in Markdown format using a FUNCTIONAL-STYLE layout.
        Candidate Information:
        - Name: {name}
        - Education: {education}
        - Experience: {experience}
        - Skills: {skills}

        Requirements:
        1. Use clean Markdown formatting:
        - Use "# " for the candidate name as the main header.
        - Use "## " for section headers.
        - Use bullet points for duties, achievements, and skills.
        2. The sections MUST appear in this order, and each section name should be exactly:

<<<<<<< HEAD
        # {name}
        ## Professional Summary
        ## Key Skills
        ## Professional Experience
        ## Education
=======
**Requirements:**
1. Use Markdown formatting (headers, bold, lists, etc.)
2. Follow functional format with sections in this order:
   - Name (as H1 header)
   - Professional Summary (brief, 2-3 sentences)
   - Core Competencies & Skills (grouped by category)
   - Relevant Experience (organized by skill areas, not chronologically)
   - Education & Credentials
3. Emphasize transferable skills and competencies
4. Do not include emojis in the output.
5. Make it ATS-friendly and professional
6. Group experiences by skill/competency area rather than by date
7. Keep the total length reasonable for a resume
>>>>>>> 22a27ef8ed00107ca62be6acd41d0f0aba76e2e5

        3. Professional Summary:
        - 2–3 concise sentences summarizing strengths, teaching/communication ability, and overall value.
        4. Key Skills:
        - Present skills in a concise, resume-like way.
        - Use either short bullet points or grouped bullets like:
            - Classroom Management, Curriculum Development, Student Support
            - Record Keeping, Microsoft Office, Data Entry
        5. Professional Experience:
        - Even though this is a functional-style resume, it should still LOOK like a normal resume section.
        - For each role, use a single line like:
            **JOB TITLE** | Organization | Dates
        - Under each role, include 3–6 bullet points describing responsibilities and achievements.
        - Use action verbs and concrete outcomes where possible.
        6. Education:
        - Use 1–3 short lines, e.g.:
            UNIVERSITY NAME | Degree, Graduation date
            - Optional GPA or minor on a separate line.
        7. Keep the layout compact and similar in density to a standard chronological resume.
        8. Do NOT use tables or multi-column layouts.
        9. Keep it ATS-friendly, professional, and easy to skim.

        Return ONLY the Markdown resume, with no extra explanation."""
    return prompt


