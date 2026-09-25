import shutil
from django.conf import settings
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
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
from io import BytesIO
from PIL import Image
from apps.core.models import Countries, StatusChoices, PropertyType, RoomCount

User = get_user_model()
fake = Faker()

class FMATesting(APITestCase):

    def setUp(self):
        return self.create_db()

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

    @staticmethod
    def create_db():
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
        users = []
        for _ in range(10):
            user = User.objects.create_user(email=fake.unique.email(),
                      username=fake.user_name(),
                      first_name=fake.unique.first_name(),
                      last_name=fake.unique.last_name(),
                      birth_date=date(year=random.randint(1970, 2008), month=9, day=19),
                      password=fake.password(length=random.randrange(8, 129, 8)),
                      is_staff=True)
            users.append(user)
        listings = [Listing(
                      title=fake.word(),
                      user=random.choice(users),
                      description=fake.paragraph(nb_sentences=random.randint(3, 5)),
                      country=random.choice(Countries.values),
                      district=fake.state(),
                      city=fake.city(),
                      street=fake.street_address(),
                      house_number=f"{i}",
                      property_type=random.choice(PropertyType.values),
                      discount=random.uniform(0.01, 1),
                      apartment_number=random.randint(1, 10),
                      max_guests=10,
                      price_per_night=Decimal(random.randint(3000, 25000)),
                      rooms=random.choice(RoomCount.values)
                    ) for i in range(20)]
        Listing.objects.bulk_create(listings)
        all_listings = list(Listing.objects.all())
        photos = [Photo(listing=listing,
                          photo=SimpleUploadedFile('our_photo.png', content=b"0" * 1024 * 1024,
                                                   content_type="image/png"),
                          photo_number=random.randint(1, 50)) for listing in all_listings]
        Photo.objects.bulk_create(photos)
        all_users = list(User.objects.all())
        random.shuffle(all_listings)
        random.shuffle(all_users)
        bookings = [Booking(
                      user=random.choice(all_users),
                      listing=random.choice(all_listings),
                      date_from=timezone.localdate() + timedelta(days=i),
                      date_to=timezone.localdate() + timedelta(days=i + 1),
                      guests_number=random.randint(2, 10),
                      booking_status=StatusChoices.COMPLETED
                    ) for i in range(30)]
        for booking in bookings:
            booking.save()
        all_bookings = list(Booking.objects.all())
        random.shuffle(all_bookings)
        reviews = [Review(booking=all_bookings.pop(),
                          property_rating=random.randint(1, 5),
                          location_rating=random.randint(1, 5),
                          text=fake.lexify(text='?' * 1500)
                        ) for _ in range(30)]
        Review.objects.bulk_create(reviews)

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
        self.client.force_authenticate(User.objects.last())
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 10)

    def test_get_all_reviews(self):
        response = self.client.get(reverse('review-list'), query_params={"limit": 25})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 25)
        self.assertEqual(response.data['count'], 30)

    def test_get_all_bookings(self):
        self.client.force_authenticate(User.objects.first())
        response = self.client.get(reverse('booking-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 30)

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

    def test_txt_file_is_forbidden(self):
        self.client.force_authenticate(User.objects.first())
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
        self.client.force_authenticate(User.objects.last())
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
        current_day = timezone.now().isoweekday()
        photos = Photo.all_objects.annotate(day_of_week=ExtractIsoWeekDay('created_at')).filter(day_of_week=current_day)
        self.assertTrue(photos.exists())
        for photo in photos:
            self.assertEqual(photo.created_at.isoweekday(), current_day)
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
        listing_id = Listing.objects.first().id
        user = User.objects.last()
        self.client.force_authenticate(user)
        data = {
              'listing': listing_id,
              'date_from': (timezone.localdate() + timedelta(days=41)).strftime('%Y-%m-%d'),
              'date_to': (timezone.localdate() + timedelta(days=43)).strftime('%Y-%m-%d'),
              'guests_number': random.randint(2, 10)
            }
        response = self.client.post(reverse('booking-list'), data=data, format='json')
        self.assertEqual(response.status_code, 201)
        response = self.client.post(reverse('booking-list'), data=data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Unfortunately the selected dates are already booked.', response.data['errors'][0]['detail'])

    def test_soft_delete(self):
        alive_users_before = User.objects.count()
        self.assertEqual(alive_users_before, 10)
        user = User.objects.first()
        user.delete()
        self.client.force_authenticate(User.objects.last())
        response = self.client.get(reverse('user-detail', args=[user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['is_deleted'] is True)
        self.assertTrue(response.data['deleted_at'] is not None)

        alive_users_after = User.objects.count()
        self.assertEqual(alive_users_after, 9)

        admin_user = User.objects.filter(is_staff=True).first()
        self.client.force_authenticate(admin_user)
        admin_response = self.client.get(reverse('user-list'))
        self.assertEqual(admin_response.status_code, 200)
        self.assertEqual(admin_response.data['count'], 10)

