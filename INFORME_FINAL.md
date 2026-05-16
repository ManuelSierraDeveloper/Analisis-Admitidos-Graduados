# Informe Final - Analisis de Admitidos y Graduados (UNIMAG)

## Resumen ejecutivo

- Registros analizados: **47,761** (tras remover 137 duplicados).
- Balance mediano admitidos/graduados por periodo: **1.03**.
- Se evidencian diferencias estadisticamente significativas por sexo y estrato frente al tipo de registro (admitido/graduado).
- El flujo analitico fue validado como **reproducible** con hashes identicos en corridas consecutivas.

## Resultados inferenciales principales

- Chi-cuadrado `sexo` vs `tipo`: `p=2.58e-49`, Cramers V=`0.068`.
- Chi-cuadrado `estrato` vs `tipo`: `p=1.217e-34`, Cramers V=`0.060`.
- Z-test proporcion femenina (admitidos vs graduados): `p=0`, Cohen h=`-0.136`.
- Mann-Whitney edad (admitidos vs graduados): `p=0`, correlacion biserial de rangos=`-0.310`.

## Visualizaciones clave

### Tendencia temporal

![Tendencia temporal](assets/images/tendencia_temporal.png)

### Segmentacion por facultad y tipo

![Heatmap facultad tipo](assets/images/heatmap_facultad_tipo.png)

### Brecha por sexo

![Brecha por sexo](assets/images/brecha_sexo.png)

## Recomendaciones para decision directiva

1. Priorizar seguimiento de cohortes con menor conversion de admitidos a graduados por programa.
2. Diseñar estrategias de permanencia focalizadas en segmentos con brechas demograficas.
3. Institucionalizar monitoreo semestral con el dashboard para reaccion temprana.

## Soporte tecnico


- Dashboard: `app.py`
