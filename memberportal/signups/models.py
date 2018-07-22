from django.db import models
from django.db.models import Count, Sum
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone


class Signup(models.Model):
    name = models.CharField(max_length=80)
    description = models.TextField(null=True, blank=True)

    audition_notice = models.CharField(max_length=250, null=True, blank=True)
    time_period = models.CharField(max_length=80, null=True, blank=True)

    payment = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    member_payment = models.DecimalField(max_digits=5,
                                         decimal_places=2,
                                         default=0.0)

    allow_queue = models.BooleanField(default=False,
                                      help_text="Not Yet Functional!")
    member_only = models.BooleanField(default=False)
    force_online_payment = models.BooleanField(default=True)

    visible = models.BooleanField(default=False)

    confirm_info = models.TextField(null=True, blank=True)

    contact = models.EmailField(null=True)
    admin = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return u"%s" % (self.name)

    def update_dates(self):
        slots = self.slot_set.extra(
            select={'day': 'date( start )'}).values('day') \
            .annotate(total=Count('start'))
        daterange = [day['day'].strftime("%d %b") for day in slots]
        self.time_period = ", ".join(daterange)
        self.save()

    def total_places(self):
        return self.slot_set.aggregate(Sum('places'))['places__sum']

    def total_confirmed(self):
        return self.slot_set.aggregate(
            Sum('confirmed_places'))['confirmed_places__sum']

    class Meta:
        permissions = (
            ('manage_signups', 'Can manage signups'),
            ('manage_all_signups', 'Can manage all signups'),
        )


class Slot(models.Model):
    signup = models.ForeignKey(
        'Signup', editable=False, on_delete=models.PROTECT)
    location = models.CharField(max_length=100, null=True, blank=True)

    start = models.DateTimeField()
    end = models.DateTimeField()

    places = models.IntegerField(default=1)
    confirmed_places = models.IntegerField(default=0, editable=False)

    def __str__(self):
        return u"Slot #%s for %s" % (self.id, self.signup)

    def save(self, *args, **kwargs):
        self.signup.update_dates()
        self.confirmed_places = self.place_set.filter(status='2').count()
        super(Slot, self).save(*args, **kwargs)

    def free_places(self):
        return max(0, self.places - self.confirmed_places)

    def other_places(self):
        if not self.places:
            return True
        return self.place_set.filter(Q(status='1') | Q(status='0'))

    def places_export(self):
        return self.place_set.filter(Q(status='1') |
                                     Q(status='0') | Q(status='2'))

    def expired(self):
        return self.end < timezone.now()


PLACESTATUS = (
    ('0', 'Pending',),
    ('1', 'Interest'),
    ('2', 'Confirmed'),
    ('3', 'Cancelled'),
    ('4', 'Place Unavailable'),  # Auto rejected by the system (no slots)
    ('5', 'Superseded'),
)


class Place(models.Model):
    slot = models.ForeignKey('Slot', on_delete=models.PROTECT)
    status = models.CharField(max_length=2, default='0', choices=PLACESTATUS)

    guid = models.CharField(max_length=32, unique=True, null=True)

    created = models.DateTimeField(auto_now_add=True, editable=False)
    changed = models.DateTimeField(auto_now=True, editable=False)
    payment = models.CharField(max_length=12, null=True, blank=True)
    # payment = models.OneToOneField(
    #    'payments.SinglePayment', blank=True, null=True,
    #    on_delete=models.SET_NULL)

    member = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return u"Place #%s for %s" % (self.id, self.slot.signup)

    def save(self, *args, **kwargs):
        super(Place, self).save(*args, **kwargs)
        self.slot.save()

    def to_pay(self):
        if self.status in ['3', '4', '5', ]:
            return False
        if self.payment:
            # Note: assumes payment is valid/for correct value
            return False
        if self.member.check_full_member():
            return self.slot.signup.member_payment
        return self.slot.signup.payment

    def can_cancel(self):
        if self.status in ['3', '4', '5']:
            #  TODO: Check expired
            return False
        return True
