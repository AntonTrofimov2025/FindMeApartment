import random
from django.core.management.base import BaseCommand
from decimal import Decimal
from django.contrib.auth import get_user_model
from apps.listings.models import Listing
from apps.core.models import Countries, PropertyType, RoomCount, MaxGuests

User = get_user_model()

germany_data = [
    {
        "title": "Modern Corporate Studio near Main Station",
        "description": "Stylish and fully equipped studio apartment in the heart of Frankfurt. Perfect for business travelers and solo adventurers. Includes high-speed Wi-Fi, a workspace, and coffee machine.",
        "city": "Frankfurt am Main", "district": "Innenstadt", "street": "Kaiserstraße", "house_number": "14", "apartment_number": None,
        "property_type": PropertyType.STUDIO, "rooms": RoomCount.STUDIO, "max_guests": MaxGuests.TWO, "price": "110.00", "discount": "1.00"
    },
    {
        "title": "Cozy Altbau Apartment in Trendy Neighborhood",
        "description": "Charming Berlin-style classic apartment with high ceilings and wooden floors. Located in a quiet backyard of Prenzlauer Berg, surrounded by local cafes, boutiques, and flea markets.",
        "city": "Berlin", "district": "Pankow", "street": "Kastanienallee", "house_number": "84", "apartment_number": "12B",
        "property_type": PropertyType.APARTMENT, "rooms": RoomCount.TWO, "max_guests": MaxGuests.FOUR, "price": "145.00", "discount": "0.90"
    },
    {
        "title": "Premium Luxury Loft with Rooftop Terrace",
        "description": "Stunning open-space industrial loft in Berlin Mitte. Features premium furniture, smart home access, and an amazing rooftop terrace with panoramic city views.",
        "city": "Berlin", "district": "Mitte", "street": "Friedrichstraße", "house_number": "105", "apartment_number": None,
        "property_type": PropertyType.LOFT, "rooms": RoomCount.TWO, "max_guests": MaxGuests.TWO, "price": "280.00", "discount": "0.85"
    },
    {
        "title": "Traditional Bavarian House close to Alps",
        "description": "Beautiful standalone Alpine-style house located in the southern suburbs of Munich. Features a private garden, terrace, fire pit, and fully authentic wooden interior.",
        "city": "München", "district": "Solln", "street": "Alpenstraße", "house_number": "7", "apartment_number": None,
        "property_type": PropertyType.HOUSE, "rooms": RoomCount.FIVE_PLUS, "max_guests": MaxGuests.TEN, "price": "350.00", "discount": "1.00"
    },
    {
        "title": "Bright Family Apartment near English Garden",
        "description": "Spacious 3-room apartment ideal for families. Just a 5-minute walk to the famous Englischer Garten. Fully equipped kitchen, child-friendly environment, and secure parking slot.",
        "city": "München", "district": "Schwabing", "street": "Leopoldstraße", "house_number": "42", "apartment_number": "3",
        "property_type": PropertyType.APARTMENT, "rooms": RoomCount.THREE, "max_guests": MaxGuests.SIX, "price": "195.00", "discount": "0.95"
    },
    {
        "title": "Quiet Private Room for Students and Backpackers",
        "description": "Affordable and cozy room in a shared apartment. Excellent dynamic neighborhood near Hamburg Harbor. Friendly environment, clean bathroom, and fast access to public transport.",
        "city": "Hamburg", "district": "Altona", "street": "Reeperbahn", "house_number": "112", "apartment_number": "15",
        "property_type": PropertyType.ROOM, "rooms": RoomCount.ONE, "max_guests": MaxGuests.ONE, "price": "55.00", "discount": "1.00"
    },
    {
        "title": "Elegant Harbor-View Townhouse",
        "description": "Stunning modern townhouse at the Hafencity district. Multi-level living experience with floor-to-ceiling windows, underfloor heating, and direct views of the harbor ships.",
        "city": "Hamburg", "district": "Hafencity", "street": "Am Sandtorkai", "house_number": "23", "apartment_number": "A1",
        "property_type": PropertyType.TOWNHOUSE, "rooms": RoomCount.FOUR, "max_guests": MaxGuests.FOUR, "price": "240.00", "discount": "0.90"
    },
    {
        "title": "Compact Sunny Apartment near Historic Center",
        "description": "Lovely renovated flat in Cologne. Quiet street but very close to the Cathedral (Kölner Dom). Ideal for couples exploring the city's rich history and night museums.",
        "city": "Köln", "district": "Altstadt-Nord", "street": "Hohe Straße", "house_number": "5", "apartment_number": "22",
        "property_type": PropertyType.APARTMENT, "rooms": RoomCount.ONE, "max_guests": MaxGuests.TWO, "price": "98.00", "discount": "0.95"
    },
    {
        "title": "Spacious Suburban House with Green Backyard",
        "description": "Large cozy detached house in a green, peaceful suburb of Stuttgart. Perfect destination for family road-trips. Spacious living room, backyard BBQ setup, and automated private garage.",
        "city": "Stuttgart", "district": "Degerloch", "street": "Waldstraße", "house_number": "19", "apartment_number": None,
        "property_type": PropertyType.HOUSE, "rooms": RoomCount.FOUR, "max_guests": MaxGuests.EIGHT, "price": "210.00", "discount": "1.00"
    },
    {
        "title": "Minimalist Industrial Loft near River Main",
        "description": "Converted former factory studio space now working as a high-end designer loft. Features concrete architecture ceilings, premium sound systems, and panoramic financial district views.",
        "city": "Frankfurt am Main", "district": "Sachsenhausen", "street": "Mainufer", "house_number": "31", "apartment_number": None,
        "property_type": PropertyType.LOFT, "rooms": RoomCount.ONE, "max_guests": MaxGuests.TWO, "price": "160.00", "discount": "0.80"
    }
]

class Command(BaseCommand):
    """
    Management command to seed the database with 10 realistic German property listings.
    """
    help = 'Seeds the database with initial responsive German real estate data for UI testing reasons.'

    def create_ten_listings(self, listings_data: list[dict]):
        landlords = list(User.all_objects.filter(groups__name='Landlord'))

        if not landlords:
            landlords = list(User.all_objects.all()[:3])

        if not landlords:
            self.stdout.write(self.style.ERROR("❌ Error: There is no any user found in db to bind with listings!"))
            return

        created_count = 0
        for item in listings_data:
            try:
                listing = Listing(
                    title=item["title"],
                    description=item["description"],
                    user=random.choice(landlords),
                    country=Countries.GERMANY,
                    district=item["district"],
                    city=item["city"],
                    street=item["street"],
                    house_number=item["house_number"],
                    apartment_number=item["apartment_number"],
                    property_type=item["property_type"],
                    rooms=item["rooms"],
                    max_guests=item["max_guests"],
                    price_per_night=Decimal(item["price"]),
                    discount=Decimal(item["discount"]),
                    is_active=True
                )
                listing.full_clean()
                listing.save()
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"✅ Successfully created: '{listing.title}' in the city {listing.city}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error during creation '{item['title']}': {e}"))

        self.stdout.write(self.style.SUCCESS(f"\n🚀 Done! In our DB have been added {created_count} deutsch listings :)"))

    def handle(self, *args, **kwargs):
        self.create_ten_listings(germany_data)