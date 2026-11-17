from django.contrib import admin
from .models import Cage, Litter, Mouse, Protocol, MouseLine, CoatColor, GenotypeTag, MatingPair, MouseGenotype, History

admin.site.register(Protocol)
admin.site.register(MouseLine)
admin.site.register(CoatColor)
admin.site.register(GenotypeTag)

class HistoryInline(admin.TabularInline):
    model = History
    extra = 1
    fields = ('event', 'date', 'new_status', 'cage', 'litter', 'mating_pair', 'pup_count', 'notes')
    readonly_fields = ()

@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ('mouse', 'event', 'date', 'new_status', 'pup_count')
    list_filter = ('event', 'new_status', 'date')
    search_fields = ('mouse_tag', 'notes')

class MouseGenotypeInline(admin.TabularInline):
    model = MouseGenotype
    fields = ["tag", "zygosity"]
    extra = 1

@admin.register(Cage)
class CageAdmin(admin.ModelAdmin):
    list_display = ('cage_id', 'cage_location', 'name')
    readonly_fields = ('name',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return('cage_id', 'name')
        return('name',)

@admin.register(Mouse)
class MouseAdmin(admin.ModelAdmin):
    inlines = [MouseGenotypeInline, HistoryInline]
    list_display = ('tag', 'sex', 'dob', 'wean_date', 'mature_date', 'mouse_line', 'owner', 'protocol')
    list_filter = ('sex', 'mouse_line', 'protocol', 'owner', 'coat_color')
    search_fields = ('tag', 'phenotype')

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing existing mouse - show tag as read-only
            return ('tag',)
        return() # Creating a new mouse - hide it entirely, let save() and generate it

    def get_exclude(self, request, obj=None):
        if not obj: # hide tag field on the add form
            return ('tag',)
        return()

@admin.register(MatingPair)
class MatingPairAdmin(admin.ModelAdmin):
    list_display = ('male', 'female', 'start_date', 'end_date', 'is_active')
    list_filter = ('end_date',)
    search_fields = ('male__tag', 'female__tag')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'male':
            kwargs['queryset'] = Mouse.objects.filter(sex='M')
        if db_field.name == 'female':
            kwargs['queryset'] = Mouse.objects.filter(sex='F')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # `is_active` is a `@proprty` not a database field
    # sort it in the admin list anyway
    @admin.display(boolean=True, description='Active')
    def is_active(self, obj):
        return obj.end_date is None


class PupInline(admin.TabularInline):
    model = Mouse
    fields = ["sex", "alt_id", "dob", "coat_color", "mouse_line"]
    extra = 1  # number of blank rows shown

@admin.register(Litter)
class LitterAdmin(admin.ModelAdmin):
    inlines = [PupInline]
