from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import os, json, re, base64
from dotenv import load_dotenv
import google.generativeai as genai
from PyPDF2 import PdfReader
from django.conf import settings
from pdfminer.high_level import extract_text
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import LETTER

load_dotenv()
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro', generation_config={"temperature": 0.3})


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





def resume_analyzer(request):
    ats_score = None
    comments = None
    generated_resume_pdf = None

    if request.method == "POST":
        # Handle resume creation
        if "create_resume" in request.POST:
            resume_text = request.session.get("resume_text", "")

            prompt = f"""
You are an expert resume writer specializing in ATS optimization.
Rewrite the following resume to maximize ATS compatibility and recruiter appeal for a target role.
Rules:
1. Preserve all correct personal details and experience.
2. Use standard section headings in ALL CAPS: CONTACT INFORMATION, PROFESSIONAL SUMMARY, SKILLS, EXPERIENCE, EDUCATION, PROJECTS, ACHIEVEMENTS.
3. Skills: Include only highly relevant, industry-standard keywords from the resume AND job description trends.
4. Experience: 
   - List most recent experience first.
   - For each role: JOB TITLE, COMPANY, LOCATION, DATES.
   - Use 3–6 bullet points starting with strong action verbs.
   - Quantify results wherever possible (e.g., “Increased model accuracy by 15%”).
5. Professional Summary: 3–4 impactful lines with top achievements, core skills, and target keywords.
6. Education: Degree, institution, location, dates.
7. Ensure the output is plain text, no markdown, no tables, no fancy formatting.
8. Keep layout clean, easy to parse, and recruiter-friendly.

Resume to optimize:
{resume_text}
"""
            response = model.generate_content(prompt)
            generated_resume = response.text

            request.session["generated_resume"] = generated_resume
            ats_score = request.session.get("ats_score")

            # Generate PDF using ReportLab (No LaTeX)
            pdf_buffer = BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=LETTER)
            styles = getSampleStyleSheet()
            story = []

            for line in generated_resume.split("\n"):
                if line.strip().isupper():  # Section heading
                    story.append(Paragraph(line.strip(), styles["Heading2"]))
                    story.append(Spacer(1, 6))
                elif line.strip().startswith("* "):  # Bullet point
                    story.append(Paragraph("• " + line.strip()[2:], styles["Normal"]))
                elif line.strip():
                    story.append(Paragraph(line.strip(), styles["Normal"]))
                story.append(Spacer(1, 4))

            doc.build(story)
            pdf_data = pdf_buffer.getvalue()
            pdf_buffer.close()

            generated_resume_pdf = base64.b64encode(pdf_data).decode("utf-8")
            comments = request.session.get("comments")

        # Handle improvement suggestions
        elif "improve" in request.POST:
            resume_text = request.session.get("resume_text", "")
            prompt = f"You are an expert resume coach. Analyze the following resume and give detailed improvement suggestions:\n\n{resume_text}"
            response = model.generate_content(prompt)
            comments = response.text
            ats_score = request.session.get("ats_score")

        # Handle initial upload & ATS scoring
        else:
            resume_file = request.FILES.get("resume")
            if resume_file:
                try:
                    resume_text = extract_text(BytesIO(resume_file.read()))
                except Exception:
                    return render(request, "Startup_app/form.html", {"error": "Failed to extract text from resume."})

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
                match = re.match(r"^\D*(\d{1,3})\D*$", first_line)
                ats_score = match.group(1) if match else "N/A"
                comments = "\n".join(raw_output.splitlines()[1:]).strip()

                request.session["resume_text"] = resume_text
                request.session["ats_score"] = ats_score
                request.session["comments"] = comments

    return render(request, "Startup_app/form.html", {
        "ats_score": ats_score,
        "comments": comments,
        "generated_resume_pdf": generated_resume_pdf
    })


def download_resume_pdf(request):
    resume_content = request.session.get("generated_resume")
    if not resume_content:
        return HttpResponse("No generated resume found.", status=400)

    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=LETTER)
    styles = getSampleStyleSheet()
    story = []

    for line in resume_content.split("\n"):
        if line.strip():
            story.append(Paragraph(line.strip(), styles["Normal"]))
            story.append(Spacer(1, 6))

    doc.build(story)
    pdf_data = pdf_buffer.getvalue()
    pdf_buffer.close()

    response = HttpResponse(pdf_data, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="ATS_Optimized_Resume.pdf"'
    return response
