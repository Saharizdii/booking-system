
from datetime import datetime, timedelta
from django_jalali.db import models as jmodels
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models


class Service(models.Model):
    name = models.CharField("نام خدمت", max_length=100)
    duration_minutes = models.PositiveIntegerField(
        "مدت تقریبی (دقیقه)",
        help_text="قابل تغییر در هر نوبت",
    )
    max_parallel = models.PositiveIntegerField(
        "حداکثر هم‌زمانی",
        default=1,
        help_text="آرایشگر حداکثر چند نفر را هم‌زمان می‌تواند انجام دهد",
    )
    price = models.PositiveIntegerField("قیمت (تومان)")
    deposit_amount=models.PositiveIntegerField("مبلغ بیعانه",default=400000)

    def __str__ (self):
        return self.name


class Stylist(models.Model):
    name = models.CharField("نام آرایشگر", max_length=100)
    services = models.ManyToManyField(Service, related_name="stylists")

    def __str__(self):
        return self.name


class WorkingHours(models.Model):
    WEEKDAYS = [
        (5, "شنبه"),
        (6, "یکشنبه"),
        (0, "دوشنبه"),
        (1, "سه‌شنبه"),
        (2, "چهارشنبه"),
        (3, "پنجشنبه"),
        (4, "جمعه"),
    ]

    stylist = models.ForeignKey(Stylist, on_delete=models.CASCADE)
    weekday = models.IntegerField("روز هفته", choices=WEEKDAYS)
    start_time = models.TimeField("ساعت شروع")
    end_time = models.TimeField("ساعت پایان")

    def __str__(self):
        return f"{self.stylist} - {self.get_weekday_display()} {self.start_time}-{self.end_time}"


class Appointment(models.Model):
    objects=jmodels.jManager()
    STATUS_CHOICES = [
        ("pending", "در انتظار"),
        ("confirmed", "تأیید شده"),
        ("cancelled", "لغو شده"),
    ]

    first_name = models.CharField("نام", max_length=50)
    last_name = models.CharField("نام خانوادگی", max_length=50)
    phone = models.CharField(
        "شماره تماس",
        max_length=11,
        validators=[
            RegexValidator(
                regex=r"^09\d{9}$",
                message="شماره موبایل باید با ۰۹ شروع شود و ۱۱ رقم باشد.",
            )
        ],
    )
    stylist = models.ForeignKey(Stylist, on_delete=models.PROTECT)
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    date = jmodels.jDateField("تاریخ]")
    start_time = models.TimeField("ساعت شروع")
    end_time = models.TimeField(
        "ساعت پایان",
        blank=True,
        null=True,
        help_text="اگر خالی بماند از مدت پیش‌فرض خدمت محاسبه می‌شود",
    )
    status = models.CharField(
        "وضعیت", max_length=10, choices=STATUS_CHOICES, default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.stylist} - {self.date} {self.start_time}"

    def clean(self):
        if not (self.date and self.start_time and self.service_id and self.stylist_id):
            return

        gregorian_date=(
            self.date.togregorian() 
            if hasattr(self.date, "togregorian") 
            else 
            self.date
        )
        if not self.end_time:
            start = datetime.combine(gregorian_date, self.start_time)
            self.end_time = (
                start + timedelta(minutes=self.service.duration_minutes)
            ).time()

        if self.end_time <= self.start_time:
            raise ValidationError("ساعت پایان باید بعد از ساعت شروع باشد.")

        if self.status == "cancelled":
            return
        day_hours = WorkingHours.objects.filter(
            stylist=self.stylist,
            weekday=gregorian_date.weekday(),
        )
        if not day_hours.exists():
            raise ValidationError("این آرایشگر در این روز هفته کار نمی‌کند.")

        within_shift = day_hours.filter(
            start_time__lte=self.start_time,
            end_time__gte=self.end_time,
        ).exists()
        if not within_shift:
            raise ValidationError("این نوبت خارج از ساعت کاری آرایشگر است.")

        overlapping = (
            Appointment.objects.filter(
                stylist=self.stylist,
                date=self.date,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
            )
            .exclude(status="cancelled")
            .exclude(pk=self.pk)
        )

        for other in overlapping:
            if other.service.max_parallel == 1 or self.service.max_parallel == 1:
                raise ValidationError("این آرایشگر در این بازه نوبت دیگری دارد.")

        if overlapping.count() >= self.service.max_parallel:
            raise ValidationError("ظرفیت این خدمت در این بازه پر است.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


           
            
           
