# Croissant Validation Notes

Validation date: 2026-05-24

## Files checked

- `docs/croissant/weather_raw_hohewarte_croissant.json`
- `data/raw/weather_raw_vienna_hohewarte_v1.csv`

## Commands

```bash
python -m json.tool docs/croissant/weather_raw_hohewarte_croissant.json
croissant docs/croissant
```

## Results

- JSON syntax check passed.
- The local `croissant docs/croissant` command exited with status 0 and produced no terminal output.
- The Croissant record declares 29 fields, matching the 29 columns in `data/raw/weather_raw_vienna_hohewarte_v1.csv` in the same order.
- The declared distribution path, byte size, and SHA-256 hash match the repository-local raw CSV.
- Licence is declared as CC BY 4.0 via `https://creativecommons.org/licenses/by/4.0/`.

## Notes

The Croissant record uses OM-2 unit URIs because T2.3 mapped repository and DBRepo units to OM-2. The assignment wording refers to unit URIs from T2.3; if the final grading expects QUDT specifically, the unit mapping and Croissant file should be aligned before submission.
