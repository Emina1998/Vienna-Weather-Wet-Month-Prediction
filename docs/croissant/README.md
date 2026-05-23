# Croissant Metadata

This directory contains the T3.4 Croissant JSON-LD metadata for the original raw input weather dataset used by the FAIR Vienna Wet Month Prediction experiment.

- Metadata file: `weather_raw_hohewarte_croissant.json`
- Described input data: `data/raw/weather_raw_vienna_hohewarte_v1.csv`
- Source: Stadt Wien via data.gv.at
- Licence: CC BY 4.0

The Croissant record describes the raw CSV fields, data types, OM-2 unit URIs, source/distribution information, and known missing-value notes. It describes the original raw input dataset only, not DBRepo-derived tables, trained models, predictions, figures, or other generated outputs.

Validate JSON syntax with:

```bash
python -m json.tool docs/croissant/weather_raw_hohewarte_croissant.json
```
