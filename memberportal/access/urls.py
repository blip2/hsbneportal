from django.urls import path
from . import views

urlpatterns = [
    path('doors/', views.manage_doors, name='manage_doors'),
    path('door/add/', views.add_door, name='add_door'),
    path('door/<int:door_id>/edit/', views.edit_door, name='edit_door'),
    path('api/door/<int:door_id>/delete/', views.delete_door, name='delete_door'),
    path('api/door/<int:door_id>/unlock/', views.unlock_door, name='unlock_door'),
    path('api/door/<int:door_id>/lock/', views.lock_door, name='lock_door'),
    path('api/door/<int:door_id>/grant/<int:member_id>/', views.admin_grant_door, name='admin_grant_door'),
    path('api/door/<int:door_id>/revoke/<int:member_id>/', views.admin_revoke_door, name='admin_revoke_door'),
    path('api/door/<int:door_id>/request/', views.request_access, name='request_access'),
    path('api/door/<int:door_id>/check/<int:rfid_code>/', views.check_door_access, name='check_access'),
    path('api/door/check/<int:rfid_code>/', views.check_door_access, name='check_access'),
    path('api/door/<int:door_id>/authorised/', views.authorised_door_tags, name='authorised_tags'),
    path('api/door/authorised/', views.authorised_door_tags, name='authorised_tags'),
    path('api/door/<int:door_id>/checkin/', views.door_checkin, name='door_checkin'),
    path('api/door/checkin/', views.door_checkin, name='door_checkin'),
    path('api/door/reset-default-access', views.reset_default_door_access, name='reset_default_access'),
    path('interlocks/', views.manage_interlocks, name='manage_interlocks'),
    path('interlocks/add', views.add_interlock, name='add_interlock'),
    path('interlocks/<int:interlock_id>/edit', views.edit_interlock, name='edit_interlock'),
    path('interlocks/<int:interlock_id>/delete', views.delete_interlock, name='delete_interlock'),
    path('interlocks/<int:interlock_id>/unlock', views.unlock_interlock, name='unlock_interlock'),
    path('interlocks/<int:interlock_id>/lock', views.lock_interlock, name='lock_interlock'),
    path('api/interlock/<int:interlock_id>/grant/<int:member_id>/', views.admin_grant_interlock, name='admin_grant_interlock'),
    path('api/interlock/<int:interlock_id>/revoke/<int:member_id>/', views.admin_revoke_interlock, name='admin_revoke_interlock'),
    path('api/interlock/<int:interlock_id>/check/<int:rfid_code>/', views.check_interlock_access, name='check_interlock_access'),
    path('api/interlock/check/<int:rfid_code>/', views.check_interlock_access, name='check_interlock_access'),
    path('api/interlock/session/<uuid:session_id>/heartbeat/', views.check_interlock_access, name='check_interlock_access'),
    path('api/interlock/session/<uuid:session_id>/end/', views.end_interlock_session, name='end_interlock_session'),
    path('api/interlock/<int:interlock_id>/checkin/', views.interlock_checkin, name='interlock_checkin'),
    path('api/interlock/checkin/', views.interlock_checkin, name='interlock_checkin'),
    path('api/interlock/authorised/', views.authorised_interlock_tags, name='authorised_interlock_tags'),
    path('api/interlock/<int:interlock_id>/authorised/', views.authorised_interlock_tags, name='authorised_interlock_tags'),
    path('api/interlock/reset-default-access', views.reset_default_interlock_access, name='reset_default_interlock_access'),
    path('cron/interlock/', views.interlock_cron, name='interlock_cron'),
]
