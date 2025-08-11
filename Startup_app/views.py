from django.shortcuts import render
from django.http import HttpResponse
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PyPDF2 import PdfReader
from django.conf import settings
from pdfminer.high_level import extract_text
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import LETTER

load_dotenv()
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro', generation_config={"temperature": 0.3})


# Views
def index(request):
    return render(request, 'Startup_app/index.html')

def form_view(request):
    return render(request, 'Startup_app/form.html')

def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text




def ask_gemini(request):
    if request.method == 'POST':
        prompt = request.POST.get('prompt', '')
        response = model.generate_content(prompt)
        return JsonResponse({'response': response.text})
    return JsonResponse({'error': 'Only POST method allowed'}, status=405)

def resume_analyzer(request):
    ats_score = None
    comments = None
    generated_resume = None
    generated_resume_pdf = None

    if request.method == "POST":
        if "create_resume" in request.POST:
            resume_text = request.session.get("resume_text", "")
            LATEX_TEMPLATE = r"""\documentclass[a4paper,11pt]{article}

\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage[usenames,dvipsnames]{color}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{fancyhdr}

\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}

\addtolength{\oddsidemargin}{-0.5in}
\addtolength{\textwidth}{1in}
\addtolength{\topmargin}{-0.5in}
\addtolength{\textheight}{1in}

\raggedright
\setlength{\tabcolsep}{0in}

\titleformat{\section}{\scshape\raggedright\large}{}{0em}{}[\color{black}\titlerule \vspace{-4pt}]

% Custom commands
\newcommand{\resumeItem}[2]{\item\small{\textbf{#1:} #2}}
\newcommand{\resumeSubheading}[4]{
  \item
    \begin{tabular*}{\textwidth}{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{#3} & \textit{#4} \\
    \end{tabular*}
}
\newcommand{\resumeSubItem}[2]{\resumeItem{#1}{#2}}
\renewcommand{\labelitemii}{$\circ$}
\newcommand{\resumeListStart}{\begin{itemize}[leftmargin=*]}
\newcommand{\resumeListEnd}{\end{itemize}}

\begin{document}

% HEADER
\begin{tabular*}{\textwidth}{l@{\extracolsep{\fill}}r}
  \textbf{\LARGE {Your Name}} & Email: \href{mailto:your@email.com}{your@email.com} \\
  Phone: +91-XXXXXXXXXX & \href{https://github.com/username}{GitHub: username} \\
  & \href{https://linkedin.com/in/username}{LinkedIn: username} \\
\end{tabular*}

% EDUCATION
\section{Education}
\resumeListStart
  \resumeSubheading
    {University Name}{City, Country}
    {Degree / Major}{Start – End}
\resumeListEnd

% SKILLS
\section{Skills}
\resumeListStart
  \resumeItem{Languages}{Python, SQL, R, JavaScript}
  \resumeItem{Frameworks}{Django, Flask, TensorFlow}
  \resumeItem{Tools}{Power BI, Git, Azure}
\resumeListEnd

% EXPERIENCE
\section{Experience}
\resumeListStart
  \resumeSubheading
    {Company Name}{Location}
    {Job Title}{Start – End}
    \resumeListStart
      \item {Key responsibility or achievement.}
      \item {Another responsibility with measurable outcome.}
    \resumeListEnd
\resumeListEnd

% PROJECTS
\section{Projects}
\resumeListStart
  \resumeItem{Project Title}{Short description and tech stack used.}
\resumeListEnd

% ACHIEVEMENTS
\section{Achievements}
\resumeListStart
  \item {Achievement or Certification}
\resumeListEnd

% PUBLICATIONS (Optional)
\section{Publications}
\resumeListStart
  \item {Publication Title – Journal/Conference, Year}
\resumeListEnd

% VOLUNTEER EXPERIENCE (Optional)
\section{Volunteer Experience}
\resumeListStart
  \item {Role – Organization, Description}
\resumeListEnd

\end{document}
"""

            prompt = f"""
You are a professional resume formatter. Rewrite the following resume in ATS-optimized LaTeX format 
using this structure exactly:

{LATEX_TEMPLATE}

Rules:
1. Only include sections where content exists.
2. Do not add placeholders like "Your Name" — use the actual data from the resume.
3. Keep ATS keywords from the original resume.
4. Keep formatting exactly as in the LaTeX template.
5. Do not include explanations or comments — output LaTeX only.

Resume:
{resume_text}
"""
            response = model.generate_content(prompt)
            generated_resume = response.text

            # Store in session for download
            request.session["generated_resume"] = generated_resume
            ats_score = request.session.get("ats_score")
            with tempfile.TemporaryDirectory() as tmpdir:
                tex_path = os.path.join(tmpdir, "resume.tex")
                pdf_path = os.path.join(tmpdir, "resume.pdf")

                with open(tex_path, "w", encoding="utf-8") as f:
                    f.write(generated_resume)

                subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", tex_path],
                    cwd=tmpdir,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

                with open(pdf_path, "rb") as f:
                    pdf_data = f.read()

            # Encode for HTML iframe
            generated_resume_pdf = base64.b64encode(pdf_data).decode("utf-8")

            ats_score = request.session.get("ats_score")

            comments = request.session.get("comments")

        elif "improve" in request.POST:
            resume_text = request.session.get("resume_text", "")

            prompt = f"""
You are an expert resume coach. Analyze the following resume and give detailed suggestions to improve it.

Resume:
{resume_text}
"""
            response = model.generate_content(prompt)
            suggestions = response.text
            ats_score = request.session.get("ats_score")
            comments = request.session.get("comments")

        else:
            resume_file = request.FILES.get("resume")
            if resume_file:
                try:
                    resume_text = extract_text(BytesIO(resume_file.read()))
                except Exception:
                    return render(request, "Startup_app/form.html", {"error": "Failed to extract text from resume."})

                # ATS scoring
                prompt = f"""
                You are an ATS evaluator.

                1. Give only a score (0-100) on the first line.
                2. Then list 3-5 bullet points about strengths and weaknesses.

                Resume:
                {resume_text}
                """
                response = model.generate_content(prompt)
                raw_output = response.text.strip()
                first_line = raw_output.splitlines()[0].strip()
                import re
                match = re.match(r"^\D*(\d{1,3})\D*$", first_line)
                ats_score = match.group(1) if match else "N/A"
                comments = "\n".join(raw_output.splitlines()[1:]).strip()

                # Save for later steps
                request.session["resume_text"] = resume_text
                request.session["ats_score"] = ats_score
                request.session["comments"] = comments

    return render(request, "Startup_app/form.html", {
        "ats_score": ats_score,
        "comments": comments,
        "generated_resume_pdf": generated_resume_pdf

    })




import subprocess
import tempfile


def download_resume_pdf(request):
    latex_code = request.session.get("generated_resume")
    if not latex_code:
        return HttpResponse("No generated resume found.", status=400)

    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = os.path.join(tmpdir, "resume.tex")
        pdf_path = os.path.join(tmpdir, "resume.pdf")

        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(latex_code)

        # Compile LaTeX → PDF
        subprocess.run(["pdflatex", "-interaction=nonstopmode", tex_path], cwd=tmpdir)

        with open(pdf_path, "rb") as f:
            pdf_data = f.read()

    response = HttpResponse(pdf_data, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="ATS_Optimized_Resume.pdf"'
    return response


import base64
