from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Position, ArtType, Hall, Employee, Exhibit, Exposition, Exhibition, Tour, Client, Ticket, PromoCode, Review
from datetime import date, timedelta
from django.utils import timezone
import random


class Command(BaseCommand):
    help = 'Populate database with museum sample data'

    def handle(self, *args, **options):
        self.stdout.write('Populating museum database...')

        # Create positions
        positions_data = ['Curator', 'Guide', 'Security', 'Conservator', 'Director']
        positions = []
        for name in positions_data:
            pos, _ = Position.objects.get_or_create(name=name)
            positions.append(pos)
        self.stdout.write(f'Created {len(positions)} positions')

        # Create art types
        art_types_data = [
            ('Painting', 'Oil, watercolor, and acrylic paintings'),
            ('Sculpture', 'Stone, metal, and wood sculptures'),
            ('Photography', 'Historical and modern photography'),
            ('Ceramics', 'Pottery and ceramic art'),
            ('Textiles', 'Fabric and textile art'),
        ]
        art_types = []
        for name, desc in art_types_data:
            at, _ = ArtType.objects.get_or_create(name=name, defaults={'description': desc})
            art_types.append(at)
        self.stdout.write(f'Created {len(art_types)} art types')

        # Create halls
        halls_data = [
            (1, 'Main Hall', 1, 500.0, True, True),
            (2, 'Modern Art', 2, 300.0, False, True),
            (3, 'Ancient History', 1, 400.0, False, True),
            (4, 'Sculpture Garden', 1, 600.0, True, False),
            (5, 'Photography', 3, 250.0, False, True),
        ]
        halls = []
        for number, name, floor, area, water, heating in halls_data:
            hall, _ = Hall.objects.get_or_create(
                number=number,
                defaults={
                    'name': name,
                    'floor': floor,
                    'area': area,
                    'has_water_feature': water,
                    'has_heating': heating
                }
            )
            halls.append(hall)
        self.stdout.write(f'Created {len(halls)} halls')

        # Create employees
        employees_data = [
            ('Ivan', 'Petrov', 'Ivanovich', '+375 (29) 111-22-33', 'ivan@museum.by', 0, 1, date(2018, 1, 1), 1500.00),
            ('Anna', 'Sidorova', 'Mikhailovna', '+375 (29) 222-33-44', 'anna@museum.by', 1, 2, date(2019, 6, 1), 1200.00),
            ('Dmitry', 'Kozlov', 'Sergeevich', '+375 (29) 333-44-55', 'dmitry@museum.by', 2, 1, date(2020, 3, 15), 1000.00),
            ('Elena', 'Novikova', 'Andreevna', '+375 (29) 444-55-66', 'elena@museum.by', 3, 3, date(2017, 9, 1), 1800.00),
            ('Sergey', 'Volkov', 'Dmitrievich', '+375 (29) 555-66-77', 'sergey@museum.by', 4, 4, date(2021, 2, 1), 900.00),
        ]
        employees = []
        for first, last, middle, phone, email, pos_idx, hall_idx, hire_date, salary in employees_data:
            user, _ = User.objects.get_or_create(
                username=f'{first.lower()}.{last.lower()}',
                defaults={'first_name': first, 'last_name': last, 'email': email, 'is_staff': True}
            )
            employee, _ = Employee.objects.get_or_create(
                user=user,
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'middle_name': middle,
                    'phone': phone,
                    'email': email,
                    'position': positions[pos_idx],
                    'hall': halls[hall_idx] if hall_idx else None,
                    'hire_date': hire_date,
                    'salary': salary
                }
            )
            employees.append(employee)
        self.stdout.write(f'Created {len(employees)} employees')

        # Create exhibits
        exhibits_data = [
            ('Mona Lisa Copy', 0, date(2020, 5, 15), 1503, 'Unknown Artist', 'A copy of the famous painting', 0, 0),
            ('David Sculpture', 1, date(2019, 8, 20), 1504, 'Michelangelo', 'Marble sculpture replica', 3, 1),
            ('War Photo', 2, date(2021, 3, 10), 1945, 'Robert Capa', 'Historical war photograph', 4, 2),
            ('Ancient Vase', 3, date(2018, 11, 5), -500, 'Greek Artist', 'Ancient Greek ceramic vase', 2, 3),
            ('Tapestry', 4, date(2022, 1, 20), 1600, 'Flemish Artist', 'Medieval tapestry', 1, 4),
            ('Sunset Painting', 0, date(2023, 6, 15), 1889, 'Van Gogh', 'Oil painting of sunset', 1, 0),
            ('Modern Sculpture', 1, date(2023, 9, 1), 2020, 'Contemporary Artist', 'Abstract metal sculpture', 3, 1),
            ('Portrait', 0, date(2020, 12, 10), 1920, 'Picasso', 'Cubist portrait', 2, 2),
            ('Landscape', 0, date(2021, 7, 25), 1850, 'Monet', 'Impressionist landscape', 1, 3),
            ('Still Life', 0, date(2022, 4, 18), 1700, 'Dutch Master', 'Oil on canvas', 2, 4),
            ('Bronze Statue', 1, date(2019, 2, 28), 100, 'Roman Artist', 'Ancient bronze statue', 3, 0),
            ('Black & White Photo', 2, date(2023, 11, 5), 1950, 'Ansel Adams', 'Nature photography', 4, 1),
        ]
        exhibits = []
        for name, art_idx, acq_date, year, author, desc, hall_idx, emp_idx in exhibits_data:
            exhibit = Exhibit.objects.create(
                name=name,
                art_type=art_types[art_idx],
                acquisition_date=acq_date,
                year_created=year,
                author=author,
                description=desc,
                hall=halls[hall_idx],
                assigned_employee=employees[emp_idx] if emp_idx else None,
                is_displayed=True
            )
            exhibits.append(exhibit)
        self.stdout.write(f'Created {len(exhibits)} exhibits')

        # Create superuser
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@museum.by', 'is_staff': True, 'is_superuser': True}
        )
        admin_user.set_password('admin123')
        admin_user.save()

        # Create clients
        clients_data = [
            ('Alice', 'Brown', 'alice@example.com', '+375 (29) 666-77-88', date(1985, 1, 1)),
            ('Charlie', 'Wilson', 'charlie@example.com', '+375 (29) 777-88-99', date(1990, 6, 15)),
            ('Diana', 'Miller', 'diana@example.com', '+375 (29) 888-99-00', date(1988, 3, 20)),
            ('Edward', 'Davis', 'edward@example.com', '+375 (29) 999-00-11', date(1992, 11, 8)),
            ('Fiona', 'Garcia', 'fiona@example.com', '+375 (29) 000-11-22', date(1995, 7, 30)),
        ]
        clients = []
        for first, last, email, phone, dob in clients_data:
            user, _ = User.objects.get_or_create(
                username=f'{first.lower()}.{last.lower()}',
                defaults={'first_name': first, 'last_name': last, 'email': email}
            )
            client, _ = Client.objects.get_or_create(
                user=user,
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'phone': phone,
                    'email': email,
                    'date_of_birth': dob
                }
            )
            clients.append(client)
        self.stdout.write(f'Created {len(clients)} clients')

        # Create tours
        seasons = ['spring', 'summer', 'autumn', 'winter']
        from datetime import datetime
        tours_data = [
            ('TOUR001', 'Art History Tour', datetime(2026, 3, 15, 10, 0), 'spring', 20, 1, 25.00),
            ('TOUR002', 'Sculpture Walk', datetime(2026, 6, 20, 14, 0), 'summer', 15, 2, 30.00),
            ('TOUR003', 'Photography Exhibition', datetime(2026, 9, 10, 11, 0), 'autumn', 25, 3, 20.00),
            ('TOUR004', 'Winter Classics', datetime(2026, 12, 5, 13, 0), 'winter', 18, 4, 35.00),
            ('TOUR005', 'Modern Art Tour', datetime(2026, 4, 25, 15, 0), 'spring', 22, 0, 28.00),
        ]
        tours = []
        for code, name, dt, season, size, guide_idx, price in tours_data:
            tour = Tour.objects.create(
                code=code,
                name=name,
                description=f'A guided tour through our {name.lower()}',
                date=dt,
                season=season,
                group_size=size,
                guide=employees[guide_idx] if guide_idx else None,
                price=price
            )
            tours.append(tour)
        self.stdout.write(f'Created {len(tours)} tours')

        # Create tickets
        for i, client in enumerate(clients):
            ticket = Ticket.objects.create(
                client=client,
                tour=tours[i % len(tours)],
                visit_date=date.today() + timedelta(days=i+7),
                ticket_type=['adult', 'child', 'senior', 'student'][i % 4],
                base_price=25.00,
                discount=i * 5,
                final_price=0  # Will be calculated
            )
            ticket.calculate_price()
            ticket.save()
        self.stdout.write(f'Created {len(clients)} tickets')

        # Create promo codes
        now = timezone.now()
        promo_codes = [
            ('MUSEUM10', 'Museum discount', 10.0, 50.0, True),
            ('STUDENT20', 'Student discount', 20.0, 0, True),
            ('EXPIRED', 'Expired code', 15.0, 0, False),
        ]
        for code, desc, discount, min_amount, is_active in promo_codes:
            PromoCode.objects.get_or_create(
                code=code,
                defaults={
                    'description': desc,
                    'discount_percent': discount,
                    'min_purchase': min_amount,
                    'is_active': is_active,
                    'valid_from': now - timedelta(days=30),
                    'valid_until': now + timedelta(days=60) if is_active else now - timedelta(days=10)
                }
            )
        self.stdout.write('Created promo codes')

        self.stdout.write(self.style.SUCCESS('Successfully populated museum database!'))
        self.stdout.write(self.style.WARNING('Superuser: admin / admin123'))
