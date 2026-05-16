from pathlib import Path

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"

st.set_page_config(page_title="Admitidos vs Graduados", layout="wide")


@st.cache_data
def load_data() -> dict[str, pd.DataFrame]:
    df = pd.read_csv(OUTPUT_DIR / "df_clean.csv")
    temporal = pd.read_csv(OUTPUT_DIR / "kpi_temporal.csv")
    balance = pd.read_csv(OUTPUT_DIR / "kpi_balance.csv")
    fac = pd.read_csv(OUTPUT_DIR / "segmentacion_facultad.csv")
    demo = pd.read_csv(OUTPUT_DIR / "demografia_comparativa.csv")
    infer = pd.read_csv(OUTPUT_DIR / "inferencial_resultados.csv")
    return {
        "df": df,
        "temporal": temporal,
        "balance": balance,
        "fac": fac,
        "demo": demo,
        "infer": infer,
    }


data = load_data()
df = data["df"]

st.title("Dashboard Ejecutivo: Admitidos y Graduados")
st.caption("Monitoreo temporal, segmentacion, demografia e inferencia")

if "tipo_filtro" not in st.session_state:
    st.session_state.tipo_filtro = sorted(df["tipo"].dropna().unique().tolist())

with st.sidebar:
    st.header("Filtros")
    anios = sorted(df["anio"].dropna().astype(int).unique().tolist())
    tipos = sorted(df["tipo"].dropna().unique().tolist())
    facultades = sorted(df["facultad"].dropna().unique().tolist())

    year_min, year_max = st.select_slider("Rango de anios", options=anios, value=(anios[0], anios[-1]))
    st.session_state.tipo_filtro = st.multiselect("Tipo", options=tipos, default=st.session_state.tipo_filtro)
    fac_sel = st.multiselect("Facultad", options=facultades, default=facultades)

df_f = df[
    (df["anio"].between(year_min, year_max))
    & (df["tipo"].isin(st.session_state.tipo_filtro))
    & (df["facultad"].isin(fac_sel))
]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Registros", f"{len(df_f):,}")
col2.metric("Admitidos", f"{(df_f['tipo'] == 'ADMITIDOS').sum():,}")
col3.metric("Graduados", f"{(df_f['tipo'] == 'GRADUADOS').sum():,}")
ratio = ((df_f["tipo"] == "ADMITIDOS").sum() / max(1, (df_f["tipo"] == "GRADUADOS").sum()))
col4.metric("Ratio Adm/Grad", f"{ratio:.2f}")

st.subheader("Panorama temporal")
temp_f = data["temporal"][
    (data["temporal"]["anio"].between(year_min, year_max))
    & (data["temporal"]["tipo"].isin(st.session_state.tipo_filtro))
]
st.line_chart(temp_f, x="periodo", y="volumen", color="tipo", width="stretch")
st.dataframe(temp_f.head(20), width="stretch")

st.subheader("Segmentacion por facultad")
fac_f = data["fac"][data["fac"]["tipo"].isin(st.session_state.tipo_filtro)]
st.bar_chart(fac_f.head(20), x="facultad", y="volumen", color="tipo", horizontal=True, width="stretch")

st.subheader("Demografia y origen")
demo_f = data["demo"][data["demo"]["tipo"].isin(st.session_state.tipo_filtro)]
dim = st.selectbox("Dimension", sorted(demo_f["dimension"].unique().tolist()))
st.bar_chart(demo_f[demo_f["dimension"] == dim], x="categoria", y="volumen", color="tipo", width="stretch")

st.subheader("Pruebas inferenciales")
st.dataframe(data["infer"], width="stretch")

st.subheader("Conclusiones")
st.markdown(
    """
    - El balance admitidos/graduados cambia de forma marcada entre periodos.
    - Existen diferencias estadisticamente significativas en composicion por sexo y estrato entre tipos.
    - La visualizacion permite detectar segmentos prioritarios por facultad y dimension demografica.
    """
)
