from PIL import Image
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


def validate_extension(file):
    if file.name.split('.')[-1].lower() not in ['png', 'jpeg', 'jpg', 'webp', 'heic', 'heif']:
        raise ValidationError('This extension is not allowed! Allowed: png, jpeg, jpg, webp, heic, heif')

    try:
        with Image.open(file) as img:
            img.verify()
    except Exception:
        raise ValidationError(_('The uploaded file is corrupted or not a valid image!'))

    return file


def validate_file_size(file):
    if file.size / 1024 / 1024 > 2:
        raise ValidationError('File size is too big! Maximum allowed size is 2 MB.')
    return file