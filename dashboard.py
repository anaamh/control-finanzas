import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, time
import base64

# --- CONFIGURACIÓN DE PÁGINA (Debe ser la primera instrucción) ---
st.set_page_config(
    page_title="Finanzas", 
    page_icon="logo.png", 
    layout="wide"
)

# --- INYECCIÓN EN EL HEAD DE SAFARI PARA IPHONE (APPLE-TOUCH-ICON) ---
try:
    with open("logo.png", "rb") as image_file:
        encoded_logo = base64.b64encode(image_file.read()).decode()
    
    components.html(f"""
        <script>
            var link = parent.document.createElement('link');
            link.rel = 'apple-touch-icon';
            link.href = 'data:image/png;base64,{encoded_logo}';
            parent.document.getElementsByTagName('head')[0].appendChild(link);
        </script>
    """, height=0)
except Exception:
    pass

API_URL = "https://control-finanzas-api-eoqj.onrender.com"

PLOTLY_CONFIG = {
    'displayModeBar': False,
    'scrollZoom': False
}

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

DEFAULT_EMOJIS = {
    "saldo": "🪎", "familia": "🫀", "lee": "🔬", "cultura": "🎟️", "artes": "🎟️",
    "comida": "🥘", "uji": "🎓", "amigos": "🎁", "restaurante": "🥘", "supermercado": "🛒",
    "compras": "🛍️", "transporte": "🚗", "gasolina": "⛽", "casa": "🏠", "hogar": "🏠",
    "alquiler": "🔑", "ocio": "🎉", "entretenimiento": "🎬", "salud": "🏥", "farmacia": "💊",
    "inversiones": "📈", "sueldo": "💰", "salario": "💰", "ingresos": "💵", "regalos": "🎁",
    "viajes": "✈️", "educacion": "📚", "mascotas": "🐾", "servicios": "💡"
}

def extract_emoji(cat_name):
    if not cat_name:
        return "🏷️"
    
    for char in str(cat_name):
        code = ord(char)
        if (0x1F600 <= code <= 0x1F64F or
            0x1F300 <= code <= 0x1F5FF or
            0x1F680 <= code <= 0x1F6FF or
            0x1F1E0 <= code <= 0x1F1FF or
            0x2600 <= code <= 0x26FF or
            0x2700 <= code <= 0x27BF or
            0x1F900 <= code <= 0x1F9FF or
            0x1FA70 <= code <= 0x1FAFF or
            code > 0x2000):
            return char
            
    name_lower = str(cat_name).lower().strip()
    for key, emo in DEFAULT_EMOJIS.items():
        if key == name_lower:
            return emo
            
    for key, emo in DEFAULT_EMOJIS.items():
        if key in name_lower:
            return emo
            
    return "🏷️"

def get_full_cat_label(cat_name):
    if not cat_name:
        return "🏷️ Sin Categoría"
    cat_str = str(cat_name).strip()
    first_char = cat_str[0] if cat_str else ""
    
    if first_char and (ord(first_char) > 0x2000 or 0x1F300 <= ord(first_char) <= 0x1FAFF):
        return cat_str
        
    emoji = extract_emoji(cat_str)
    return f"{emoji} {cat_str}"

def format_period_es(period_str):
    try:
        dt = datetime.strptime(period_str, "%Y-%m")
        return f"{MESES_ES[dt.month]} {dt.year}"
    except Exception:
        return period_str

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@400;600;700&family=Quicksand:wght@500;600;700&display=swap');
    
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

    h1, h2, h3 {
        color: #F2ACC6 !important;
        font-weight: 700 !important;
    }

    h4, h5, h6 {
        color: #A8DADC !important;
        font-weight: 600 !important;
    }

    [data-testid="stMetricValue"], [data-testid="stMetricValue"] * {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {
        color: #A8DADC !important;
        font-weight: 700 !important;
    }

    label, [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p {
        color: #A8DADC !important;
        font-weight: 700 !important;
    }

    div[role="radiogroup"] label p {
        color: #FFFFFF !important;
    }

    div[data-baseweb="input"],
    div[data-baseweb="select"] > div {
        background-color: #103338 !important;
        border: 2px solid #2D6A70 !important;
        border-radius: 12px !important;
        color: #FFFFFF !important;
    }

    div[data-testid="stTextInput"] > div > div,
    div[data-testid="stNumberInput"] > div > div,
    div[data-testid="stDateInput"] > div > div,
    div[data-testid="stSelectbox"] > div > div {
        background-color: #103338 !important;
        border: 2px solid #2D6A70 !important;
        border-radius: 12px !important;
    }

    div[data-baseweb="select"] svg {
        fill: #A8DADC !important;
    }

    ul[data-baseweb="menu"] {
        background-color: #103338 !important;
        border: 1px solid #2D6A70 !important;
        border-radius: 12px !important;
    }

    li[data-baseweb="option"] {
        color: #FFFFFF !important;
    }

    li[data-baseweb="option"]:hover,
    li[data-baseweb="option"][aria-selected="true"] {
        background-color: #1A464C !important;
        color: #F2ACC6 !important;
    }

    div[data-baseweb="input"] input {
        color: #FFFFFF !important;
        background-color: transparent !important;
    }

    input::placeholder {
        color: #8ECAE6 !important;
        opacity: 0.7 !important;
    }

    div[data-baseweb="input"] button, 
    [data-testid="stNumberInputStepDown"], 
    [data-testid="stNumberInputStepUp"] {
        background-color: #1A464C !important;
        color: #F2ACC6 !important;
        border: none !important;
    }

    .stButton > button, [data-testid="stFormSubmitButton"] > button {
        background-color: #F2ACC6 !important;
        color: #0B2528 !important;
        border-radius: 30px !important;
        border: none !important;
        font-weight: 600 !important;
        white-space: nowrap !important;
        padding: 8px 20px !important;
    }

    .stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
        background-color: #8ECAE6 !important;
        color: #0B2528 !important;
    }

    div[data-testid="stFormSubmitButton"] {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }

    div[data-testid="stRadio"] [aria-checked="true"] *,
    div[data-baseweb="radio"] [aria-checked="true"] * {
        background-color: #F2ACC6 !important;
        border-color: #F2ACC6 !important;
    }

    [data-testid="stTabs"] button[aria-selected="true"] *,
    button[data-baseweb="tab"][aria-selected="true"] * {
        color: #F2ACC6 !important;
        font-weight: 700 !important;
    }

    [data-testid="stTabs"] [data-baseweb="tab-highlight"],
    div[data-baseweb="tab-highlight"] {
        background-color: #F2ACC6 !important;
    }

    button[data-baseweb="tab"] p {
        color: #A8DADC !important;
    }

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

    div[data-testid="stDataFrame"], div[data-testid="stTable"] {
        background-color: #07191B !important;
        border-radius: 18px !important;
        border: 1px solid #1F4E53 !important;
        padding: 6px !important;
    }

    [data-testid="stMetric"], [data-testid="stForm"] {
        background-color: #14373B !important;
        border-radius: 22px !important;
        padding: 26px !important;
        border: 1px solid #1F4E53 !important;
    }

    [data-testid="stExpander"] {
        background-color: #14373B !important;
        border: 1px solid #1F4E53 !important;
        border-radius: 18px !important;
        overflow: hidden !important;
    }

    [data-testid="stExpander"] summary {
        background-color: transparent !important;
        border: none !important;
        color: #8ECAE6 !important;
    }

    [data-testid="stExpander"] summary:hover {
        color: #F2ACC6 !important;
    }

    hr { border-color: #1F4E53 !important; }
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

cat_options_map = {get_full_cat_label(c["name"]): c["id"] for c in categories_data}
cat_info = {c["id"]: {"name": get_full_cat_label(c["name"]), "type": c.get("type", "gasto").lower()} for c in categories_data}

if transactions_data:
    df = pd.DataFrame(transactions_data)
    df["date_parsed"] = pd.to_datetime(df["date"])
    df["period"] = df["date_parsed"].dt.strftime("%Y-%m")
    df["category_name"] = df["category_id"].apply(lambda cid: cat_info.get(cid, {}).get("name", "🏷️ Sin Categoría"))
    df["category_emoji"] = df["category_name"].apply(extract_emoji)
    
    if "type" in df.columns:
        df["category_type"] = df["type"].astype(str).str.lower()
    else:
        df["category_type"] = df["category_id"].apply(lambda cid: cat_info.get(cid, {}).get("type", "gasto").lower())
else:
    df = pd.DataFrame()

# --- 1. RESUMEN MES ACTUAL ---
current_period = date.today().strftime("%Y-%m")
current_period_label = format_period_es(current_period)

st.title("Control de Finanzas")
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
    df_curr = pd.DataFrame()
    curr_inc, curr_exp, curr_net, saldo_total = 0.0, 0.0, 0.0, 0.0

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Ingresos del mes", f"{curr_inc:.2f} €")
col_m2.metric("Gastos del mes", f"{curr_exp:.2f} €")
col_m3.metric("Valor Neto del mes", f"{curr_net:.2f} €", delta=f"{curr_net:.2f} €" if curr_net != 0 else None)
col_m4.metric("Saldo Total", f"{saldo_total:.2f} €")
st.divider()

# --- 2. REGISTRO Y ACTIVIDAD DEL MES ACTUAL ---
col_form, col_data = st.columns([1.2, 1.8])

with col_form:
    st.subheader("➕ Añadir Movimiento")

    with st.form("new_transaction_form", clear_on_submit=True):
        amount = st.number_input("1. Cantidad (€)", min_value=0.01, step=1.0)
        trans_type = st.radio("2. Tipo de movimiento", ["Gasto", "Ingreso"], horizontal=True)
        description = st.text_input("3. Descripción")
        
        sorted_cat_labels = sorted(list(cat_options_map.keys()))

        if sorted_cat_labels:
            selected_cat_label = st.selectbox("4. Categoría", options=sorted_cat_labels)
        else:
            st.warning("⚠️ No hay categorías registradas.")
            selected_cat_label = None

        selected_date = st.date_input("5. Fecha del movimiento", value=date.today(), format="DD/MM/YYYY")

        st.write("")
        submitted = st.form_submit_button("Guardar Movimiento", use_container_width=True)
        
        if submitted:
            if not selected_cat_label:
                st.error("Debes seleccionar una categoría válida.")
            else:
                cat_id = cat_options_map.get(selected_cat_label)
                if cat_id:
                    full_datetime = datetime.combine(selected_date, time.min)
                    payload = {
                        "amount": amount,
                        "type": trans_type.lower(),
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
    tab_tabla, tab_grafico = st.tabs(["🔔 Actividad del Mes", "🍩 Distribución del Mes por Categorías"])
    
    if not df_curr.empty:
        if "id" in df_curr.columns:
            df_table = df_curr.sort_values(by=["date_parsed", "id"], ascending=[False, False]).reset_index(drop=True)
        else:
            df_table = df_curr.sort_values(by="date_parsed", ascending=False).reset_index(drop=True)

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
                def style_tx_rows(row):
                    val = str(row["Monto (€)"])
                    bg_style = "background-color: #07191B; border-bottom: 1px solid #1F4E53;"
                    if val.startswith("+"):
                        return [f"{bg_style} color: #8ECAE6; font-weight: 700;"] * len(row)
                    elif val.startswith("-"):
                        return [f"{bg_style} color: #F2ACC6; font-weight: 700;"] * len(row)
                    return [f"{bg_style} color: #FFFFFF;"] * len(row)

                styled_df = df_display.style.apply(style_tx_rows, axis=1)
                st.dataframe(styled_df, use_container_width=True, hide_index=True)
            else:
                if "visible_cards" not in st.session_state:
                    st.session_state.visible_cards = 5

                df_cards = df_table.head(st.session_state.visible_cards)

                for _, row in df_cards.iterrows():
                    is_ingreso = row["category_type"] == "ingreso"
                    amount_color = "#8ECAE6" if is_ingreso else "#F2ACC6"
                    amount_sign = "+" if is_ingreso else "-"
                    icon = row["category_emoji"]
                    
                    title_name = row['category_name']
                    if title_name.startswith(icon):
                        title_name = title_name[len(icon):].strip()
                        
                    desc_text = row['description'] if str(row['description']).strip() else title_name
                    
                    card_html = f"""
                    <div class="ios-notification-card">
                        <div style="display: flex; align-items: center; gap: 14px;">
                            <div style="font-size: 1.4rem;">{icon}</div>
                            <div>
                                <div style="display: flex; gap: 8px; align-items: center;">
                                    <span class="ios-card-title">{title_name.upper()}</span>
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
                    if st.button(f"➕ Ver más movimientos ({st.session_state.visible_cards}/{total_items})", use_container_width=True):
                        st.session_state.visible_cards += 5
                        st.rerun()
                elif st.session_state.visible_cards > 5:
                    if st.button("🔄 Mostrar menos", use_container_width=True):
                        st.session_state.visible_cards = 5
                        st.rerun()

        with tab_grafico:
            col_filter, _ = st.columns([2.5, 1])
            with col_filter:
                tipo_grafico = st.radio(
                    "Mostrar en el rosco:",
                    ["Solo Gastos", "Todos (Gastos e Ingresos)", "Solo Ingresos"],
                    horizontal=True,
                    key="pie_filter_type"
                )

            if tipo_grafico == "Solo Gastos":
                df_pie = df_curr[df_curr["category_type"] == "gasto"]
            elif tipo_grafico == "Solo Ingresos":
                df_pie = df_curr[df_curr["category_type"] == "ingreso"]
            else:
                df_pie = df_curr.copy()

            if not df_pie.empty:
                cat_summary = df_pie.groupby(["category_name", "category_emoji", "category_type"])["amount"].sum().reset_index()
                cat_summary["type_label"] = cat_summary["category_type"].str.capitalize()
                
                palette = ["#F2ACC6", "#8ECAE6", "#A8DADC", "#E7C6FF", "#B8C0FF", "#FFB703", "#FB8500", "#52B788", "#74C69D"]
                
                fig_pie = px.pie(
                    cat_summary, 
                    values="amount", 
                    names="category_name",
                    hole=0.55, 
                    color_discrete_sequence=palette,
                    custom_data=["category_emoji", "category_name", "type_label"]
                )
                
                fig_pie.update_traces(
                    texttemplate='%{customdata[0]} %{percent}',
                    textposition='outside', 
                    textfont=dict(size=12),
                    marker=dict(line=dict(color='#0B2528', width=2)),
                    hovertemplate="<b>%{customdata[1]}</b> (%{customdata[2]})<br>Monto: %{value:.2f} €<br>Porcentaje: %{percent}"
                )
                fig_pie.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", 
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Comfortaa, sans-serif", size=12, color="#FFFFFF"),
                    margin=dict(t=40, b=40, l=40, r=40), 
                    showlegend=False, 
                    height=420
                )
                st.plotly_chart(fig_pie, use_container_width=True, config=PLOTLY_CONFIG)
            else:
                st.info("No hay datos registrados en este mes para el filtro seleccionado.")
    else:
        with tab_tabla:
            st.info("No hay movimientos registrados en el mes actual.")
        with tab_grafico:
            st.info("Añade movimientos en el mes actual para visualizar el rosco.")

st.divider()

# --- 3. DESPLEGABLE 1: GESTIÓN DE CATEGORÍAS ---
with st.expander("🏷️ Gestión de Categorías", expanded=False):
    col_add_c, col_del_c = st.columns(2)
    
    with col_add_c:
        with st.form("add_cat_form", clear_on_submit=True):
            st.markdown("##### ➕ Crear Nueva Categoría")
            
            c_emo, c_nom = st.columns([1, 3])
            with c_emo:
                cat_emoji_input = st.text_input("Emoji", value="🏷️")
            with c_nom:
                cat_name_input = st.text_input("Nombre de la categoría")
                
            submit_cat = st.form_submit_button("Crear Categoría", use_container_width=True)
            
            if submit_cat:
                clean_name = cat_name_input.strip()
                emoji_str = cat_emoji_input.strip() if cat_emoji_input.strip() else "🏷️"
                
                if not clean_name:
                    st.warning("Escribe un nombre para la categoría.")
                else:
                    if extract_emoji(clean_name) != "🏷️":
                        full_cat_name = clean_name
                    else:
                        full_cat_name = f"{emoji_str} {clean_name}"
                        
                    existing_names_lower = [c["name"].lower() for c in categories_data]
                    if full_cat_name.lower() in existing_names_lower:
                        st.warning("Esta categoría ya existe.")
                    else:
                        res_c = requests.post(
                            f"{API_URL}/categories/",
                            json={"name": full_cat_name},
                            timeout=60
                        )
                        if res_c.status_code == 200:
                            st.success(f"¡Categoría '{full_cat_name}' creada correctamente!")
                            st.rerun()
                        else:
                            st.error("Error al crear la categoría.")

    with col_del_c:
        with st.form("del_cat_form"):
            st.markdown("##### 🗑️ Eliminar Categoría")
            if categories_data:
                selected_del_label = st.selectbox("Selecciona la categoría a eliminar:", sorted(list(cat_options_map.keys())))
                submit_del = st.form_submit_button("Eliminar Categoría", use_container_width=True)
                
                if submit_del:
                    target_id = cat_options_map[selected_del_label]
                    res_del = requests.delete(f"{API_URL}/categories/{target_id}", timeout=60)
                    if res_del.status_code == 200:
                        st.success("Categoría eliminada con éxito.")
                        st.rerun()
                    else:
                        st.error("No se pudo eliminar la categoría (es posible que tenga movimientos vinculados).")
            else:
                st.info("No hay categorías registradas.")
                st.form_submit_button("Eliminar Categoría", disabled=True, use_container_width=True)

# --- 4. DESPLEGABLE 2: CONSULTA Y DETALLE POR MES ---
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
                gastos_cat = df_month_gastos.groupby(["category_name", "category_emoji"])["amount"].sum().reset_index().sort_values(by="amount", ascending=False)
                fig_gastos = px.bar(
                    gastos_cat, x="category_emoji", y="amount", text="amount",
                    custom_data=["category_name"],
                    color_discrete_sequence=["#F2ACC6"]
                )
                fig_gastos.update_traces(
                    texttemplate='-%{text:.2f} €', textposition='outside',
                    textfont=dict(color="#F2ACC6", size=11),
                    hovertemplate="<b>%{customdata[0]}</b><br>Monto: %{y:.2f} €",
                    marker=dict(cornerradius=12, line_width=0)
                )
                fig_gastos.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Comfortaa, sans-serif", size=12, color="#FFFFFF"),
                    xaxis=dict(title="", showgrid=False, linecolor="#1F4E53", tickfont=dict(size=18), fixedrange=True),
                    yaxis=dict(title="Monto (€)", showgrid=True, gridcolor="#14373B", zeroline=False, fixedrange=True),
                    height=340, margin=dict(t=30, b=20, l=10, r=10)
                )
                st.plotly_chart(fig_gastos, use_container_width=True, config=PLOTLY_CONFIG)
            else:
                st.info("No hay gastos registrados en este mes.")
                
        with col_ingreso_chart:
            st.markdown("##### 🟢 Ingresos por Categoría")
            if not df_month_ingresos.empty:
                ingresos_cat = df_month_ingresos.groupby(["category_name", "category_emoji"])["amount"].sum().reset_index().sort_values(by="amount", ascending=False)
                fig_ingresos = px.bar(
                    ingresos_cat, x="category_emoji", y="amount", text="amount",
                    custom_data=["category_name"],
                    color_discrete_sequence=["#8ECAE6"]
                )
                fig_ingresos.update_traces(
                    texttemplate='+%{text:.2f} €', textposition='outside',
                    textfont=dict(color="#8ECAE6", size=11),
                    hovertemplate="<b>%{customdata[0]}</b><br>Monto: %{y:.2f} €",
                    marker=dict(cornerradius=12, line_width=0)
                )
                fig_ingresos.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Comfortaa, sans-serif", size=12, color="#FFFFFF"),
                    xaxis=dict(title="", showgrid=False, linecolor="#1F4E53", tickfont=dict(size=18), fixedrange=True),
                    yaxis=dict(title="Monto (€)", showgrid=True, gridcolor="#14373B", zeroline=False, fixedrange=True),
                    height=340, margin=dict(t=30, b=20, l=10, r=10)
                )
                st.plotly_chart(fig_ingresos, use_container_width=True, config=PLOTLY_CONFIG)
            else:
                st.info("No hay ingresos registrados en este mes.")
    else:
        st.info("No hay transacciones registradas para consultar.")

# --- 5. DESPLEGABLE 3: HISTÓRICO GLOBAL ---
with st.expander("🌐 Histórico Global", expanded=False):
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
        
        st.markdown("##### 📊 Balance Neto Histórico por Categoría")
        
        df_net = df.copy()
        df_net["signed_amount"] = df_net.apply(
            lambda r: r["amount"] if r["category_type"] == "ingreso" else -r["amount"],
            axis=1
        )
        
        cat_net = df_net.groupby(["category_name", "category_emoji"])["signed_amount"].sum().reset_index()
        cat_net = cat_net.sort_values(by="signed_amount", ascending=True)
        
        bar_colors = ["#8ECAE6" if val >= 0 else "#F2ACC6" for val in cat_net["signed_amount"]]
        text_labels = [f"+{val:.2f} €" if val >= 0 else f"{val:.2f} €" for val in cat_net["signed_amount"]]
        
        fig_global_net = go.Figure()
        fig_global_net.add_trace(go.Bar(
            x=cat_net["category_emoji"],
            y=cat_net["signed_amount"],
            marker=dict(color=bar_colors, cornerradius=10),
            text=text_labels,
            textposition="outside",
            textfont=dict(color=bar_colors, size=11),
            customdata=cat_net["category_name"],
            hovertemplate="<b>%{customdata}</b><br>Balance Neto: %{y:.2f} €<extra></extra>"
        ))
        
        fig_global_net.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Comfortaa, sans-serif", size=12, color="#FFFFFF"),
            xaxis=dict(title="", showgrid=False, linecolor="#1F4E53", tickfont=dict(size=18), fixedrange=True),
            yaxis=dict(title="Balance Neto (€)", showgrid=True, gridcolor="#14373B", zeroline=True, zerolinecolor="#2D6A70", fixedrange=True),
            margin=dict(t=40, b=20, l=10, r=10),
            showlegend=False,
            height=380
        )
        st.plotly_chart(fig_global_net, use_container_width=True, config=PLOTLY_CONFIG)
    else:
        st.info("No hay datos históricos registrados.")