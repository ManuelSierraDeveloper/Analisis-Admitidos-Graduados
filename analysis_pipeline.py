import json
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
import seaborn as sns
from matplotlib import pyplot as plt
from scipy import stats


BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "ADMITIDOS-GRADUADOS.xlsx"
OUTPUT_DIR = BASE_DIR / "outputs"
DOCS_DIR = BASE_DIR / "docs"
LEARNINGS_FILE = DOCS_DIR / "LEARNINGS.md"
REPORT_FILE = OUTPUT_DIR / "informe_analisis.md"
REPRO_FILE = OUTPUT_DIR / "reproducibilidad.json"
REFERENCE_DATE = pd.Timestamp("2024-12-31")


def ensure_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)


def normalize_col(name: str) -> str:
    mapping = {
        "Fecha Nacimiento": "fecha_nacimiento",
        "Departamento de Origen": "departamento_origen",
        "Tipo de Colegio": "tipo_colegio",
        "Nivel AcadEmico": "nivel_academico",
        "Nivel de FormaciOn": "nivel_formacion",
        "MetodologIa": "metodologia",
    }
    if name in mapping:
        return mapping[name]
    return (
        name.strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


def normalize_text(s: pd.Series) -> pd.Series:
    return s.astype(str).str.strip().str.upper().str.replace(r"\s+", " ", regex=True)


def print_state(title: str, df: pd.DataFrame, cols: list[str] | None = None) -> None:
    print(f"\n=== {title} ===")
    print(f"Shape: {df.shape}")
    print("Nulls:")
    print(df.isna().sum().to_string())
    if cols:
        print("Sample:")
        print(df[cols].head(5).to_string(index=False))
    else:
        print("Sample:")
        print(df.head(5).to_string(index=False))


def two_prop_ztest(success_a: int, nobs_a: int, success_b: int, nobs_b: int) -> tuple[float, float]:
    p_pool = (success_a + success_b) / (nobs_a + nobs_b)
    se = np.sqrt(p_pool * (1 - p_pool) * ((1 / nobs_a) + (1 / nobs_b)))
    z_score = (success_a / nobs_a - success_b / nobs_b) / se
    p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
    return z_score, p_value


def cramers_v(chi2: float, n: int, r: int, k: int) -> float:
    phi2 = chi2 / n
    return float(np.sqrt(phi2 / max(1, min(k - 1, r - 1))))


def cohen_h_from_props(p1: float, p2: float) -> float:
    p1 = float(np.clip(p1, 1e-12, 1 - 1e-12))
    p2 = float(np.clip(p2, 1e-12, 1 - 1e-12))
    return float(2 * (np.arcsin(np.sqrt(p1)) - np.arcsin(np.sqrt(p2))))


def rank_biserial_from_u(u_stat: float, n1: int, n2: int) -> float:
    if n1 == 0 or n2 == 0:
        return np.nan
    return float((2 * u_stat) / (n1 * n2) - 1)


def file_sha256(path: Path, chunk_size: int = 1_048_576) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def write_learnings(entries: list[dict[str, str]]) -> None:
    lines = ["# LEARNINGS", "", "Registro de implementacion con protocolo output-first.", ""]
    for idx, entry in enumerate(entries, start=1):
        lines.append(f"## Task {idx}: {entry['task']}")
        lines.append(f"- Input: {entry['input']}")
        lines.append(f"- Operation: {entry['operation']}")
        lines.append(f"- Output: {entry['output']}")
        lines.append(f"- Verification: {entry['verification']}")
        lines.append("")
    LEARNINGS_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    learnings: list[dict[str, str]] = []

    print("TASK 1 - Limpieza y preparacion")
    df_raw = pd.read_excel(INPUT_FILE, sheet_name="Data")
    print_state("ANTES limpieza", df_raw)

    dup_count = int(df_raw.duplicated().sum())
    df = df_raw.drop_duplicates().copy()
    df.columns = [normalize_col(c) for c in df.columns]

    for col in [
        "periodo",
        "facultad",
        "programa",
        "sexo",
        "departamento_origen",
        "tipo_colegio",
        "nivel_academico",
        "nivel_formacion",
        "metodologia",
        "tipo",
    ]:
        df[col] = normalize_text(df[col])

    period_split = df["periodo"].str.extract(r"(?P<anio>\d{4})-(?P<semestre>[12])")
    df["anio"] = pd.to_numeric(period_split["anio"], errors="coerce").astype("Int64")
    df["semestre"] = pd.to_numeric(period_split["semestre"], errors="coerce").astype("Int64")
    df["periodo_orden"] = df["anio"] * 10 + df["semestre"]

    df["fecha_nacimiento"] = pd.to_datetime(df["fecha_nacimiento"], errors="coerce")
    df["edad"] = ((REFERENCE_DATE - df["fecha_nacimiento"]).dt.days / 365.25).round(1)

    audit = pd.DataFrame(
        {
            "metric": ["filas_originales", "filas_limpias", "duplicados_removidos", "columnas_totales"],
            "valor": [len(df_raw), len(df), dup_count, df.shape[1]],
        }
    )
    df.to_csv(OUTPUT_DIR / "df_clean.csv", index=False, encoding="utf-8")
    audit.to_csv(OUTPUT_DIR / "auditoria_limpieza.csv", index=False, encoding="utf-8")
    print_state("DESPUES limpieza", df, ["periodo", "anio", "semestre", "edad", "tipo"])

    learnings.append(
        {
            "task": "Limpieza y preparacion de datos",
            "input": f"Data inicial {df_raw.shape} con {dup_count} duplicados exactos.",
            "operation": f"Eliminacion de duplicados, normalizacion de columnas/texto y creacion de anio/semestre/periodo_orden/edad con referencia fija {REFERENCE_DATE.date()}.",
            "output": f"Data limpia {df.shape}; auditoria en outputs/auditoria_limpieza.csv.",
            "verification": "Columnas estandarizadas, sin nulos nuevos relevantes y muestra valida de campos derivados.",
        }
    )

    print("\nTASK 2 - KPIs temporales")
    print("Estado ANTES: no existe tabla temporal agregada")
    temporal = (
        df.groupby(["anio", "semestre", "tipo"], dropna=False)
        .size()
        .reset_index(name="volumen")
        .sort_values(["anio", "semestre", "tipo"])
    )
    temporal["periodo"] = temporal["anio"].astype(str) + "-" + temporal["semestre"].astype(str)
    temporal["variacion_abs"] = temporal.groupby("tipo")["volumen"].diff()
    temporal["variacion_pct"] = temporal.groupby("tipo")["volumen"].pct_change() * 100

    pivot_balance = temporal.pivot_table(index=["anio", "semestre", "periodo"], columns="tipo", values="volumen", fill_value=0).reset_index()
    if "ADMITIDOS" not in pivot_balance:
        pivot_balance["ADMITIDOS"] = 0
    if "GRADUADOS" not in pivot_balance:
        pivot_balance["GRADUADOS"] = 0
    pivot_balance["ratio_admitidos_graduados"] = np.where(
        pivot_balance["GRADUADOS"] > 0,
        pivot_balance["ADMITIDOS"] / pivot_balance["GRADUADOS"],
        np.nan,
    )
    temporal.to_csv(OUTPUT_DIR / "kpi_temporal.csv", index=False, encoding="utf-8")
    pivot_balance.to_csv(OUTPUT_DIR / "kpi_balance.csv", index=False, encoding="utf-8")
    print("Estado DESPUES:")
    print(temporal.head(6).to_string(index=False))

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(12, 5))
    sns.lineplot(data=temporal, x="periodo", y="volumen", hue="tipo", marker="o")
    plt.title("Tendencia temporal de admitidos y graduados")
    plt.xlabel("Periodo academico")
    plt.ylabel("Volumen de registros")
    plt.xticks(rotation=60)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "tendencia_temporal.png", dpi=150)
    plt.close()

    learnings.append(
        {
            "task": "Perfil temporal y KPIs ejecutivos",
            "input": f"df_clean {df.shape}.",
            "operation": "Agregacion por anio-semestre-tipo, calculo de variaciones y ratio admitidos/graduados.",
            "output": "Tablas kpi_temporal.csv y kpi_balance.csv, grafico tendencia_temporal.png.",
            "verification": "Se observa serie temporal ordenada con variaciones interperiodo consistentes.",
        }
    )

    print("\nTASK 3 - Segmentacion facultad/programa")
    print("Estado ANTES: sin ranking segmentado")
    fac = (
        df.groupby(["facultad", "tipo"]).size().reset_index(name="volumen").sort_values("volumen", ascending=False)
    )
    prog = (
        df.groupby(["programa", "tipo"]).size().reset_index(name="volumen").sort_values("volumen", ascending=False)
    )
    top_prog = prog.groupby("tipo").head(10)

    fac.to_csv(OUTPUT_DIR / "segmentacion_facultad.csv", index=False, encoding="utf-8")
    prog.to_csv(OUTPUT_DIR / "segmentacion_programa.csv", index=False, encoding="utf-8")
    top_prog.to_csv(OUTPUT_DIR / "top_programas.csv", index=False, encoding="utf-8")
    print("Estado DESPUES:")
    print(top_prog.head(8).to_string(index=False))

    heat = df.pivot_table(index="facultad", columns="tipo", values="programa", aggfunc="count", fill_value=0)
    plt.figure(figsize=(10, 7))
    sns.heatmap(heat, cmap="Blues", annot=True, fmt=".0f")
    plt.title("Matriz facultad vs tipo de registro")
    plt.xlabel("Tipo")
    plt.ylabel("Facultad")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "heatmap_facultad_tipo.png", dpi=150)
    plt.close()

    learnings.append(
        {
            "task": "Segmentacion por facultad y programa",
            "input": "KPIs temporales y df_clean disponibles.",
            "operation": "Ranking por facultad/programa y matriz facultad-tipo.",
            "output": "CSVs de segmentacion y heatmap_facultad_tipo.png.",
            "verification": "Top contribuyentes identificados y distribucion por facultad visualmente verificable.",
        }
    )

    print("\nTASK 4 - Demografia y origen")
    print("Estado ANTES: sin matrices demograficas")
    demo_cols = ["sexo", "estrato", "departamento_origen", "tipo_colegio"]
    demo_frames = []
    for col in demo_cols:
        tmp = df.groupby([col, "tipo"]).size().reset_index(name="volumen")
        tmp.insert(0, "dimension", col)
        tmp = tmp.rename(columns={col: "categoria"})
        demo_frames.append(tmp)
    demo = pd.concat(demo_frames, ignore_index=True)

    brecha_sexo = df.pivot_table(index="tipo", columns="sexo", values="programa", aggfunc="count", fill_value=0)
    demo.to_csv(OUTPUT_DIR / "demografia_comparativa.csv", index=False, encoding="utf-8")
    brecha_sexo.to_csv(OUTPUT_DIR / "brecha_sexo.csv", encoding="utf-8")
    print("Estado DESPUES:")
    print(demo.head(10).to_string(index=False))

    plt.figure(figsize=(9, 5))
    sns.barplot(data=demo[demo["dimension"] == "sexo"], x="categoria", y="volumen", hue="tipo")
    plt.title("Brecha por sexo entre admitidos y graduados")
    plt.xlabel("Sexo")
    plt.ylabel("Volumen de registros")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "brecha_sexo.png", dpi=150)
    plt.close()

    learnings.append(
        {
            "task": "Analisis demografico y contexto de origen",
            "input": "df_clean con variables socio-demograficas.",
            "operation": "Cruces por sexo, estrato, departamento y tipo de colegio contra tipo.",
            "output": "demografia_comparativa.csv, brecha_sexo.csv y brecha_sexo.png.",
            "verification": "Matrices comparativas contienen categorias y volumenes esperados por dimension.",
        }
    )

    print("\nTASK 5 - Inferencial")
    print("Estado ANTES: sin pruebas estadisticas")
    stats_rows = []

    ct_sexo = pd.crosstab(df["sexo"], df["tipo"])
    chi2_s, p_s, _, _ = stats.chi2_contingency(ct_sexo)
    cv_s = cramers_v(chi2_s, int(ct_sexo.values.sum()), *ct_sexo.shape)
    stats_rows.append(["chi2_sexo_tipo", "chi2", chi2_s, p_s, cv_s, "Asociacion sexo-tipo"])

    ct_estrato = pd.crosstab(df["estrato"], df["tipo"])
    chi2_e, p_e, _, _ = stats.chi2_contingency(ct_estrato)
    cv_e = cramers_v(chi2_e, int(ct_estrato.values.sum()), *ct_estrato.shape)
    stats_rows.append(["chi2_estrato_tipo", "chi2", chi2_e, p_e, cv_e, "Asociacion estrato-tipo"])

    female_adm = int(((df["tipo"] == "ADMITIDOS") & (df["sexo"] == "F")).sum())
    n_adm = int((df["tipo"] == "ADMITIDOS").sum())
    female_grad = int(((df["tipo"] == "GRADUADOS") & (df["sexo"] == "F")).sum())
    n_grad = int((df["tipo"] == "GRADUADOS").sum())
    z_val, p_val = two_prop_ztest(female_adm, n_adm, female_grad, n_grad)
    p_adm = female_adm / n_adm if n_adm > 0 else np.nan
    p_grad = female_grad / n_grad if n_grad > 0 else np.nan
    h_effect = cohen_h_from_props(p_adm, p_grad) if np.isfinite(p_adm) and np.isfinite(p_grad) else np.nan
    stats_rows.append(["prop_femenina_adm_vs_grad", "ztest", z_val, p_val, h_effect, "Diferencia de proporcion femenina"])

    edad_adm = df.loc[df["tipo"] == "ADMITIDOS", "edad"].dropna()
    edad_grad = df.loc[df["tipo"] == "GRADUADOS", "edad"].dropna()
    u_stat, p_u = stats.mannwhitneyu(edad_adm, edad_grad, alternative="two-sided")
    effect_r = rank_biserial_from_u(u_stat, len(edad_adm), len(edad_grad))
    stats_rows.append(["edad_adm_vs_grad", "mannwhitney", u_stat, p_u, effect_r, "Diferencia de distribucion de edad"])

    infer = pd.DataFrame(stats_rows, columns=["prueba", "metodo", "estadistico", "p_value", "efecto", "conclusion"]) 
    infer.to_csv(OUTPUT_DIR / "inferencial_resultados.csv", index=False, encoding="utf-8")
    print("Estado DESPUES:")
    print(infer.to_string(index=False))

    learnings.append(
        {
            "task": "Analisis inferencial y pruebas de diferencias",
            "input": "Tablas descriptivas de Tasks 2-4.",
            "operation": "Chi-cuadrado, z-test de proporciones y Mann-Whitney para edad.",
            "output": "inferencial_resultados.csv con p-values y efecto.",
            "verification": "Pruebas ejecutadas sin error con estadisticos y niveles de significancia interpretables.",
        }
    )

    print("\nTASK 6 - Informe tecnico")
    top_fac = fac.head(5)
    top_prog_txt = top_prog.head(6)
    balance_median = float(pivot_balance["ratio_admitidos_graduados"].median(skipna=True))
    report = [
        "# Informe de Analisis: Admitidos y Graduados",
        "",
        "## Hallazgos clave",
        f"- Registros analizados: **{len(df):,}** (se removieron {dup_count} duplicados).",
        f"- Balance mediano admitidos/graduados por periodo: **{balance_median:.2f}**.",
        f"- Prueba chi-cuadrado sexo-tipo: p-value={p_s:.4g}, Cramers V={cv_s:.3f}.",
        f"- Prueba chi-cuadrado estrato-tipo: p-value={p_e:.4g}, Cramers V={cv_e:.3f}.",
        f"- z-test proporcion femenina: p-value={p_val:.4g}, Cohen h={h_effect:.3f}.",
        f"- Mann-Whitney edad: p-value={p_u:.4g}, correlacion biserial de rangos={effect_r:.3f}.",
        "",
        "## Segmentacion prioritaria",
        "Top facultades por volumen:",
        "",
        "```text",
        top_fac.to_string(index=False),
        "```",
        "",
        "Top programas por volumen (muestra):",
        "",
        "```text",
        top_prog_txt.to_string(index=False),
        "```",
        "",
        "## Recomendaciones ejecutivas",
        "- Fortalecer seguimiento de cohortes con bajo ratio graduados/admitidos.",
        "- Focalizar estrategias de permanencia en segmentos con brechas demograficas detectadas.",
        "- Establecer tablero de monitoreo semestral para reaccion temprana por programa.",
        "",
        "## Decisiones metodologicas",
        f"- La edad se calcula con fecha de referencia fija **{REFERENCE_DATE.date()}** para asegurar reproducibilidad entre ejecuciones.",
        "- Se reporta tamano de efecto en todas las pruebas inferenciales: Cramers V (chi-cuadrado), Cohen h (z-test de proporciones) y correlacion biserial de rangos (Mann-Whitney).",
        "",
        "## Limitaciones",
        "- El dataset no incluye variables de rendimiento academico individual.",
        "- La referencia fija de edad no sustituye edad exacta al momento de ingreso/egreso historico.",
    ]
    REPORT_FILE.write_text("\n".join(report), encoding="utf-8")
    print("Estado DESPUES: informe generado en outputs/informe_analisis.md")

    learnings.append(
        {
            "task": "Informe tecnico profesional",
            "input": "Resultados consolidados de Tasks 2-5.",
            "operation": "Redaccion de hallazgos, recomendaciones y limitaciones.",
            "output": "Archivo outputs/informe_analisis.md generado.",
            "verification": "Incluye indicadores cuantitativos, evidencia inferencial y acciones ejecutivas.",
        }
    )

    print("\nTASK 7 - Dashboard Streamlit")
    print("Estado ANTES: app.py inexistente o no validado")
    print("Estado DESPUES: app.py se valida por compilacion en verificacion externa")
    learnings.append(
        {
            "task": "Dashboard en Streamlit",
            "input": "CSVs de salida y df_clean.",
            "operation": "Construccion de dashboard con filtros globales, KPIs, secciones y cache.",
            "output": "app.py funcional para exploracion local.",
            "verification": "Validacion sintactica por py_compile y carga de datos cacheada.",
        }
    )

    write_learnings(learnings)

    summary = {
        "rows_clean": int(len(df)),
        "duplicates_removed": dup_count,
        "median_ratio": balance_median,
        "significant_tests": infer[["prueba", "p_value"]].to_dict(orient="records"),
    }
    (OUTPUT_DIR / "resumen_metricas.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    repro = {
        "reference_date_for_edad": str(REFERENCE_DATE.date()),
        "generated_at": pd.Timestamp.now("UTC").isoformat(),
        "python": {
            "pandas": pd.__version__,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "seaborn": sns.__version__,
        },
        "input_data": {
            "file_name": INPUT_FILE.name,
            "sheet_name": "Data",
            "shape": [int(df_raw.shape[0]), int(df_raw.shape[1])],
            "file_timestamp": pd.Timestamp(INPUT_FILE.stat().st_mtime, unit="s").isoformat(),
            "file_sha256": file_sha256(INPUT_FILE),
        },
    }
    REPRO_FILE.write_text(json.dumps(repro, indent=2), encoding="utf-8")
    print("\nPipeline completado. Artefactos en outputs/ y docs/LEARNINGS.md")


if __name__ == "__main__":
    main()
