import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Dashboard Dinâmico", layout="wide", initial_sidebar_state="expanded")

st.title("📊 Gerador Automático de Dashboard")

# --- A MÁGICA AQUI: LENDO DIRETO DO COLAB ---
arquivo_teste = 'planilha_teste_dashboard.xlsx'
df = None

# O site verifica se o arquivo já existe no mesmo lugar que ele
if os.path.exists(arquivo_teste):
    st.success(f"✅ Arquivo local '{arquivo_teste}' detectado automaticamente!")
    df = pd.read_excel(arquivo_teste)
else:
    # Se não achar, ele mostra o botão de upload normal
    arquivo = st.file_uploader("Selecione a sua base de dados (Excel ou CSV)", type=['xlsx', 'csv'])
    if arquivo:
        if arquivo.name.endswith('.csv'):
            df = pd.read_csv(arquivo)
        else:
            df = pd.read_excel(arquivo)

# Se o 'df' foi preenchido (seja pelo upload ou arquivo automático), roda o dashboard
if df is not None:
    try:
        colunas_todas = df.columns.tolist()
        colunas_numericas = df.select_dtypes(include=['number']).columns.tolist()
        colunas_categoricas = df.select_dtypes(exclude=['number']).columns.tolist()

        st.sidebar.header("🔍 Filtros Dinâmicos")
        
        if colunas_categoricas:
            coluna_filtro = st.sidebar.selectbox("Escolha uma coluna para filtrar:", colunas_categoricas)
            valores_unicos = df[coluna_filtro].dropna().unique().tolist()
            selecao = st.sidebar.multiselect("Selecione os valores:", valores_unicos, default=valores_unicos)
            
            if selecao:
                df_filtrado = df[df[coluna_filtro].isin(selecao)]
            else:
                df_filtrado = df
        else:
            df_filtrado = df

        st.markdown("### 📈 Resumo Geral")
        col1, col2, col3 = st.columns(3)
        
        col1.metric("Total de Registros (Linhas)", len(df_filtrado))
        
        if colunas_numericas:
            coluna_kpi = colunas_numericas[-1] # Pega a última coluna numérica (Valor Total)
            soma_total = df_filtrado[coluna_kpi].sum()
            media_total = df_filtrado[coluna_kpi].mean()
            
            col2.metric(f"Soma de {coluna_kpi}", f"R$ {soma_total:,.2f}")
            col3.metric(f"Média de {coluna_kpi}", f"R$ {media_total:,.2f}")

        st.divider()

        st.markdown("### 📊 Análise Visual")
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("**Gráfico de Barras**")
            eixo_x = st.selectbox("Eixo X (Categorias):", colunas_todas, index=1) # Puxa Vendedor
            eixo_y = st.selectbox("Eixo Y (Valores):", colunas_numericas, index=0) if colunas_numericas else None
            
            if eixo_y:
                df_agrupado = df_filtrado.groupby(eixo_x)[eixo_y].sum().reset_index()
                fig_bar = px.bar(df_agrupado, x=eixo_x, y=eixo_y, text_auto='.2s', color=eixo_x)
                st.plotly_chart(fig_bar, use_container_width=True)

        with c2:
            st.markdown("**Gráfico de Proporção (Pizza)**")
            if colunas_numericas and colunas_categoricas:
                col_pizza = st.selectbox("Dividir por:", colunas_categoricas, index=2) # Puxa Região
                val_pizza = st.selectbox("Medida de:", colunas_numericas, index=0)
                
                fig_pie = px.pie(df_filtrado, names=col_pizza, values=val_pizza, hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)

        with st.expander("Ver Tabela de Dados (Brutos)"):
            st.dataframe(df_filtrado)

    except Exception as e:
        st.error(f"Ocorreu um erro: {e}")
else:
    st.info("👆 Aguardando os dados...")
