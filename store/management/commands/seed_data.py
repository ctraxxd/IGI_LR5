import logging
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, date
from store.models import (
    Position, ArtType, Hall, Employee, Exhibit, Exposition,
    Exhibition, Tour, Client, Ticket, PromoCode, Review,
    Vacancy, CompanyHistory, CompanyInfo
)

logger = logging.getLogger('museum')


class Command(BaseCommand):
    help = 'Populate database with sample data for Museum project (Variant 9)'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting database seeding...')

        # Create superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@museum.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created superuser: admin / admin123'))

        # Create positions
        positions_data = [
            ('Director', 'Museum director'),
            ('Curator', 'Exhibition curator'),
            ('Guide', 'Tour guide'),
            ('Security Guard', 'Security personnel'),
            ('Restorer', 'Art restorer'),
            ('Administrator', 'Front desk administrator'),
        ]
        positions = {}
        for name, desc in positions_data:
            pos, _ = Position.objects.get_or_create(name=name, defaults={'description': desc})
            positions[name] = pos
        self.stdout.write(f'Created {len(positions)} positions')

        # Create art types
        art_types_data = [
            ('Painting', 'Oil, watercolor, and acrylic paintings'),
            ('Sculpture', '3D artworks in various materials'),
            ('Photography', 'Photographic art'),
            ('Graphics', 'Drawings, prints, and digital art'),
            ('Decorative Arts', 'Ceramics, glass, textiles'),
            ('Modern Art', 'Contemporary and modern artworks'),
        ]
        art_types = {}
        for name, desc in art_types_data:
            at, _ = ArtType.objects.get_or_create(name=name, defaults={'description': desc})
            art_types[name] = at
        self.stdout.write(f'Created {len(art_types)} art types')

        # Create halls
        halls_data = [
            (1, 'Main Hall', 1, 250.00, True, True),
            (2, 'European Art', 1, 180.00, False, True),
            (3, 'Asian Art', 2, 150.00, True, True),
            (4, 'Modern Gallery', 2, 200.00, False, True),
            (5, 'Sculpture Hall', 3, 300.00, True, True),
            (6, 'Temporary Exhibitions', 3, 175.00, False, True),
        ]
        halls = {}
        for number, name, floor, area, water, heating in halls_data:
            hall, _ = Hall.objects.get_or_create(
                number=number,
                defaults={
                    'name': name,
                    'floor': floor,
                    'area': area,
                    'has_water_feature': water,
                    'has_heating': heating,
                }
            )
            halls[number] = hall
        self.stdout.write(f'Created {len(halls)} halls')

        # Create employees
        employees_data = [
            ('Ivanov', 'Ivan', 'Petrovich', '+375 (29) 123-45-67', 'ivanov@museum.by', 'Director', 1, '2015-03-15', 5000),
            ('Petrova', 'Anna', 'Sergeevna', '+375 (29) 234-56-78', 'petrova@museum.by', 'Curator', 2, '2017-06-20', 3500),
            ('Sidorov', 'Dmitry', 'Alexeevich', '+375 (29) 345-67-89', 'sidorov@museum.by', 'Guide', 1, '2019-01-10', 2500),
            ('Kozlova', 'Elena', 'Dmitrievna', '+375 (29) 456-78-90', 'kozlova@museum.by', 'Guide', 3, '2020-04-05', 2500),
            ('Novikov', 'Andrey', 'Ivanovich', '+375 (29) 567-89-01', 'novikov@museum.by', 'Security Guard', 1, '2018-09-12', 2000),
            ('Morozova', 'Olga', 'Pavlovna', '+375 (29) 678-90-12', 'morozova@museum.by', 'Restorer', 2, '2016-11-30', 4000),
            ('Volkov', 'Sergey', 'Nikolaevich', '+375 (29) 789-01-23', 'volkov@museum.by', 'Administrator', 1, '2021-02-14', 2200),
            ('Lebedeva', 'Maria', 'Andreevna', '+375 (29) 890-12-34', 'lebedeva@museum.by', 'Curator', 4, '2019-07-22', 3500),
            ('Sokolov', 'Pavel', 'Dmitrievich', '+375 (29) 901-23-45', 'sokolov@museum.by', 'Security Guard', 3, '2020-08-18', 2000),
            ('Pavlova', 'Natalia', 'Sergeevna', '+375 (29) 012-34-56', 'pavlova@museum.by', 'Guide', 2, '2018-05-25', 2500),
        ]
        employees = {}
        for last, first, middle, phone, email, pos_name, hall_num, hire_date, salary in employees_data:
            emp, _ = Employee.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'middle_name': middle,
                    'phone': phone,
                    'position': positions[pos_name],
                    'hall': halls.get(hall_num),
                    'hire_date': hire_date,
                    'salary': salary,
                }
            )
            employees[last] = emp
        self.stdout.write(f'Created {len(employees)} employees')

        # Create exhibits
        exhibits_data = [
            ('Mona Lisa Replica', 'Painting', '2023-01-15', 1503, 'Leonardo da Vinci', 'Famous portrait', 1, 'Ivanov'),
            ('The Scream Copy', 'Painting', '2023-02-20', 1893, 'Edvard Munch', 'Expressionist masterpiece', 2, 'Petrova'),
            ('David Sculpture', 'Sculpture', '2023-03-10', 1504, 'Michelangelo', 'Renaissance sculpture', 5, 'Morozova'),
            ('Sunflowers', 'Painting', '2023-04-05', 1888, 'Vincent van Gogh', 'Post-impressionist work', 2, 'Petrova'),
            ('The Kiss', 'Painting', '2023-05-12', 1908, 'Gustav Klimt', 'Art Nouveau painting', 4, 'Lebedeva'),
            ('Thinker', 'Sculpture', '2023-06-18', 1902, 'Auguste Rodin', 'Bronze sculpture', 5, 'Morozova'),
            ('Girl with a Pearl Earring', 'Painting', '2023-07-22', 1665, 'Johannes Vermeer', 'Dutch Golden Age', 1, 'Ivanov'),
            ('Starry Night', 'Painting', '2023-08-30', 1889, 'Vincent van Gogh', 'Night landscape', 2, 'Petrova'),
            ('Asian Dragon', 'Sculpture', '2023-09-14', 1750, 'Unknown Master', 'Chinese bronze dragon', 3, 'Kozlova'),
            ('Modern Abstract', 'Modern Art', '2023-10-25', 2020, 'Contemporary Artist', 'Abstract composition', 4, 'Lebedeva'),
            ('Cherry Blossom', 'Photography', '2023-11-08', 2022, 'Japanese Photographer', 'Spring in Kyoto', 3, 'Kozlova'),
            ('Geometric Dreams', 'Graphics', '2023-12-01', 2021, 'Digital Artist', 'Digital art piece', 4, 'Lebedeva'),
        ]
        exhibits = {}
        for name, art_type, acq_date, year, author, desc, hall_num, emp_last in exhibits_data:
            exhibit, _ = Exhibit.objects.get_or_create(
                name=name,
                defaults={
                    'art_type': art_types[art_type],
                    'acquisition_date': acq_date,
                    'year_created': year,
                    'author': author,
                    'description': desc,
                    'hall': halls.get(hall_num),
                    'assigned_employee': employees.get(emp_last),
                    'is_displayed': True,
                }
            )
            exhibits[name] = exhibit
        self.stdout.write(f'Created {len(exhibits)} exhibits')

        # Create expositions
        exposition_data = [
            ('Renaissance Masters', 'Collection of Renaissance art', 1, ['Mona Lisa Replica', 'David Sculpture', 'Girl with a Pearl Earring']),
            ('Impressionism', 'Impressionist and Post-impressionist works', 2, ['Sunflowers', 'Starry Night', 'The Scream Copy']),
            ('Modern Vision', 'Contemporary and modern art', 4, ['The Kiss', 'Modern Abstract', 'Geometric Dreams']),
        ]
        for name, desc, hall_num, exhibit_names in exposition_data:
            exp, _ = Exposition.objects.get_or_create(
                name=name,
                defaults={
                    'description': desc,
                    'hall': halls.get(hall_num),
                }
            )
            for en in exhibit_names:
                exp.exhibits.add(exhibits.get(en))
        self.stdout.write('Created expositions')

        # Create exhibitions (temporary)
        exhibitions_data = [
            ('Winter Wonderland', 'Winter-themed art', '2024-12-01', '2025-02-28', ['Starry Night', 'Cherry Blossom']),
            ('Spring Renewal', 'Spring collection', '2025-03-01', '2025-05-31', ['Sunflowers', 'Cherry Blossom', 'Geometric Dreams']),
        ]
        for name, desc, start, end, exhibit_names in exhibitions_data:
            exh, _ = Exhibition.objects.get_or_create(
                name=name,
                defaults={
                    'description': desc,
                    'start_date': start,
                    'end_date': end,
                    'is_active': True,
                }
            )
            for en in exhibit_names:
                exh.exhibits.add(exhibits.get(en))
        self.stdout.write('Created exhibitions')

        # Create tours
        tours_data = [
            ('TOUR-001', 'Classic Museum Tour', 'Overview of main exhibits', '2025-01-15 10:00:00', 15, 'spring', 'Sidorov', 25.00),
            ('TOUR-002', 'Renaissance Journey', 'Deep dive into Renaissance art', '2025-02-20 14:00:00', 10, 'spring', 'Petrova', 35.00),
            ('TOUR-003', 'Modern Art Experience', 'Contemporary artworks tour', '2025-06-10 11:00:00', 12, 'summer', 'Lebedeva', 30.00),
            ('TOUR-004', 'Sculpture Walk', '3D art through the ages', '2025-07-15 15:00:00', 8, 'summer', 'Kozlova', 28.00),
            ('TOUR-005', 'Asian Art Discovery', 'Explore Asian masterpieces', '2025-09-05 10:00:00', 10, 'autumn', 'Sidorov', 32.00),
            ('TOUR-006', 'Evening at the Museum', 'Special evening tour', '2025-10-20 18:00:00', 20, 'autumn', 'Pavlova', 40.00),
            ('TOUR-007', 'Winter Tales', 'Winter-themed exhibits', '2025-12-15 12:00:00', 15, 'winter', 'Kozlova', 30.00),
            ('TOUR-008', 'Holiday Special', 'Festive season tour', '2025-12-25 14:00:00', 25, 'winter', 'Sidorov', 45.00),
        ]
        tours = {}
        for code, name, desc, tour_date, size, season, guide_last, price in tours_data:
            tour, _ = Tour.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'description': desc,
                    'date': tour_date,
                    'group_size': size,
                    'season': season,
                    'guide': employees.get(guide_last),
                    'price': price,
                }
            )
            tours[code] = tour
        self.stdout.write(f'Created {len(tours)} tours')

        # Create clients
        clients_data = [
            ('Smirnov', 'Alexey', 'Ivanovich', '+375 (29) 111-22-33', 'smirnov@mail.by', '1990-05-15', 'Minsk, Independence Ave 10'),
            ('Kuznetsova', 'Maria', 'Petrovna', '+375 (29) 222-33-44', 'kuznetsova@mail.by', '1985-08-22', 'Gomel, Lenin St 25'),
            ('Popov', 'Dmitry', 'Sergeevich', '+375 (29) 333-44-55', 'popov@mail.by', '1992-12-01', 'Brest, Soviet St 5'),
            ('Vasilieva', 'Anna', 'Dmitrievna', '+375 (29) 444-55-66', 'vasilieva@mail.by', '1988-03-10', 'Vitebsk, Kirova St 15'),
            ('Mikhailov', 'Pavel', 'Andreevich', '+375 (29) 555-66-77', 'mikhailov@mail.by', '1995-07-20', 'Mogilev, Leninskaya St 30'),
            ('Fedorova', 'Elena', 'Sergeevna', '+375 (29) 666-77-88', 'fedorova@mail.by', '1980-11-05', 'Minsk, Yakuba Kolasa St 42'),
            ('Romanov', 'Andrey', 'Pavlovich', '+375 (29) 777-88-99', 'romanov@mail.by', '1993-04-18', 'Grodno, Ozheshko St 8'),
            ('Lebedev', 'Sergey', 'Nikolaevich', '+375 (29) 888-99-00', 'lebedev@mail.by', '1987-09-30', 'Minsk, Nemiga St 20'),
            ('Solovyova', 'Natalia', 'Andreevna', '+375 (29) 999-00-11', 'solovyova@mail.by', '1991-06-14', 'Brest, Gogolya St 12'),
            ('Morozov', 'Ivan', 'Dmitrievich', '+375 (29) 000-11-22', 'morozov@mail.by', '1989-02-28', 'Vitebsk, Frunze St 7'),
        ]
        clients = {}
        for last, first, middle, phone, email, dob, address in clients_data:
            client, _ = Client.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'middle_name': middle,
                    'phone': phone,
                    'date_of_birth': dob,
                    'address': address,
                }
            )
            clients[last] = client
        self.stdout.write(f'Created {len(clients)} clients')

        # Create tickets
        ticket_types = ['adult', 'adult', 'child', 'senior', 'student', 'adult', 'adult', 'student', 'adult', 'child']
        for i, (last, t_type) in enumerate(zip(list(clients.keys())[:10], ticket_types)):
            tour = list(tours.values())[i % len(tours)]
            visit_date = tour.date.date() if hasattr(tour.date, 'date') else date(2025, 1, 15)
            base_price = tour.price
            discount = 10 if i % 3 == 0 else 0
            
            # Calculate final price before creating
            temp_ticket = Ticket(
                client=clients[last],
                tour=tour,
                visit_date=visit_date,
                ticket_type=t_type,
                base_price=base_price,
                discount=discount,
            )
            final_price = temp_ticket.calculate_price()
            
            ticket, created = Ticket.objects.get_or_create(
                client=clients[last],
                tour=tour,
                visit_date=visit_date,
                defaults={
                    'ticket_type': t_type,
                    'base_price': base_price,
                    'discount': discount,
                    'final_price': final_price,
                }
            )
        self.stdout.write('Created 10 tickets')

        # Create promo codes
        promo_codes_data = [
            ('WELCOME10', 'Welcome discount for new visitors', 10.00, 20.00, True, '2025-01-01 00:00:00', '2025-12-31 23:59:59'),
            ('SUMMER2025', 'Summer special offer', 15.00, 30.00, True, '2025-06-01 00:00:00', '2025-08-31 23:59:59'),
            ('STUDENT20', 'Student discount', 20.00, 25.00, True, '2025-01-01 00:00:00', '2025-12-31 23:59:59'),
            ('FAMILY', 'Family package discount', 25.00, 50.00, True, '2025-01-01 00:00:00', '2025-12-31 23:59:59'),
            ('EARLYBIRD', 'Early booking discount', 10.00, 0.00, True, '2025-01-01 00:00:00', '2025-06-30 23:59:59'),
        ]
        for code, desc, discount, min_purch, active, valid_from, valid_until in promo_codes_data:
            PromoCode.objects.get_or_create(
                code=code,
                defaults={
                    'description': desc,
                    'discount_percent': discount,
                    'min_purchase': min_purch,
                    'is_active': active,
                    'valid_from': valid_from,
                    'valid_until': valid_until,
                }
            )
        self.stdout.write('Created 5 promo codes')

        # Create reviews
        reviews_data = [
            ('Smirnov', 5, 'Excellent museum! Very impressed with the collection.', '2025-01-10'),
            ('Kuznetsova', 4, 'Great experience, especially the Renaissance hall.', '2025-01-12'),
            ('Popov', 5, 'Amazing guides and beautiful exhibits!', '2025-01-15'),
            ('Vasilieva', 4, 'Well organized tours, friendly staff.', '2025-01-18'),
            ('Mikhailov', 5, 'Best museum in the city. Highly recommend!', '2025-01-20'),
        ]
        for last, rating, text, visit_date in reviews_data:
            Review.objects.get_or_create(
                client=clients.get(last),
                defaults={
                    'rating': rating,
                    'text': text,
                    'visit_date': visit_date,
                }
            )
        self.stdout.write('Created 5 reviews')

        # Create vacancies
        vacancies_data = [
            ('Senior Tour Guide', 'Lead guided tours for museum visitors', '5+ years experience, excellent communication skills', '2500-3500 BYN'),
            ('Art Restorer', 'Restore and preserve museum exhibits', 'Degree in Art Conservation, 3+ years experience', '4000-5000 BYN'),
            ('Museum Educator', 'Develop educational programs for schools', 'Teaching degree, passion for art history', '2800-3500 BYN'),
            ('Security Supervisor', 'Oversee museum security operations', 'Security certification, leadership experience', '2500-3000 BYN'),
        ]
        for title, desc, req, salary in vacancies_data:
            Vacancy.objects.get_or_create(
                title=title,
                defaults={
                    'description': desc,
                    'requirements': req,
                    'salary_range': salary,
                    'is_active': True,
                }
            )
        self.stdout.write('Created 4 vacancies')

        # Create company history
        history_data = [
            (1950, 'Museum founded by local art enthusiasts'),
            (1965, 'First permanent exposition opened'),
            (1980, 'Major renovation and expansion completed'),
            (1995, 'International partnership program launched'),
            (2005, 'Digital catalog of all exhibits created'),
            (2015, 'New modern art wing inaugurated'),
            (2020, 'Virtual tours introduced during pandemic'),
            (2024, 'Major Renaissance exhibition hosted'),
        ]
        for year, event in history_data:
            CompanyHistory.objects.get_or_create(
                year=year,
                defaults={'event': event}
            )
        self.stdout.write('Created 8 company history events')

        # Create company info
        if not CompanyInfo.objects.exists():
            CompanyInfo.objects.create(
                name='National Art Museum',
                description='The National Art Museum houses an impressive collection of European and Asian art spanning five centuries. Our mission is to preserve, study, and showcase masterpieces for current and future generations.',
                address='Minsk, Independence Avenue 20, 220030, Belarus',
                email='info@museum.by',
                phone='+375 (17) 123-45-67',
            )
            self.stdout.write('Created company info')

        self.stdout.write(self.style.SUCCESS('\n✅ Database seeding completed successfully!'))
        self.stdout.write(self.style.WARNING('\n⚠️ Remember to:'))
        self.stdout.write('  1. Run migrations: python manage.py makemigrations && python manage.py migrate')
        self.stdout.write('  2. Create superuser if not created: admin / admin123')
        self.stdout.write('  3. Add images via admin panel for better presentation')
