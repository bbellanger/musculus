from django.contrib import admin
from .models import Mouse, Protocol, MouseLine, CoatColor, GenotypeTag, MatingPair

admin.site.register(Protocol)
admin.site.register(MouseLine)
admin.site.register(CoatColor)
admin.site.register(GenotypeTag)

@admin.register(Mouse)
class MouseAdmin(admin.ModelAdmin):
    list_display = ('tag', 'sex', 'dob', 'wean_date', 'mature_date', 'mouse_line', 'owner', 'protocol')
    list_filter = ('sex', 'mouse_line', 'protocol', 'owner', 'coat_color')
    search_fields = ('tag', 'phenotype')
    filter_horizontal = ('genotype',)

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

