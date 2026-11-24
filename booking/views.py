from django.shortcuts import render

from .models import Service, Stylist

# کلمه‌ی کلیدی در اسم خدمت ← آیکون. ترتیب مهمه: اولین تطابق برنده است.
ICON_RULES = [
    ("رنگ", "bi-palette"),
    ("هایلایت", "bi-palette"),
    ("ناخن", "bi-gem"),
    ("کاشت", "bi-gem"),
    ("میکاپ", "bi-brush"),
    ("آرایش", "bi-brush"),
    ("ابرو", "bi-eye"),
    ("مژه", "bi-eye"),
    ("پوست", "bi-flower1"),
    ("فیشیال", "bi-flower1"),
    ("اپیلاسیون", "bi-flower2"),
    ("کوتاه", "bi-scissors"),
    ("اصلاح", "bi-scissors"),
    ("مو", "bi-scissors"),
]
DEFAULT_ICON = "bi-stars"


def icon_for(name):
    for keyword, icon in ICON_RULES:
        if keyword in name:
            return icon
    return DEFAULT_ICON


def home(request):
    services = list(Service.objects.all())
    for service in services:
        service.icon = icon_for(service.name)

    context = {
        "services": services,
        "stylists": Stylist.objects.prefetch_related("services"),
    }
    return render(request, "booking/home.html", context)
