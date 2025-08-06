from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PyPDF2 import PdfReader  # Use python-docx for DOCX support
from django.conf import settings
# Load environment variables (if using .env)
load_dotenv()


genai.configure(api_key=settings.GEMINI_API_KEY)# Recommended way

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
        resume_text = extract_text_from_pdf(resume_file)

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
