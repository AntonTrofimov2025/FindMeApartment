from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _


class UniqueID(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          help_text='Unique UUID Primary Key', verbose_name='UUID pk')

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, help_text='Date of creation', verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Date of update', verbose_name='Updated at')
    deleted_at = models.DateTimeField(null=True, blank=True, help_text='Date of deletion', verbose_name='Deleted at')

    class Meta:
        abstract = True

class Countries(models.IntegerChoices):
    # Asia and Middle East
    AZERBAIJAN = 31, _('Azerbaijan')
    ARMENIA = 51, _('Armenia')
    CHINA = 156, _('China')
    GEORGIA = 268, _('Georgia')
    INDIA = 356, _('India')
    INDONESIA = 360, _('Indonesia')
    ISRAEL = 376, _('Israel')
    JAPAN = 392, _('Japan')
    KAZAKHSTAN = 398, _('Kazakhstan')
    KYRGYZSTAN = 417, _('Kyrgyzstan')
    MALAYSIA = 458, _('Malaysia')
    S_KOREA = 410, _('South Korea')
    TAIWAN = 158, _('Taiwan')
    TAJIKISTAN = 762, _('Tajikistan')
    THAILAND = 764, _('Thailand')
    TURKEY = 792, _('Turkey')
    TURKMENISTAN = 795, _('Turkmenistan')
    UAE = 784, _('United Arab Emirates')
    UZBEKISTAN = 860, _('Uzbekistan')
    VIETNAM = 704, _('Vietnam')

    # Europe
    AUSTRIA = 40, _('Austria')
    BELARUS = 112, _('Belarus')
    BELGIUM = 56, _('Belgium')
    BULGARIA = 100, _('Bulgaria')
    CYPRUS = 196, _('Cyprus')
    CZECHIA = 203, _('Czechia')
    DENMARK = 208, _('Denmark')
    FINLAND = 246, _('Finland')
    FRANCE = 250, _('France')
    GERMANY = 276, _('Germany')
    GREECE = 300, _('Greece')
    HUNGARY = 348, _('Hungary')
    IRELAND = 372, _('Ireland')
    ITALY = 380, _('Italy')
    MOLDOVA = 498, _('Moldova')
    NETHERLANDS = 528, _('Netherlands')
    NORWAY = 578, _('Norway')
    POLAND = 616, _('Poland')
    PORTUGAL = 620, _('Portugal')
    ROMANIA = 642, _('Romania')
    RUSSIA = 643, _('Russia')
    SERBIA = 688, _('Serbia')
    SPAIN = 724, _('Spain')
    SWEDEN = 752, _('Sweden')
    SWITZERLAND = 756, _('Switzerland')
    UKRAINE = 804, _('Ukraine')
    UK = 826, _('United Kingdom')

    # North and South America
    ARGENTINA = 32, _('Argentina')
    BRAZIL = 76, _('Brazil')
    CANADA = 124, _('Canada')
    MEXICO = 484, _('Mexico')
    USA = 840, _('United States')

    # Africa and Oceania
    AUSTRALIA = 36, _('Australia')
    EGYPT = 818, _('Egypt')
    NEW_ZEALAND = 554, _('New Zealand')
    SOUTH_AFRICA = 710, _('South Africa')

class PropertyType(models.TextChoices):
    APARTMENT = 'apartment', _('Apartment')
    STUDIO = 'studio', _('Studio')
    HOUSE = 'house', _('House')
    TOWNHOUSE = 'townhouse', _('Townhouse')
    ROOM = 'room', _('Room')
    LOFT = 'loft', _('Loft')

class RoomCount(models.IntegerChoices):
    STUDIO = 0, _('0 Rooms (Studio / Loft)')
    ONE = 1, _('1 Room')
    TWO = 2, _('2 Rooms')
    THREE = 3, _('3 Rooms')
    FOUR = 4, _('4 Rooms')
    FIVE_PLUS = 5, _('5+ Rooms')

class MaxGuests(models.IntegerChoices):
    ONE = 1, '1'
    TWO = 2, '2'
    THREE = 3, '3'
    FOUR = 4, '4'
    FIVE = 5, '5'
    SIX = 6, '6'
    SEVEN = 7, '7'
    EIGHT = 8, '8'
    NINE = 9, '9'
    TEN = 10, '10'

class StatusChoices(models.TextChoices):
    PENDING = 'pending', _('Pending')
    CONFIRMED = 'confirmed', _('Confirmed')
    CHECKED_IN = 'checked_in', _('Checked In')
    COMPLETED = 'completed', _('Completed')
    CANCELLED = 'cancelled', _('Cancelled')
    REJECTED = 'rejected', _('Rejected')