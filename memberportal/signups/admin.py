from django.contrib import admin

from signups.models import Signup, Slot, Place

class SlotInline(admin.TabularInline):
    model = Slot
    extra = 1

@admin.register(Signup)
class SignupAdmin(admin.ModelAdmin):
    inlines = [SlotInline,]

class PlaceInline(admin.TabularInline):
    model = Place
    forms = ('status', 'payment', 'member', 'guid')
    extra = 0

@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    inlines = [PlaceInline,]
    list_display = ('signup', 'location', 'start', 'places', 'confirmed_places')

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    pass
