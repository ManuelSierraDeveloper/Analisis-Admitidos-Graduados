# Probando tecnologias nuevas: Python + Streamlit

Hoy publico un proyecto de analisis de datos enfocado en admitidos y graduados, construido con **Python** y desplegado como dashboard con **Streamlit**.

## Lo mas importante del proyecto

- Pipeline reproducible de analisis (`analysis_pipeline.py`)
- Dashboard interactivo (`app.py`)
- Informe tecnico ejecutivo (`outputs/informe_analisis.md`)
- Verificacion metodologica y tecnica (`docs/VERIFICATION_REPORT.md`)

## Hallazgos de referencia

- Registros finales limpios: **47,761**
- Duplicados removidos: **137**
- Evidencia inferencial significativa en variables clave
- Reproducibilidad validada con hashes identicos entre corridas

## Como ejecutarlo

```bash
pip install -r requirements.txt
python analysis_pipeline.py
streamlit run app.py
```

## Despliegue

En el `README.md` deje un paso a paso completo para desplegar en Streamlit Community Cloud.

---

Si quieres, te comparto una segunda version con enfoque en storytelling para portafolio o para presentacion ejecutiva.
