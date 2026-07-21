from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Mouse, Cage, MatingPair, Litter, MouseLine, CoatColor, Protocol, GenotypeTag, MouseGenotype, History
from django.db.models import Prefetch

# Thermal label generator
from django.views.decorators.http import require_GET
from django.views.decorators.clickjacking import xframe_options_exempt
from .cage_label import render_cage_label_pdf

#Read-only Mouse history import
from django.http import JsonResponse, HttpResponse


# ── Shared context helper ──────────────────────────────────────────────────

def _base_context():
    return {
        'mice':         Mouse.objects.select_related(
                            'mouse_line', 'coat_color', 'protocol', 'owner', 'cage', 'litter'
                        ).prefetch_related('genotype_entries__tag').all(),
        #'cages':        Cage.objects.select_related(Prefetch('mice', queryset=Mouse.objects.order_by('sex', 'tag'))).select_related('mating_pair__male', 'mating_pair__female').all(),
        'cages': Cage.objects.prefetch_related(Prefetch('mice', queryset=Mouse.objects.order_by('sex', 'tag'))).select_related('mating_pair__male', 'mating_pair__female').all(),
        'mating_pairs': MatingPair.objects.filter(end_date__isnull=True).select_related('male', 'female').all(),
        'litters':      Litter.objects.select_related(
                            'mating_pair__male', 'mating_pair__female', 'mating_pair__cage'
                        ).prefetch_related('pups').all(),
        'mouse_lines':    MouseLine.objects.all(),
        'coat_colors':    CoatColor.objects.all(),
        'protocols':      Protocol.objects.all(),
        'users':          User.objects.all(),
        'genotype_tags':  GenotypeTag.objects.all(),
        'males':          Mouse.objects.filter(sex='M'),
        'females':        Mouse.objects.filter(sex='F'),
        'alt_id_choices': ['L', 'R', 'LL', 'RR', 'LR', 'LLR', 'LRR', 'LLRR',
                           'LLL', 'RRR', 'LLLR', 'LLLRR', 'LRRR', 'LLRRR'],
        'pup_range':      range(1, 13),
    }


def _save_genotypes(mouse, post):
    """
    Replace all MouseGenotype rows for this mouse, then re-sync the mouse line.

    Sequence matters:
      1. Delete existing genotypes
      2. Recreate from POST data
      3. Call _sync_mouse_line() so mouse_line reflects the NEW genotypes
         (mouse.save() already called it on the OLD genotypes — too early)
    """
    tags       = post.getlist('genotype_tag')
    zygosities = post.getlist('genotype_zygosity')

    MouseGenotype.objects.filter(mouse=mouse).delete()

    for tag_pk, zyg in zip(tags, zygosities):
        if not tag_pk:
            continue
        gt = GenotypeTag.objects.filter(pk=tag_pk).first()
        if gt and zyg in ('HET', 'HOM', 'WT'):
            MouseGenotype.objects.create(mouse=mouse, tag=gt, zygosity=zyg)

    # Re-run _sync_mouse_line() now that genotypes are correct.
    # mouse.save() ran it before genotypes were updated, so we must call it again.
    mouse._sync_mouse_line()


# ── Index ──────────────────────────────────────────────────────────────────

@login_required
def index(request):
    return render(request, 'colony/index.html', _base_context())


# ── Mouse CRUD ─────────────────────────────────────────────────────────────

@login_required
def mouse_create(request):
    if request.method == 'POST':
        mouse = Mouse.objects.create(
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
        _save_genotypes(mouse, request.POST)
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
        mouse.status     = request.POST.get('status', 'alive')
        mouse.save()
        _save_genotypes(mouse, request.POST)
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
        litter = Litter.objects.create(
            mating_pair = get_object_or_404(MatingPair, pk=request.POST.get('mating_pair')),
            dob         = request.POST.get('dob'),
            notes       = request.POST.get('notes', ''),
            cage        = request.POST.get('cage'),
        )
        pup_count = int(request.POST.get('pups') or 0)
        for _ in range(pup_count):
            Mouse.objects.create(litter=litter, dob=litter.dob, cage=litter.cage)
    return redirect('index')


@login_required
def litter_update(request, pk):
    litter = get_object_or_404(Litter, pk=pk)
    if request.method == 'POST':
        litter.mating_pair = get_object_or_404(MatingPair, pk=request.POST.get('mating_pair'))
        litter.dob         = request.POST.get('dob')
        litter.notes       = request.POST.get('notes', '')
        litter.cage        = request.POST.get('cage')
        litter.save()
        # Update each pup — fields posted as pup_<pk>_<fieldname>
        for pup in litter.pups.all():
            prefix = f'pup_{pup.pk}_'
            sex        = request.POST.get(prefix + 'sex')
            alt_id     = request.POST.get(prefix + 'alt_id')
            coat_color = request.POST.get(prefix + 'coat_color')
            cage_id    = request.POST.get(prefix + 'cage')
            notes      = request.POST.get(prefix + 'notes', '')

            if alt_id is not None:
                pup.alt_id = alt_id
            if sex is not None:
                pup.sex = sex
            if coat_color is not None:
                pup.coat_color = _fk(CoatColor, coat_color) if coat_color else None
            if cage_id is not None:
                pup.cage = _fk(Cage, cage_id) if cage_id else None
            pup.notes = notes
            pup.save()

    return redirect('index')


@login_required
def litter_delete(request, pk):
    litter = get_object_or_404(Litter, pk=pk)
    if request.method == 'POST':
        litter.delete()
    return redirect('index')


# ── Mouse history READONLY ────────────────────────────────────────────────────────────

@login_required
def mouse_history(request, pk):
    """
    Returns a JSON list of history events for a single mouse.
    Called by the front-end when the user clicks a mouse row.
    No Post - read only by design.
    """
    mouse = get_object_or_404(Mouse, pk=pk)
    events = mouse.history.select_related('cage', 'litter').order_by('date', 'created_at')

    data = []
    for e in events:
        data.append({
            'event': e.get_event_display(),
            'date': str(e.date),
            'cage': e.cage.cage_id if e.cage else '',
            'litter': str(e.litter.dob) if e.litter else '',
            'notes': e.notes,
        })

    return JsonResponse({'mouse': mouse.tag, 'history': data})

# ── Cage content READONLY ────────────────────────────────────────────────────────────

@login_required
def cage_animals(request, pk):
    """
    Returns a JSON list of every Mouse currently assigned to a cage.
    Called by the front-end when the user clicks a cage row.
    """

    cage = get_object_or_404(Cage, pk=pk)
    mice = cage.mice.select_related('owner', 'mouse_line', 'coat_color', 'litter').prefetch_related('genotype_entries__tag').order_by('sex', 'tag')

    data = []
    for m in mice:
        genotypes = [
            f"{mg.tag.label} ({mg.get_zygosity_display()})"
            #for mg in m.genotypes.select_related('genotype_entries').all()
            for mg in m.genotype_entries.all()
        ]
        data.append({
            'pk':                        str(m.pk),
            'tag':                       m.tag,
            'sex':                       m.get_sex_display() if m.sex else '-',
            'alt_id':                    m.alt_id or '-',
            'dob':                       str(m.dob) if m.dob else '-',
            'wean_date':  str(m.wean_date) if m.dob else '—',
            'mouse_line': str(m.mouse_line) if m.mouse_line else '—',
            'coat_color': str(m.coat_color) if m.coat_color else '—',
            'phenotype':  m.phenotype or '—',
            'genotypes':  ', '.join(genotypes) or '—',
            'owner':      m.owner.username if m.owner else '—',
            'protocol':   str(m.protocol) if m.protocol else '—',
            'litter':     str(m.litter.dob) if m.litter else '—',
        })

    return JsonResponse({
        'cage_id': cage.cage_id,
        'location': cage.cage_location or '',
        'animals': data,
    })

# __ Thermal Cage Label _____________________________________________________

@login_required
@require_GET
@xframe_options_exempt
def cage_label_pdf(request, pk):
    """Returns the raw 4x6in label PDF for one cage.
    Exempt from X-Frame-Options so print_label.html can embed it in an
    iframe (same-origin) to trigger the browser print dialog automatically."""
    cage = get_object_or_404(Cage, pk=pk)
    pdf_buffer = render_cage_label_pdf(cage)
    response = HttpResponse(pdf_buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="cage_{cage.cage_id}_label.pdf"'
    return response


@login_required
@require_GET
def cage_label_print(request, pk):
    """Opens a page that embeds the label PDF and auto-triggers the print dialog."""
    cage = get_object_or_404(Cage, pk=pk)
    return render(request, "colony/print_label.html", {"cage": cage})

# ── Utility ────────────────────────────────────────────────────────────────

def _fk(model, pk_str):
    if pk_str:
        return model.objects.filter(pk=pk_str).first()
    return None
