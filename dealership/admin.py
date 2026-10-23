from django.contrib import admin
from .models import Dealer, Review, CarMake, CarModel

@admin.register(Dealer)
class DealerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'city', 'state', 'phone')
    list_filter = ('state',)
    search_fields = ('name', 'city')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'dealer', 'author', 'rating', 'created_at')
    list_filter = ('rating',)

@admin.register(CarMake)
class CarMakeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'make', 'name')
    list_filter = ('make',)
