# meineschule-digital

Unofficial Python client for MeineSchule.digital.

> [!WARNING]
> This project is unofficial and is not affiliated with or endorsed by
> MeineSchule.digital or RHC Software.

## Status

Early development / reverse engineering.

Currently investigated:

- Authentication
- School selection
- Student discovery
- Home.InfoPoint
- Grades
- Absences
- Remarks
- Homework

## Installation

Development installation:

    python -m venv .venv
    source .venv/bin/activate
    pip install -e ".[test]"

## Security and privacy

Do not commit credentials, authentication cookies, HAR files, or HTML
responses containing personal or student data.

## License

MIT

## Local example

Install the package and the optional dependency for the local example:

    pip install -e ".[test]"
    pip install python-dotenv

Copy `.env.example` to `.env` and set `MSD_USERNAME`, `MSD_PASSWORD` and
`MSD_SCHOOL`. The school value is the URL slug, for example
`salza-gymnasium`. Optionally set `MSD_EXCLUDED_SUBJECTS` to comma-separated
subject codes that the student does not attend. The `.env` file is ignored by
Git.

Run:

    python examples/read_home_info.py

The example prints counts only and does not display student records.

## Homework dates

`get_homework(school_slug, from_date, until_date, excluded_subjects=...)`
returns homework entries with an assignment date, subject, text, due date and
`due_date_source`:

- `explicit`: a date was written as `zum DD.MM.YYYY` in the homework text.
- `schedule`: the next non-cancelled lesson of that subject was found in
  successfully retrieved schedule weeks.
- `unknown`: no reliable date could be determined within the requested weeks.

`from_date` filters by the day the homework was assigned. `until_date` is the
last week searched for a lesson; it does not override explicit due dates.
