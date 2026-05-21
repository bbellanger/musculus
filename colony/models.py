from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import timedelta

# Create your models here.
# Each field needs to be an individual class so to be able to be able
# to group queris if needed (ForeignKey)

class Protocol(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class MouseLine(models.Model):
    name = models.CharField(max_length=15)

    def __str__(self):
        return self.name

class CoatColor(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class GenotypeTag(models.Model):
    label = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.label

# Mouse model

class Mouse(models.Model):
    SEX_CHOICES = {"F": "Female", "M": "Male"}
    MATURITY_DAYS = 42 # Equivalent to 6 weeks

    uuid = models.UUIDField(primary_key =True, default=uuid.uuid4, editable=False)
    tag = models.CharField(max_length=10)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    dob = models.DateField()

    ## Mouse - Foreign Keys

    protocol = models.ForeignKey(Protocol, on_delete=models.SET_NULL, null=True, blank=True, related_name="mice")
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="mice")
    mouse_line = models.ForeignKey(MouseLine, on_delete=models.SET_NULL, null=True, blank=True, related_name="mice")
    coat_color = models.ForeignKey(CoatColor, on_delete=models.SET_NULL, null=True, blank=True, related_name="mice")

    ## Mouse - free text and tag fields
    phenotype = models.CharField(max_length=200, blank=True)
    genotype = models.ManyToManyField(GenotypeTag, blank=True, related_name="mice")

    ## Mouse - weaning and adulthood
    ##         computed date properties
    ##         Uses @property to turn the method into an attribute
    ##         mouse.wean_date() -> mouse.wean_date
    @property
    def wean_date(self):
        return self.dob + timedelta(days=21)


    @property
    def mature_date(self):
        return self.dob + timedelta(days=self.MATURITY_DAYS)

    ## Mouse - Mating
    @property
    def is_mating(self):
        return self.mating_as_male.filter(end_date__isnull=True).exists() or self.mating_as_female.filter(end_date__isnull=True).exists()

    ## define __str__ method to avoid UUID fallback
    def __str__(self):
        return self.tag

# MatingPair
class MatingPair(models.Model):
    male = models.ForeignKey(Mouse, on_delete=models.SET_NULL, null=True, related_name="mated_as_male")
    female = models.ForeignKey(Mouse, on_delete=models.SET_NULL, null=True, related_name="mated_as_female")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True) #null means still active

    ## MatingPair - turn method into attribute
    @property
    def is_active(self):
        return self.end_date is None

    def __str__(self):
        return f"{self.male} x {self.female} ({'active' if self.is_active else 'ended'})"
