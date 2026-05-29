### musculus
Musculus is a python Django framework based interface for mice colony management.

### Setup

1. Clone the repo
2. Create a virtual environment: `python -m venv venv && source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and fill in values
5. Run migrations: `python manage.py migrate`
6. Create a superuser: `python manage.py createsuperuser`
7. Run: `python manage.py runserver`

### Structure

```bash
musculus/
├── settings/
│   ├── settings.py
│   └── urls.py
├── colony/
│   ├── models.py        (Mouse, CoatColor, Protocol, MatingPair)
│   ├── admin.py         (MatingPairAdmin with sex filtering, is_active display)
│   └── urls.py
├── templates/
│   └── registration/
│       └── login.html
└── manage.py
```

### Method
Full path of the model.py method walk:

```bash
self                          ← the new mouse (pup)
  .litter                     ← ForeignKey to Litter
    .mating_pair              ← ForeignKey to MatingPair
      .male                   ← ForeignKey to Mouse (the father)
        .genotype_entries     ← reverse relation to MouseGenotype rows
          .filter(zygosity="HOM")
          .values_list("tag_id", flat=True)
```
