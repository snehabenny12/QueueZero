# 🏥 QueueZero - Smart Queue Management System

## Overview
QueueZero is an intelligent queue management system fully integrated with the Hospital Management System (HMS). It automates patient token generation, provides real-time queue updates, and offers comprehensive doctor-side management, eliminating the need for patients to wait physically at the hospital.

## ✨ Key Features

### For Patients:
- **Digital Token Generation**: Generate tokens online from anywhere
- **QR Code Integration**: Each token comes with a unique QR code for verification
- **Real-time Status Updates**: Live updates on queue position and estimated wait time
- **Print/Download Tokens**: Easy token printing and saving functionality
- **Mobile-Responsive Design**: Works perfectly on all devices

### For Doctors:
- **Smart Dashboard**: Comprehensive overview of patient queue
- **Availability Toggle**: Easy availability status management
- **Call Next Patient**: One-click patient calling system
- **Queue Statistics**: Real-time queue analytics
- **Patient Management**: Track token status and patient information

### For Administrators:
- **Multi-Department Support**: Manage queues across different departments
- **Real-time Monitoring**: Monitor all queues from a central location
- **Analytics Dashboard**: Comprehensive reporting and analytics

## 🛠️ Technical Stack

- **Backend**: Django 5.2 + Django REST Framework
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Database**: SQLite (production-ready for MySQL/PostgreSQL)
- **QR Code Generation**: Python `qrcode` library with PIL support
- **Authentication**: Django's built-in User model
- **Real-time Updates**: AJAX polling for live status updates

## 📁 Project Structure

```
HMSPROJ/
├── hospital/                    # Base HMS application
│   ├── models.py               # Patient, Doctor, Department models
│   ├── views.py                # Hospital management views
│   └── templates/hospital/     # Base templates
├── queuezero/                  # QueueZero application
│   ├── models.py               # Token model with QR code support
│   ├── views.py                # Queue management views
│   ├── urls.py                 # URL routing
│   ├── templates/queuezero/    # QueueZero-specific templates
│   └── static/queuezero/       # CSS and static assets
├── hms/                        # Django project settings
│   ├── settings.py             # Project configuration
│   └── urls.py                 # Main URL configuration
└── manage.py                   # Django management script
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- Django 5.2+
- SQLite (or MySQL/PostgreSQL for production)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd HMSPROJ
   ```

2. **Install dependencies**
   ```bash
   pip install qrcode[pil]
   ```

3. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run the development server**
   ```bash
   python manage.py runserver
   ```

6. **Access the application**
   - Main site: `http://127.0.0.1:8000/`
   - Admin panel: `http://127.0.0.1:8000/admin/`

## 📱 Usage Guide

### For Patients

1. **Register/Login**: Create an account or login to the system
2. **Generate Token**: 
   - Navigate to "Generate Token"
   - Select your preferred doctor
   - Click "Generate Token"
3. **Monitor Queue**: 
   - View your token details with QR code
   - Check estimated wait time
   - Monitor real-time status updates
4. **Print/Download**: Use the print button to save your token

### For Doctors

1. **Login**: Access doctor dashboard with your credentials
2. **Set Availability**: Toggle your availability status
3. **View Queue**: Monitor all patients in your queue
4. **Call Patients**: Use "Call Next" button to call the next patient
5. **Track Progress**: Monitor queue statistics and patient flow

### Sample Doctor Accounts

| Department    | Doctor Name        | Username  | Password   |
|---------------|--------------------|-----------|-----------| 
| Cardiology    | Dr. Arjun Menon    | dr_arjun  | arjun123  |
| Orthopedics   | Dr. Priya Nair     | dr_priya  | priya123  |
| Pediatrics    | Dr. Kiran Kumar    | dr_kiran  | kiran123  |
| Dermatology   | Dr. Sneha Rao      | dr_sneha  | sneha123  |

## 🔧 API Endpoints

### Patient Endpoints
- `GET /queuezero/patient/` - Patient dashboard
- `GET /queuezero/token/generate/` - Token generation form
- `POST /queuezero/token/generate/` - Create new token
- `GET /queuezero/token/<id>/` - Token details
- `GET /queuezero/token/status/<id>/` - Token status (JSON)

### Doctor Endpoints
- `GET /queuezero/doctor/` - Doctor dashboard
- `POST /queuezero/doctor/call-next/` - Call next patient
- `POST /queuezero/doctor/toggle-availability/` - Toggle availability

### Utility Endpoints
- `GET /queuezero/doctors_by_department/` - Get doctors by department (JSON)

## 🎨 UI/UX Features

### Design Philosophy
- **Modern & Clean**: Contemporary design with gradient backgrounds
- **User-Friendly**: Intuitive navigation and clear information hierarchy
- **Responsive**: Mobile-first design that works on all devices
- **Accessible**: High contrast colors and clear typography

### Key UI Components
- **Token Cards**: Beautiful token display with QR codes
- **Dashboard Layout**: Comprehensive overview with statistics
- **Status Badges**: Color-coded status indicators
- **Interactive Elements**: Hover effects and smooth transitions
- **Print Optimization**: Print-friendly token layouts

## 🔒 Security Features

- **Authentication Required**: All queue operations require user login
- **CSRF Protection**: Django's built-in CSRF protection
- **User Permissions**: Role-based access control
- **Secure QR Codes**: Encoded token information for verification
- **Data Validation**: Server-side validation for all inputs

## 📊 Database Schema

### Token Model
```python
class Token(models.Model):
    patient = ForeignKey(Patient)
    doctor = ForeignKey(Doctor)
    token_number = IntegerField()
    status = CharField(choices=['waiting', 'called', 'served'])
    is_called = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    qr_image = ImageField(upload_to="qr_codes/")
```

### Key Relationships
- **Patient** → **Token** (One-to-Many)
- **Doctor** → **Token** (One-to-Many)
- **Doctor** → **Department** (Many-to-One)

## 🚀 Deployment

### Production Setup
1. **Database**: Use PostgreSQL or MySQL for production
2. **Static Files**: Configure static file serving
3. **Media Files**: Set up media file handling for QR codes
4. **Environment Variables**: Use environment variables for sensitive data
5. **SSL**: Enable HTTPS for secure communication

### Environment Variables
```bash
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/dbname
ALLOWED_HOSTS=yourdomain.com
```

## 🔧 Configuration

### Settings Configuration
```python
# In settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# For QR code storage
QR_CODE_STORAGE = 'qr_codes/'
```

### Static Files
```bash
python manage.py collectstatic
```

## 🐛 Troubleshooting

### Common Issues

1. **QR Code Not Generating**
   - Ensure `qrcode[pil]` is installed
   - Check media directory permissions
   - Verify PIL/Pillow installation

2. **Migration Errors**
   - Run `python manage.py makemigrations`
   - Apply migrations with `python manage.py migrate`
   - Check for conflicting model changes

3. **Static Files Not Loading**
   - Run `python manage.py collectstatic`
   - Check STATIC_URL and STATIC_ROOT settings
   - Verify static file serving configuration

## 📈 Performance Optimization

### Database Optimization
- Use database indexes on frequently queried fields
- Implement pagination for large token lists
- Optimize queries with `select_related` and `prefetch_related`

### Frontend Optimization
- Minify CSS and JavaScript files
- Optimize images and QR codes
- Implement browser caching
- Use CDN for static assets

## 🔄 Future Enhancements

### Planned Features
- **SMS/Email Notifications**: Automated patient notifications
- **WebSocket Integration**: Real-time updates without polling
- **Mobile App**: Native mobile applications
- **Analytics Dashboard**: Advanced reporting and insights
- **Multi-language Support**: Internationalization
- **Integration APIs**: Third-party system integration

### Technical Improvements
- **Caching**: Redis integration for improved performance
- **Background Tasks**: Celery for async operations
- **API Versioning**: REST API with versioning
- **Testing**: Comprehensive test suite
- **Monitoring**: Application performance monitoring

## 📞 Support

For technical support or feature requests:
- **Documentation**: Check this README and inline code comments
- **Issues**: Report bugs through the issue tracker
- **Contact**: Reach out to the development team

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**QueueZero** - Revolutionizing hospital queue management with smart technology! 🏥✨



