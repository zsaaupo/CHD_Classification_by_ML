from django.db import models


class PredictionResult(models.Model):
    """Stores one form submission + the model's prediction, so it can be
    shown on the dashboard and revisited later from the history table."""

    class Gender(models.TextChoices):
        FEMALE = 'FEMENINO', 'Femenino'
        MALE = 'MASCULINO', 'Masculino'

    class CHDClass(models.TextChoices):
        VSD = 'VSD', 'VSD (Ventricular Septal Defect)'
        ASD = 'ASD', 'ASD (Atrial Septal Defect)'
        PDA = 'PDA', 'PDA (Patent Ductus Arteriosus)'

    # ── Raw input fields (mirrors the notebook's cleaned feature set) ──
    gender = models.CharField(max_length=20, choices=Gender.choices)
    weight_kg = models.FloatField(help_text="Weight in kilograms")
    height_cm = models.FloatField(help_text="Height in centimeters")
    heart_rate = models.FloatField(help_text="Beats per minute")
    oxygen_saturation = models.FloatField(help_text="Arterial O2 saturation (%)")
    age_months = models.FloatField(help_text="Age at first visit, in months")
    systolic_bp = models.FloatField()
    diastolic_bp = models.FloatField()
    primary_symptom = models.CharField(max_length=100)
    secondary_symptoms = models.CharField(max_length=100)
    murmur_type = models.CharField(max_length=50)
    murmur_grade = models.CharField(max_length=20)
    murmur_zone = models.CharField(max_length=150)

    # ── Prediction output ──
    predicted_class = models.CharField(max_length=10, choices=CHDClass.choices)
    probability_asd = models.FloatField(default=0.0)
    probability_pda = models.FloatField(default=0.0)
    probability_vsd = models.FloatField(default=0.0)
    confidence = models.FloatField(help_text="Probability of the predicted class (0-1)")
    recommendation = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.pk} - {self.predicted_class} ({self.confidence:.0%}) - {self.created_at:%Y-%m-%d %H:%M}"

    @property
    def confidence_pct(self):
        return round(self.confidence * 100, 1)

    @property
    def probability_breakdown(self):
        return {
            'ASD': round(self.probability_asd * 100, 1),
            'PDA': round(self.probability_pda * 100, 1),
            'VSD': round(self.probability_vsd * 100, 1),
        }
