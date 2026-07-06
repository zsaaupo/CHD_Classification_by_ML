import json
from collections import Counter

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import PredictionForm
from .ml.predictor import predict_chd
from .models import PredictionResult


def dashboard(request):
    qs = PredictionResult.objects.all()
    total = qs.count()

    class_counts = dict(qs.values_list('predicted_class').annotate(c=Count('id')))
    for cls in ['VSD', 'ASD', 'PDA']:
        class_counts.setdefault(cls, 0)

    avg_confidence = qs.aggregate(avg=Avg('confidence'))['avg'] or 0

    most_common_class = max(class_counts, key=class_counts.get) if total else '—'

    # Predictions over time (by date, most recent 14 days that have data)
    history_qs = qs.order_by('-created_at')[:200]
    date_counter = Counter(p.created_at.strftime('%Y-%m-%d') for p in history_qs)
    date_labels = sorted(date_counter.keys())[-14:]
    date_series = [date_counter[d] for d in date_labels]

    page_number = request.GET.get('page', 1)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(page_number)

    context = {
        'total': total,
        'class_counts': class_counts,
        'avg_confidence_pct': round(avg_confidence * 100, 1),
        'most_common_class': most_common_class,
        'page_obj': page_obj,
        'chart_class_labels': json.dumps(['VSD', 'ASD', 'PDA']),
        'chart_class_data': json.dumps([class_counts['VSD'], class_counts['ASD'], class_counts['PDA']]),
        'chart_date_labels': json.dumps(date_labels),
        'chart_date_data': json.dumps(date_series),
    }
    return render(request, 'predictor/dashboard.html', context)


def predict_form(request):
    if request.method == 'POST':
        form = PredictionForm(request.POST)
        if form.is_valid():
            raw = form.to_raw_dict()
            result = predict_chd(raw)

            record = PredictionResult.objects.create(
                gender=raw['Gender'],
                weight_kg=raw['Weight (KG)'],
                height_cm=raw['Height (CM)'],
                heart_rate=raw['Heart Rate'],
                oxygen_saturation=raw['Arterial Oxygen Saturation'],
                age_months=raw['Age at First Visit (months)'],
                systolic_bp=raw['Systolic BP'],
                diastolic_bp=raw['Diastolic BP'],
                primary_symptom=raw['Primary Symptom'],
                secondary_symptoms=raw['Secondary Symptoms'],
                murmur_type=raw['Murmur Type'],
                murmur_grade=raw['Murmur Grade'],
                murmur_zone=raw['Murmur Zone'],
                predicted_class=result['predicted_class'],
                probability_asd=result['probabilities'].get('ASD', 0.0),
                probability_pda=result['probabilities'].get('PDA', 0.0),
                probability_vsd=result['probabilities'].get('VSD', 0.0),
                confidence=result['confidence'],
                recommendation=result['recommendation'],
            )
            return redirect(reverse('predictor:result', args=[record.pk]))
        messages.error(request, "Please correct the errors below.")
    else:
        form = PredictionForm()

    return render(request, 'predictor/predict_form.html', {'form': form})


def result_view(request, pk):
    record = get_object_or_404(PredictionResult, pk=pk)
    breakdown = record.probability_breakdown
    context = {
        'record': record,
        'chart_labels': json.dumps(list(breakdown.keys())),
        'chart_data': json.dumps(list(breakdown.values())),
        'is_history': False,
    }
    return render(request, 'predictor/result.html', context)


def history_detail(request, pk):
    record = get_object_or_404(PredictionResult, pk=pk)
    breakdown = record.probability_breakdown
    context = {
        'record': record,
        'chart_labels': json.dumps(list(breakdown.keys())),
        'chart_data': json.dumps(list(breakdown.values())),
        'is_history': True,
    }
    return render(request, 'predictor/result.html', context)
