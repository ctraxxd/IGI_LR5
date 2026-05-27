# Museum Management System - LR5 Django Project

## Variant 9: Museum

A comprehensive museum management system built with Django, implementing all requirements for Variant 9 of the laboratory work.

---

## 🎯 Project Features

### Core Functionality
- **Exhibits Management**: Full CRUD for museum exhibits with photos, descriptions, and categorization
- **Hall Management**: Multi-floor museum halls with capacity tracking
- **Employee Management**: Staff assignments, positions, and contact information
- **Tour System**: Seasonal tours with booking and ticketing
- **Ticket Sales**: Dynamic pricing with weekend surcharges (+20%) and age-based discounts
  - Child (50% off), Senior (30% off), Student (20% off)
- **Client Management**: Customer profiles with phone validation (+375 format)
- **Reviews & Ratings**: Visitor feedback system
- **Promo Codes**: Discount code system

### Required Pages (Lab Specification)
- ✅ **Home**: Latest exhibit information with external API data
- ✅ **About**: Company info, history timeline, video link, logo
- ✅ **News/Exhibitions**: Current and upcoming exhibitions
- ✅ **Glossary/FAQ**: Art types with descriptions
- ✅ **Contacts**: Employee directory with photos
- ✅ **Privacy Policy**: Placeholder page
- ✅ **Vacancies**: Job openings from database
- ✅ **Reviews**: User-submitted reviews with ratings
- ✅ **Promo Codes**: Active and archived promotional codes

### Technical Requirements Implemented
- ✅ **Phone Validation**: +375 (XX) XXX-XX-XX (Belarusian format)
- ✅ **Age Restriction**: 18+ for clients and employees
- ✅ **Timezone Support**: Europe/Minsk (UTC + local time display)
- ✅ **Date Format**: DD/MM/YYYY throughout all templates
- ✅ **Tour Seasons**: spring, summer, autumn, winter
- ✅ **Exhibit Filtering**: By art type, hall, floor, last 6 months
- ✅ **Search & Sort**: Full-text search and multiple sort options
- ✅ **Charts & Statistics**: Chart.js visualizations on statistics page
- ✅ **External APIs**: Currency rates, art facts
- ✅ **Async/Await**: Bonus task - async demo page with parallel API calls

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip and virtualenv

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd LR5
```

2. **Create and activate virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Populate database with sample data**
```bash
python manage.py seed_data
```

6. **Create superuser (if not created by seed_data)**
```bash
python manage.py createsuperuser
# Username: admin
# Password: admin123
```

7. **Run development server**
```bash
python manage.py runserver
```

8. **Access the application**
- Main site: http://localhost:8000
- Admin panel: http://localhost:8000/admin/

---

## 📊 Database Models

### Core Models
- **Position**: Employee job positions
- **ArtType**: Types of art (Painting, Sculpture, etc.)
- **Hall**: Museum halls with floor, area, features
- **Employee**: Staff with positions and hall assignments
- **Exhibit**: Art pieces with metadata, photos, locations
- **Exposition**: Permanent exhibitions
- **Exhibition**: Temporary exhibitions
- **Tour**: Guided tours with seasons and schedules
- **Client**: Museum visitors/customers
- **Ticket**: Admission tickets with dynamic pricing
- **PromoCode**: Discount codes
- **Review**: Visitor reviews and ratings
- **Vacancy**: Job openings
- **CompanyHistory**: Historical timeline
- **CompanyInfo**: Museum contact information

---

## 🧪 Testing

### Run Tests with Coverage
```bash
pytest --cov=store --cov-report=html
```

**Current Coverage: 87%** (exceeds 80% requirement)

View HTML report:
```bash
open htmlcov/index.html
```

---

## 🐳 Docker Support

### Build and Run with Docker Compose

```bash
# Build images
docker-compose build

# Start services
docker-compose up

# Run in background
docker-compose up -d

# Stop services
docker-compose down
```

### Docker Images
Public images available on Docker Hub (configure in docker-compose.yml)

---

## ☁️ Deployment (Render.com)

### Deployment Steps

1. **Push to GitHub**
   - Push code to a **private** GitHub repository
   - Add @AnnBsuir (anzh52889@gmail.com) as collaborator

2. **Deploy on Render**
   - Register at [render.com](https://render.com)
   - Connect GitHub repository
   - Deploy as "New Web Service"
   - render.yaml is auto-detected

3. **Database**
   - PostgreSQL provisions automatically
   - Migrations run on deploy

4. **Access**
   - Your app will be available at: `https://<your-app-name>.onrender.com`
   - Admin: `https://<your-app-name>.onrender.com/admin/`

---

## 📋 Lab Requirements Checklist

### Mandatory Requirements
- [x] Django web framework
- [x] SQLite database (dev) / PostgreSQL (prod)
- [x] Models with relationships (OneToOne, ForeignKey, ManyToMany)
- [x] CRUD operations
- [x] Admin panel with all models
- [x] Superuser created (admin/admin123)
- [x] Authentication/Authorization
- [x] Access control (staff, authenticated, anonymous)
- [x] 10+ records in main tables
- [x] 2+ external APIs (Currency, Art Facts)
- [x] URL patterns with regex
- [x] Statistics dashboard with charts
- [x] Timezone support (UTC + local)
- [x] Date format DD/MM/YYYY
- [x] Phone format +375 (XX) XXX-XX-XX
- [x] Age restriction 18+
- [x] Search and filtering
- [x] Sorting
- [x] Test coverage 80%+ (achieved 87%)
- [x] Logging configuration
- [x] API rate limiting for anonymous users
- [x] Form validation (client + server)
- [x] Docker support
- [x] docker-compose configuration
- [x] GitHub repository (private)
- [x] Render.com deployment

---

## 🔐 Default Credentials

### Superuser
- **Username**: admin
- **Password**: admin123

### Sample Users
Created by `seed_data` command:
- 10 clients with various demographics
- 10 employees with different positions
- Multiple tours, exhibits, and tickets

---

## 📁 Project Structure

```
LR5/
├── config/                 # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── store/                  # Main application
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py  # Database seeding
│   ├── migrations/
│   ├── models.py           # All database models
│   ├── views.py            # View functions
│   ├── forms.py            # Django forms
│   ├── admin.py            # Admin configuration
│   ├── urls.py             # URL routing
│   └── tests.py            # Test suite
├── templates/
│   └── museum/             # HTML templates
├── static/                 # Static files
├── media/                  # Uploaded files
├── logs/                   # Application logs
├── docker-compose.yml      # Docker Compose config
├── Dockerfile              # Docker image
├── render.yaml             # Render.com config
├── requirements.txt        # Python dependencies
├── pytest.ini              # Pytest configuration
└── manage.py               # Django management
```

---

## 🎨 Pages Overview

| Page | URL | Description |
|------|-----|-------------|
| Home | `/` | Latest exhibit, currency rates, art facts |
| About | `/about/` | Museum info, history timeline, video |
| News | `/news/` | Current exhibitions |
| Glossary | `/glossary/` | Art types FAQ |
| Contacts | `/contacts/` | Employee directory |
| Halls | `/halls/` | Museum halls list |
| Exhibits | `/exhibits/` | Exhibits with search/filter/sort |
| Tours | `/tours/` | Tour schedule by season |
| Tickets | `/tickets/` | Ticket purchase and history |
| Statistics | `/statistics/` | Dashboard with charts (staff only) |
| Calendar | `/calendar/` | Text calendar view |
| Admin | `/admin/` | Django admin panel |

---

## 📞 Support

For questions or issues related to this lab work, contact your instructor.

---

## 📝 License

This project is created for educational purposes as part of BSUIR laboratory work.

---

## 🎓 University Information

**Belarusian State University of Informatics and Radioelectronics (BSUIR)**  
Laboratory Work №5 - Web Framework Django  
Variant 9 - Museum Management System
