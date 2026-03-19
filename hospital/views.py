from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Patient
from hospital.models import Department, Doctor
from queuezero.models import Token

# Patient Registration
def patient_register(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        name = request.POST["name"]
        age = request.POST["age"]
        gender = request.POST["gender"]

        user = User.objects.create_user(username=username, password=password)
        patient = Patient.objects.create(user=user, name=name, age=age, gender=gender)

        login(request, user)
        return redirect("hospital:home")  # ✅ Redirect only after successful registration

    # ✅ Show the registration form for GET requests
    return render(request, "hospital/patient_register.html")


# Login View
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Redirect based on role
            if hasattr(user, "patient"):
                return redirect("hospital:home")  # patient_home removed
            elif user.groups.filter(name="Doctor").exists():
                return redirect("hospital:doctor_dashboard")
            elif user.is_superuser or user.groups.filter(name="Admin").exists():
                return redirect("hospital:home")  # admin_dashboard removed
            else:
                return redirect("hospital:home")

        return render(request, "hospital/login.html", {"error": "Invalid credentials"})

    return render(request, "hospital/login.html")


def logout_view(request):
    logout(request)
    return redirect("hospital:home")  # Redirect to homepage instead of patient_token


# ---------------- Home ----------------
def home(request):
    return render(request, "hospital/home.html")


# ---------------- Patient Dashboard ----------------

@login_required
def patient_dashboard(request):
    departments = Department.objects.all()
    doctors = Doctor.objects.all()
    context = {
        "departments": departments,
        "doctors": doctors,
    }
    return render(request, "queuezero/generate_token.html", context)

# ---------------- Generate Token ----------------
@login_required
def generate_token(request):
    patient = get_object_or_404(Patient, user=request.user)

    if request.method == "POST":
        dept_id = request.POST.get("department")
        doctor_id = request.POST.get("doctor")

        department = get_object_or_404(Department, id=dept_id)
        doctor = get_object_or_404(Doctor, id=doctor_id)

        # Create a new token
        last_token = Token.objects.filter(doctor=doctor).order_by("-token_number").first()
        token_number = 1 if not last_token else last_token.token_number + 1

        token = Token.objects.create(
            patient=patient,
            doctor=doctor,
            token_number=token_number,
            status="pending"
        )

        return redirect("queuezero:token_detail", token_id=token.id)

    # If GET request, go back to dashboard
    return redirect("queuezero:patient_dashboard")


# ---------------- Patient Token Page ----------------
@login_required
def patient_token(request):
    patient = get_object_or_404(Patient, user=request.user)
    token = Token.objects.filter(patient=patient, status="waiting").first()

    if not token:
        return redirect("queuezero:patient_dashboard")

    return render(request, "hospital/patient_token.html", {"token": token})
def patient_redirect(request):
    # Redirect patient directly to their token list page
    return redirect('queuezero:patient_token')
def about(request):
    return render(request, 'hospital/about.html')