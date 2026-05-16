# Informe de Analisis: Admitidos y Graduados

## Hallazgos clave
- Registros analizados: **47,761** (se removieron 137 duplicados).
- Balance mediano admitidos/graduados por periodo: **1.03**.
- Prueba chi-cuadrado sexo-tipo: p-value=2.58e-49, Cramers V=0.068.
- Prueba chi-cuadrado estrato-tipo: p-value=1.217e-34, Cramers V=0.060.
- z-test proporcion femenina: p-value=0, Cohen h=-0.136.
- Mann-Whitney edad: p-value=0, correlacion biserial de rangos=-0.310.

## Segmentacion prioritaria
Top facultades por volumen:

```text
                                       facultad      tipo  volumen
FACULTAD DE CIENCIAS EMPRESARIALES Y ECONOMICAS ADMITIDOS     9115
            CIENCIAS EMPRESARIALES Y ECONOMICAS GRADUADOS     6413
                         FACULTAD DE INGENIERIA ADMITIDOS     5515
                         FACULTAD DE INGENIERIA GRADUADOS     4765
               FACULTAD DE CIENCIAS DE LA SALUD ADMITIDOS     4042
```

Top programas por volumen (muestra):

```text
                                                                                  programa      tipo  volumen
                                                                    PROFESIONAL EN DEPORTE ADMITIDOS     2149
                                    TECNICO PROFESIONAL EN PREVENCION DE RIESGOS LABORALES ADMITIDOS     1974
                                            LICENCIATURA EN LITERATURA Y LENGUA CASTELLANA ADMITIDOS     1465
LICENCIATURA EN EDUCACION BASICA CON ENFASIS EN FACULTAD DE HUMANIDADES- LENGUA CASTELLANA GRADUADOS     1129
                                                                                   DERECHO GRADUADOS     1086
                                                                        CONTADURIA PUBLICA ADMITIDOS     1059
```

## Recomendaciones ejecutivas
- Fortalecer seguimiento de cohortes con bajo ratio graduados/admitidos.
- Focalizar estrategias de permanencia en segmentos con brechas demograficas detectadas.
- Establecer tablero de monitoreo semestral para reaccion temprana por programa.

## Decisiones metodologicas
- La edad se calcula con fecha de referencia fija **2024-12-31** para asegurar reproducibilidad entre ejecuciones.
- Se reporta tamano de efecto en todas las pruebas inferenciales: Cramers V (chi-cuadrado), Cohen h (z-test de proporciones) y correlacion biserial de rangos (Mann-Whitney).

## Limitaciones
- El dataset no incluye variables de rendimiento academico individual.
- La referencia fija de edad no sustituye edad exacta al momento de ingreso/egreso historico.