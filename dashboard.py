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

# Estilos CSS generales
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif !important;
    }
    
    .stApp {
        background-color: #F8FAFC;
    }
    
    [data-testid="stMetric"] {
        background: white;
        border-radius: 16px;
        padding: 18px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    </style>
""", unsafe_allow_html=True)

# --- CARGA DE DATOS GENERALES ---
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

# --- 1. RESUMEN DEL MES ACTUAL ---
current_period = date.today().strftime("%Y-%m")
current_period_label = format_period_es(current_period)

st.title("💳 Panel de Control Financiero")
st.subheader(f"🗓️ Resumen de {current_period_label}")

if not df.empty:
    df_curr = df[df["period"] == current_period]
    curr_inc = df_curr[df_curr["category_type"] == "ingreso"]["amount"].sum()
    curr_exp = df_curr[df_curr["category_type"] == "gasto"]["amount"].sum()
    curr_net = curr_inc - curr_exp
    
    # Saldo histórico total (acumulado global sin filtro de mes)
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

# --- 2. REGISTRO Y TABLA DE HISTORIAL ---
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
    tab_tabla, tab_grafico = st.tabs(["📊 Tabla de Historial", "🍩 Distribución Global por Categorías"])
    
    if not df.empty:
        # Ordenación cronológica para correlativo Nº
        if "id" in df.columns:
            df_table = df.sort_values(by=["date_parsed", "id"], ascending=[True, True]).reset_index(drop=True)
        else:
            df_table = df.sort_values(by="date_parsed", ascending=True).reset_index(drop=True)
            
        df_table["Nº"] = df_table.groupby("period").cumcount() + 1
        
        # Ordenación descendente para la vista
        if "id" in df_table.columns:
            df_table = df_table.sort_values(by=["date_parsed", "id"], ascending=[False, False]).reset_index(drop=True)
        else:
            df_table = df_table.sort_values(by="date_parsed", ascending=False).reset_index(drop=True)

        df_table["date_formatted"] = df_table["date_parsed"].dt.strftime("%d/%m/%Y")
        
        def format_amount(row):
            amt = row["amount"]
            return f"+{amt:.2f} €" if row["category_type"] == "ingreso" else f"-{amt:.2f} €"
        
        df_table["Monto (€)"] = df_table.apply(format_amount, axis=1)
        
        df_display = df_table[["Nº", "date_formatted", "category_name", "description", "Monto (€)"]].rename(
            columns={"date_formatted": "Fecha", "category_name": "Categoría", "description": "Descripción"}
        )
        
        def style_tx_rows(row):
            val = str(row["Monto (€)"])
            if val.startswith("+"):
                return ["color: #15803D; font-weight: 600;"] * len(row)
            elif val.startswith("-"):
                return ["color: #991B1B; font-weight: 600;"] * len(row)
            return [""] * len(row)
        
        styled_df = df_display.style.apply(style_tx_rows, axis=1)
        
        with tab_tabla:
            st.dataframe(
                styled_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Nº": st.column_config.NumberColumn("Nº", width="small"),
                    "Fecha": st.column_config.TextColumn("Fecha", width="medium"),
                    "Categoría": st.column_config.TextColumn("Categoría", width="small"),
                    "Descripción": st.column_config.TextColumn("Descripción", width="small"),
                    "Monto (€)": st.column_config.TextColumn("Monto (€)", width="small")
                }
            )
        
        with tab_grafico:
            cat_summary = df.groupby("category_name")["amount"].sum().reset_index()
            pastel_palette = ["#C7D2FE", "#A7F3D0", "#FDE68A", "#FCA5A5", "#DDD6FE", "#99F6E4", "#FBCFE8"]
            
            fig_pie = px.pie(
                cat_summary, values="amount", names="category_name", hole=0.6, color_discrete_sequence=pastel_palette
            )
            fig_pie.update_traces(
                textposition='outside', textinfo='label+percent',
                marker=dict(line=dict(color='#FFFFFF', width=2)),
                hovertemplate="<b>%{label}</b><br>Monto: %{value:.2f} €<br>Porcentaje: %{percent}"
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Poppins, sans-serif", size=13, color="#334155"),
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
                    color_discrete_sequence=["#FCA5A5"]
                )
                fig_gastos.update_traces(
                    texttemplate='-%{text:.2f} €', textposition='outside',
                    textfont=dict(color="#991B1B", size=11),
                    marker=dict(cornerradius=10, line_width=0)
                )
                fig_gastos.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Poppins, sans-serif", size=12, color="#334155"),
                    xaxis=dict(title="", showgrid=False, linecolor="#CBD5E1"),
                    yaxis=dict(title="Monto (€)", showgrid=True, gridcolor="#F1F5F9", zeroline=False),
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
                    color_discrete_sequence=["#86EFAC"]
                )
                fig_ingresos.update_traces(
                    texttemplate='+%{text:.2f} €', textposition='outside',
                    textfont=dict(color="#15803D", size=11),
                    marker=dict(cornerradius=10, line_width=0)
                )
                fig_ingresos.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Poppins, sans-serif", size=12, color="#334155"),
                    xaxis=dict(title="", showgrid=False, linecolor="#CBD5E1"),
                    yaxis=dict(title="Monto (€)", showgrid=True, gridcolor="#F1F5F9", zeroline=False),
                    height=340, margin=dict(t=30, b=20, l=10, r=10)
                )
                st.plotly_chart(fig_ingresos, use_container_width=True)
            else:
                st.info("No hay ingresos registrados en este mes.")
    else:
        st.info("No hay transacciones registradas para consultar.")

# --- 4. DESPLEGABLE: HISTÓRICO GLOBAL Y TOTALES ---
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
                marker=dict(color="#86EFAC", cornerradius=10),
                text=[f"+{v:.2f} €" for v in df_hist["ingreso"]],
                textposition="outside",
                textfont=dict(color="#15803D", size=11)
            ))
            fig_bar.add_trace(go.Bar(
                x=df_hist["period_label"],
                y=df_hist["gasto"],
                name="Gastos",
                marker=dict(color="#FCA5A5", cornerradius=10),
                text=[f"-{v:.2f} €" for v in df_hist["gasto"]],
                textposition="outside",
                textfont=dict(color="#991B1B", size=11)
            ))

            fig_bar.update_layout(
                barmode="group",
                bargap=0.4,
                bargroupgap=0.15,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Poppins, sans-serif", size=12, color="#334155"),
                xaxis=dict(showgrid=False, linecolor="#CBD5E1"),
                yaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False),
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
            
            bar_color = "#86EFAC" if cat_type == "ingreso" else "#FCA5A5"
            text_color = "#15803D" if cat_type == "ingreso" else "#991B1B"
            prefix = "+" if cat_type == "ingreso" else "-"
            
            fig_cat = go.Figure()
            fig_cat.add_trace(go.Bar(
                x=df_cat_summary["period_label"],
                y=df_cat_summary["amount"],
                name=selected_hist_cat,
                marker=dict(color=bar_color, cornerradius=10),
                text=[f"{prefix}{v:.2f} €" for v in df_cat_summary["amount"]],
                textposition="outside",
                textfont=dict(color=text_color, size=11)
            ))
            
            fig_cat.update_layout(
                bargap=0.5,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Poppins, sans-serif", size=12, color="#334155"),
                xaxis=dict(showgrid=False, linecolor="#CBD5E1"),
                yaxis=dict(title="Monto (€)", showgrid=True, gridcolor="#F1F5F9", zeroline=False),
                margin=dict(t=30, b=20, l=10, r=10),
                showlegend=False,
                height=360
            )
            st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.info("No hay datos históricos registrados.")