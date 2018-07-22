from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.db.models import Q, F
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.decorators import permission_required
from django.utils import timezone
from datetime import datetime

import uuid
from collections import OrderedDict

from django.conf import settings
from signups.models import Signup, Slot, Place
from signups.forms import *


def signup_list(request, template_name='signups/signup_list.html'):
    return render(request, template_name, {
        'signups': Signup.objects.filter(
            slot__start__gt=timezone.now()).distinct(),
    }, )


def slot_list(request, id, template_name='signups/slot_list.html'):
    signup = get_object_or_404(Signup, pk=id)

    slots = signup.slot_set.all().order_by('start')

    ordered = OrderedDict()
    for slot in slots:
        day = datetime.date(slot.start)
        if day in ordered:
            ordered[day].append(slot)
        else:
            ordered[day] = [slot, ]

    return render(request, template_name, {
        'signup': signup,
        'ordered': ordered,
    }, )


def slot_signup(request, id, template_name='signups/slot_signup.html'):
    slot = get_object_or_404(Slot, pk=id)
    if slot.free_places() < 1 and slot.places:
        messages.add_message(request, messages.ERROR,
                             "Sorry, there are no longer any free places "
                             "left for that slot.")
        return redirect('signups.slot-list', id=slot.signup.id)

    more = False
    if request.method == 'POST':
        form = SignupForm(data=request.POST)
        if form.is_valid():
            more = True
            member = Search(filters={
                'email': form.cleaned_data["email"],
            }).qs.first()
            if member:
                if Place.objects.filter(member=member,
                                        slot__signup=slot.signup).filter(
                                            Q(status='0') | Q(status='2')):
                    messages.add_message(request, messages.WARNING,
                                         "Sorry, you have already signed up "
                                         "to a place for this event. Please "
                                         "check your email for details.")
                    return redirect('signups.slot-list', id=slot.signup.id)
                if not member.membercontact_set.filter(category=1):
                    form = SignupForm_NoPhone(data=request.POST)
                    if form.is_valid():
                        member.add_contact_detail(1,
                                                  form.cleaned_data["phone"])
                        member.save()
                        more = False
                else:
                    more = False
            else:
                if slot.signup.member_only:
                    messages.add_message(request, messages.ERROR,
                                         "Sorry, this is a member-only event."
                                         " You need to use your membership "
                                         "email address to signup to this "
                                         "event.")
                    return redirect('signups.list')
                form = SignupForm_NotMember(data=request.POST)
                if form.is_valid():
                    member = Member(surname=form.cleaned_data["surname"],
                                    forenames=form.cleaned_data["forenames"],
                                    email=form.cleaned_data["email"])
                    member.save()
                    member.add_contact_detail(1, form.cleaned_data["phone"])
                    more = False

            if not more:
                similar = Place.objects.filter(slot__signup=slot.signup,
                                               member=member)
                if similar:
                    for place in similar:
                        place.status = '5'
                        place.save()

                place = Place(slot=slot, member=member)
                place.save()
                place.guid = str(uuid.uuid4())[-12:]
                place.save()

                body = "Signup Details: " + str(slot.signup.name) + "\n"
                body += "Date: " + slot.start.strftime("%A %d %B %Y") + "\n"
                body += ("Time: " + slot.start.strftime("%H:%M") + " - " +
                         slot.end.strftime("%H:%M") + "\n")
                body += "Location: " + str(slot.location) + "\n\n"

                body += ("Please note your place has NOT been confirmed until "
                         "you click on the link below:\n\n "
                         "http://membership.sedos.co.uk/signup/place/" +
                         str(place.guid) + "\n\n")
                body += ("If there is a signup fee due you will be redirected "
                         "to make this payment before your place is confirmed."
                         "\n\n")

                body += ("Contact the event organiser directly at " +
                         str(slot.signup.contact) + " for signup related "
                         "questions.\nContact membership@sedos.co.uk for any "
                         "technical/website issues or if you did not send "
                         "this request.")

                try:
                    send_mail('Sedos Event Signup',
                              body,
                              "noreply@sedos.co.uk",
                              [str(member.email), ],
                              fail_silently=False)
                except Exception:
                    messages.add_message(request, messages.ERROR,
                                         "There was a problem and we couldn't "
                                         "send your confirmation email... "
                                         "Don't worry we still have your "
                                         "signup details and someone will be "
                                         "in touch soon.")

                return redirect('signups.confirm')
    else:
        form = SignupForm()

    return render(request, template_name, {
        'slot': slot,
        'form': form,
        'more': more,
    }, )


def place_update_email(place, change=False):
    body = "Signup Details: " + str(place.slot.signup.name) + "\n"
    body += "Date: " + place.slot.start.strftime("%A %d %B %Y") + "\n"
    body += ("Time: " + place.slot.start.strftime("%H:%M") + " - " +
             place.slot.end.strftime("%H:%M") + "\n")
    body += "Location: " + str(place.slot.location) + "\n\n"

    if change:
        body += ("Please note you have been assigned a MODIFIED DATE/TIME "
                 "for this event\n\n")
    else:
        body += ("Please note the status of your place for the above event "
                 "has been changed to: " + place.get_status_display() + "\n\n")

    if place.status == '2' and place.slot.signup.confirm_info:
        body += ("--- Important Information ---\n")
        body += (place.slot.signup.confirm_info + "\n\n")

    body += ("You can review your place at the link below:\n"
             "http://membership.sedos.co.uk/signup/place/" +
             str(place.guid) + "\n\n")

    body += ("If you have any queries please contact the event organiser "
             "directly at " + str(place.slot.signup.contact) + "\n")

    send_mail('Sedos Event Signup',
              body,
              "noreply@sedos.co.uk",
              [str(place.member.email), ],
              fail_silently=True)


def confirm(request, template_name='signups/confirm.html'):
    return render(request, template_name)


def place_review(request, guid, template_name='signups/place_review.html'):
    place = get_object_or_404(Place, guid=guid)

    if ((not place.slot.free_places() and place.status in ['0', '1']) or
            place.status == '4'):
        messages.add_message(request, messages.ERROR,
                             "Sorry, all the places for this slot have been "
                             "taken already (your place was not confirmed in "
                             "time).")
        place.status = '4'
        place.save()
        place.slot.save()
        return redirect('signups.slot-list', id=place.slot.signup.id)

    if place.status == '5':
        messages.add_message(request, messages.ERROR,
                             "The link you have followed has been superseded "
                             "by a more recent request, please make sure you "
                             "are clicking on the most recent email.")
        return redirect('signups.slot-list', id=place.slot.signup.id)

    if place.to_pay():
        if payment_transfer:
            messages.add_message(request, messages.INFO,
                                 "Your previous payment for this signup "
                                 "has been transferred to this place.")
            old_place = Place.objects.get(payment=payment_transfer[0])
            old_place.payment = None
            old_place.save()
            place.payment = payment_transfer[0]
            place.save()

    if place.to_pay() and place.slot.signup.force_online_payment:
        return redirect('signups.place-payment', guid=place.guid)

    # TODO: Check for other places with 'interest'
    if place.status in ['0', '1'] and place.slot.free_places():
        messages.add_message(request, messages.SUCCESS,
                             "Your place has now been confirmed. You can "
                             "review and cancel your place using the link "
                             "previously emailed to you.")
        place.status = '2'
        place.save()
        place.slot.save()
        place_update_email(place)

    if request.method == 'POST':
        if request.POST['cancel'] == "cancel" and place.can_cancel():
            Log(member=place.member,
                message='Place ' + str(place.id) +
                        ' cancelled via URL').save()
            messages.add_message(request, messages.SUCCESS,
                                 "Your place has now been cancelled. "
                                 "Please note: you will not be refunded if"
                                 " you have made a payment.")
            place.status = '3'
            place.save()
            place.slot.save()
            place_update_email(place)

    return render(request, template_name, {
        'place': place,
        'slot': place.slot,
    }, )


def place_payment(request, guid, template_name='signups/place_payment.html'):
    place = get_object_or_404(Place, guid=guid)

    to_pay = place.to_pay()

    if not to_pay:
        return redirect('signups.place-review', guid=place.guid)

    error = None
    if request.method == 'POST':
        if request.POST.get('stripeToken', False):
            import stripe
            stripe.api_key = settings.STRIPE_PRIVATE_KEY
            token = request.POST.get('stripeToken')

            try:
                charge = stripe.Charge.create(
                    amount=int(to_pay * 100),
                    currency="gbp",
                    source=token,
                    description="Signup Fee",
                    metadata={
                        "signup": place.slot.signup,
                        "name": place.member,
                        "email": place.member.email,
                    },
                    receipt_email=place.member.email,
                    statement_descriptor="Sedos Signup Fee",
                )

                Log(member=place.member,
                    message='Paid for place ' + str(place.id) +
                            ' - Stripe Charge ID: ' + str(charge.id)
                    ).save()
                payment = SinglePayment(
                    payment_type="3", value=to_pay,
                    parameters='{"stripe_charge_id": "' +
                    str(charge.id) + '", ' +
                    '"stripe_receipt": "' +
                    str(charge.receipt_number) + '", }',
                    comment="Payment for " +
                    str(place.slot.signup),)
                payment.save()
                place.payment = payment
                place.status = '2'
                place.save()

                place_update_email(place)

                messages.add_message(request, messages.SUCCESS,
                                     ("Your payment was successful and your "
                                      "place has been confirmed."))
                return redirect('signups.place-review', guid=place.guid)
            except Exception as e:
                error = str(e)

    return render(request, template_name, {
        'place': place,
        'error': error,
        'slot': place.slot,
        'stripekey': settings.STRIPE_PUBLIC_KEY,
    }, )


def interest(request, id, template_name='signups/slot_interest.html'):
    slot = get_object_or_404(Slot, pk=id)
    slots = slot.signup.slot_set.filter(
        confirmed_slots=F('slots')).order_by('start')

    more = False
    if request.method == 'POST':
        form = SignupForm(data=request.POST)
        if form.is_valid():
            more = True
            member = Search(
                filters={'email': form.cleaned_data["email"], }).qs.first()
            if member:
                if slot.signup.slot_set.filter(place__member=member):
                    messages.add_message(request, messages.WARNING,
                                         ("Sorry, you have already signed up"
                                          " to a place for this event. Please "
                                          "check your email for details."))
                    return redirect('signups.slot-list', id=slot.signup.id)
                if not member.membercontact_set.filter(category=1):
                    form = SignupForm_NoPhone(data=request.POST)
                    if form.is_valid():
                        member.add_contact_detail(1,
                                                  form.cleaned_data["phone"])
                        member.save()
                        more = False
                else:
                    more = False
            else:
                if slot.signup.member_only:
                    messages.add_message(request, messages.ERROR,
                                         ("Sorry, this is a member-only event."
                                          " You need to use your membership "
                                          "email address to signup to this "
                                          "event."))
                    return redirect('signups.list')
                form = SignupForm_NotMember(data=request.POST)
                if form.is_valid():
                    member = Member(surname=form.cleaned_data["surname"],
                                    forenames=form.cleaned_data["forenames"],
                                    email=form.cleaned_data["email"])
                    member.save()
                    member.add_contact_detail(1, form.cleaned_data["phone"])
                    more = False

            if not more:
                # TODO: Register Interest
                pass
    else:
        form = SignupForm()

    ordered = {}
    for slot in slots:
        day = datetime.date(slot.start)
        if ordered in day:
            ordered[day].append(slot)
        else:
            ordered[day] = [slot, ]

    return render(request, template_name, {
        'slot': slot,
        'form': form,
        'ordered': ordered,
    }, )


def interest_edit(request, guid):
    return render(request, 'signups/slot_interest_edit.html')


@permission_required('signups.manage_signups')
def admin_signup_add(request, template_name='signups/manage/add.html'):
    if request.method == 'POST':
        form = SignupAddForm(data=request.POST)
        if form.is_valid():
            signup = form.save()
            signup.admin.set([request.user, ])
            signup.save()
            return redirect('signups.manage', id=signup.id)
    else:
        form = SignupAddForm()

    return render(request, template_name, {
        'form': form,
    }, )


@permission_required('signups.manage_signups')
def admin_signup_edit(request, id, template_name='signups/manage/edit.html'):
    signup = get_object_or_404(Signup, pk=id)
    if (request.user not in signup.admin.all() and not
            request.user.has_perm('signups.manage_all_signups')):
        return HttpResponse('Unauthorized', status=401)

    if request.method == 'POST':
        form = SignupEditForm(instance=signup, data=request.POST)
        if form.is_valid():
            signup = form.save()
            return redirect('signups.manage', id=signup.id)
    else:
        form = SignupEditForm(instance=signup, )

    return render(request, template_name, {
        'signup': signup,
        'form': form,
    }, )


@permission_required('signups.manage_signups')
def manage_signup(request, id, template_name='signups/manage/signup.html'):
    signup = get_object_or_404(Signup, pk=id)
    if (request.user not in signup.admin.all() and not
            request.user.has_perm('signups.manage_all_signups')):
        return HttpResponse('Unauthorized', status=401)

    slots = signup.slot_set.all().order_by('start')

    return render(request, template_name, {
        'signup': signup,
        'slots': slots,
    }, )


@permission_required('signups.manage_signups')
def export_signup(request, id, template_name='signups/manage/export.html'):
    signup = get_object_or_404(Signup, pk=id)
    if (request.user not in signup.admin.all() and not
            request.user.has_perm('signups.manage_all_signups')):
        return HttpResponse('Unauthorized', status=401)

    slots = signup.slot_set.all().order_by('start')

    return render(request, template_name, {
        'signup': signup,
        'slots': slots,
    }, )


@permission_required('signups.manage_signups')
def manage_slot(request, id, template_name='signups/manage/slot.html'):
    slot = get_object_or_404(Slot, pk=id)
    if (request.user not in slot.signup.admin.all() and not
            request.user.has_perm('signups.manage_all_signups')):
        return HttpResponse('Unauthorized', status=401)

    places = slot.place_set.exclude(status='5').order_by(
        'status', 'member__surname')

    return render(request, template_name, {
        'slot': slot,
        'places': places,
    }, )


@permission_required('signups.manage_signups')
def manage_add_slot(request, id, template_name='signups/manage/add-slot.html'):
    signup = get_object_or_404(Signup, pk=id)
    if (request.user not in signup.admin.all() and not
            request.user.has_perm('signups.manage_all_signups')):
        return HttpResponse('Unauthorized', status=401)

    if request.method == 'POST':
        form = SlotAddForm(data=request.POST)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.signup = signup
            slot.save()
            signup.update_dates()
            return redirect('signups.manage', id=signup.id)
    else:
        form = SlotAddForm()
    return render(request, template_name, {
        'signup': signup,
        'latest': signup.slot_set.all().order_by('-pk').first(),
        'form': form,
    }, )


@permission_required('signups.manage_signups')
def manage_edit_slot(request, id,
                     template_name='signups/manage/edit-slot.html'):
    slot = get_object_or_404(Slot, pk=id)
    if (request.user not in slot.signup.admin.all() and not
            request.user.has_perm('signups.manage_all_signups')):
        return HttpResponse('Unauthorized', status=401)

    if request.method == 'POST':
        form = SlotAddForm(data=request.POST, instance=slot)
        if request.POST['submit'] == "delete":
            if not slot.place_set.all():
                signup = slot.signup
                slot.delete()
                messages.add_message(request, messages.ERROR,
                                     "Slot has been deleted.")
                return redirect('signups.manage', id=signup.id)
        if form.is_valid():
            form.save()
            slot.signup.update_dates()
            return redirect('signups.manage-slot', id=slot.id)
    else:
        form = SlotAddForm(instance=slot, )

    return render(request, template_name, {
        'slot': slot,
        'form': form,
    }, )


# @permission_required('signups.manage_signups')
# def manage_remove_slot(request, id):
#     return HttpResponse("OK")


@permission_required('signups.manage_signups')
def manage_add_place(request, id,
                     template_name='signups/manage/add-place.html'):
    return HttpResponse("OK")


@permission_required('signups.manage_signups')
def manage_place(request, id, action,
                 template_name='signups/manage/place.html'):
    place = get_object_or_404(Place, pk=id)
    if (request.user not in place.slot.signup.admin.all() and not
            request.user.has_perm('signups.manage_all_signups')):
        return HttpResponse('Unauthorized', status=401)
    if action in ['2', '3']:
        place.status = action
        place.save()

        place_update_email(place)
        return redirect('signups.manage-slot', id=place.slot.id)
    elif action == '1':
        if place.to_pay():
            payment = SinglePayment(payment_type="0", value=place.to_pay(),
                                    comment="Payment for " +
                                    str(place.slot.signup) +
                                    ' - Cash paid to ' +
                                    str(request.user.get_full_name()))
            payment.save()
            place.payment = payment
            place.status = '2'
            place.save()

            place_update_email(place)
        return redirect('signups.manage-slot', id=place.slot.id)
    elif action == '4':
        pass
    elif action == '5':
        messages.add_message(request, messages.SUCCESS,
                             ("Reminder Email Sent"))
        place_update_email(place)
        return redirect('signups.manage-slot', id=place.slot.id)

    slots = place.slot.signup.slot_set.exclude(
        id=place.slot.pk).order_by('start')
    return render(request, template_name, {
        'place': place,
        'slots': slots,
    }, )


@permission_required('signups.manage_signups')
def manage_move_place(request, id, slot):
    place = get_object_or_404(Place, pk=id)
    if (request.user not in place.slot.signup.admin.all() and not
            request.user.has_perm('signups.manage_all_signups')):
        return HttpResponse('Unauthorized', status=401)

    slot = get_object_or_404(Slot, pk=slot)

    old_slot = place.slot

    place.slot = slot
    place.save()
    place.slot.save()

    old_slot.save()

    place_update_email(place, True)

    return redirect('signups.manage-slot', id=place.slot.id)
