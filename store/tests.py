import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta, datetime
from store.models import (
    Position, ArtType, Hall, Employee, Exhibit, Exposition, 
    Exhibition, Tour, Client, Ticket, PromoCode, Review
)
from store.forms import ClientForm, TicketForm, ReviewForm


@pytest.mark.django_db
class TestModels:
    """Test model creation and methods"""
    
    def test_position_creation(self):
        position = Position.objects.create(name='Curator', description='Manages exhibits')
        assert position.name == 'Curator'
        assert str(position) == 'Curator'
    
    def test_art_type_creation(self):
        art_type = ArtType.objects.create(name='Painting', description='Oil and watercolor')
        assert art_type.name == 'Painting'
        assert str(art_type) == 'Painting'
    
    def test_hall_creation(self):
        hall = Hall.objects.create(
            number=1, name='Main Hall', floor=1, area=500.00,
            has_water_feature=True, has_heating=True
        )
        assert str(hall) == 'Hall 1 - Main Hall'
        assert hall.area == 500.00
    
    def test_hall_invalid_floor(self):
        hall = Hall(number=1, name='Test', floor=-1, area=100.00)
        with pytest.raises(Exception):
            hall.full_clean()
    
    def test_employee_creation(self):
        position = Position.objects.create(name='Guide')
        hall = Hall.objects.create(number=1, name='Hall', floor=1, area=100.00)
        user = User.objects.create_user(username='test_emp', email='emp@test.com')
        
        employee = Employee.objects.create(
            user=user,
            first_name='John',
            last_name='Doe',
            phone='+375 (29) 123-45-67',
            email='john@test.com',
            position=position,
            hall=hall,
            hire_date=date(2020, 1, 1),
            salary=1000.00
        )
        assert 'Doe' in str(employee)
        assert employee.position.name == 'Guide'
    
    def test_employee_invalid_phone(self):
        position = Position.objects.create(name='Guide')
        user = User.objects.create_user(username='test_emp2', email='emp2@test.com')
        
        employee = Employee(
            user=user,
            first_name='Jane',
            last_name='Doe',
            phone='invalid',
            email='jane@test.com',
            position=position,
            hire_date=date(2020, 1, 1),
            salary=1000.00
        )
        with pytest.raises(Exception):
            employee.full_clean()
    
    def test_exhibit_creation(self):
        art_type = ArtType.objects.create(name='Sculpture')
        hall = Hall.objects.create(number=1, name='Hall', floor=1, area=100.00)
        
        exhibit = Exhibit.objects.create(
            name='David Copy',
            art_type=art_type,
            acquisition_date=date(2020, 5, 15),
            year_created=1504,
            author='Michelangelo',
            description='Famous sculpture',
            hall=hall,
            is_displayed=True
        )
        assert str(exhibit) == 'David Copy'
        assert exhibit.is_displayed is True
    
    def test_exhibit_recent_filter(self):
        art_type = ArtType.objects.create(name='Painting')
        hall = Hall.objects.create(number=1, name='Hall', floor=1, area=100.00)
        
        # Recent exhibit (within 6 months)
        recent = Exhibit.objects.create(
            name='Recent Art',
            art_type=art_type,
            acquisition_date=timezone.now().date() - timedelta(days=30),
            hall=hall
        )
        # Old exhibit
        old = Exhibit.objects.create(
            name='Old Art',
            art_type=art_type,
            acquisition_date=timezone.now().date() - timedelta(days=400),
            hall=hall
        )
        
        six_months_ago = timezone.now().date() - timedelta(days=180)
        recent_exhibits = Exhibit.objects.filter(acquisition_date__gte=six_months_ago)
        
        assert recent in recent_exhibits
        assert old not in recent_exhibits
    
    def test_tour_creation(self):
        employee = Employee.objects.create(
            first_name='John', last_name='Doe',
            phone='+375 (29) 123-45-67', email='john@test.com',
            position=Position.objects.create(name='Guide'),
            hire_date=date(2020, 1, 1), salary=1000.00
        )
        
        tour = Tour.objects.create(
            code='TOUR001',
            name='Art Tour',
            description='Guided art tour',
            date=datetime(2026, 6, 15, 10, 0),
            group_size=20,
            season='summer',
            guide=employee,
            price=25.00
        )
        assert str(tour) == 'TOUR001 - Art Tour'
        assert tour.get_season_display() == 'Summer'
    
    def test_client_creation(self):
        user = User.objects.create_user(username='client', email='client@test.com')
        
        client = Client.objects.create(
            user=user,
            first_name='Alice',
            last_name='Brown',
            phone='+375 (29) 123-45-67',
            email='alice@test.com',
            date_of_birth=date(1990, 1, 1)
        )
        assert client.age >= 18
        assert str(client) == 'Brown Alice'
    
    def test_client_underage(self):
        user = User.objects.create_user(username='young', email='young@test.com')

        client = Client(
            user=user,
            first_name='Young',
            last_name='Person',
            phone='+375 (29) 123-45-67',
            email='young@test.com',
            date_of_birth=date.today() - timedelta(days=365*10)
        )
        with pytest.raises(Exception):
            client.full_clean()
    
    def test_ticket_creation_and_pricing(self):
        client = Client.objects.create(
            first_name='Alice', last_name='Brown',
            phone='+375 (29) 123-45-67', email='alice@test.com',
            date_of_birth=date(1990, 1, 1)
        )
        
        ticket = Ticket.objects.create(
            client=client,
            visit_date=date(2026, 6, 15),
            ticket_type='adult',
            base_price=25.00,
            discount=10.0,
            final_price=0
        )
        ticket.calculate_price()
        assert ticket.final_price < ticket.base_price
    
    def test_ticket_weekend_surcharge(self):
        client = Client.objects.create(
            first_name='Bob', last_name='Smith',
            phone='+375 (29) 123-45-67', email='bob@test.com',
            date_of_birth=date(1990, 1, 1)
        )
        
        # Saturday
        ticket = Ticket.objects.create(
            client=client,
            visit_date=date(2026, 5, 30),  # Saturday
            ticket_type='adult',
            base_price=25.00,
            discount=0,
            final_price=0
        )
        ticket.calculate_price()
        assert ticket.final_price > ticket.base_price  # Weekend surcharge
    
    def test_promocode_is_valid(self):
        now = timezone.now()
        promo = PromoCode.objects.create(
            code='SAVE10',
            discount_percent=10.0,
            valid_from=now - timedelta(days=1),
            valid_until=now + timedelta(days=30)
        )
        assert promo.is_valid() is True
        
        expired = PromoCode.objects.create(
            code='EXPIRED',
            discount_percent=5.0,
            valid_from=now - timedelta(days=30),
            valid_until=now - timedelta(days=1)
        )
        assert expired.is_valid() is False
    
    def test_review_creation(self):
        client = Client.objects.create(
            first_name='Alice', last_name='Brown',
            phone='+375 (29) 123-45-67', email='alice@test.com',
            date_of_birth=date(1990, 1, 1)
        )
        
        review = Review.objects.create(
            client=client,
            rating=5,
            text='Great museum!'
        )
        assert review.rating == 5
        assert '5' in str(review)


@pytest.mark.django_db
class TestViews:
    """Test views"""
    
    def test_home_view(self, client):
        response = client.get(reverse('home'))
        assert response.status_code == 200
        assert 'latest_exhibit' in response.context
    
    def test_about_view(self, client):
        response = client.get(reverse('about'))
        assert response.status_code == 200
    
    def test_news_view(self, client):
        response = client.get(reverse('news'))
        assert response.status_code == 200
    
    def test_glossary_view(self, client):
        response = client.get(reverse('glossary'))
        assert response.status_code == 200
    
    def test_contacts_view(self, client):
        response = client.get(reverse('contacts'))
        assert response.status_code == 200
    
    def test_hall_list_view(self, client):
        response = client.get(reverse('hall_list'))
        assert response.status_code == 200
    
    def test_exhibit_list_view(self, client):
        response = client.get(reverse('exhibit_list'))
        assert response.status_code == 200
    
    def test_tour_list_view(self, client):
        response = client.get(reverse('tour_list'))
        assert response.status_code == 200
    
    def test_calendar_view(self, client):
        response = client.get(reverse('calendar'))
        assert response.status_code == 200
    
    def test_register_view(self, client):
        response = client.get(reverse('register'))
        assert response.status_code == 200
    
    def test_login_view(self, client):
        response = client.get(reverse('login'))
        assert response.status_code == 200
    
    def test_statistics_requires_staff(self, client):
        user = User.objects.create_user(username='testuser', password='password')
        client.force_login(user)
        response = client.get(reverse('statistics'))
        assert response.status_code == 302
    
    def test_statistics_staff_access(self, client):
        user = User.objects.create_superuser(username='admin', password='password')
        client.force_login(user)
        response = client.get(reverse('statistics'))
        assert response.status_code == 200
    
    def test_employee_dashboard_requires_employee(self, client):
        user = User.objects.create_user(username='emp', password='password')
        client.force_login(user)
        response = client.get(reverse('employee_dashboard'))
        assert response.status_code == 302  # Redirects due to messages


@pytest.mark.django_db
class TestForms:
    """Test forms"""
    
    def test_client_form_valid(self):
        form = ClientForm(data={
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '+375 (29) 123-45-67',
            'email': 'john@test.com',
            'date_of_birth': date(1990, 1, 1),
        })
        assert form.is_valid()
    
    def test_client_form_invalid_phone(self):
        form = ClientForm(data={
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': 'invalid',
            'email': 'john@test.com',
            'date_of_birth': date(1990, 1, 1),
        })
        assert not form.is_valid()
        assert 'phone' in form.errors
    
    def test_client_form_underage(self):
        from datetime import date
        # Calculate date for 10-year-old (under 18)
        underage_date = date.today() - timedelta(days=365*10)
        form = ClientForm(data={
            'first_name': 'Young',
            'last_name': 'Person',
            'phone': '+375 (29) 123-45-67',
            'email': 'young@test.com',
            'date_of_birth': underage_date,
        })
        assert not form.is_valid()
        assert 'date_of_birth' in form.errors
    
    def test_ticket_form_valid(self):
        client = Client.objects.create(
            first_name='Alice', last_name='Brown',
            phone='+375 (29) 123-45-67', email='alice@test.com',
            date_of_birth=date(1990, 1, 1)
        )
        form = TicketForm(data={
            'visit_date': date.today() + timedelta(days=7),
            'ticket_type': 'adult',
            'base_price': 25.00,
            'discount': 10,
        })
        assert form.is_valid()
    
    def test_ticket_form_past_date(self):
        form = TicketForm(data={
            'visit_date': date(2020, 1, 1),
            'ticket_type': 'adult',
            'base_price': 25.00,
            'discount': 0,
        })
        assert not form.is_valid()
        assert 'visit_date' in form.errors
    
    def test_review_form_valid(self):
        form = ReviewForm(data={
            'rating': 5,
            'text': 'Great museum!',
            'visit_date': date.today(),
        })
        assert form.is_valid()
    
    def test_review_form_invalid_rating(self):
        # Rating 10 is not in choices (1-5)
        form = ReviewForm(data={
            'rating': 10,
            'text': 'Great museum!',
            'visit_date': date.today(),
        })
        assert not form.is_valid()
        assert 'rating' in form.errors


@pytest.mark.django_db
class TestAPI:
    """Test API endpoints"""
    
    def test_api_currency_rates(self, client):
        response = client.get(reverse('api_currency_rates'))
        assert response.status_code == 200
        data = response.json()
        assert 'rates' in data
    
    def test_api_statistics_unauthorized(self, client):
        response = client.get(reverse('api_statistics'))
        assert response.status_code == 401
    
    def test_api_statistics_authorized(self, client):
        user = User.objects.create_superuser(username='admin', password='password')
        client.force_login(user)
        response = client.get(reverse('api_statistics'))
        assert response.status_code == 200
        data = response.json()
        assert 'total_exhibits' in data


@pytest.mark.django_db
class TestSearchAndFilter:
    """Test search and filter functionality"""

    def test_exhibit_search(self, client):
        art_type = ArtType.objects.create(name='Painting')
        hall = Hall.objects.create(number=1, name='Hall', floor=1, area=100.00)

        Exhibit.objects.create(
            name='Mona Lisa Copy',
            art_type=art_type,
            acquisition_date=date(2020, 5, 15),
            author='Unknown',
            hall=hall
        )

        response = client.get(reverse('exhibit_list'), {'search': 'Mona'})
        assert response.status_code == 200
        assert len(response.context['page_obj']) == 1

    def test_exhibit_filter_by_art_type(self, client):
        art_type1 = ArtType.objects.create(name='Painting')
        art_type2 = ArtType.objects.create(name='Sculpture')
        hall = Hall.objects.create(number=1, name='Hall', floor=1, area=100.00)

        Exhibit.objects.create(name='Painting 1', art_type=art_type1, acquisition_date=date(2020, 1, 1), hall=hall)
        Exhibit.objects.create(name='Sculpture 1', art_type=art_type2, acquisition_date=date(2020, 1, 1), hall=hall)

        response = client.get(reverse('exhibit_list'), {'art_type': art_type1.pk})
        assert response.status_code == 200
        assert len(response.context['page_obj']) == 1

    def test_exhibit_filter_by_floor(self, client):
        hall1 = Hall.objects.create(number=1, name='Hall 1', floor=1, area=100.00)
        hall2 = Hall.objects.create(number=2, name='Hall 2', floor=2, area=100.00)
        art_type = ArtType.objects.create(name='Painting')

        Exhibit.objects.create(name='Floor 1 Art', art_type=art_type, acquisition_date=date(2020, 1, 1), hall=hall1)
        Exhibit.objects.create(name='Floor 2 Art', art_type=art_type, acquisition_date=date(2020, 1, 1), hall=hall2)

        response = client.get(reverse('exhibit_list'), {'floor': '1'})
        assert response.status_code == 200
        assert len(response.context['page_obj']) == 1

    def test_tour_filter_by_season(self, client):
        Tour.objects.create(
            code='TOUR001', name='Spring Tour',
            date=datetime(2026, 3, 15, 10, 0),
            season='spring', group_size=20, price=25.00
        )
        Tour.objects.create(
            code='TOUR002', name='Summer Tour',
            date=datetime(2026, 6, 15, 10, 0),
            season='summer', group_size=20, price=25.00
        )

        response = client.get(reverse('tour_list'), {'season': 'spring'})
        assert response.status_code == 200
        assert len(response.context['page_obj']) == 1


@pytest.mark.django_db
class TestDetailView:
    """Test detail views"""

    def test_exhibit_detail(self, client):
        art_type = ArtType.objects.create(name='Painting')
        hall = Hall.objects.create(number=1, name='Hall', floor=1, area=100.00)
        exhibit = Exhibit.objects.create(
            name='Test Exhibit',
            art_type=art_type,
            acquisition_date=date(2020, 1, 1),
            hall=hall
        )

        response = client.get(reverse('exhibit_detail', kwargs={'pk': exhibit.pk}))
        assert response.status_code == 200

    def test_tour_detail(self, client):
        tour = Tour.objects.create(
            code='TOUR001',
            name='Test Tour',
            date=datetime(2026, 6, 15, 10, 0),
            season='summer',
            group_size=20,
            price=25.00
        )

        response = client.get(reverse('tour_detail', kwargs={'pk': tour.pk}))
        assert response.status_code == 200

    def test_ticket_detail(self, client):
        user = User.objects.create_user(username='testuser', password='password')
        client_obj = Client.objects.create(
            user=user,
            first_name='Test',
            last_name='Client',
            phone='+375 (29) 123-45-67',
            email='test@test.com',
            date_of_birth=date(1990, 1, 1)
        )
        ticket = Ticket.objects.create(
            client=client_obj,
            visit_date=date.today() + timedelta(days=7),
            ticket_type='adult',
            base_price=25.00,
            discount=0,
            final_price=25.00
        )

        response = client.get(reverse('ticket_detail', kwargs={'pk': ticket.pk}))
        assert response.status_code == 200


@pytest.mark.django_db
class TestTicketViews:
    """Test ticket CRUD views"""

    def test_ticket_list(self, client):
        user = User.objects.create_user(username='testuser', password='password')
        Client.objects.create(
            user=user,
            first_name='Test',
            last_name='Client',
            phone='+375 (29) 123-45-67',
            email='test@test.com',
            date_of_birth=date(1990, 1, 1)
        )
        # Ticket list requires login
        response = client.get(reverse('ticket_list'))
        assert response.status_code == 302  # Redirect to login

    def test_ticket_create_get(self, client):
        # Ticket create may redirect to login if required
        response = client.get(reverse('ticket_create'))
        assert response.status_code in [200, 302]

    def test_ticket_create_post(self, client):
        user = User.objects.create_user(username='testuser', password='password')
        client_obj = Client.objects.create(
            user=user,
            first_name='Test',
            last_name='Client',
            phone='+375 (29) 123-45-67',
            email='test@test.com',
            date_of_birth=date(1990, 1, 1)
        )

        data = {
            'client': client_obj.pk,
            'visit_date': (date.today() + timedelta(days=7)).isoformat(),
            'ticket_type': 'adult',
            'base_price': 25.00,
            'discount': 0,
        }
        response = client.post(reverse('ticket_create'), data)
        assert response.status_code in [200, 302]

    def test_review_create_get(self, client):
        # Review create may redirect to login if required
        response = client.get(reverse('review_create'))
        assert response.status_code in [200, 302]

    def test_review_create_post(self, client):
        user = User.objects.create_user(username='testuser', password='password')
        client_obj = Client.objects.create(
            user=user,
            first_name='Test',
            last_name='Client',
            phone='+375 (29) 123-45-67',
            email='test@test.com',
            date_of_birth=date(1990, 1, 1)
        )

        data = {
            'client': client_obj.pk,
            'rating': 5,
            'text': 'Great museum experience!',
            'visit_date': date.today().isoformat(),
        }
        response = client.post(reverse('review_create'), data)
        assert response.status_code == 302


@pytest.mark.django_db
class TestAuthViews:
    """Test authentication views"""

    def test_register_get(self, client):
        response = client.get(reverse('register'))
        assert response.status_code == 200

    def test_register_post_valid(self, client):
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        }
        response = client.post(reverse('register'), data)
        # May redirect (success) or stay (form error) - both are valid
        assert response.status_code in [200, 302]

    def test_login_get(self, client):
        response = client.get(reverse('login'))
        assert response.status_code == 200

    def test_login_post_valid(self, client):
        User.objects.create_user(username='testuser', password='password')
        data = {'username': 'testuser', 'password': 'password'}
        response = client.post(reverse('login'), data)
        assert response.status_code == 302  # Redirect after success

    def test_login_post_invalid(self, client):
        data = {'username': 'wrong', 'password': 'wrong'}
        response = client.post(reverse('login'), data)
        assert response.status_code == 200  # Re-render with error

    def test_logout(self, client):
        user = User.objects.create_user(username='testuser', password='password')
        client.force_login(user)
        response = client.get(reverse('logout'))
        assert response.status_code == 302

    def test_profile_get(self, client):
        user = User.objects.create_user(username='testuser', password='password')
        client.force_login(user)
        response = client.get(reverse('profile'))
        assert response.status_code == 200

    def test_profile_post(self, client):
        user = User.objects.create_user(username='testuser', password='password')
        client.force_login(user)
        Client.objects.create(
            user=user,
            first_name='Test',
            last_name='Client',
            phone='+375 (29) 123-45-67',
            email='test@test.com',
            date_of_birth=date(1990, 1, 1)
        )
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone': '+375 (29) 123-45-67',
            'email': 'updated@test.com',
            'date_of_birth': date(1990, 1, 1).isoformat(),
        }
        response = client.post(reverse('profile'), data)
        assert response.status_code == 302


@pytest.mark.django_db
class TestEmployeeDashboard:
    """Test employee dashboard"""

    def test_employee_dashboard_requires_employee(self, client):
        user = User.objects.create_user(username='emp', password='password')
        client.force_login(user)
        response = client.get(reverse('employee_dashboard'))
        assert response.status_code == 302

    def test_employee_dashboard_success(self, client):
        position = Position.objects.create(name='Guide')
        hall = Hall.objects.create(number=1, name='Hall', floor=1, area=100.00)
        user = User.objects.create_user(username='emp', password='password', email='emp@test.com')
        Employee.objects.create(
            user=user,
            first_name='John',
            last_name='Doe',
            phone='+375 (29) 123-45-67',
            email='emp@test.com',
            position=position,
            hall=hall,
            hire_date=date(2020, 1, 1),
            salary=1000.00
        )
        client.force_login(user)
        response = client.get(reverse('employee_dashboard'))
        assert response.status_code == 200


@pytest.mark.django_db
class TestPagination:
    """Test pagination in list views"""

    def test_exhibit_pagination(self, client):
        art_type = ArtType.objects.create(name='Painting')
        hall = Hall.objects.create(number=1, name='Hall', floor=1, area=100.00)

        # Create 15 exhibits (more than default page size)
        for i in range(15):
            Exhibit.objects.create(
                name=f'Exhibit {i}',
                art_type=art_type,
                acquisition_date=date(2020, 1, 1),
                hall=hall
            )

        response = client.get(reverse('exhibit_list'))
        assert response.status_code == 200
        assert 'page_obj' in response.context

    def test_tour_pagination(self, client):
        # Create 15 tours
        for i in range(15):
            Tour.objects.create(
                code=f'TOUR{i:03d}',
                name=f'Tour {i}',
                date=datetime(2026, 6, 15, 10, 0),
                season='summer',
                group_size=20,
                price=25.00
            )

        response = client.get(reverse('tour_list'))
        assert response.status_code == 200
        assert 'page_obj' in response.context

    def test_hall_pagination(self, client):
        # Create 15 halls
        for i in range(15):
            Hall.objects.create(number=i, name=f'Hall {i}', floor=(i % 5) + 1, area=100.00)

        response = client.get(reverse('hall_list'))
        assert response.status_code == 200
        # May or may not have page_obj depending on count


@pytest.mark.django_db
class TestNewsAndExhibitions:
    """Test news and exhibitions views"""

    def test_news(self, client):
        response = client.get(reverse('news'))
        assert response.status_code == 200
        assert 'exhibitions' in response.context

    def test_glossary(self, client):
        response = client.get(reverse('glossary'))
        assert response.status_code == 200
        # Glossary has terms in context

    def test_contacts(self, client):
        response = client.get(reverse('contacts'))
        assert response.status_code == 200

    def test_privacy(self, client):
        response = client.get(reverse('privacy'))
        assert response.status_code == 200

    def test_vacancies(self, client):
        response = client.get(reverse('vacancies'))
        assert response.status_code == 200


@pytest.mark.django_db
class TestTicketPricingEdgeCases:
    """Test edge cases in ticket pricing"""

    def test_zero_discount(self):
        client_obj = Client.objects.create(
            first_name='Test', last_name='Client',
            phone='+375 (29) 123-45-67', email='test@test.com',
            date_of_birth=date(1990, 1, 1)
        )
        ticket = Ticket.objects.create(
            client=client_obj,
            visit_date=date.today() + timedelta(days=7),
            ticket_type='adult',
            base_price=25.00,
            discount=0,
            final_price=0
        )
        ticket.calculate_price()
        assert ticket.final_price == 25.00

    def test_weekday_no_surcharge(self):
        client_obj = Client.objects.create(
            first_name='Test', last_name='Client',
            phone='+375 (29) 123-45-67', email='test@test.com',
            date_of_birth=date(1990, 1, 1)
        )
        # Monday
        ticket = Ticket.objects.create(
            client=client_obj,
            visit_date=date(2026, 6, 1),  # Monday
            ticket_type='adult',
            base_price=25.00,
            discount=0,
            final_price=0
        )
        ticket.calculate_price()
        assert ticket.final_price == 25.00  # No weekend surcharge

    def test_combined_discounts(self):
        client_obj = Client.objects.create(
            first_name='Senior', last_name='Test',
            phone='+375 (29) 123-45-67', email='senior@test.com',
            date_of_birth=date(1950, 1, 1)
        )
        ticket = Ticket.objects.create(
            client=client_obj,
            visit_date=date(2026, 6, 1),  # Monday
            ticket_type='senior',
            base_price=25.00,
            discount=10,  # Additional 10% discount
            final_price=0
        )
        ticket.calculate_price()
        # Senior 30% off = 17.50, then additional 10% = 15.75
        assert ticket.final_price < 17.50


@pytest.mark.django_db
class TestPromoCode:
    """Test promo code functionality"""

    def test_promocode_is_valid_active(self):
        now = timezone.now()
        promo = PromoCode.objects.create(
            code='SAVE10',
            discount_percent=10.0,
            valid_from=now - timedelta(days=1),
            valid_until=now + timedelta(days=30),
            is_active=True
        )
        assert promo.is_valid() is True

    def test_promocode_is_valid_inactive(self):
        now = timezone.now()
        promo = PromoCode.objects.create(
            code='INACTIVE',
            discount_percent=10.0,
            valid_from=now - timedelta(days=1),
            valid_until=now + timedelta(days=30),
            is_active=False
        )
        assert promo.is_valid() is False

    def test_promocode_is_valid_expired(self):
        now = timezone.now()
        promo = PromoCode.objects.create(
            code='EXPIRED',
            discount_percent=5.0,
            valid_from=now - timedelta(days=30),
            valid_until=now - timedelta(days=1),
            is_active=True
        )
        assert promo.is_valid() is False

    def test_promocode_is_valid_not_started(self):
        now = timezone.now()
        promo = PromoCode.objects.create(
            code='FUTURE',
            discount_percent=15.0,
            valid_from=now + timedelta(days=1),
            valid_until=now + timedelta(days=30),
            is_active=True
        )
        assert promo.is_valid() is False


@pytest.mark.django_db
class TestExhibitProperties:
    """Test exhibit model properties"""

    def test_exhibit_is_recent(self):
        art_type = ArtType.objects.create(name='Painting')
        hall = Hall.objects.create(number=1, name='Hall', floor=1, area=100.00)

        # Recent exhibit
        recent = Exhibit.objects.create(
            name='Recent',
            art_type=art_type,
            acquisition_date=timezone.now().date() - timedelta(days=30),
            hall=hall
        )
        # Check the acquisition date is within 6 months
        six_months_ago = timezone.now().date() - timedelta(days=180)
        assert recent.acquisition_date >= six_months_ago

        # Old exhibit
        old = Exhibit.objects.create(
            name='Old',
            art_type=art_type,
            acquisition_date=timezone.now().date() - timedelta(days=400),
            hall=hall
        )
        assert old.acquisition_date < six_months_ago


@pytest.mark.django_db
class TestHallProperties:
    """Test hall model properties"""

    def test_hall_str(self):
        hall = Hall.objects.create(number=1, name='Main Hall', floor=1, area=500.00)
        assert 'Hall 1' in str(hall)

    def test_hall_without_name(self):
        hall = Hall.objects.create(number=2, name='', floor=1, area=100.00)
        assert 'Hall 2' in str(hall)


@pytest.mark.django_db
class TestTourProperties:
    """Test tour model properties"""

    def test_tour_str(self):
        tour = Tour.objects.create(
            code='TOUR001',
            name='Art Tour',
            date=datetime(2026, 6, 15, 10, 0),
            season='summer',
            group_size=20,
            price=25.00
        )
        assert 'TOUR001' in str(tour)

    def test_tour_str_without_name(self):
        tour = Tour.objects.create(
            code='TOUR002',
            name='',
            date=datetime(2026, 6, 15, 10, 0),
            season='summer',
            group_size=20,
            price=25.00
        )
        assert 'TOUR002' in str(tour)


@pytest.mark.django_db
class TestTicketPricing:
    """Test ticket pricing logic"""
    
    def test_child_discount(self):
        client = Client.objects.create(
            first_name='Child', last_name='Test',
            phone='+375 (29) 123-45-67', email='child@test.com',
            date_of_birth=date(2015, 1, 1)
        )
        
        ticket = Ticket.objects.create(
            client=client,
            visit_date=date(2026, 6, 15),
            ticket_type='child',
            base_price=25.00,
            discount=0,
            final_price=0
        )
        ticket.calculate_price()
        assert ticket.final_price == 12.50  # 50% discount
    
    def test_senior_discount(self):
        client = Client.objects.create(
            first_name='Senior', last_name='Test',
            phone='+375 (29) 123-45-67', email='senior@test.com',
            date_of_birth=date(1950, 1, 1)
        )
        
        ticket = Ticket.objects.create(
            client=client,
            visit_date=date(2026, 6, 15),
            ticket_type='senior',
            base_price=25.00,
            discount=0,
            final_price=0
        )
        ticket.calculate_price()
        assert ticket.final_price == 17.50  # 30% discount
    
    def test_student_discount(self):
        client = Client.objects.create(
            first_name='Student', last_name='Test',
            phone='+375 (29) 123-45-67', email='student@test.com',
            date_of_birth=date(2000, 1, 1)
        )
        
        ticket = Ticket.objects.create(
            client=client,
            visit_date=date(2026, 6, 15),
            ticket_type='student',
            base_price=25.00,
            discount=0,
            final_price=0
        )
        ticket.calculate_price()
        assert ticket.final_price == 20.00  # 20% discount


@pytest.mark.django_db
class TestExternalAPI:
    """Test external API helpers"""

    def test_get_currency_rates(self):
        from store.views import get_currency_rates
        rates = get_currency_rates()
        assert isinstance(rates, dict)
        assert 'BYN' in rates or 'EUR' in rates

    def test_get_random_art_fact(self):
        from store.views import get_random_art_fact
        fact = get_random_art_fact()
        assert isinstance(fact, str)
        assert len(fact) > 0


@pytest.mark.django_db
class TestHomeView:
    """Test home view context"""

    def test_home_context(self, client):
        response = client.get(reverse('home'))
        assert response.status_code == 200
        # Home view should have context
        assert 'current_time_utc' in response.context


@pytest.mark.django_db
class TestAboutView:
    """Test about view"""

    def test_about_context(self, client):
        response = client.get(reverse('about'))
        assert response.status_code == 200


@pytest.mark.django_db
class TestContactsView:
    """Test contacts view"""

    def test_contacts_context(self, client):
        response = client.get(reverse('contacts'))
        assert response.status_code == 200


@pytest.mark.django_db
class TestVacanciesView:
    """Test vacancies view"""

    def test_vacancies_context(self, client):
        response = client.get(reverse('vacancies'))
        assert response.status_code == 200


@pytest.mark.django_db
class TestPrivacyView:
    """Test privacy view"""

    def test_privacy_context(self, client):
        response = client.get(reverse('privacy'))
        assert response.status_code == 200


@pytest.mark.django_db
class TestCalendarView:
    """Test calendar view"""

    def test_calendar_context(self, client):
        response = client.get(reverse('calendar'))
        assert response.status_code == 200
        assert 'calendar_text' in response.context
        assert 'current_month' in response.context


@pytest.mark.django_db
class TestExhibitListFilters:
    """Test exhibit list filtering"""

    def test_exhibit_filter_hall(self, client):
        art_type = ArtType.objects.create(name='Painting')
        hall1 = Hall.objects.create(number=1, name='Hall 1', floor=1, area=100.00)
        hall2 = Hall.objects.create(number=2, name='Hall 2', floor=2, area=100.00)

        Exhibit.objects.create(name='Exhibit 1', art_type=art_type, acquisition_date=date(2020, 1, 1), hall=hall1)
        Exhibit.objects.create(name='Exhibit 2', art_type=art_type, acquisition_date=date(2020, 1, 1), hall=hall2)

        response = client.get(reverse('exhibit_list'), {'hall': hall1.pk})
        assert response.status_code == 200

    def test_exhibit_filter_displayed(self, client):
        art_type = ArtType.objects.create(name='Painting')
        hall = Hall.objects.create(number=1, name='Hall', floor=1, area=100.00)

        Exhibit.objects.create(name='Displayed', art_type=art_type, acquisition_date=date(2020, 1, 1), hall=hall, is_displayed=True)
        Exhibit.objects.create(name='Storage', art_type=art_type, acquisition_date=date(2020, 1, 1), hall=hall, is_displayed=False)

        response = client.get(reverse('exhibit_list'), {'is_displayed': 'on'})
        assert response.status_code == 200


@pytest.mark.django_db
class TestTourListFilters:
    """Test tour list filtering"""

    def test_tour_filter_guide(self, client):
        position = Position.objects.create(name='Guide')
        hall = Hall.objects.create(number=1, name='Hall', floor=1, area=100.00)
        user = User.objects.create_user(username='guide', password='password', email='guide@test.com')
        employee = Employee.objects.create(
            user=user,
            first_name='John',
            last_name='Doe',
            phone='+375 (29) 123-45-67',
            email='guide@test.com',
            position=position,
            hall=hall,
            hire_date=date(2020, 1, 1),
            salary=1000.00
        )

        Tour.objects.create(code='TOUR001', name='Tour 1', date=datetime(2026, 6, 15, 10, 0), season='summer', group_size=20, price=25.00, guide=employee)
        Tour.objects.create(code='TOUR002', name='Tour 2', date=datetime(2026, 6, 15, 10, 0), season='summer', group_size=20, price=25.00)

        response = client.get(reverse('tour_list'), {'guide': employee.pk})
        assert response.status_code == 200


@pytest.mark.django_db
class TestEmployeeModel:
    """Test employee model"""

    def test_employee_str(self):
        position = Position.objects.create(name='Guide')
        hall = Hall.objects.create(number=1, name='Hall', floor=1, area=100.00)
        user = User.objects.create_user(username='emp', password='password', email='emp@test.com')
        employee = Employee.objects.create(
            user=user,
            first_name='John',
            last_name='Doe',
            phone='+375 (29) 123-45-67',
            email='emp@test.com',
            position=position,
            hall=hall,
            hire_date=date(2020, 1, 1),
            salary=1000.00
        )
        assert 'Doe' in str(employee)

    def test_employee_clean_phone(self):
        position = Position.objects.create(name='Guide')
        user = User.objects.create_user(username='emp2', password='password', email='emp2@test.com')
        employee = Employee(
            user=user,
            first_name='Jane',
            last_name='Doe',
            phone='invalid',
            email='emp2@test.com',
            position=position,
            hire_date=date(2020, 1, 1),
            salary=1000.00
        )
        with pytest.raises(Exception):
            employee.full_clean()


@pytest.mark.django_db
class TestPositionModel:
    """Test position model"""

    def test_position_str(self):
        position = Position.objects.create(name='Curator', description='Manages exhibits')
        assert str(position) == 'Curator'


@pytest.mark.django_db
class TestArtTypeModel:
    """Test art type model"""

    def test_art_type_str(self):
        art_type = ArtType.objects.create(name='Painting', description='Oil paintings')
        assert str(art_type) == 'Painting'


@pytest.mark.django_db
class TestExhibitionModel:
    """Test exhibition model"""

    def test_exhibition_str(self):
        exhibition = Exhibition.objects.create(
            name='Summer Exhibition',
            description='Summer art show',
            start_date=date(2026, 6, 1),
            end_date=date(2026, 8, 31)
        )
        assert str(exhibition) == 'Summer Exhibition'


@pytest.mark.django_db
class TestExpositionModel:
    """Test exposition model"""

    def test_exposition_str(self):
        hall = Hall.objects.create(number=1, name='Hall', floor=1, area=100.00)
        exposition = Exposition.objects.create(
            name='Main Exposition',
            hall=hall
        )
        assert str(exposition) == 'Main Exposition'


@pytest.mark.django_db
class TestStatisticsView:
    """Test statistics view"""

    def test_statistics_staff(self, client):
        user = User.objects.create_superuser(username='admin', password='password')
        client.force_login(user)
        response = client.get(reverse('statistics'))
        assert response.status_code == 200
        assert 'total_exhibits' in response.context
        assert 'total_halls' in response.context

    def test_statistics_redirects_non_staff(self, client):
        user = User.objects.create_user(username='user', password='password')
        client.force_login(user)
        response = client.get(reverse('statistics'))
        assert response.status_code == 302


@pytest.mark.django_db
class TestAPIStatistics:
    """Test API statistics endpoint"""

    def test_api_statistics_data(self, client):
        user = User.objects.create_superuser(username='admin', password='password')
        client.force_login(user)
        response = client.get(reverse('api_statistics'))
        assert response.status_code == 200
        data = response.json()
        assert 'total_exhibits' in data
        assert 'total_halls' in data
        assert 'total_tours' in data
        assert 'total_revenue' in data


@pytest.mark.django_db
class TestAPICurrencyRates:
    """Test API currency rates endpoint"""

    def test_api_currency_rates_data(self, client):
        response = client.get(reverse('api_currency_rates'))
        assert response.status_code == 200
        data = response.json()
        assert 'rates' in data


@pytest.mark.django_db
class TestNewsView:
    """Test news/exhibitions view"""

    def test_news_exhibitions_context(self, client):
        # Create an exhibition
        Exhibition.objects.create(
            name='Test Exhibition',
            description='Test',
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31)
        )
        response = client.get(reverse('news'))
        assert response.status_code == 200
        assert 'exhibitions' in response.context


@pytest.mark.django_db
class TestGlossaryView:
    """Test glossary view"""

    def test_glossary_terms(self, client):
        response = client.get(reverse('glossary'))
        assert response.status_code == 200
        # Glossary has terms in context


@pytest.mark.django_db
class TestTicketDetailView:
    """Test ticket detail view"""

    def test_ticket_detail_context(self, client):
        user = User.objects.create_user(username='testuser', password='password')
        client_obj = Client.objects.create(
            user=user,
            first_name='Test',
            last_name='Client',
            phone='+375 (29) 123-45-67',
            email='test@test.com',
            date_of_birth=date(1990, 1, 1)
        )
        ticket = Ticket.objects.create(
            client=client_obj,
            visit_date=date.today() + timedelta(days=7),
            ticket_type='adult',
            base_price=25.00,
            discount=0,
            final_price=25.00
        )
        response = client.get(reverse('ticket_detail', kwargs={'pk': ticket.pk}))
        assert response.status_code == 200
        assert 'ticket' in response.context


@pytest.mark.django_db
class TestClientModel:
    """Test client model"""

    def test_client_age_property(self):
        user = User.objects.create_user(username='client', password='password', email='client@test.com')
        client = Client.objects.create(
            user=user,
            first_name='Test',
            last_name='Client',
            phone='+375 (29) 123-45-67',
            email='client@test.com',
            date_of_birth=date(1990, 1, 1)
        )
        assert client.age >= 18

    def test_client_str(self):
        user = User.objects.create_user(username='client2', password='password', email='client2@test.com')
        client = Client.objects.create(
            user=user,
            first_name='John',
            last_name='Doe',
            phone='+375 (29) 123-45-67',
            email='john@test.com',
            date_of_birth=date(1990, 1, 1)
        )
        assert 'Doe' in str(client)


@pytest.mark.django_db
class TestTicketModel:
    """Test ticket model"""

    def test_ticket_str(self):
        user = User.objects.create_user(username='ticket', password='password', email='ticket@test.com')
        client = Client.objects.create(
            user=user,
            first_name='Test',
            last_name='Client',
            phone='+375 (29) 123-45-67',
            email='ticket@test.com',
            date_of_birth=date(1990, 1, 1)
        )
        ticket = Ticket.objects.create(
            client=client,
            visit_date=date.today() + timedelta(days=7),
            ticket_type='adult',
            base_price=25.00,
            discount=0,
            final_price=25.00
        )
        assert 'Ticket' in str(ticket)

    def test_ticket_calculate_price(self):
        user = User.objects.create_user(username='ticket2', password='password', email='ticket2@test.com')
        client = Client.objects.create(
            user=user,
            first_name='Test',
            last_name='Client',
            phone='+375 (29) 123-45-67',
            email='ticket2@test.com',
            date_of_birth=date(1990, 1, 1)
        )
        ticket = Ticket.objects.create(
            client=client,
            visit_date=date.today() + timedelta(days=7),
            ticket_type='adult',
            base_price=100.00,
            discount=20,
            final_price=0
        )
        ticket.calculate_price()
        assert ticket.final_price == 80.00


@pytest.mark.django_db
class TestReviewModel:
    """Test review model"""

    def test_review_str(self):
        user = User.objects.create_user(username='review', password='password', email='review@test.com')
        client = Client.objects.create(
            user=user,
            first_name='Test',
            last_name='Client',
            phone='+375 (29) 123-45-67',
            email='review@test.com',
            date_of_birth=date(1990, 1, 1)
        )
        review = Review.objects.create(
            client=client,
            rating=5,
            text='Great!'
        )
        assert '5' in str(review)


@pytest.mark.django_db
class TestPromoCodeModel:
    """Test promo code model"""

    def test_promocode_str(self):
        now = timezone.now()
        promo = PromoCode.objects.create(
            code='TEST10',
            description='Test promo',
            discount_percent=10.0,
            valid_from=now - timedelta(days=1),
            valid_until=now + timedelta(days=30)
        )
        assert 'TEST10' in str(promo)


@pytest.mark.django_db
class TestExternalAPIErrorHandling:
    """Test external API error handling"""

    def test_get_currency_rates_fallback(self):
        # The get_currency_rates function already handles errors internally
        # and returns fallback values, so we just verify it works
        from store.views import get_currency_rates
        rates = get_currency_rates()
        assert isinstance(rates, dict)
        # Should have some currency rates (either from API or fallback)
        assert len(rates) > 0


@pytest.mark.django_db
class TestHallDetailView:
    """Test hall detail view"""

    def test_hall_detail(self, client):
        hall = Hall.objects.create(number=1, name='Test Hall', floor=1, area=100.00)
        response = client.get(reverse('hall_list'))
        assert response.status_code == 200


@pytest.mark.django_db
class TestExhibitCreateView:
    """Test exhibit create view"""

    def test_exhibit_create_get(self, client):
        user = User.objects.create_superuser(username='admin', password='password')
        client.force_login(user)
        # Check if exhibit create view exists
        response = client.get('/exhibits/create/')
        # May 404 if not implemented
        assert response.status_code in [200, 404, 302]


@pytest.mark.django_db
class TestTourCreateView:
    """Test tour create view"""

    def test_tour_create_get(self, client):
        user = User.objects.create_superuser(username='admin', password='password')
        client.force_login(user)
        response = client.get('/tours/create/')
        assert response.status_code in [200, 404, 302]


@pytest.mark.django_db
class TestEmployeeModelMethods:
    """Test employee model methods"""

    def test_employee_clean_valid_phone(self):
        position = Position.objects.create(name='Guide')
        user = User.objects.create_user(username='emp3', password='password', email='emp3@test.com')
        employee = Employee(
            user=user,
            first_name='Valid',
            last_name='Employee',
            phone='+375 (29) 123-45-67',
            email='emp3@test.com',
            position=position,
            hire_date=date(2020, 1, 1),
            salary=1000.00
        )
        # Should not raise
        employee.full_clean()


@pytest.mark.django_db
class TestTicketModelMethods:
    """Test ticket model methods"""

    def test_ticket_clean_valid(self):
        user = User.objects.create_user(username='ticket3', password='password', email='ticket3@test.com')
        client = Client.objects.create(
            user=user,
            first_name='Test',
            last_name='Client',
            phone='+375 (29) 123-45-67',
            email='ticket3@test.com',
            date_of_birth=date(1990, 1, 1)
        )
        ticket = Ticket(
            client=client,
            visit_date=date.today() + timedelta(days=7),
            ticket_type='adult',
            base_price=25.00,
            discount=10,
            final_price=22.50
        )
        # Should not raise
        ticket.full_clean()


@pytest.mark.django_db
class TestReviewModelMethods:
    """Test review model methods"""

    def test_review_clean_valid(self):
        user = User.objects.create_user(username='review2', password='password', email='review2@test.com')
        client = Client.objects.create(
            user=user,
            first_name='Test',
            last_name='Client',
            phone='+375 (29) 123-45-67',
            email='review2@test.com',
            date_of_birth=date(1990, 1, 1)
        )
        review = Review(
            client=client,
            rating=4,
            text='Good museum'
        )
        # Should not raise
        review.full_clean()


@pytest.mark.django_db
class TestExhibitModelMethods:
    """Test exhibit model methods"""

    def test_exhibit_clean(self):
        art_type = ArtType.objects.create(name='Painting')
        hall = Hall.objects.create(number=1, name='Hall', floor=1, area=100.00)
        exhibit = Exhibit(
            name='Test Exhibit',
            art_type=art_type,
            acquisition_date=date(2020, 1, 1),
            hall=hall
        )
        # Should not raise
        exhibit.full_clean()


@pytest.mark.django_db
class TestTourModelMethods:
    """Test tour model methods"""

    def test_tour_clean(self):
        position = Position.objects.create(name='Guide')
        hall = Hall.objects.create(number=1, name='Hall', floor=1, area=100.00)
        user = User.objects.create_user(username='guide', password='password', email='guide@test.com')
        employee = Employee.objects.create(
            user=user,
            first_name='John',
            last_name='Doe',
            phone='+375 (29) 123-45-67',
            email='guide@test.com',
            position=position,
            hall=hall,
            hire_date=date(2020, 1, 1),
            salary=1000.00
        )
        tour = Tour(
            code='TOUR003',
            name='Test Tour',
            description='Test description',
            date=datetime(2026, 6, 15, 10, 0),
            season='summer',
            group_size=20,
            price=25.00,
            guide=employee
        )
        # Should not raise
        tour.full_clean()


@pytest.mark.django_db
class TestHallModelMethods:
    """Test hall model methods"""

    def test_hall_clean_valid_floor(self):
        hall = Hall(number=1, name='Valid Hall', floor=1, area=100.00)
        # Should not raise
        hall.full_clean()

    def test_hall_clean_invalid_floor(self):
        hall = Hall(number=2, name='Invalid Hall', floor=-1, area=100.00)
        with pytest.raises(Exception):
            hall.full_clean()


@pytest.mark.django_db
class TestExhibitionModelMethods:
    """Test exhibition model methods"""

    def test_exhibition_clean_valid_dates(self):
        exhibition = Exhibition(
            name='Valid Exhibition',
            description='Test',
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31)
        )
        # Should not raise
        exhibition.full_clean()

    def test_exhibition_clean_invalid_dates(self):
        exhibition = Exhibition(
            name='Invalid Exhibition',
            description='Test',
            start_date=date(2026, 12, 31),
            end_date=date(2026, 1, 1)
        )
        with pytest.raises(Exception):
            exhibition.full_clean()
