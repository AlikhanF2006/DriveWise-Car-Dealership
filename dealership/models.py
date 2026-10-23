from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Dealer(models.Model):
    name = models.CharField(max_length=180)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2, db_index=True)
    zipcode = models.CharField(max_length=12)
    phone = models.CharField(max_length=30, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f'{self.name} — {self.city}, {self.state}'

class Review(models.Model):
    dealer = models.ForeignKey(Dealer, related_name='reviews', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    review = models.TextField(max_length=2000)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.dealer.name}: {self.rating}/5 by {self.author.username}'

class CarMake(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class CarModel(models.Model):
    make = models.ForeignKey(CarMake, related_name='models', on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['make', 'name'], name='uniq_car_make_model')]
    def __str__(self):
        return f'{self.make.name} {self.name}'
