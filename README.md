# Streamlit-App: Kosten des Klimawandels vs. Klimaschutz

Diese kleine Streamlit-App visualisiert eine harmonisierte Auswahl von Studien seit dem Stern Review (2006), die Klimaschäden bzw. Kosten von Klimaschutz/Dekarbonisierung quantifizieren.

## Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Dateien

- `app.py`: Streamlit-App mit eingebetteten Daten und Plotly-Grafik
- `climate_costs_chart_data.csv`: dieselben Daten als CSV
- `requirements.txt`: benötigte Python-Pakete

## Hinweis zur Interpretation

Die Werte sind bewusst als **Grössenordnungen** visualisiert. Sie stammen aus Studien mit unterschiedlichen Methoden, Kostenbegriffen und Zeithorizonten. Für eine Buchgrafik sollte in der Bildunterschrift klargestellt werden, dass GDP-, Konsum-, Einkommens- und Welfare-Verluste nicht vollständig identisch sind und dass Investitionsvolumina der Transformation nicht automatisch Netto-Kosten darstellen.
