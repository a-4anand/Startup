from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PyPDF2 import PdfReader  # Use python-docx for DOCX support
from django.conf import settings
# Load environment variables (if using .env)
load_dotenv()
from pdfminer.high_level import extract_text
from django.shortcuts import render
from pdfminer.high_level import extract_text
from io import BytesIO


genai.configure(api_key=settings.GEMINI_API_KEY)# Recommended way
model = genai.GenerativeModel("gemini-1.5-pro")

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

def analyze_resume(request):
    if request.method == 'POST' and request.FILES.get('resume'):
        resume_file = request.FILES['resume']
        job_info = request.POST.get('job_info', '')

        # Only allow PDF for now
        if not resume_file.name.endswith('.pdf'):
            return render(request, 'error.html', {'message': 'Only PDF resumes supported for now'})

        # Extract text from resume
        resume_text = extract_text(BytesIO(resume_file.read()))



        # Create prompt
        prompt = f"""
        This is a resume text:\n{resume_text}\n
        The candidate is applying for the following role:\n{job_info}\n
        Suggest improvements to make the resume better for this role.
        """

        # Generate Gemini response using the latest stable model
        model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
        response = model.generate_content(prompt)

        return render(request, 'Startup_app/result.html', {'feedback': response.text})

    return render(request, 'error.html', {'message': 'Invalid request. Please upload a resume.'})


def ask_gemini(request):
    if request.method == 'POST':
        prompt = request.POST.get('prompt', '')
        model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
        response = model.generate_content(prompt)
        return JsonResponse({'response': response.text})
    return JsonResponse({'error': 'Only POST method allowed'}, status=405)
def resume_analyzer(request):
    ats_score = None
    suggestions = None
    comments = None

    if request.method == "POST":


        if "improve" in request.POST:
            resume_text = request.session.get("resume_text", "")
            job_desc = request.session.get("job_desc", "")

            prompt = f"""
You are an expert resume coach. Analyze the following resume in context of the job description and give detailed suggestions to improve ATS matching.

Resume:
{resume_text}

Job Description:
{job_desc}
"""
            response = model.generate_content(prompt)
            suggestions = response.text
            ats_score = request.session.get("ats_score")

        else:
            resume_file = request.FILES.get("resume")
            job_desc = request.POST.get("job_desc", "")

            if resume_file:
                try:
                    resume_text = extract_text(BytesIO(resume_file.read()))
                except Exception:
                    return render(request, "Startup_app/form.html", {
                        "error": "Failed to extract text from resume. Ensure it's a valid PDF."
                    })

                prompt = f"""
You are an ATS (Applicant Tracking System) evaluator.

Compare the following resume with the job description and return:
1. Only the ATS match **score out of 100** (just a number) on the first line.
2. Then provide 3-5 bullet points:
   - What matches well (skills, keywords, experience).
   - What can be improved.

### FORMAT:
<Score (number only)>
- Bullet point 1
- Bullet point 2
...

### Resume:
{resume_text}

### Job Description:
{job_desc}
"""
                response = model.generate_content(prompt)
                raw_output = response.text.strip()

                # Extract score
                import re
                first_line = raw_output.splitlines()[0].strip()
                match = re.match(r"^\D*(\d{1,3})\D*$", first_line)
                ats_score = match.group(1) if match else "N/A"

                # Extract bullet points
                comments = "\n".join(raw_output.splitlines()[1:]).strip()

                # Save in session
                request.session["resume_text"] = resume_text
                request.session["job_desc"] = job_desc
                request.session["ats_score"] = ats_score

    return render(request, "Startup_app/form.html", {
        "ats_score": ats_score,
        "suggestions": suggestions,
        "comments": comments
    })

