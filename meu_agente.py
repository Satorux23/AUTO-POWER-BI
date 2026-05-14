import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="BI Universal", layout="wide", initial_sidebar_state="expanded")

st.title("📊 Seu Power BI Universal")
st.markdown("Faça o upload de qualquer Excel e crie seus próprios cruzamentos de dados.")

# Upload do arquivo
arquivo = st.file_uploader("Suba qualquer planilha (Excel ou CSV)", type=['xlsx', 'csv'])

if arquivo:
    try:
        # Lê qualquer arquivo sem importar o que tem dentro
        if arquivo.name.endswith('.csv'):
            df = pd.read_csv(arquivo)
        else:
            df = pd.read_excel(arquivo)
        
        st.success("✅ Base de dados carregada! Agora monte seu gráfico.")
        
        # Mapeia dinamicamente TODAS as colunas do seu arquivo
        colunas_todas = df.columns.tolist()
        colunas_numericas = df.select_dtypes(include=['number']).columns.tolist()
        colunas_texto = df.select_dtypes(exclude=['number']).columns.tolist()

        # --- MENU LATERAL (FILTROS UNIVERSAIS) ---
        st.sidebar.header("🔍 Filtros")
        
        if colunas_texto:
            coluna_filtro = st.sidebar.selectbox("Filtrar planilha usando a coluna:", ["Nenhum Filtro"] + colunas_texto)
            
            if coluna_filtro != "Nenhum Filtro":
                valores_unicos = df[coluna_filtro].dropna().unique().tolist()
                selecao = st.sidebar.multiselect(f"Selecione o que deseja ver em '{coluna_filtro}':", valores_unicos, default=valores_unicos)
                
                if selecao:
                    df_filtrado = df[df[coluna_filtro].isin(selecao)]
                else:
                    df_filtrado = df
            else:
                df_filtrado = df
        else:
            df_filtrado = df

        st.divider()

        # --- CONSTRUTOR DE GRÁFICOS UNIVERSAL ---
        st.markdown("### 🛠️ Construtor de Gráficos")
        
        # Aqui você escolhe o que quer cruzar com o que
        col_opcoes1, col_opcoes2, col_opcoes3 = st.columns(3)
        
        with col_opcoes1:
            tipo_grafico = st.selectbox("Tipo de Gráfico:", ["Barras", "Linha", "Dispersão", "Pizza"])
            
        with col_opcoes2:
            # Pode escolher QUALQUER coluna para a base do gráfico
            eixo_x = st.selectbox("Eixo X (Base/Categorias):", colunas_todas)
            
        with col_opcoes3:
            # Pega só as colunas numéricas para fazer os cálculos
            if colunas_numericas:
                eixo_y = st.selectbox("Eixo Y (Valores Numéricos):", colunas_numericas)
            else:
                eixo_y = None
                st.warning("Seu Excel não tem colunas com números.")

        # --- RENDERIZAÇÃO MÁGICA DOS GRÁFICOS ---
        if eixo_y:
            st.markdown("---")
            
            # Gráfico de BARRAS
            if tipo_grafico == "Barras":
                df_agrupado = df_filtrado.groupby(eixo_x)[eixo_y].sum().reset_index()
                fig = px.bar(df_agrupado, x=eixo_x, y=eixo_y, text_auto='.2s', color=eixo_x, title=f"Soma de {eixo_y} por {eixo_x}")
                st.plotly_chart(fig, use_container_width=True)

            # Gráfico de LINHA
            elif tipo_grafico == "Linha":
                # Ideal para cruzar datas com valores
                df_agrupado = df_filtrado.groupby(eixo_x)[eixo_y].sum().reset_index()
                fig = px.line(df_agrupado, x=eixo_x, y=eixo_y, markers=True, title=f"Evolução de {eixo_y} por {eixo_x}")
                st.plotly_chart(fig, use_container_width=True)

            # Gráfico de DISPERSÃO
            elif tipo_grafico == "Dispersão":
                fig = px.scatter(df_filtrado, x=eixo_x, y=eixo_y, color=eixo_x, title=f"Dispersão: {eixo_y} vs {eixo_x}")
                st.plotly_chart(fig, use_container_width=True)

            # Gráfico de PIZZA
            elif tipo_grafico == "Pizza":
                fig = px.pie(df_filtrado, names=eixo_x, values=eixo_y, hole=0.4, title=f"Proporção de {eixo_y} em {eixo_x}")
                st.plotly_chart(fig, use_container_width=True)

        # Mostrar os dados
        with st.expander("Ver Tabela de Dados Original"):
            st.dataframe(df_filtrado)

    except Exception as e:
        st.error(f"Erro ao processar arquivo: {e}")
