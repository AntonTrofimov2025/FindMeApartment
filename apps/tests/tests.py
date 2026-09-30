import shutil
from django.conf import settings
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import date, timedelta
from apps.listings.models import Listing, Photo
from apps.bookings.models import Booking
from apps.reviews.models import Review
from decimal import Decimal
import random
from faker import Faker
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.db.models.functions import ExtractIsoWeekDay
from django.db.models import Q
from io import BytesIO
from PIL import Image
from apps.core.models import Countries, StatusChoices, PropertyType, RoomCount

User = get_user_model()
fake = Faker()

class FMATesting(APITestCase):

    @classmethod
    def setUpTestData(cls):
        return cls.create_db()

    def setUp(self):
        self.client.force_authenticate(None)
        self.client.logout()

    @classmethod
    def tearDownClass(cls):
        """
        Automated test environment cleanup pipeline.

        Executes immediately after the execution of the final test case sequence.
        Recursively targets and wipes out the isolated 'test_media' storage volume
        to maintain local and container filesystem hygiene.
        """
        if hasattr(settings, 'MEDIA_ROOT') and settings.MEDIA_ROOT.exists():
            try:
                shutil.rmtree(settings.MEDIA_ROOT)
                print(f"\n✨ [CLEANUP SUCCESS] Isolated directory '{settings.MEDIA_ROOT}' was cleanly wiped out!")
            except Exception as e:
                print(f"\n⚠️ [CLEANUP WARNING] Failed to remove test media directory: {e}")

    @classmethod
    def create_db(cls):
        """
        Database orchestration workflow designed to seed the isolated test database environment.

        Leverages the Faker library alongside structural procedural generation loops to programmatically
        instantiate a full-scale platform ecosystem schema:
          - Users: Generates 10 high-privilege staff profiles with structured cryptographic password salts.
          - Listings: Populates 20 diverse real estate properties enforcing systemic model bounds.
          - Photos: Attaches mock multi-part binary image buffers validating custom format extensions.
          - Bookings: Instantiates 30 chronological rental contracts executed iteratively via native model
            `.save()` invocations to guarantee transaction logging, pricing evaluations, and snapshot logs.
          - Reviews: Seeds 30 relational post-trip evaluation logs tied strictly to completed bookings.
        """
        permissions_tenant = settings.ROLE_PERMISSION['Tenant']
        permissions_landlord = settings.ROLE_PERMISSION['Landlord']
        tenant_group, _ = Group.objects.get_or_create(name='Tenant')
        landlord_group, _ = Group.objects.get_or_create(name='Landlord')
        cls.tenant_group = tenant_group
        cls.landlord_group = landlord_group

        def get_your_permissions(permission_list: list[str]):
            matched_permissions = Q()
            for permission in permission_list:
                app_label, codename = permission.split('.', 1)
                matched_permissions |= Q(content_type__app_label=app_label.lower(), codename=codename.lower())
            return Permission.objects.filter(matched_permissions) if matched_permissions else Permission.objects.none()

        tenant_group.permissions.set(get_your_permissions(permissions_tenant))
        landlord_group.permissions.set(get_your_permissions(permissions_landlord))

        admin_user = User.objects.create_superuser(email=fake.unique.email(),
                                 username=fake.user_name(),
                                 first_name=fake.unique.first_name(),
                                 last_name=fake.unique.last_name(),
                                 phone=fake.unique.numerify(text="+###########"),
                                 birth_date=date(year=random.randint(1970, 2008), month=9, day=19),
                                 password=fake.password(length=random.randrange(8, 129, 8)),
                                 is_staff=True,
                                 is_superuser=True)
        cls.admin_user = admin_user

        tenants = []
        for _ in range(5):
            tenant = User.objects.create_user(email=fake.unique.email(),
                      username=fake.user_name(),
                      first_name=fake.unique.first_name(),
                      last_name=fake.unique.last_name(),
                      phone=fake.unique.numerify(text="+###########"),
                      birth_date=date(year=random.randint(1970, 2008), month=9, day=19),
                      password=fake.password(length=random.randrange(8, 129, 8)),
                      is_staff=False)
            tenants.append(tenant)
        landlords = []
        for _ in range(5):
            landlord = User.objects.create_user(email=fake.unique.email(),
                      username=fake.user_name(),
                      first_name=fake.unique.first_name(),
                      last_name=fake.unique.last_name(),
                      phone=fake.unique.numerify(text="+###########"),
                      birth_date=date(year=random.randint(1970, 2008), month=9, day=19),
                      password=fake.password(length=random.randrange(8, 129, 8)),
                      is_staff=False)
            landlord.groups.set([landlord_group])
            landlords.append(landlord)
        cls.tenants = tenants
        cls.landlords = landlords
        listings = [Listing(
                      title=fake.sentence(nb_words=3),
                      user=random.choice(landlords),
                      description=fake.paragraph(nb_sentences=random.randint(3, 5)),
                      country=random.choice(Countries.values),
                      district=fake.state(),
                      city=fake.city(),
                      street=fake.street_address(),
                      house_number=f"{i}",
                      property_type=(prop_type := random.choice(PropertyType.values)),
                      discount=Decimal(f"{random.uniform(0.01, 1):.2f}"),
                      apartment_number=random.randint(1, 10) if prop_type not
                                                                in [PropertyType.STUDIO, PropertyType.HOUSE] else None,
                      max_guests=random.randint(1, 10),
                      price_per_night=Decimal(random.randint(3000, 25000)),
                      rooms=random.choice(RoomCount.values)
                    ) for i in range(20)]
        for listing in listings:
            listing.save()
        all_listings = list(Listing.objects.all())
        buffer = BytesIO()
        image = Image.new(mode='RGB', size=(100, 100), color='white')
        image.save(buffer, format='PNG', quality=100, subsampling='4:4:4')
        photos = [Photo(listing=listing,
                        photo=SimpleUploadedFile('our_photo.png', content=buffer.getvalue(),
                                                   content_type="image/png"),
                        photo_number=1) for listing in all_listings]
        for photo in photos:
            photo.save()
        all_users = list(User.objects.all())
        random.shuffle(all_listings)
        random.shuffle(all_users)
        bookings = [Booking(
                      listing=(selected_listing := random.choice(all_listings)),
                      user=random.choice([user for user in all_users if user.id != selected_listing.user_id]),
                      date_from=timezone.localdate() + timedelta(days=i + 2),
                      date_to=timezone.localdate() + timedelta(days=i + 3),
                      guests_number=random.randint(1, selected_listing.max_guests),
                      booking_status=StatusChoices.CONFIRMED
                    ) for i in range(60)]
        bookings_completed, bookings = bookings[:30], bookings[30:]
        for b in bookings_completed:
            b.booking_status = StatusChoices.COMPLETED
        bookings += bookings_completed
        for booking in bookings:
            booking.save()
        all_bookings = list(Booking.objects.filter(booking_status=StatusChoices.COMPLETED))
        random.shuffle(all_bookings)
        reviews = [Review(booking=all_bookings.pop(),
                          property_rating=random.randint(1, 5),
                          location_rating=random.randint(1, 5),
                          text=fake.lexify(text='?' * 1500)
                        ) for _ in range(30)]
        for review in reviews:
            review.save()

    def test_pagination_structure(self):
        pagination_keys = ('count', 'next', 'previous', 'results')
        response = self.client.get(reverse('listing-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)
        for key in pagination_keys:
            self.assertIn(key, response.data)

    def test_not_authenticated(self, viewname='booking-list', viewname_detail: str | None='booking-detail',
                               args=None):
        if viewname_detail == 'booking-detail' and args is None:
            args = Booking.objects.first().id
        args = [args] if args else []
        response = self.client.get(reverse(viewname))
        self.assertEqual(response.status_code, 401)
        self.assertIn('Authentication credentials were not provided.', response.data['errors'][0]['detail'])
        if viewname_detail:
            response = self.client.get(reverse(viewname_detail, args=args))
            self.assertEqual(response.status_code, 401)
            self.assertIn('Authentication credentials were not provided.', response.data['errors'][0]['detail'])

    def test_not_authenticated_part_2(self):
        self.test_not_authenticated('user-list', 'user-detail', User.objects.first().id)

    def test_not_authenticated_part_3(self):
        self.test_not_authenticated('user-profile-view', None)
        self.test_not_authenticated('user-become-landlord-view', None)

    def test_not_authenticated_part_4(self):
        self.test_not_authenticated('logout-view', None)

    def test_not_authenticated_booking_endpoints(self):
        booking_id = Booking.objects.last().id
        viewnames = ('booking-approve-view', 'booking-cancel-view', 'booking-reject-view', 'booking-check-in-view')
        for viewname in viewnames:
            response = self.client.get(reverse(viewname, args=[booking_id]))
            self.assertEqual(response.status_code, 401)

    def test_get_all_users(self):
        self.client.force_authenticate(self.admin_user)
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 11)

    def test_user_register(self):
        buffer = BytesIO()
        image = Image.new(mode='RGB', size=(100, 100), color='white')
        image.save(buffer, format='PNG', quality=100, subsampling='4:4:4')
        buffer.seek(0)
        user_data = {
              "email": "neu_user@beispiel.com",
              "username": "Heyhey :)",
              "first_name": "Tony",
              "last_name": "Kwark",
              "birth_date": "1976-04-12",
              "avatar": SimpleUploadedFile(name='avatar.png', content=buffer.getvalue(), content_type='image/png'),
              "phone": "+49312371283",
              "password": "fish_sword_223",
              "re_password": "fish_sword_223"
            }
        response = self.client.post(reverse("user-create-view"), data=user_data, format='multipart')
        self.assertEqual(response.status_code, 201)

    def test_get_all_reviews(self):
        response = self.client.get(reverse('review-list'), query_params={"limit": 25})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 25)
        self.assertEqual(response.data['count'], 30)

    def test_get_all_bookings(self):
        self.client.force_authenticate(self.admin_user)
        response = self.client.get(reverse('booking-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 60)

    def test_get_all_listings(self):
        response = self.client.get(reverse('listing-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 20)

    def test_get_all_photos(self):
        response = self.client.get(reverse('photo-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 20)
        for photo in response.data['results']:
            self.assertEqual(photo['photo'],f'http://testserver/media/listings/{str(photo['listing'])}/our_photo.png')

    def test_post_listing_tenant(self):
        user = random.choice(self.tenants)
        self.client.force_authenticate(user)
        data = {
                "title": fake.sentence(nb_words=3),
                "user": user.id,
                "description": fake.paragraph(nb_sentences=random.randint(3, 5)),
                "country": random.choice(Countries.values),
                "district": fake.state(),
                "city": fake.city(),
                "street": fake.street_address(),
                "house_number": f"{random.randint(1, 100)}",
                "property_type": PropertyType.APARTMENT,
                "discount": Decimal(f"{random.uniform(0.01, 1):.2f}"),
                "apartment_number": random.randint(1, 10),
                "max_guests": random.randint(1, 10),
                "price_per_night": float(Decimal(random.randint(3000, 25000))),
                "rooms": random.choice(RoomCount.values)
              }
        response = self.client.post(reverse('listing-list'), data=data, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertIn('Only Landlords can access this resource!', response.data['errors'][0]['detail'])

    def test_post_listing_landlord(self):
        new_landlord = get_user_model().objects.create_user(
            username="brand_new_landlord_guy",
            email="new_landlord@example.com",
            password="secure_password_123"
        )
        new_landlord.groups.add(self.landlord_group)
        self.client.force_authenticate(new_landlord)
        data = {
                "title": fake.sentence(nb_words=3),
                "user": new_landlord.id,
                "description": fake.paragraph(nb_sentences=random.randint(3, 5)),
                "country": random.choice(Countries.values),
                "district": fake.state(),
                "city": fake.city(),
                "street": fake.street_address(),
                "house_number": f"{random.randint(1, 100)}",
                "property_type": PropertyType.APARTMENT,
                "discount": Decimal(f"{random.uniform(0.01, 1):.2f}"),
                "apartment_number": random.randint(1, 10),
                "max_guests": random.randint(1, 10),
                "price_per_night": float(Decimal(random.randint(3000, 25000))),
                "rooms": random.choice(RoomCount.values)
              }
        response = self.client.post(reverse('listing-list'), data=data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data['id'])
        self.assertEqual(response.data['user'], new_landlord.id)

    def test_tenant_post_booking(self):
        user = random.choice(self.tenants)
        self.client.force_authenticate(user)
        listing = Listing.objects.first()
        data = {
              'listing': listing.id,
              'date_from': (timezone.localdate() + timedelta(days=71)).strftime('%Y-%m-%d'),
              'date_to': (timezone.localdate() + timedelta(days=73)).strftime('%Y-%m-%d'),
              'guests_number': random.randint(1, listing.max_guests)
            }
        response = self.client.post(reverse('booking-list'), data=data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_landlord_post_booking(self):
        landlord = random.choice(self.landlords)
        refresh = RefreshToken.for_user(landlord)
        access = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

        listing = Listing.objects.filter(~Q(user=landlord.id)).first()
        data = {
            'listing': listing.id,
            'date_from': (timezone.localdate() + timedelta(days=41)).strftime('%Y-%m-%d'),
            'date_to': (timezone.localdate() + timedelta(days=43)).strftime('%Y-%m-%d'),
            'guests_number': random.randint(1, listing.max_guests)
        }
        response = self.client.post(reverse('booking-list'), data=data, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertIn('You do not have permission to perform this action.',
                      response.data['errors'][0]['detail'])

    def test_tenant_post_review(self):
        self.client.force_authenticate(random.choice(self.tenants))
        listing = Listing.objects.last()
        booking_data = {
            'listing': listing.id,
            'date_from': (timezone.localdate() + timedelta(days=71)).strftime('%Y-%m-%d'),
            'date_to': (timezone.localdate() + timedelta(days=73)).strftime('%Y-%m-%d'),
            'guests_number': random.randint(1, listing.max_guests)
        }
        response = self.client.post(reverse('booking-list'), data=booking_data, format='json')
        self.assertEqual(response.status_code, 201)
        Booking.objects.filter(pk=response.data['id']).update(booking_status=StatusChoices.COMPLETED)

        data = {"booking": response.data['id'],
                "property_rating": random.randint(1, 5),
                "location_rating": random.randint(1, 5),
                "text": fake.lexify(text='?' * 1500)
                }
        response = self.client.post(reverse('review-list'), data=data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_txt_file_is_forbidden(self):
        self.client.force_authenticate(random.choice(self.landlords))
        bad_file = SimpleUploadedFile('diary.txt', content=b"fake bytes", content_type="text/plain")
        listing_id = Listing.objects.last().id
        data = {
            'listing': listing_id,
            'photo': bad_file,
            'photo_number': 35
        }
        response = self.client.post(reverse('photo-list'), data=data, format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Upload a valid image.'
                      ' The file you uploaded was either not an image or a corrupted image.',
                      response.data['errors'][0]['detail'])

    def test_file_size_is_too_big(self):
        buffer = BytesIO()
        image = Image.new(mode='RGB', size=(1, 1), color='white')
        image.save(buffer, format='JPEG', quality=100, subsampling='4:4:4')
        buffer.write(b"0" * int(2.5 * 1024 * 1024))
        buffer.seek(0)
        self.client.force_authenticate(random.choice(self.landlords))
        bad_file = SimpleUploadedFile('too_big_file.jpeg', content=buffer.read(),
                                      content_type='image/jpeg')
        listing_id = Listing.objects.first().id
        data = {
            'listing': listing_id,
            'photo': bad_file,
            'photo_number': 35
        }
        response = self.client.post(reverse('photo-list'), data=data, format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertIn('File size is too big! Maximum allowed size is 2 MB.', response.data['errors'][0]['detail'])

    def test_photos_per_week_day(self):
        current_day = timezone.localdate(timezone.now()).isoweekday()
        photos = (Photo.all_objects.annotate(day_of_week=ExtractIsoWeekDay('created_at',
                                                                          tzinfo=timezone.get_current_timezone())).
                  filter(day_of_week=current_day))
        self.assertTrue(photos.exists())
        for photo in photos:
            self.assertEqual(timezone.localdate(photo.created_at).isoweekday(), current_day)
            self.assertEqual(photo.day_of_week, current_day)

    def test_age_greater_120(self):
        user_data = {'email': fake.unique.email(),
                    'username': fake.user_name(),
                    'first_name': fake.unique.first_name(),
                    'last_name': fake.unique.last_name(),
                    'birth_date': date(year=1900, month=1, day=1),
                    'password': fake.password(length=random.randrange(8, 129, 8)),
                    'is_staff': True}
        response = self.client.post(reverse('user-create-view'), data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('You are so old my friend! :D Try again :)', response.data['errors'][0]['detail'])

    def test_overlapping_dates(self):
        user = random.choice(self.tenants)
        listing = Listing.objects.exclude(user_id=user.id).first()
        listing_id = listing.id
        self.client.force_authenticate(user)
        data = {
              'listing': listing_id,
              'date_from': (timezone.localdate() + timedelta(days=71)).strftime('%Y-%m-%d'),
              'date_to': (timezone.localdate() + timedelta(days=73)).strftime('%Y-%m-%d'),
              'guests_number': random.randint(1, listing.max_guests)
            }
        response = self.client.post(reverse('booking-list'), data=data, format='json')
        self.assertEqual(response.status_code, 201)
        response = self.client.post(reverse('booking-list'), data=data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Unfortunately the selected dates are already booked.', response.data['errors'][0]['detail'])

    def test_soft_delete(self):
        alive_users_before = User.objects.count()
        self.assertEqual(alive_users_before, 11)
        user = random.choice(self.tenants)
        Booking.objects.filter(listing__user=user).update(booking_status=StatusChoices.CANCELLED)
        Booking.objects.filter(user=user).update(booking_status=StatusChoices.CANCELLED)
        user.delete()
        self.client.force_authenticate(self.admin_user)
        response = self.client.get(reverse('user-detail', args=[user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['is_deleted'])
        self.assertIsNotNone(response.data['deleted_at'])

        alive_users_after = User.objects.count()
        self.assertEqual(alive_users_after, 10)

        self.client.force_authenticate(self.admin_user)
        admin_response = self.client.get(reverse('user-list'))
        self.assertEqual(admin_response.status_code, 200)
        self.assertEqual(admin_response.data['count'], 11)

    def test_user_registration(self):
        data = {"email": "neu_user@beispiel.com",
              "username": "Heyhey :)",
              "first_name": "Tony",
              "last_name": "Kwark",
              "birth_date": "1976-04-12",
              "password": "fish_sword_223",
              "re_password": "fish_sword_223"}
        response = self.client.post(reverse('user-create-view'), data=data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['email'], 'neu_user@beispiel.com')
        self.assertEqual(response.data['username'], 'Heyhey :)')
        self.assertIsNone(response.data.get('password'))
        self.assertIsNone (response.data.get('re_password'))

    def test_user_self_delete(self):
        data = {"email": "neu_user_to_be_soft_deleted@beispiel.com",
                "birth_date": "1976-04-12",
                "password": "fish_sword_223",
                "re_password": "fish_sword_223"}
        response = self.client.post(reverse('user-create-view'), data=data, format='json')
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email="neu_user_to_be_soft_deleted@beispiel.com", birth_date="1976-04-12")
        self.client.force_authenticate(user)
        response = self.client.delete(reverse('user-profile-view'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Your account has been successfully deleted."
                      " We'd like to kindly thank you for being with us! :)", response.data['msg'])

        self.client.force_authenticate(None)
        self.client.logout()
        self.client.force_authenticate(self.admin_user)
        response = self.client.get(reverse('user-detail', args=[user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], 'neu_user_to_be_soft_deleted@beispiel.com')
        self.assertIsNotNone(response.data['deleted_at'])
        self.assertTrue(response.data['is_deleted'])
        self.assertIsNone(response.data.get('password'))
        self.assertIsNone(response.data.get('re_password'))

    def test_review_revival(self):
        self.client.force_authenticate(random.choice(self.tenants))
        listing = Listing.objects.last()
        booking_data = {
            'listing': listing.id,
            'date_from': (timezone.localdate() + timedelta(days=71)).strftime('%Y-%m-%d'),
            'date_to': (timezone.localdate() + timedelta(days=73)).strftime('%Y-%m-%d'),
            'guests_number': random.randint(1, listing.max_guests)
        }
        response = self.client.post(reverse('booking-list'), data=booking_data, format='json')
        self.assertEqual(response.status_code, 201)
        Booking.objects.filter(pk=response.data['id']).update(booking_status=StatusChoices.COMPLETED)

        data = {"booking": response.data['id'],
                "property_rating": random.randint(1, 5),
                "location_rating": random.randint(1, 5),
                "text": fake.lexify(text='?' * 1500)
                }
        response_success = self.client.post(reverse('review-list'), data=data, format='json')
        self.assertEqual(response_success.status_code, 201)
        response = self.client.post(reverse('review-list'), data=data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Review with this Booking already exists.', response.data['errors'][0]['detail'])
        Review.objects.filter(pk=response_success.data['id']).delete()
        data['property_rating'] = 3
        data['text'] = 'Gracias! :D'
        response = self.client.post(reverse('review-list'), data=data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['property_rating'], 3)
        self.assertEqual(response.data['text'], 'Gracias! :D')

    def test_not_active_listing_n_booking_approval_n_check_in_only_between_stay_dates(self):
        user = random.choice(self.landlords)
        self.client.force_authenticate(user)
        data = {
            "title": fake.sentence(nb_words=3),
            "user": user.id,
            "description": fake.paragraph(nb_sentences=random.randint(3, 5)),
            "country": random.choice(Countries.values),
            "district": fake.state(),
            "city": fake.city(),
            "street": fake.street_address(),
            "house_number": f"{random.randint(1, 100)}",
            "property_type": PropertyType.APARTMENT,
            "discount": Decimal(f"{random.uniform(0.01, 1):.2f}"),
            "apartment_number": random.randint(1, 10),
            "max_guests": random.randint(1, 10),
            "price_per_night": float(Decimal(random.randint(3000, 25000))),
            "rooms": random.choice(RoomCount.values)
        }
        response_listing = self.client.post(reverse('listing-list'), data=data, format='json')
        self.assertEqual(response_listing.status_code, 201)

        self.client.force_authenticate(None)
        self.client.logout()
        self.client.force_authenticate(random.choice(self.tenants))

        book_data = {
            'listing': response_listing.data['id'],
            'date_from': (timezone.localdate() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'date_to': (timezone.localdate() + timedelta(days=3)).strftime('%Y-%m-%d'),
            'guests_number': 1
        }
        response = self.client.post(reverse('booking-list'), data=book_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['booking_status'], StatusChoices.PENDING)

        book_to_check_in = {
            'listing': response_listing.data['id'],
            'date_from': (timezone.localdate()).strftime('%Y-%m-%d'),
            'date_to': (timezone.localdate() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'guests_number': 1
        }
        response_for_check_in = self.client.post(reverse('booking-list'), data=book_to_check_in, format='json')
        self.assertEqual(response_for_check_in.status_code, 201)

        self.client.force_authenticate(None)
        self.client.logout()
        self.client.force_authenticate(user)
        approve_booking = self.client.post(reverse('booking-approve-view', args=[response_for_check_in.data['id']]), format='json')
        self.assertEqual(approve_booking.status_code, 200)
        patch_listing = self.client.patch(reverse('listing-detail', args=[response_listing.data['id']]), data={'is_active': False},
                         format='json')
        self.assertEqual(patch_listing.status_code, 200)

        response_approval = self.client.post(reverse('booking-approve-view', args=[response.data['id']]), format='json')
        self.assertEqual(response_approval.status_code, 200)
        response = self.client.post(reverse('booking-check-in-view', args=[response.data['id']]),
                                    format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('You cannot check in your guest before the start date', response.data['errors'][0]['detail'])
        response_checked_in = self.client.post(reverse('booking-check-in-view', args=[response_for_check_in.data['id']]),
                                    format='json')
        self.assertEqual(response_checked_in .status_code, 200)

