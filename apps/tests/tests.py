from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date
from apps.listings.models import Listing, Photo
from apps.bookings.models import Booking
from apps.reviews.models import Review
from decimal import Decimal
import random
from faker import Faker
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()
fake = Faker()

class FMATesting(APITestCase):

    def setUp(self):
        return self.create_db()

    @staticmethod
    def create_db():
        users = []
        for _ in range(10):
            user = User.objects.create_user(email=fake.unique.email(),
                      username="hell",
                      first_name="oy",
                      last_name="boy",
                      birth_date=date(year=2026, month=9, day=19),
                      password="s23tringst",
                      is_staff=True)
            users.append(user)
        listings = [Listing(
                      title="Helloy",
                      user=random.choice(users),
                      description="dasdasdas",
                      country=276,
                      district="goody",
                      city="SPB",
                      street="not yet",
                      house_number=f"{i}",
                      property_type="apartment",
                      discount=random.uniform(0.01, 1),
                      apartment_number=fake.unique.word(),
                      max_guests=10,
                      price_per_night=Decimal("14550.50"),
                      rooms=0
                    ) for i in range(20)]
        Listing.objects.bulk_create(listings)
        all_listings = list(Listing.objects.all())
        photos = [Photo(listing=listing,
                          photo=SimpleUploadedFile('our_photo.png', content=b"0" * 1024 * 1024, content_type="image/png"),
                          photo_number=50) for listing in all_listings]
        Photo.objects.bulk_create(photos)
        all_users = list(User.objects.all())
        random.shuffle(all_listings)
        random.shuffle(all_users)
        bookings = [Booking(
                      user=random.choice(all_users),
                      listing=random.choice(all_listings),
                      date_from=date(year=2026, month=12, day=1 + i),
                      date_to=date(year=2026, month=12, day=2 + i),
                      guests_number=random.randint(2, 10)
                    ) for i in range(30)]
        for booking in bookings:
            booking.save()
        all_bookings = list(Booking.objects.all())
        random.shuffle(all_bookings)
        reviews = [Review(booking=all_bookings.pop(),
                          property_rating=5,
                          location_rating=5,
                          text="heeeyy :DD"
                        ) for _ in range(30)]
        Review.objects.bulk_create(reviews)

    def test_pagination_structure(self):
        pagination_keys = ('count', 'next', 'previous', 'results')
        response = self.client.get(reverse('listing-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)
        for key in pagination_keys:
            self.assertIn(key, response.data)

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
        bad_file = SimpleUploadedFile('image.txt', content=b"fake bytes", content_type="text/plain")
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

