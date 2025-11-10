# Week 3 - Resume Templates: Visual Comparison

This document shows the visual difference between the two implemented templates.

---

## Same Candidate, Two Different Templates

**Candidate Information:**
- Name: Sarah Johnson
- Education: Bachelor of Science in Computer Science, UC Berkeley, 2018-2022, GPA: 3.8/4.0, Dean's List
- Experience: Software Engineer at TechCorp (2022-Present) and Intern at StartupXYZ (Summer 2021)
- Skills: Python, JavaScript, TypeScript, Java, Go, React, Node.js, Django, Flask, AWS, Docker, Kubernetes, etc.

---

## Template 1: Chronological Format

**Focus:** Work history in reverse chronological order

**Section Order:**
1. Name
2. 📚 Education
3. 💼 Professional Experience
4. 🛠 Technical Skills

**Best For:**
- Traditional career progression
- Consistent work history
- Linear career path

**Output:**
```markdown
# Sarah Johnson

---

## 📚 Education

Bachelor of Science in Computer Science, UC Berkeley, 2018-2022
GPA: 3.8/4.0, Dean's List

---

## 💼 Professional Experience

Software Engineer at TechCorp (2022-Present): Developed microservices architecture 
serving 1M+ users. Led migration to Kubernetes resulting in 40% cost reduction. 
Mentored 3 junior developers.

Software Engineering Intern at StartupXYZ (Summer 2021): Built real-time analytics 
dashboard using React and Node.js. Optimized database queries improving response 
time by 60%.

---

## 🛠 Technical Skills

Programming: Python, JavaScript, TypeScript, Java, Go
Frameworks: React, Node.js, Django, Flask, Spring Boot
Cloud & DevOps: AWS, Docker, Kubernetes, CI/CD, Terraform
Databases: PostgreSQL, MongoDB, Redis
Soft Skills: Team Leadership, Agile/Scrum, Technical Writing

---
```

---

## Template 2: Functional Format

**Focus:** Skills and competencies over chronological timeline

**Section Order:**
1. Name
2. 🛠 Core Competencies & Skills
3. 💼 Relevant Experience
4. 📚 Education & Credentials

**Best For:**
- Career changers
- Employment gaps
- Diverse skill sets
- Emphasizing transferable skills

**Output:**
```markdown
# Sarah Johnson

---

## 🛠 Core Competencies & Skills

Programming: Python, JavaScript, TypeScript, Java, Go
Frameworks: React, Node.js, Django, Flask, Spring Boot
Cloud & DevOps: AWS, Docker, Kubernetes, CI/CD, Terraform
Databases: PostgreSQL, MongoDB, Redis
Soft Skills: Team Leadership, Agile/Scrum, Technical Writing

---

## 💼 Relevant Experience

Software Engineer at TechCorp (2022-Present): Developed microservices architecture 
serving 1M+ users. Led migration to Kubernetes resulting in 40% cost reduction. 
Mentored 3 junior developers.

Software Engineering Intern at StartupXYZ (Summer 2021): Built real-time analytics 
dashboard using React and Node.js. Optimized database queries improving response 
time by 60%.

---

## 📚 Education & Credentials

Bachelor of Science in Computer Science, UC Berkeley, 2018-2022
GPA: 3.8/4.0, Dean's List

---
```

---

## Key Differences

| Aspect | Chronological | Functional |
|--------|---------------|------------|
| **Primary Focus** | Work history timeline | Skills & competencies |
| **Education Placement** | After name, before experience | Last section |
| **Skills Placement** | Last section | First section after name |
| **Experience Format** | Chronological order emphasized | Relevant to skills highlighted |
| **Best Use Case** | Traditional careers | Career transitions |
| **Section Count** | 3 main sections | 3 main sections |
| **Emoji Icons** | 📚 💼 🛠 | 🛠 💼 📚 |

---

## How Users Select Templates

In the Flutter UI, users see a dropdown with:

```
┌─────────────────────────────────────┐
│ Select Resume Template ▼            │
├─────────────────────────────────────┤
│ • Chronological                     │
│ • Functional                        │
└─────────────────────────────────────┘

Template Description:
┌─────────────────────────────────────────────────────────────┐
│ Traditional format emphasizing work history in reverse      │
│ chronological order. Best for those with consistent career  │
│ progression.                                                │
└─────────────────────────────────────────────────────────────┘
```

---

## Technical Implementation

Both templates are:
- ✅ Generated in **Markdown** format
- ✅ Rendered beautifully with **flutter_markdown** in the UI
- ✅ Accessible via the `/generate-resume` API endpoint
- ✅ Available with or without AI API key (mock data)
- ✅ Ready for AI enhancement in Week 5

---

## Next Steps

Week 4 will add **Cover Letter Generation** with similar template support!
