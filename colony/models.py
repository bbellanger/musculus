from django.db import models, transaction # For unique auto id attribution
from django.contrib.auth.models import User
import uuid, re # For unique auto id attribution
from datetime import timedelta

# Create your models here.
# Each field needs to be an individual class so to be able to be able
# to group queris if needed (ForeignKey)

class Protocol(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class MouseLine(models.Model):
    name = models.CharField(max_length=50)

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

# Model History added
# Relate full history for Mouse
class History(models.Model):
    """
    One record per life event for a mouse
    Covers: birth, move, mating, litter, status changes, vet care, etc.
    """

    EVENT_CHOICES = [
        ("birth",          'Birth'),
        ('move',           'Cage move'),
        ('matting',        'Mating'),
        ('litter',         'Litter'),
        ('status',         'Status change'),
        ('vet',            'Vet care'),
        ('EEG Surgery',     'EEG surgery experiment'),
        ('EEG rec',        'EEG recording'),
        ('sleep dep',      'Sleep deprivation experiment'),
        ('Sleep rec',      'Sleep recording'),
        ('Injury',         'Injury'),
        ('death',          'Death'),
        ('other',          'Other'),
    ]

    STATUS_CHOICES = [
        ('alive',          'Alive'),
        ('breeder',        'Reserved for breeding'),
        ('vet',            'Under vet surveillance'),
        ('dead',           'Dead'),
    ]

    mouse = models.ForeignKey('Mouse', on_delete=models.CASCADE, related_name='history')
    event = models.CharField(max_length=20, choices=EVENT_CHOICES)
    date = models.DateField()

    # ----------------------------- Foreign keys for events -------------------------------------#

    cage = models.ForeignKey('Cage', on_delete=models.SET_NULL, null=True, blank=True, related_name='history', help_text='Destination cage for a move event')
    litter = models.ForeignKey('Litter', on_delete=models.SET_NULL, null=True, blank=True, related_name='history', help_text='Litter event (link to litter)')
    mating_pair = models.ForeignKey('MatingPair', on_delete=models.SET_NULL, null=True, blank=True, related_name='history', help_text='Mating event')
    pup_count = models.PositiveSmallIntegerField(null=True, blank=True, help_text='Number of pups (for litter events)')
    new_status = models.CharField(max_length=20, choices=EVENT_CHOICES, blank=True, help_text='New.mouse status (for status change events)')
    notes = models.TextField(blank=True, help_text='Experiment details, vet notes, injury description, etc.')

    class Meta:
        ordering = ['-date', '-pk']

    def __str__(self):
        return f'{self.mouse.tag} - {self.get_event_display()} {self.date})'

# Model for genotype tag inhiritance
class MouseGenotype(models.Model):
    mouse = models.ForeignKey("Mouse", on_delete=models.CASCADE, related_name="genotype_entries")
    tag = models.ForeignKey(GenotypeTag, on_delete=models.CASCADE)
    zygosity = models.CharField(max_length=3, choices=[("HET", "Heterozygous"), ("HOM", "Homozygous"), ("WT", "Wild Type")])

    class Meta:
        unique_together = ("mouse", "tag") # one row per mouse+tag combination


# Mouse model
class Mouse(models.Model):

    STATUS_CHOICES = [
        ('alive',          'Alive'),
        ('breeder',        'Reserved for breeding'),
        ('vet',            'Under vet surveillance'),
        ('dead',           'Dead'),
    ]

    SEX_CHOICES = {"F": "Female", "M": "Male"}
    ALT_ID = {"None": "None", "L": "L","R": "R","LL": "LL","RR": "RR","LR": "LR","LLR": "LLR","LRR": "LRR","LLRR": "LLRR","LLL": "LLL","RRR": "RRR","LLLR": "LLLR","LLLRR": "LLLRR","LLLLRRR": "LLLRRR", "LRRR": "LRRR","LLRRR": "LLRRR"}
    MATURITY_DAYS = 42 # Equivalent to 6 weeks

    uuid = models.UUIDField(primary_key =True, default=uuid.uuid4, editable=False)
    tag = models.CharField(max_length=10, unique=True, blank=True)
    cage = models.ForeignKey('Cage', on_delete=models.SET_NULL, null=True, blank=True, related_name='mice')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='alive')

    ## Genotyp parental inheritance
    def  _inherit_parental_genotypes(self):
        if not self.litter_id:
            return
        pair = self.litter.mating_pair
        if pair is None:
            return
        def _hom_set(parent):
            if parent is None:
                return set()
            return set(
                parent.genotype_entries
                    .filter(zygosity="HOM")
                    .values_list("tag_id", flat=True)
            )

        male_hom   = _hom_set(pair.male)    # e.g. {3, 5}   (tag IDs for Cre and fl/fl)
        female_hom = _hom_set(pair.female)  # e.g. {3}      (tag ID for Cre only)

        both_hom = male_hom & female_hom    # {3}     — intersection: in BOTH sets
        one_hom  = (male_hom | female_hom) - both_hom  # {5} — in either but NOT both

        # Create hom inh tags
        for tag_id in both_hom:
            MouseGenotype.objects.get_or_create( # Don;t overwrite existant genotype, in case it was genotyped
                mouse=self, tag_id=tag_id,
                defaults={"zygosity": "HOM"},
            )

        # Create het inh tags
        for tag_id in one_hom:
            MouseGenotype.objects.get_or_create( # No overwritting
                mouse=self, tag_id=tag_id,
                defaults={"zygosity": "HET"},
            )

    ## Mouse - sync MouseLine
    def _sync_mouse_line(self):
        het_labels = list(
            self.genotype_entries
                .filter(zygosity="HET")
                .order_by("tag__label")
                .values_list("tag__label", flat=True)
        )

        if not het_labels:
            return
        line_name = " ; ".join(het_labels)
        mouse_line, _ = MouseLine.objects.get_or_create(name=line_name)

        if self.mouse_line_id != mouse_line.pk:
            Mouse.objects.filter(pk=self.pk).update(mouse_line=mouse_line)
            self.mouse_line = mouse_line

    ## Mouse - Save
    def save(self, *args, **kwargs):
        if not self.tag:
            self.tag = self._generate_tag()

        if not self.owner and self.litter and self.litter.owner:
            self.owner = self.litter.owner

        if self.litter_id:
            if not self.owner_id and self.litter.owner:
                self.owner = self.litter.owner
            if not self.protocol_id and self.litter.protocol_id:
                self.protocol = self.litter.protocol

#        if not self.cage_id and hasattr(self.litter.mating_pair, 'cage'):
        if not self.cage_id and self.litter_id and hasattr(self.litter.mating_pair, 'cage'):
            self.cage = self.litter.mating_pair.cage

        super().save(*args, **kwargs)

        # Creat genotype entries inherited from parents
        self._inherit_parental_genotypes()
        # Derive and assign to MouseLine
        self._sync_mouse_line()

    @classmethod
    # The method is attached to the class rather than an instance, so it receives cls (the Mouse class itself) instead of self.
    # This lets it query the database without needing an existing mouse object
    def _generate_tag(cls):
        with transaction.atomic(): # Wraps everything in a single database transaction | If anything fails inside, the entire block is rolled back
            # Lock existing rows to prevent two mice grabbing the same tag
            existing_tags = cls.objects.select_for_update().values_list("tag", flat=True)
            nums = [
                int(m.group(1))
                for tag in existing_tags
                if (m := re.match(r"^M(\d+)$", tag))
            ]
            next_num = max(nums) + 1 if nums else 1
            return f"M{next_num:06d}" #M000001, M000002, ...


    sex = models.CharField(max_length=1, choices=SEX_CHOICES, null=True, blank=True)
    alt_id = models.CharField(max_length=7, choices=ALT_ID, null=True, blank=True)
    dob = models.DateField()
    litter = models.ForeignKey('Litter', on_delete=models.SET_NULL, null=True, blank=True, related_name="pups")

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
        return self.mated_as_male.filter(end_date__isnull=True).exists() or self.mated_as_female.filter(end_date__isnull=True).exists()

    ## define __str__ method to avoid UUID fallback
    def __str__(self):
        return self.tag

    ## Mouse - MatingProtocol
    @property
    def on_protocol(self):
        if self.sex == "M" and self.protocol.exist():
            return self.protocol
        return None

# MatingPair
class MatingPair(models.Model):
    male = models.ForeignKey(Mouse, on_delete=models.SET_NULL, null=True, related_name="mated_as_male")
    female = models.ForeignKey(Mouse, on_delete=models.SET_NULL, null=True, related_name="mated_as_female")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True) #null means still active

    ## MatingPair - Inherit Female ownership
    @property
    def owner(self):
        if self.female:
            return self.female.owner
        return None

    ## MatingPair - turn method into attribute
    @property
    def is_active(self):
        return self.end_date is None

    def __str__(self):
        return f"{self.male} x {self.female} ({'active' if self.is_active else 'ended'})"

# Litter model
class Litter(models.Model):
    mating_pair = models.ForeignKey(MatingPair, on_delete=models.SET_NULL, null=True, related_name="litters")
    cage = models.ForeignKey('Cage', on_delete=models.SET_NULL, null=True, blank=True, related_name='litters')
    dob = models.DateField()
    notes = models.CharField(max_length=200, null=True, blank=True)
    protocol = models.ForeignKey(Protocol, on_delete=models.SET_NULL, null=True, blank=True, related_name="litters_on_protocol")
    #owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="litters")

    def __str__(self):
        return f"litter from {self.mating_pair} on {self.dob}"

    @property
    def owner(self):
        if self.mating_pair and self.mating_pair.female:
            return self.mating_pair.female.owner
        return None

# Cage model
class Cage(models.Model):
    cage_id = models.CharField(max_length=10, unique=True, blank=True)
    cage_location = models.CharField(max_length=10, unique=True, blank=True)
    mating_pair = models.OneToOneField(
        MatingPair,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cage"
    )

    def _generate_cage_id(self):
        last = Cage.objects.order_by("-cage_id").first()
        if last and last.cage_id.startswith("C"):
            try:
                num = int(last.cage_id[1:]) + 1
            except ValueError:
                num = 1
        else :
            num = 1
        return f"C{num:06d}" # e.g. C000001, C000002, ...

    def save(self, *args, **kwargs):
        if not self.cage_id:
            self.cage_id = self._generate_cage_id()
        super().save(*args, **kwargs)

    @property
    def name(self):
        if not self.mating_pair:
            return None
        het_labels = set()
        for parent in [self.mating_pair.male, self.mating_pair.female]:
            if parent:
                for mg in parent.genotype_entries.filter(zygosity__in=["HET", "HOM"]):
                    het_labels.add(mg.tag.label)
        if het_labels:
            line_name = " ; ".join(sorted(het_labels))
            return MouseLine.objects.filter(name=line_name).first()
        return None

    def __str__(self):
        return f"{self.cage_id} - {self.name or 'Unknow line'}"
