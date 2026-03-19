def mark_served(request, token_id):
    token = get_object_or_404(Token, id=token_id, doctor__user=request.user)
    if request.method == "POST" and token.status == "called":
        token.status = "served"
        token.save()
        messages.success(request, f"Token #{token.token_number} marked as served.")
    return redirect('queuezero:doctor_dashboard')
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Token
import qrcode
import base64
import os
from io import BytesIO
from django.core.files.base import ContentFile
from hospital.models import Patient, Doctor
from django.views.decorators.http import require_GET
from hospital.models import Department
from twilio.rest import Client
from django.conf import settings   
# ----------------------
# QueueZero Token Views
# ----------------------

@login_required
def generate_token(request):
    try:
        patient = get_object_or_404(Patient, user=request.user)
    except:
        messages.error(request, "Patient profile not found. Please contact administrator.")
        return redirect('home')

    if request.method == "POST":
        doctor_id = request.POST.get("doctor_id")
        doctor = get_object_or_404(Doctor, id=doctor_id, is_available=True)

        # Generate sequential token number for this doctor
        last_token = Token.objects.filter(doctor=doctor).order_by("-token_number").first()
        token_number = last_token.token_number + 1 if last_token else 1

        # Create token
        token = Token.objects.create(
            patient=patient,
            doctor=doctor,
            token_number=token_number,
            status="waiting",
        )

        # Generate QR Code with more detailed information
        doctor_name = f"{doctor.user.first_name} {doctor.user.last_name}".strip()
        qr_data = f"Token {token.token_number} for Dr. {doctor_name} - {doctor.department}"
        img = qrcode.make(qr_data)
        buffer = BytesIO()
        img.save(buffer, format="PNG")

        # Save QR code to file
        qr_file = ContentFile(buffer.getvalue())
        qr_file.name = f"token_{token.id}.png"
        token.qr_image = qr_file
        token.save()

        messages.success(request, f"Token #{token_number} generated successfully!")
        return redirect("queuezero:token_detail", token_id=token.id)

    # GET → show departments for selection
    departments = [choice[0] for choice in Doctor.DEPARTMENT_CHOICES]
    return render(
        request,
        "queuezero/generate_token.html",
        {"departments": departments},
    )

@login_required
def token_detail(request, token_id):
    # ✅ Fixed: use patient__user instead of user
    token = get_object_or_404(Token, id=token_id, patient__user=request.user)
    patients_ahead = Token.objects.filter(
        doctor=token.doctor,
        status="waiting",
        created_at__lt=token.created_at
    ).count()
    avg_time = getattr(token.doctor, "avg_slot_minutes", 10)
    estimated_wait = patients_ahead * avg_time

    # Generate QR code data for fallback display
    doctor_name = f"{token.doctor.user.first_name} {token.doctor.user.last_name}".strip()
    qr_data = f"Token {token.token_number} for Dr. {doctor_name} - {token.doctor.department}"
    qr_img = qrcode.make(qr_data)
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    qr_img_str = base64.b64encode(buffer.getvalue()).decode()

    context = {
        "token": token,
        "patients_ahead": patients_ahead,
        "estimated_wait": estimated_wait,
        "qr_code_base64": qr_img_str,  # Fallback QR code as base64
    }
    return render(request, "queuezero/token_detail.html", context)

@login_required
def token_print(request, token_id):
    """Print-only view for professional clinical token"""
    token = get_object_or_404(Token, id=token_id, patient__user=request.user)
    patients_ahead = Token.objects.filter(
        doctor=token.doctor,
        status="waiting",
        created_at__lt=token.created_at
    ).count()
    avg_time = getattr(token.doctor, "avg_slot_minutes", 10)
    estimated_wait = patients_ahead * avg_time

    # Generate QR code data for fallback display
    doctor_name = f"{token.doctor.user.first_name} {token.doctor.user.last_name}".strip()
    qr_data = f"Token {token.token_number} for Dr. {doctor_name} - {token.doctor.department}"
    qr_img = qrcode.make(qr_data)
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    qr_img_str = base64.b64encode(buffer.getvalue()).decode()

    context = {
        "token": token,
        "patients_ahead": patients_ahead,
        "estimated_wait": estimated_wait,
        "qr_code_base64": qr_img_str,
    }
    return render(request, "queuezero/token_print.html", context)


@login_required
def my_token(request):
    latest = Token.objects.filter(patient__user=request.user).order_by("-created_at").first()

    if latest:
        return redirect("queuezero:token_detail", token_id=latest.id)

    messages.info(request, "You don’t have a token yet.")
    return redirect('queuezero:patient_dashboard')


from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Token
from hospital.models import Doctor
from twilio.rest import Client
from django.conf import settings

@login_required
def call_next_token(request, token_id):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect("queuezero:doctor_dashboard")

    doctor = get_object_or_404(Doctor, user=request.user)
    token = get_object_or_404(Token, id=token_id, doctor=doctor)

    if not token.is_called:
        # Mark current token as called
        token.is_called = True
        token.status = "called"
        token.save(update_fields=["is_called", "status"])

        # Send SMS to the patient being called
        try:
            patient_phone = token.patient.phone
            message_body = (
                f"Hello {token.patient.user.first_name}, your token "
                f"({token.token_number}) with Dr. {doctor.user.first_name} is now being called."
            )
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=message_body,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=patient_phone
            )
        except Exception as e:
            print(f"Error sending SMS to called patient: {e}")

        # --- NEW: Send pre-call alerts to next 1–2 patients ---
        next_tokens = Token.objects.filter(
            doctor=doctor,
            status="waiting",
            is_called=False
        ).order_by("token_number")[:2]

        for next_token in next_tokens:
            if not next_token.pre_alert_sent:
                try:
                    patient_phone = next_token.patient.phone
                    message_body = (
                        f"Hello {next_token.patient.user.first_name}, "
                        f"you have {next_token.token_number - token.token_number} patient(s) ahead. "
                        "Please be ready."
                    )
                    client.messages.create(
                        body=message_body,
                        from_=settings.TWILIO_PHONE_NUMBER,
                        to=patient_phone
                    )
                    next_token.pre_alert_sent = True
                    next_token.save(update_fields=["pre_alert_sent"])
                except Exception as e:
                    print(f"Error sending pre-alert SMS: {e}")

        messages.success(request, f"Token #{token.token_number} called successfully!")

    else:
        messages.info(request, f"Token #{token.token_number} has already been called.")

    return redirect("queuezero:doctor_dashboard")

@login_required
def check_token_status(request, token_id):
    token = get_object_or_404(Token, id=token_id, patient__user=request.user)

    patients_ahead = Token.objects.filter(
        doctor=token.doctor,
        status="waiting",
        created_at__lt=token.created_at
    ).count()
    avg_time = getattr(token.doctor, "avg_slot_minutes", 10)
    estimated_wait = patients_ahead * avg_time

    return JsonResponse({
        "token_number": token.token_number,
        "status": token.status,
        "patients_ahead": patients_ahead,
        "estimated_wait": estimated_wait,
    })


# ----------------------
# Dashboard Views
# ----------------------
@login_required
def patient_dashboard(request):
    send_pre_call_alerts() 
    latest_token = Token.objects.filter(
        patient__user=request.user, status="waiting"
    ).order_by("-created_at").first()

    if latest_token:
        # Generate QR code data for fallback display
        doctor_name = f"{latest_token.doctor.user.first_name} {latest_token.doctor.user.last_name}".strip()
        qr_data = f"Token {latest_token.token_number} for Dr. {doctor_name} - {latest_token.doctor.department}"
        qr_img = qrcode.make(qr_data)
        buffer = BytesIO()
        qr_img.save(buffer, format="PNG")
        qr_img_str = base64.b64encode(buffer.getvalue()).decode()
        
        context = {
            "token": latest_token,
            "qr_code_base64": qr_img_str,
        }
        return render(request, "queuezero/patient_dashboard.html", context)

    # If no active token → show dropdowns
    departments = Department.objects.all()
    doctors = Doctor.objects.all()
    return render(
        request,
        "queuezero/patient_dashboard.html",
        {"departments": departments, "doctors": doctors},
    )

@login_required
def doctor_dashboard(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    tokens = Token.objects.filter(doctor=doctor).order_by("created_at")

    # Calculate counts for stats cards
    total_tokens = tokens.count()
    waiting_tokens = tokens.filter(status="waiting").count()
    called_tokens = tokens.filter(status="called").count()
    
    return render(request, "queuezero/doctor_dashboard.html", {
        "doctor": doctor,
        "tokens": tokens,
        "total_tokens": total_tokens,
        "waiting_tokens": waiting_tokens,
        "called_tokens": called_tokens,
    })

@login_required
def toggle_availability(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    if request.method == "POST":
        doctor.is_available = not doctor.is_available
        doctor.save(update_fields=["is_available"])
    return redirect('queuezero:doctor_dashboard')

@login_required
@require_GET
def doctors_by_department(request):
    dept_name = request.GET.get("department")  # Get name, not id
    doctors = Doctor.objects.filter(department=dept_name).values(
        "id", "user__first_name", "user__last_name"
    )
    return JsonResponse(list(doctors), safe=False)

def send_pre_call_alerts():
    waiting_tokens = Token.objects.filter(status="waiting", pre_alert_sent=False)

    for token in waiting_tokens:
        # Count patients ahead of this token
        patients_ahead = Token.objects.filter(
            doctor=token.doctor,
            status="waiting",
            created_at__lt=token.created_at
        ).count()

        if patients_ahead in [1, 2]:  # Only alert if 1 or 2 patients ahead
            try:
                patient_phone = token.patient.phone
                message_body = (
                    f"Hello {token.patient.user.first_name}, your turn with "
                    f"Dr. {token.doctor.user.first_name} is coming soon! "
                    f"({patients_ahead} patient(s) ahead)"
                )
                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                client.messages.create(
                    body=message_body,
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=patient_phone
                )
                # Mark alert as sent
                token.pre_alert_sent = True
                token.save(update_fields=["pre_alert_sent"])
            except Exception as e:
                print(f"Error sending pre-call SMS: {e}")