from django.conf.urls import url

from signups import views

urlpatterns = [
    url(r'^$', views.signup_list, name='signups.list'),

    url(r'^place/payment/(?P<guid>[-\w]*)$',
        views.place_payment, name='signups.place-payment'),
    url(r'^place/(?P<guid>[-\w]*)$',
        views.place_review, name='signups.place-review'),

    url(r'^interest/edit/(?P<guid>[-\w]*)$',
        views.interest_edit, name='signups.interest-edit'),
    url(r'^interest/(?P<id>[-\w]*)$',
        views.interest, name='signups.interest'),
    url(r'^(?P<id>[-\w]*)$',
        views.slot_list, name='signups.slot-list'),
    url(r'^slot/(?P<id>[-\w]*)$',
        views.slot_signup, name='signups.slot-signup'),
    url(r'^confirm-email/$',
        views.confirm, name='signups.confirm'),

    url(r'^add/$',
        views.admin_signup_add, name='signups.add'),
    url(r'^edit/(?P<id>[-\w]*)$',
        views.admin_signup_edit, name='signups.edit'),
    url(r'^manage/(?P<id>[-\w]*)$',
        views.manage_signup, name='signups.manage'),
    url(r'^export/(?P<id>[-\w]*)$',
        views.export_signup, name='signups.export'),
    url(r'^manage/slot/add/(?P<id>[-\w]*)$',
        views.manage_add_slot, name='signups.add-slot'),
    url(r'^manage/slot/edit/(?P<id>[-\w]*)$',
        views.manage_edit_slot, name='signups.edit-slot'),
    url(r'^manage/slot/(?P<id>[-\w]*)$',
        views.manage_slot, name='signups.manage-slot'),
    url(r'^manage/place/move/(?P<id>[-\w]*)/(?P<slot>[-\w]*)$',
        views.manage_move_place, name='signups.move-place'),
    url(r'^manage/place/(?P<id>[-\w]*)/(?P<action>[-\w]*)$',
        views.manage_place, name='signups.manage-place'),
]
