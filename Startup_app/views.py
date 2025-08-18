from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import os, json, re, base64
from dotenv import load_dotenv
import google.generativeai as genai
from PyPDF2 import PdfReader
from django.conf import settings
from pdfminer.high_level import extract_text
from io import BytesIO
import re
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
import random
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
import google.api_core.exceptions

load_dotenv()
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro', generation_config={"temperature": 0.3})

# views.py


def send_otp_email(email, otp):
    subject = "Your OTP for Registration"
    message = f"Your OTP for registration is {otp}. Please do not share this with anyone."
    from_email = "your-email@example.com"  # Update with your email
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

def user_register(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already Registered")
        return redirect('index')

    if request.method == 'POST':
        # Get data from the registration form
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not email:
            return render(request, 'Startup_app/register.html', {
                "error": "Email is required"
            })

        if not username:
            return render(request, 'Startup_app/register.html', {
                "error": "Username is required"
            })

        if len(password1) < 8:
            return render(request, 'Startup_app/register.html', {
                "error": "Password is too short."
            })
        if password1.isdigit():
            return render(request, 'Startup_app/register.html', {
                "error": "Password cannot be entirely numeric."
            })

        if password1.lower() in ['password', '12345678', 'qwerty', 'admin']:
            return render(request, 'Startup_app/register.html', {
                "error": "Password is too common."
            })

        if not re.search(r"[A-Za-z]", password1):
            return render(request, 'Startup_app/register.html', {
                "error": "Password must contain at least one letter."
            })

        if not re.search(r"[0-9]", password1):
            return render(request, 'Startup_app/register.html', {
                "error": "Password must contain at least one digit."
            })

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password1):
            return render(request, 'Startup_app/register.html', {
                "error": "Password must contain at least one special character."
            })

        if password1 != password2:
            return render(request, 'Startup_app/register.html',{
                "error": "Passwords does not match"
            })



        # Generate OTP and send it via email
        otp = random.randint(100000, 999999)
        send_otp_email(email, otp)

        # Store the OTP and email in the session
        request.session['otp'] = otp
        request.session['email'] = email
        request.session['username'] = username
        request.session['password1'] = password1
        request.session['password2'] = password2

        # Redirect to OTP verification page
        return redirect('otp_verify')

    # Initial form load for GET request
    form = UserCreationForm()
    return render(request, 'Startup_app/register.html', {
        "form": form
    })


def otp_verify_view(request):
    print("Session data:", request.session.items())
    if request.method == 'POST':
        # Get OTP entered by the user
        otp_entered = request.POST.get('otp')
        stored_otp = request.session.get('otp')

        if not otp_entered:
            return render(request, 'Startup_app/otp-verify.html', {
                "error": "OTP is required"
            })

        # Validate OTP
        if otp_entered != str(stored_otp):
            return render(request, 'Startup_app/otp-verify.html', {
                "error": "Invalid OTP. Please try again."
            })

        # OTP is correct, so create the user
        email = request.session.get('email')
        username = request.session.get('username')
        password1 = request.session.get('password1')
        password2 = request.session.get('password2')

        # Create the user
        form = UserCreationForm({
            'username': username,
            'email': email,
            'password1': password1,
            'password2': password2
        })

        if form.is_valid():
            user = form.save()
            login(request, user)

            request.session.pop('otp', None)
            request.session.pop('email', None)
            request.session.pop('username', None)
            request.session.pop('password1', None)
            request.session.pop('password2', None)

            return redirect('index')

        return render(request, 'Startup_app/otp-verify.html', {
            "error": "The Email is already registered or There was an issue with your registration."
        })


    return render(request, 'Startup_app/password/otp-verify.html')



def user_login(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in")
        return redirect('index')  # Redirect so the popup shows on home page

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password!")

    return render(request, "Startup_app/login.html")


def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("index")

def profile_view(request):
    return render(request,"Startup_app/profile.html")





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

            # Step 1 — Rewrite resume (Professional, ATS-Ready)
            rewrite_prompt = f"""
            You are an expert resume writer and ATS optimization specialist.

Task:
Rewrite the given resume into a **FINAL, job-ready, ATS-optimized resume** targeted to maximize ATS score for a generic tech/business role.
- Actively improve keyword density by adding relevant industry terms where appropriate.
- Replace generic verbs with strong action verbs.
- Emphasize measurable results and achievements.
- Remove fluff and filler phrases.
- Keep resume under 1 page (~500 words).


            Your goal: Produce a FINAL, **professionally written, ATS-optimized resume** that looks like it was written by a top career coach.
            - The output must be clean, single-column, plain text.
            - Keep the entire resume within 1 page (max ~500 words).
            - Omit any section that does not have relevant details — completely skip the heading if no meaningful content exists.
            - Do NOT use placeholders like [Institution Name] or "N/A".
            - Optimize for ANY industry (universal template).
            - Ensure proper grammar, consistency, and alignment.

            Formatting rules:
            1. FULL NAME — in bold (will be styled in blue in PDF).
            2. Contact line: email | phone | LinkedIn | location (skip missing items).
            3. Between sections, insert exactly this line: ===== BLUE LINE =====
            4. Keep layout ATS-compliant — no graphics, tables, or special symbols.
            5. Use strong action verbs and measurable results in bullet points.
            6. Keep descriptions concise but impactful.
            7. Only output the final resume — no suggestions, no commentary.

            Preferred section order (only include if not empty):
            - FULL NAME & Contact
            - PROFESSIONAL SUMMARY (3–4 lines summarizing expertise and achievements)
            - SKILLS (grouped into categories like Technical Skills, Tools, Soft Skills)
            - EXPERIENCE (chronological, with role, company, dates, and 2–4 bullet points)
            - EDUCATION (degree, institution, dates, and optional coursework)
            - PROJECTS (title, short description, and 2 bullet points)
            - ACHIEVEMENTS (bullet points of measurable accomplishments)

            Resume to rewrite:
            {resume_text}
            """

            rewrite_response = model.generate_content(rewrite_prompt)
            generated_resume = rewrite_response.text.strip()
            request.session["generated_resume"] = generated_resume


            # Step 2 — Recalculate ATS score for rewritten resume
            scoring_prompt = f"""
            You are an ATS (Applicant Tracking System) evaluation expert.

            Instructions:
            1. On the first line, output ONLY the ATS score (integer between 0–100, no extra text).
            2. Then provide exactly 4 bullet points:
               - 2 strongest aspects of the resume.
               - 2 most important weaknesses or gaps to improve.
            3. Keep the feedback concise and ATS-focused.

            Resume content:
            {generated_resume}
            """
            scoring_response = model.generate_content(scoring_prompt)
            raw_output = scoring_response.text.strip()

            first_line = raw_output.splitlines()[0].strip()
            match = re.match(r"^\D*(\d{1,3})\D*$", first_line)
            ats_score = match.group(1) if match else "N/A"
            comments = "\n".join(raw_output.splitlines()[1:]).strip()

            request.session["ats_score"] = ats_score
            request.session["comments"] = comments

            # Step 3 — Create PDF
            pdf_buffer = BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=LETTER)
            styles = getSampleStyleSheet()
            story = []

            for line in generated_resume.split("\n"):
                clean_line = re.sub(r"[*_]{1,2}(.*?)\1?[*_]{1,2}", r"\1", line).strip()

                if "===== BLUE LINE =====" in clean_line:
                    story.append(Table([[""]], colWidths=[450], style=TableStyle([
                        ('LINEBELOW', (0, 0), (-1, -1), 2, colors.HexColor("#0D47A1"))
                    ])))
                    story.append(Spacer(1, 4))
                    continue
                if clean_line.isupper():
                    story.append(Paragraph(clean_line, styles["Heading2"]))
                    story.append(Spacer(1, 3))
                elif clean_line.startswith(("-", "*")):
                    story.append(Paragraph("• " + clean_line.lstrip("-* ").strip(), styles["Normal"]))
                elif clean_line:
                    story.append(Paragraph(clean_line, styles["Normal"]))
                story.append(Spacer(1, 2))

                if len(generated_resume.split()) > 500:
                    generated_resume = " ".join(generated_resume.split()[:500])

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


@login_required
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

