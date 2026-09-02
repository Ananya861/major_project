# Crop recommendation dataset

## Source

File: `crop_recommendation.csv`

This is the widely used **Crop Recommendation Dataset** originally published on Kaggle by Atharva Ingle:

- Kaggle: https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset
- Public GitHub mirror used for this clone (Harvestify, processed CSV):  
  https://github.com/Gladiator07/Harvestify/blob/master/Data-processed/crop_recommendation.csv  
  Raw: https://raw.githubusercontent.com/Gladiator07/Harvestify/master/Data-processed/crop_recommendation.csv

The CSV was copied unchanged (2,200 labeled rows). No synthetic rows were added.

## Features (columns)

| Column | Type | Meaning |
|---|---|---|
| `N` | numeric | Soil nitrogen content |
| `P` | numeric | Soil phosphorus content |
| `K` | numeric | Soil potassium content |
| `temperature` | numeric | Temperature (°C) |
| `humidity` | numeric | Relative humidity (%) |
| `ph` | numeric | Soil pH |
| `rainfall` | numeric | Rainfall (mm) |
| `label` | categorical | Crop name (classification target) |

There are **22 crop classes** (100 samples each), including rice, maize, chickpea, kidneybeans, pigeonpeas, mothbeans, mungbean, blackgram, lentil, pomegranate, banana, mango, grapes, watermelon, muskmelon, apple, orange, coconut, cotton, jute, and coffee.

## Target variable

`label` — the crop recommended for those soil and climate conditions. This is a **multi-class classification** problem.

## Compatibility with this API (important)

The FastAPI soil payload includes extra fields that **are not in this dataset**:

| API field (`SoilData` / farm) | In dataset? | How inference uses it |
|---|---|---|
| `nitrogen` | Yes, as `N` | Mapped to `N` |
| `phosphorus` | Yes, as `P` | Mapped to `P` |
| `potassium` | Yes, as `K` | Mapped to `K` |
| `ph` | Yes | Mapped to `ph` |
| `temperature` / weather `temp` | Yes | Mapped to `temperature` when weather is available |
| weather `humidity` | Yes | Mapped to `humidity` |
| weather `rainfall` | Yes | Mapped to `rainfall` |
| `moisture` | **No** | Not a training column. If weather humidity is missing, moisture is used as a **humidity proxy** at inference only (same 0–100 scale). Documented fallback, not a fabricated training feature. |
| `soil_type` | **No** | **Ignored by the model.** Do not invent soil-type labels for training. |

Weather (`temperature`, `humidity`, `rainfall`) comes from the existing OpenWeatherMap integration at request time, not from made-up climate rows.

## Limitations

- Climate features in training are historical dataset values, not live weather.
- `moisture` and `soil_type` cannot be learned from this file without fabricating data, which we do not do.
- Crop names (e.g. `rice`) may not all exist in the seeded `crop` table (Wheat, Rice, Tomato, Onion, Cotton). The existing API already returns `crop_id=null` for unknown names.
- This dataset is an educational agronomic sample, not a farm-specific survey of Indian mandis.

## License / usage

The Kaggle listing does not attach a machine-readable SPDX license in the CSV itself. The Harvestify project that redistributes the same processed file is MIT-licensed (see that repository). Use is intended for **academic / non-commercial coursework**. Re-download from Kaggle if you need the platform’s current license terms.
