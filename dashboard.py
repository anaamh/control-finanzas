import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, time

API_URL = "https://control-finanzas-api-eoqj.onrender.com"
st.set_page_config(page_title="Control de Finanzas", layout="wide")

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

def format_period_es(period_str):
    try:
        dt = datetime.strptime(period_str, "%Y-%m")
        return f"{MESES_ES[dt.month]} {dt.year}"
    except Exception:
        return period_str

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@400;600;700&family=Quicksand:wght@500;600;700&display=swap');
    
    /* Configuración global del color primario (reemplaza el rojo/naranja nativo) */
    :root, .stApp {
        --primary-color: #F2ACC6 !important;
    }

    html, body, .stApp, .stMarkdown, p, label, input, button, h1, h2, h3, h4, h5, h6 {
        font-family: 'Comfortaa', 'Quicksand', cursive, sans-serif !important;
    }

    .stApp {
        background-color: #0B2528 !important;
        color: #FFFFFF !important;
    }

    /* TÍTULOS EN ROSA #F2ACC6 */
    h1, h2, h3 {
        color: #F2ACC6 !important;
        font-weight: 700 !important;
    }

    h4, h5, h6 {
        color: #A8DADC !important;
        font-weight: 600 !important;
    }

    /* --- LEGIBILIDAD EN MÉTRICAS --- */
    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] *,
    div[data-testid="stMetricValue"] > div {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] *,
    [data-testid="stMetricLabel"] p {
        color: #A8DADC !important;
        font-weight: 700 !important;
    }

    /* --- ETIQUETAS Y TEXTOS DE FORMULARIOS --- */
    label, 
    [data-testid="stWidgetLabel"], 
    [data-testid="stWidgetLabel"] p,
    div[data-testid="stRadio"] label,
    div[data-testid="stRadio"] label p,
    div[data-baseweb="radio"] label {
        color: #A8DADC !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }

    div[role="radiogroup"] label p {
        color: #FFFFFF !important;
    }

    /* --- BOTONES DE RADIO SELECCIONADOS --- */
    div[data-baseweb="radio"] [aria-checked="true"] {
        background-color: #F2ACC6 !important;
        border-color: #F2ACC6 !important;
    }

    div[data-baseweb="radio"] div {
        border-color: #F2ACC6 !important;
    }

    /* --- ENTRADAS DE TEXTO / INPUTS --- */
    div[data-baseweb="input"], 
    div[data-baseweb="base-input"],
    div[data-baseweb="select"] > div {
        background-color: #07191B !important;
        border: 1.5px solid #1F4E53 !important;
        border-radius: 16px !important;
        overflow: hidden !important;
    }

    div[data-baseweb="input"] input,
    div[data-baseweb="base-input"] input {
        background-color: transparent !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 600 !important;
    }

    input::placeholder {
        color: #8ECAE6 !important;
        opacity: 0.6 !important;
    }

    div[data-baseweb="input"] button {
        background-color: #14373B !important;
        color: #F2ACC6 !important;
        border: none !important;
    }

    div[data-baseweb="input"] button:hover {
        background-color: #F2ACC6 !important;
        color: #0B2528 !important;
    }

    /* --- PESTAÑAS (TABS) --- */
    button[data-baseweb="tab"] p {
        color: #A8DADC !important;
        font-weight: 600 !important;
    }

    button[aria-selected="true"] p {
        color: #F2ACC6 !important;
        font-weight: 700 !important;
    }

    div[data-baseweb="tab-highlight"] {
        background-color: #F2ACC6 !important;
    }

    button[aria-selected="true"] {
        border-bottom: 3px solid #F2ACC6 !important;
    }

    /* --- TARJETAS TIPO NOTIFICACIÓN iOS --- */
    .ios-notification-card {
        background-color: #14373B !important;
        border: 1px solid #1F4E53 !important;
        border-radius: 20px !important;
        padding: 14px 18px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25) !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }

    .ios-notification-card:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35) !important;
        border-color: #8ECAE6 !important;
    }

    .ios-card-title {
        color: #A8DADC !important;
        font-size: 0.85rem !important;
        font-weight: 700 !important;
    }

    .ios-card-desc {
        color: #FFFFFF !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        margin-top: 2px !important;
    }

    .ios-card-date {
        color: #8ECAE6 !important;
        font-size: 0.78rem !important;
        opacity: 0.8 !important;
    }

    /* --- TABLA CLÁSICA --- */
    div[data-testid="stDataFrame"],
    div[data-testid="stTable"] {
        background-color: #07191B !important;
        border-radius: 18px !important;
        border: 1px solid #1F4E53 !important;
        padding: 6px !important;
    }

    /* --- MÉTRICAS Y CONTENEDORES --- */
    [data-testid="stMetric"] {
        background-color: #14373B !important;
        border-radius: 22px !important;
        padding: 20px !important;
        border: 1px solid #1F4E53 !important;
    }

    [data-testid="stForm"] {
        background-color: #14373B !important;
        border-radius: 24px !important;
        padding: 26px !important;
        border: 1px solid #1F4E53 !important;
    }

    .stButton > button, [data-testid="stFormSubmitButton"] > button {
        background-color: #F2ACC6 !important;
        color: #0B2528 !important;
        border-radius: 30px !important;
        border: none !important;
        padding: 10px 24px !important;
        font-weight: 700 !important;
    }

    .stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
        background-color: #8ECAE6 !important;
        color: #0B2528 !important;
    }

    [data-testid="stExpander"] summary {
        background-color: #14373B !important;
        border-radius: 18px !important;
        color: #8ECAE6 !important;
        border: 1px solid #1F4E53 !important;
    }

    hr {
        border-color: #1F4E53 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- CARGA DE DATOS ---
transactions_data = []
categories_data = []

try:
    c_res = requests.get(f"{API_URL}/categories/", timeout=60).json()
    if isinstance(c_res, list):
        categories_data = c_res
except Exception:
    pass

try:
    t_res = requests.get(f"{API_URL}/transactions/", timeout=60).json()
    if isinstance(t_res, list):
        transactions_data = t_res
except Exception:
    pass

cat_dict = {c["name"]: c["id"] for c in categories_data}
cat_info = {c["id"]: {"name": c["name"], "type": c.get("type", "gasto").lower()} for c in categories_data}
existing_cats_str = ", ".join(sorted(list(cat_dict.keys()))) if cat_dict else "Ninguna creada aún"

if transactions_data:
    df = pd.DataFrame(transactions_data)
    df["date_parsed"] = pd.to_datetime(df["date"])
    df["period"] = df["date_parsed"].dt.strftime("%Y-%m")
    df["category_name"] = df["category_id"].apply(lambda cid: cat_info.get(cid, {}).get("name", "Sin Categoría"))
    df["category_type"] = df["category_id"].apply(lambda cid: cat_info.get(cid, {}).get("type", "gasto"))
else:
    df = pd.DataFrame()

# --- 1. RESUMEN MES ACTUAL ---
current_period = date.today().strftime("%Y-%m")
current_period_label = format_period_es(current_period)

st.title("💳 Control de Finanzas")
st.subheader(f"🗓️ Resumen de {current_period_label}")

if not df.empty:
    df_curr = df[df["period"] == current_period]
    curr_inc = df_curr[df_curr["category_type"] == "ingreso"]["amount"].sum()
    curr_exp = df_curr[df_curr["category_type"] == "gasto"]["amount"].sum()
    curr_net = curr_inc - curr_exp
    
    total_inc_all = df[df["category_type"] == "ingreso"]["amount"].sum()
    total_exp_all = df[df["category_type"] == "gasto"]["amount"].sum()
    saldo_total = total_inc_all - total_exp_all
else:
    curr_inc, curr_exp, curr_net, saldo_total = 0.0, 0.0, 0.0, 0.0

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Ingresos del mes", f"{curr_inc:.2f} €")
col_m2.metric("Gastos del mes", f"{curr_exp:.2f} €")
col_m3.metric("Valor Neto del mes", f"{curr_net:.2f} €", delta=f"{curr_net:.2f} €" if curr_net != 0 else None)
col_m4.metric("Saldo Total", f"{saldo_total:.2f} €")
st.divider()

# --- 2. REGISTRO Y NOTIFICACIONES / TABLA ---
col_form, col_data = st.columns([1.2, 1.8])

with col_form:
    st.subheader("➕ Añadir Movimiento")

    with st.form("new_transaction_form", clear_on_submit=True):
        amount = st.number_input("1. Cantidad (€)", min_value=0.01, step=1.0)
        trans_type = st.radio("2. Tipo de movimiento", ["Gasto", "Ingreso"], horizontal=True)
        description = st.text_input("3. Descripción")
        
        cat_input = st.text_input("4. Categoría", placeholder="Escribe o selecciona una categoría...")
        if cat_dict:
            st.caption(f"🏷️ **Categorías existentes:** {existing_cats_str}")

        selected_date = st.date_input("5. Fecha del movimiento", value=date.today(), format="DD/MM/YYYY")

        submitted = st.form_submit_button("Guardar Movimiento")
        
        if submitted:
            clean_cat_name = cat_input.strip()
            
            if not clean_cat_name:
                st.warning("Escribe un nombre de categoría.")
            else:
                selected_type_str = trans_type.lower()
                matched_id = None
                for existing_name, existing_id in cat_dict.items():
                    if existing_name.lower() == clean_cat_name.lower():
                        matched_id = existing_id
                        break
                
                if matched_id:
                    cat_id = matched_id
                else:
                    res_c = requests.post(f"{API_URL}/categories/", json={"name": clean_cat_name, "type": selected_type_str}, timeout=60)
                    cat_id = res_c.json()["id"] if res_c.status_code == 200 else None

                if cat_id:
                    full_datetime = datetime.combine(selected_date, time.min)
                    payload = {
                        "amount": amount,
                        "description": description,
                        "category_id": cat_id,
                        "date": full_datetime.isoformat()
                    }
                    res_tx = requests.post(f"{API_URL}/transactions/", json=payload, timeout=60)
                    if res_tx.status_code == 200:
                        st.success("¡Movimiento guardado con éxito!")
                        st.rerun()
                    else:
                        st.error("Error al guardar el movimiento.")

with col_data:
    tab_tabla, tab_grafico = st.tabs(["🔔 Actividad Reciente", "🍩 Distribución Global por Categorías"])
    
    if not df.empty:
        if "id" in df.columns:
            df_table = df.sort_values(by=["date_parsed", "id"], ascending=[False, False]).reset_index(drop=True)
        else:
            df_table = df.sort_values(by="date_parsed", ascending=False).reset_index(drop=True)

        df_table["date_formatted"] = df_table["date_parsed"].dt.strftime("%d/%m/%Y")
        
        def format_amount(row):
            amt = row["amount"]
            return f"+{amt:.2f} €" if row["category_type"] == "ingreso" else f"-{amt:.2f} €"
        
        df_table["Monto (€)"] = df_table.apply(format_amount, axis=1)
        
        df_display = df_table[["date_formatted", "category_name", "description", "Monto (€)"]].rename(
            columns={"date_formatted": "Fecha", "category_name": "Categoría", "description": "Descripción"}
        )
        
        with tab_tabla:
            col_ctrl1, col_ctrl2 = st.columns([1.2, 1.0])
            
            with col_ctrl1:
                ver_modo_tabla = st.toggle("📋 Modo tabla tradicional", value=False)
            
            with col_ctrl2:
                csv_data = df_display.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar CSV",
                    data=csv_data,
                    file_name=f"historial_finanzas_{date.today()}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            st.write("")

            if ver_modo_tabla:
                # VISTA DE TABLA TRADICIONAL
                def style_tx_rows(row):
                    val = str(row["Monto (€)"])
                    bg_style = "background-color: #07191B; border-bottom: 1px solid #1F4E53;"
                    if val.startswith("+"):
                        return [f"{bg_style} color: #8ECAE6; font-weight: 700;"] * len(row)
                    elif val.startswith("-"):
                        return [f"{bg_style} color: #F2ACC6; font-weight: 700;"] * len(row)
                    return [f"{bg_style} color: #FFFFFF;"] * len(row)

                styled_df = df_display.style.apply(style_tx_rows, axis=1)
                st.dataframe(
                    styled_df,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                # VISTA TARJETAS iOS
                if "visible_cards" not in st.session_state:
                    st.session_state.visible_cards = 5

                df_cards = df_table.head(st.session_state.visible_cards)

                for _, row in df_cards.iterrows():
                    is_ingreso = row["category_type"] == "ingreso"
                    amount_color = "#8ECAE6" if is_ingreso else "#F2ACC6"
                    amount_sign = "+" if is_ingreso else "-"
                    icon = "🟢" if is_ingreso else "🔻"
                    desc_text = row['description'] if str(row['description']).strip() else row['category_name']
                    
                    card_html = f"""
                    <div class="ios-notification-card">
                        <div style="display: flex; align-items: center; gap: 14px;">
                            <div style="font-size: 1.4rem;">{icon}</div>
                            <div>
                                <div style="display: flex; gap: 8px; align-items: center;">
                                    <span class="ios-card-title">{row['category_name'].upper()}</span>
                                    <span style="color: #1F4E53; font-size: 0.8rem;">•</span>
                                    <span class="ios-card-date">{row['date_formatted']}</span>
                                </div>
                                <div class="ios-card-desc">{desc_text}</div>
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 1.2rem; font-weight: 700; color: {amount_color}; font-family: 'Comfortaa', sans-serif;">
                                {amount_sign}{row['amount']:.2f} €
                            </div>
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)

                total_items = len(df_table)
                if total_items > st.session_state.visible_cards:
                    col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
                    with col_b2:
                        if st.button(f"➕ Ver más movimientos ({st.session_state.visible_cards}/{total_items})", use_container_width=True):
                            st.session_state.visible_cards += 5
                            st.rerun()
                elif st.session_state.visible_cards > 5:
                    col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
                    with col_b2:
                        if st.button("🔄 Mostrar menos", use_container_width=True):
                            st.session_state.visible_cards = 5
                            st.rerun()

        with tab_grafico:
            cat_summary = df.groupby("category_name")["amount"].sum().reset_index()
            palette = ["#F2ACC6", "#8ECAE6", "#A8DADC", "#E7C6FF", "#B8C0FF"]
            
            fig_pie = px.pie(
                cat_summary, values="amount", names="category_name", hole=0.6, color_discrete_sequence=palette
            )
            fig_pie.update_traces(
                textposition='outside', textinfo='label+percent',
                marker=dict(line=dict(color='#0B2528', width=2)),
                hovertemplate="<b>%{label}</b><br>Monto: %{value:.2f} €<br>Porcentaje: %{percent}"
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Comfortaa, sans-serif", size=13, color="#FFFFFF"),
                margin=dict(t=20, b=20, l=20, r=20), showlegend=False, height=350
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        with tab_tabla:
            st.info("No hay transacciones registradas todavía.")
        with tab_grafico:
            st.info("Añade movimientos para visualizar la distribución.")

st.divider()

# --- 3. DESPLEGABLE: CONSULTA Y DETALLE POR MES ---
with st.expander("🔍 Consulta y Detalle por Mes", expanded=False):
    if not df.empty:
        available_periods = sorted(df["period"].unique(), reverse=True)
        selected_period = st.selectbox(
            "Selecciona un mes para analizar:",
            available_periods,
            format_func=format_period_es
        )
        
        df_month = df[df["period"] == selected_period].copy()
        
        m_inc = df_month[df_month["category_type"] == "ingreso"]["amount"].sum()
        m_exp = df_month[df_month["category_type"] == "gasto"]["amount"].sum()
        m_net = m_inc - m_exp
        
        df_upto_sel = df[df["period"] <= selected_period]
        m_balance = df_upto_sel[df_upto_sel["category_type"] == "ingreso"]["amount"].sum() - df_upto_sel[df_upto_sel["category_type"] == "gasto"]["amount"].sum()
        
        sm_col1, sm_col2, sm_col3, sm_col4 = st.columns(4)
        sm_col1.metric("Ingresos del mes", f"{m_inc:.2f} €")
        sm_col2.metric("Gastos del mes", f"{m_exp:.2f} €")
        sm_col3.metric("Resultado Neto", f"{m_net:.2f} €")
        sm_col4.metric("Fondos al cierre", f"{m_balance:.2f} €")
        
        st.markdown(f"#### 📊 Desglose por Categorías - {format_period_es(selected_period)}")
        col_gasto_chart, col_ingreso_chart = st.columns(2)
        
        df_month_gastos = df_month[df_month["category_type"] == "gasto"]
        df_month_ingresos = df_month[df_month["category_type"] == "ingreso"]
        
        with col_gasto_chart:
            st.markdown("##### 🔻 Gastos por Categoría")
            if not df_month_gastos.empty:
                gastos_cat = df_month_gastos.groupby("category_name")["amount"].sum().reset_index().sort_values(by="amount", ascending=False)
                fig_gastos = px.bar(
                    gastos_cat, x="category_name", y="amount", text="amount",
                    color_discrete_sequence=["#F2ACC6"]
                )
                fig_gastos.update_traces(
                    texttemplate='-%{text:.2f} €', textposition='outside',
                    textfont=dict(color="#F2ACC6", size=11),
                    marker=dict(cornerradius=12, line_width=0)
                )
                fig_gastos.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Comfortaa, sans-serif", size=12, color="#FFFFFF"),
                    xaxis=dict(title="", showgrid=False, linecolor="#1F4E53"),
                    yaxis=dict(title="Monto (€)", showgrid=True, gridcolor="#14373B", zeroline=False),
                    height=340, margin=dict(t=30, b=20, l=10, r=10)
                )
                st.plotly_chart(fig_gastos, use_container_width=True)
            else:
                st.info("No hay gastos registrados en este mes.")
                
        with col_ingreso_chart:
            st.markdown("##### 🟢 Ingresos por Categoría")
            if not df_month_ingresos.empty:
                ingresos_cat = df_month_ingresos.groupby("category_name")["amount"].sum().reset_index().sort_values(by="amount", ascending=False)
                fig_ingresos = px.bar(
                    ingresos_cat, x="category_name", y="amount", text="amount",
                    color_discrete_sequence=["#8ECAE6"]
                )
                fig_ingresos.update_traces(
                    texttemplate='+%{text:.2f} €', textposition='outside',
                    textfont=dict(color="#8ECAE6", size=11),
                    marker=dict(cornerradius=12, line_width=0)
                )
                fig_ingresos.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Comfortaa, sans-serif", size=12, color="#FFFFFF"),
                    xaxis=dict(title="", showgrid=False, linecolor="#1F4E53"),
                    yaxis=dict(title="Monto (€)", showgrid=True, gridcolor="#14373B", zeroline=False),
                    height=340, margin=dict(t=30, b=20, l=10, r=10)
                )
                st.plotly_chart(fig_ingresos, use_container_width=True)
            else:
                st.info("No hay ingresos registrados en este mes.")
    else:
        st.info("No hay transacciones registradas para consultar.")

# --- 4. DESPLEGABLE: HISTÓRICO GLOBAL ---
with st.expander("🌐 Histórico Global y Totales de la App", expanded=False):
    if not df.empty:
        total_income = df[df["category_type"] == "ingreso"]["amount"].sum()
        total_expense = df[df["category_type"] == "gasto"]["amount"].sum()
        net_value = total_income - total_expense
        total_balance = net_value
        
        st.markdown("##### 💰 Resumen Total Histórico")
        h_col1, h_col2, h_col3, h_col4 = st.columns(4)
        h_col1.metric("Ingresos Totales", f"{total_income:.2f} €")
        h_col2.metric("Gastos Totales", f"{total_expense:.2f} €")
        h_col3.metric("Valor Neto Histórico", f"{net_value:.2f} €")
        h_col4.metric("Saldo Total Disponible", f"{total_balance:.2f} €")
        
        st.markdown("##### 📈 Evolución Histórica")
        
        cat_options = ["🌐 Todas las categorías (Visión General)"] + sorted(df["category_name"].unique().tolist())
        selected_hist_cat = st.selectbox("Filtrar gráfico histórico por:", cat_options)
        
        if selected_hist_cat == "🌐 Todas las categorías (Visión General)":
            df_hist = df.groupby(["period", "category_type"])["amount"].sum().unstack(fill_value=0).reset_index()
            if "ingreso" not in df_hist.columns:
                df_hist["ingreso"] = 0.0
            if "gasto" not in df_hist.columns:
                df_hist["gasto"] = 0.0
                
            df_hist = df_hist.sort_values(by="period")
            df_hist["period_label"] = df_hist["period"].apply(format_period_es)
            
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                x=df_hist["period_label"],
                y=df_hist["ingreso"],
                name="Ingresos",
                marker=dict(color="#8ECAE6", cornerradius=12),
                text=[f"+{v:.2f} €" for v in df_hist["ingreso"]],
                textposition="outside",
                textfont=dict(color="#8ECAE6", size=11)
            ))
            fig_bar.add_trace(go.Bar(
                x=df_hist["period_label"],
                y=df_hist["gasto"],
                name="Gastos",
                marker=dict(color="#F2ACC6", cornerradius=12),
                text=[f"-{v:.2f} €" for v in df_hist["gasto"]],
                textposition="outside",
                textfont=dict(color="#F2ACC6", size=11)
            ))

            fig_bar.update_layout(
                barmode="group",
                bargap=0.4,
                bargroupgap=0.15,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Comfortaa, sans-serif", size=12, color="#FFFFFF"),
                xaxis=dict(showgrid=False, linecolor="#1F4E53"),
                yaxis=dict(showgrid=True, gridcolor="#14373B", zeroline=False),
                margin=dict(t=30, b=20, l=10, r=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=360
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            df_cat_hist = df[df["category_name"] == selected_hist_cat].copy()
            cat_type = df_cat_hist["category_type"].iloc[0] if not df_cat_hist.empty else "gasto"
            
            df_cat_summary = df_cat_hist.groupby("period")["amount"].sum().reset_index().sort_values(by="period")
            df_cat_summary["period_label"] = df_cat_summary["period"].apply(format_period_es)
            
            bar_color = "#8ECAE6" if cat_type == "ingreso" else "#F2ACC6"
            text_color = "#8ECAE6" if cat_type == "ingreso" else "#F2ACC6"
            prefix = "+" if cat_type == "ingreso" else "-"
            
            fig_cat = go.Figure()
            fig_cat.add_trace(go.Bar(
                x=df_cat_summary["period_label"],
                y=df_cat_summary["amount"],
                name=selected_hist_cat,
                marker=dict(color=bar_color, cornerradius=12),
                text=[f"{prefix}{v:.2f} €" for v in df_cat_summary["amount"]],
                textposition="outside",
                textfont=dict(color=text_color, size=11)
            ))
            
            fig_cat.update_layout(
                bargap=0.5,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Comfortaa, sans-serif", size=12, color="#FFFFFF"),
                xaxis=dict(showgrid=False, linecolor="#1F4E53"),
                yaxis=dict(title="Monto (€)", showgrid=True, gridcolor="#14373B", zeroline=False),
                margin=dict(t=30, b=20, l=10, r=10),
                showlegend=False,
                height=360
            )
            st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.info("No hay datos históricos registrados.")