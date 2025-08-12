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

        # ==== Handle resume improvement & PDF generation ====
        if "create_resume" in request.POST:
            resume_text = request.session.get("resume_text", "")

            prompt = f"""
            You are an expert resume writer and ATS optimization specialist.

            Your task:
            - Rewrite the resume below into a FINAL, fully polished, job-ready version.
            - DO NOT include placeholders like [Institution Name] or [Job Title] — instead, fill gaps with realistic, industry-appropriate content.
            - Use only standard ATS-friendly section headings in ALL CAPS: CONTACT INFORMATION, PROFESSIONAL SUMMARY, SKILLS, EXPERIENCE, EDUCATION, PROJECTS, ACHIEVEMENTS.
            - Between each section, insert a plain text divider: ========================== (this will later be styled as a blue line in the PDF).
            - Keep layout strictly single-column, plain text, and ATS-compliant (no tables, columns, or graphics).
            - Write Experience bullets starting with strong action verbs, including measurable results where possible.
            - Skills section must include relevant industry keywords for tech/business roles.
            - Professional Summary: 3–4 impactful lines summarizing top achievements, expertise, and career goals.
            - Ensure every section has meaningful, professional-sounding content — infer details if missing.
            - DO NOT add suggestions, improvement notes, or extra commentary — only output the final resume.

            Resume to rewrite:
            {resume_text}
            """

            response = model.generate_content(prompt)
            generated_resume = response.text.strip()

            # Save to session
            request.session["generated_resume"] = generated_resume
            ats_score = request.session.get("ats_score")
            comments = request.session.get("comments")

            # PDF creation
            pdf_buffer = BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=LETTER)
            styles = getSampleStyleSheet()
            story = []

            for line in generated_resume.split("\n"):
                if line.strip().isupper():
                    story.append(Paragraph(line.strip(), styles["Heading2"]))
                    story.append(Spacer(1, 6))
                elif line.strip().startswith(("-", "*")):
                    story.append(Paragraph("• " + line.strip().lstrip("-* ").strip(), styles["Normal"]))
                elif line.strip():
                    story.append(Paragraph(line.strip(), styles["Normal"]))
                story.append(Spacer(1, 4))

            doc.build(story)
            pdf_data = pdf_buffer.getvalue()
            pdf_buffer.close()

            generated_resume_pdf = base64.b64encode(pdf_data).decode("utf-8")

        # ==== Handle suggestions only ====
        elif "improve" in request.POST:
            resume_text = request.session.get("resume_text", "")
            prompt = f"You are an expert resume coach. Analyze and give actionable improvement suggestions:\n\n{resume_text}"
            response = model.generate_content(prompt)
            comments = response.text.strip()
            ats_score = request.session.get("ats_score")
            request.session["comments"] = comments

        # ==== Handle first upload & ATS score ====
        else:
            resume_file = request.FILES.get("resume")
            if resume_file:
                try:
                    resume_text = extract_text(BytesIO(resume_file.read()))
                except Exception:
                    return render(request, "Startup_app/form.html", {"error": "Failed to read resume."})

                prompt = f"""
You are an ATS (Applicant Tracking System) evaluation expert.

Instructions:
1. On the first line, output ONLY the ATS score (integer between 0–100, no extra text).
2. Then provide exactly 4 bullet points:
   - 2 bullet points for the strongest aspects of the resume.
   - 2 bullet points for the most important weaknesses or gaps to improve.
3. Keep the feedback concise, specific, and relevant to ATS optimization for the target industry.

Resume content:
{resume_text}
"""

                response = model.generate_content(prompt)
                raw_output = response.text.strip()

                first_line = raw_output.splitlines()[0].strip()
                match = re.match(r"^\D*(\d{1,3})\D*$", first_line)
                ats_score = match.group(1) if match else "N/A"
                comments = "\n".join(raw_output.splitlines()[1:]).strip()

                # Save to session
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
