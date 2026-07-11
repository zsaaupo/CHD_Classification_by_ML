# CHD Classifier — Django App: [**LIVE**](https://chd-classification-by-ml.onrender.com/)

A Django 5 application that uses the **Logistic Regression** model from your
`Copy_of_Final_CHD_Classification.ipynb` thesis notebook to predict a
congenital heart disease subtype — **VSD**, **ASD**, or **PDA** — from a
clinical intake form, stores every prediction in SQLite, and shows a
dashboard with stats, charts, and history.

> ⚠️ **Not a medical device.** This is a research/educational tool. Predictions
> are shown with a disclaimer and should never replace evaluation by a
> qualified pediatric cardiologist.

---

## 1. What's included

```
chd_predictor/
├── manage.py
├── requirements.txt              # runtime deps (Django + inference)
├── requirements-training.txt     # extra deps only needed to retrain
├── chd_predictor/                # project settings/urls
├── predictor/                    # the app
│   ├── models.py                 # PredictionResult (saved to SQLite)
│   ├── forms.py                  # the intake form (choices loaded from encoding_config.json)
│   ├── views.py                  # dashboard, predict, result, history
│   ├── ml/
│   │   ├── predictor.py          # loads the model & runs inference
│   │   └── artifacts/            # ← the exported model files (already included)
│   │       ├── lr_model.joblib
│   │       ├── scaler.joblib
│   │       ├── label_encoder.joblib
│   │       ├── encoding_config.json
│   │       └── metrics.json
│   ├── templates/predictor/      # Bootstrap 5 templates
└── static/predictor/css       # custom styling and favicon

```

**The model is already trained and exported** — the artifacts in
`predictor/ml/artifacts/` are ready to use. You do **not** need to run the
notebook or the training script to use the app. They're included in case you
want to retrain later (e.g. with more data).

---

## 2. How the ML pipeline was carried over

Your notebook trains 4 models on an encoded feature matrix built from the
cleaned `DB1_cleaned_SOPLO.csv`. `training/train_lr.py` reproduces **exactly**
the same steps used for the Logistic Regression model:

1. Select & rename the same 10 raw columns, map ICD-10 codes to `VSD/ASD/PDA`.
2. Parse age strings → months, split blood pressure → systolic/diastolic,
   parse the free-text murmur field → type/grade/zone.
3. Impute missing values (median for most numerics, mean for weight/height,
   mode for categoricals) — the exact fitted values are saved to
   `encoding_config.json` so the Django form can't silently drift from what
   the model expects.
4. Encode: Gender (binary), Murmur Grade (ordinal), Primary Symptom / Murmur
   Type (full one-hot), Secondary Symptoms / Murmur Zone (top-N one-hot + an
   `_Other` bucket) — **the exact categories learned from your training split
   are saved and reused at inference time.**
5. Balance the training split with SMOTE, scale with `StandardScaler`, fit
   `LogisticRegression(class_weight='balanced')`.

`predictor/ml/predictor.py` re-implements steps 1 file's worth of encoding
logic for a **single form submission**, using the saved `encoding_config.json`
so a user's dropdown selection is encoded into the exact 46-column layout the
model expects, then scaled and passed to the model.

Test-set performance on your data (see `predictor/ml/artifacts/metrics.json`):
**~86% accuracy, ~0.95 macro ROC-AUC** for the LR model.

### If you retrain later
```bash
pip install -r requirements.txt -r requirements-training.txt
cd training
python train_lr.py
# copy the new artifacts over the old ones:
cp artifacts/*.joblib artifacts/*.json ../predictor/ml/artifacts/
```

---

## 3. Setup & run locally

**Requirements:** Python 3.12+

```bash
# 1. Create & activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply database migrations
python manage.py migrate

# 4. (Optional) create an admin user to browse /admin/
python manage.py createsuperuser

# 5. Run the dev server
python manage.py runserver
```

Open **http://127.0.0.1:8000/** — you'll land on the Dashboard.

- **Dashboard** (`/`) — stat cards, class/time charts, prediction history table.
- **Predict Heart Disease** (`/predict/`) — the intake form.
- **Result page** (`/result/<id>/`) — shown right after a prediction.
- **History detail** (`/history/<id>/`) — same layout, reached from the dashboard table.
- **Admin** (`/admin/`) — read-only browsing of saved predictions (after creating a superuser).

---

## 4. About the prediction output

The app reports the model's predicted CHD class, confidence, and probability
breakdown for **VSD**, **ASD**, and **PDA**. It no longer computes or displays
a separate risk level.

The **Recommendation** text is templated per predicted class in
`build_recommendation` in `predictor/ml/predictor.py`, and always ends with a
disclaimer to consult a qualified pediatric cardiologist. You can edit that
text in the same file to match your thesis's clinical framing.

---

## 5. Notes on the frontend

- Bootstrap 5 + Bootstrap Icons + Chart.js are loaded via CDN
  (`jsdelivr.net`) — an internet connection is needed the first time your
  browser loads the page (it'll be cached after that). If you need a fully
  offline setup, download the Bootstrap/Chart.js files into
  `predictor/static/predictor/vendor/` and update the `<script>`/`<link>`
  tags in `predictor/templates/predictor/base.html`.
- Class colors: VSD = blue, ASD = teal, PDA = amber.

---

## 6. Known limitations to mention in your thesis write-up

- Trained on a small dataset (350 raw rows → a few hundred after filtering to
  the 3 target classes), so generalization outside this hospital's patient
  population is unproven.
- The "top-N + Other" one-hot encoding for `Secondary Symptoms` and `Murmur
  Zone` means rare/unseen categories at inference time are bucketed into
  `_Other`, same as they were during training's test split.
- SMOTE was applied only to the training split (as in the notebook); the
  Django app performs single-row inference, so SMOTE never runs at request
  time — only during `train_lr.py`.
