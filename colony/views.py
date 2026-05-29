from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Mouse, Cage, MatingPair, Litter, MouseLine, CoatColor, Protocol, GenotypeTag


# ── Shared context helper ──────────────────────────────────────────────────

def _base_context():
    """All queryset dropdowns needed by the template."""
    return {
        'mice':         Mouse.objects.select_related(
                            'mouse_line', 'coat_color', 'protocol', 'owner', 'cage', 'litter'
                        ).prefetch_related('genotype_entries__tag').all(),
        'cages':        Cage.objects.select_related('mating_pair__male', 'mating_pair__female').all(),
        'mating_pairs': MatingPair.objects.select_related('male', 'female').all(),
        'litters':      Litter.objects.select_related(
                            'mating_pair__male', 'mating_pair__female', 'mating_pair__cage'
                        ).prefetch_related('pups').all(),
        # Dropdown option lists
        'mouse_lines':   MouseLine.objects.all(),
        'coat_colors':   CoatColor.objects.all(),
        'protocols':     Protocol.objects.all(),
        'users':         User.objects.all(),
        'genotype_tags': GenotypeTag.objects.all(),
        'males':         Mouse.objects.filter(sex='M'),
        'females':       Mouse.objects.filter(sex='F'),
        'alt_id_choices': ['L', 'R', 'LL', 'RR', 'LR', 'LLR', 'LRR', 'LLRR',
                           'LLL', 'RRR', 'LLLR', 'LLLRR', 'LRRR', 'LLRRR'],
    }


# ── Index ──────────────────────────────────────────────────────────────────

@login_required
def index(request):
    return render(request, 'colony/index.html', _base_context())


# ── Mouse CRUD ─────────────────────────────────────────────────────────────

@login_required
def mouse_create(request):
    if request.method == 'POST':
        Mouse.objects.create(
            sex        = request.POST.get('sex'),
            alt_id     = request.POST.get('alt_id') or '',
            dob        = request.POST.get('dob'),
            mouse_line = _fk(MouseLine, request.POST.get('mouse_line')),
            coat_color = _fk(CoatColor, request.POST.get('coat_color')),
            protocol   = _fk(Protocol,  request.POST.get('protocol')),
            owner      = _fk(User,      request.POST.get('owner')),
            cage       = _fk(Cage,      request.POST.get('cage')),
            phenotype  = request.POST.get('phenotype', ''),
        )
    return redirect('index')


@login_required
def mouse_update(request, pk):
    mouse = get_object_or_404(Mouse, pk=pk)
    if request.method == 'POST':
        mouse.sex        = request.POST.get('sex')
        mouse.alt_id     = request.POST.get('alt_id') or ''
        mouse.dob        = request.POST.get('dob')
        mouse.mouse_line = _fk(MouseLine, request.POST.get('mouse_line'))
        mouse.coat_color = _fk(CoatColor, request.POST.get('coat_color'))
        mouse.protocol   = _fk(Protocol,  request.POST.get('protocol'))
        mouse.owner      = _fk(User,      request.POST.get('owner'))
        mouse.cage       = _fk(Cage,      request.POST.get('cage'))
        mouse.phenotype  = request.POST.get('phenotype', '')
        mouse.save()
    return redirect('index')


@login_required
def mouse_delete(request, pk):
    mouse = get_object_or_404(Mouse, pk=pk)
    if request.method == 'POST':
        mouse.delete()
    return redirect('index')


# ── Cage CRUD ──────────────────────────────────────────────────────────────

@login_required
def cage_create(request):
    if request.method == 'POST':
        Cage.objects.create(
            cage_location = request.POST.get('cage_location', ''),
            mating_pair   = _fk(MatingPair, request.POST.get('mating_pair')),
        )
    return redirect('index')


@login_required
def cage_update(request, pk):
    cage = get_object_or_404(Cage, pk=pk)
    if request.method == 'POST':
        cage.cage_location = request.POST.get('cage_location', '')
        cage.mating_pair   = _fk(MatingPair, request.POST.get('mating_pair'))
        cage.save()
    return redirect('index')


@login_required
def cage_delete(request, pk):
    cage = get_object_or_404(Cage, pk=pk)
    if request.method == 'POST':
        cage.delete()
    return redirect('index')


# ── MatingPair CRUD ────────────────────────────────────────────────────────

@login_required
def matingpair_create(request):
    if request.method == 'POST':
        MatingPair.objects.create(
            male       = get_object_or_404(Mouse, pk=request.POST.get('male')),
            female     = get_object_or_404(Mouse, pk=request.POST.get('female')),
            start_date = request.POST.get('start_date'),
            end_date   = request.POST.get('end_date') or None,
        )
    return redirect('index')


@login_required
def matingpair_update(request, pk):
    mp = get_object_or_404(MatingPair, pk=pk)
    if request.method == 'POST':
        mp.male       = get_object_or_404(Mouse, pk=request.POST.get('male'))
        mp.female     = get_object_or_404(Mouse, pk=request.POST.get('female'))
        mp.start_date = request.POST.get('start_date')
        mp.end_date   = request.POST.get('end_date') or None
        mp.save()
    return redirect('index')


@login_required
def matingpair_delete(request, pk):
    mp = get_object_or_404(MatingPair, pk=pk)
    if request.method == 'POST':
        mp.delete()
    return redirect('index')


# ── Litter CRUD ────────────────────────────────────────────────────────────

@login_required
def litter_create(request):
    if request.method == 'POST':
        Litter.objects.create(
            mating_pair = get_object_or_404(MatingPair, pk=request.POST.get('mating_pair')),
            dob         = request.POST.get('dob'),
            notes       = request.POST.get('notes', ''),
        )
    return redirect('index')


@login_required
def litter_update(request, pk):
    litter = get_object_or_404(Litter, pk=pk)
    if request.method == 'POST':
        litter.mating_pair = get_object_or_404(MatingPair, pk=request.POST.get('mating_pair'))
        litter.dob         = request.POST.get('dob')
        litter.notes       = request.POST.get('notes', '')
        litter.save()
    return redirect('index')


@login_required
def litter_delete(request, pk):
    litter = get_object_or_404(Litter, pk=pk)
    if request.method == 'POST':
        litter.delete()
    return redirect('index')


# ── Utility ────────────────────────────────────────────────────────────────

def _fk(model, pk_str):
    """Return a model instance or None for empty/missing FK values."""
    if pk_str:
        return model.objects.filter(pk=pk_str).first()
    return None
