from django import forms

from .ml.predictor import get_config


def _choices(values):
    return [(v, v) for v in values]


class PredictionForm(forms.Form):
    """Raw clinical input form. Field names intentionally match the cleaned
    feature names from the notebook (via `to_raw_dict`) so they can be fed
    straight into `predict_chd`."""

    gender = forms.ChoiceField(
        label="Gender",
        choices=[('FEMENINO', 'Femenino'), ('MASCULINO', 'Masculino')],
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    weight_kg = forms.FloatField(
        label="Weight (KG)", min_value=0, max_value=200,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'e.g. 12'}),
    )
    height_cm = forms.FloatField(
        label="Height (CM)", min_value=0, max_value=250,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'e.g. 91.44'}),
    )
    heart_rate = forms.FloatField(
        label="Heart Rate (bpm)", min_value=0, max_value=300,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'placeholder': 'e.g. 120'}),
    )
    oxygen_saturation = forms.FloatField(
        label="Arterial Oxygen Saturation (%)", min_value=0, max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'e.g. 88'}),
    )
    age_months = forms.FloatField(
        label="Age at First Visit (months)", min_value=0, max_value=1200,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'e.g. 12'}),
    )
    systolic_bp = forms.FloatField(
        label="Systolic BP", min_value=0, max_value=300,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'placeholder': 'e.g. 120'}),
    )
    diastolic_bp = forms.FloatField(
        label="Diastolic BP", min_value=0, max_value=200,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'placeholder': 'e.g. 80'}),
    )
    primary_symptom = forms.ChoiceField(
        label="Primary Symptom",
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    secondary_symptoms = forms.ChoiceField(
        label="Secondary Symptoms",
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    murmur_type = forms.ChoiceField(
        label="Murmur Type",
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    murmur_grade = forms.ChoiceField(
        label="Murmur Grade",
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    murmur_zone = forms.ChoiceField(
        label="Murmur Zone",
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        options = get_config()['categorical_options']
        self.fields['primary_symptom'].choices = _choices(options['Primary Symptom'])
        self.fields['secondary_symptoms'].choices = _choices(options['Secondary Symptoms'])
        self.fields['murmur_type'].choices = _choices(options['Murmur Type'])
        self.fields['murmur_grade'].choices = _choices(options['Murmur Grade'])
        self.fields['murmur_zone'].choices = _choices(options['Murmur Zone'])

    def to_raw_dict(self):
        """Maps cleaned form data to the exact feature names the ML pipeline expects."""
        d = self.cleaned_data
        return {
            'Gender': d['gender'],
            'Weight (KG)': d['weight_kg'],
            'Height (CM)': d['height_cm'],
            'Heart Rate': d['heart_rate'],
            'Arterial Oxygen Saturation': d['oxygen_saturation'],
            'Age at First Visit (months)': d['age_months'],
            'Systolic BP': d['systolic_bp'],
            'Diastolic BP': d['diastolic_bp'],
            'Primary Symptom': d['primary_symptom'],
            'Secondary Symptoms': d['secondary_symptoms'],
            'Murmur Type': d['murmur_type'],
            'Murmur Grade': d['murmur_grade'],
            'Murmur Zone': d['murmur_zone'],
        }
