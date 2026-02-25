from django.shortcuts import render,redirect,get_object_or_404
from jobs.models import Job,Application,Profile
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from .forms import JobForm
import PyPDF2
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.
def home(request):
    jobs = Job.objects.all()
    return render(request , 'home.html' , {'jobs' : jobs})


@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # Check if user already applied
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, "You have already applied for this job!")
        return redirect('home')

    if request.method == "POST":
        resume = request.FILES.get('resume')
        if not resume:
            messages.error(request, "Please upload a resume!")
            return redirect('home')

        # Extract text from PDF
        pdf_reader = PyPDF2.PdfReader(resume)
        resume_text = ""
        for page in pdf_reader.pages:
            resume_text += page.extract_text().lower()

        # Keyword matching logic
        raw_skills = job.skill_required.replace(',', '\n')
        job_skills = [s.strip().lower() for s in raw_skills.split('\n') if s.strip()]

        match_count = sum(1 for skill in job_skills if skill in resume_text)
        total_skills = len(job_skills)
        match_score = int((match_count / total_skills) * 100) if total_skills > 0 else 0

        # Create application
        application = Application.objects.create(
            job=job,
            applicant=request.user,
            resume=resume,
            match_score=match_score
        )

        messages.success(request, f"You applied for {job.title}! Your match score is {match_score}%.")
        return render(request, "success.html", {
            "score": match_score,
            "application": application
        })

    return render(request, "apply.html", {"job": job})

@login_required
def post_job(request):
    if request.user.profile.role != 'recruiter':
        return redirect('home')

    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            return redirect('dashboard')
    else:
        form = JobForm()

    return render(request, 'post_job.html', {'form' : form})

@login_required
def dashboard(request):
    jobs = Job.objects.filter(posted_by = request.user)
    applications = Application.objects.filter(job__posted_by = request.user)

    return render(request, 'dashboard.html' , {
        'jobs' : jobs,
        'applications' : applications
        })


@login_required
def delete_job(request,job_id):
    job = Job.objects.get(id=job_id, posted_by=request.user)
    job.delete()
    return redirect('dashboard')

@login_required
def update_status(request, app_id):
    if request.method == "POST":
        application = get_object_or_404(
        Application,
        id=app_id,
        job__posted_by=request.user
        )
        new_status = request.POST.get("status")

        application.status = new_status
        application.save()

        # Send email only when shortlisted
        if new_status == "Shortlisted":
            print("Email function triggered")
            send_mail(
                
                subject='Congratulations! You are shortlisted',
                message=f'Hi {application.applicant.username},\n\n'
                        f'You have been shortlisted for the job: {application.job.title}.\n'
                        f'We will contact you soon.\n\n'
                        f'Thank you!',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[application.applicant.email],
                fail_silently=False,
            )

    return redirect('dashboard')

@login_required
def applicant_dashboard(request):
    applications = Application.objects.filter(applicant = request.user)

    return render(request, 'applicant_dashboard.html', {
        'applications' : applications
    })

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! You are now logged in.")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'login.html')

def register_view(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST['role']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, 'register.html')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        profile = Profile.objects.get(user=user)
        profile.role=role
        profile.save()

        messages.success(request, f"Account created for {username}! You can now log in.")
        return redirect('login')

    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    return redirect('login')

