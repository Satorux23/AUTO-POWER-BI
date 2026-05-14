import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Power BI 2.0", layout="wide")

st.title("🚀 Power BI 2.0 - Modo Avançado")
st.markdown("Crie cruzamentos multidimensionais. Adicione múltiplos Eixos Y e quebre os dados por Cor.")

arquivo = st.file_uploader("Suba a planilha (Excel ou CSV)", type=['xlsx', 'csv'])

if arquivo:
    try:
        # Leitura Inteligente
        df = pd.read_csv(arquivo) if arquivo.name.endswith('.csv') else pd.read_excel(arquivo)
        
        colunas_todas = df.columns.tolist()
        colunas_numericas = df.select_dtypes(include=['number']).columns.tolist()
        colunas_texto = df.select_dtypes(exclude=['number']).columns.tolist()

        # --- FILTROS LATERAIS AUTOMÁTICOS ---
        st.sidebar.header("🔍 Filtros Avançados")
        df_filtrado = df.copy()
        
        # Cria um filtro para cada coluna de texto (limitado a 5 para a tela não ficar gigante)
        if colunas_texto:
            for col in colunas_texto[:5]:
                valores = df[col].dropna().unique().tolist()
                selecao = st.sidebar.multiselect(f"Filtrar por {col}:", valores, default=valores)
                if selecao:
                    df_filtrado = df_filtrado[df_filtrado[col].isin(selecao)]

        st.divider()

        # --- CONSTRUTOR MULTIDIMENSIONAL ---
        st.markdown("### 🛠️ Montagem do Gráfico")
        
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            tipo_grafico = st.selectbox("Tipo de Gráfico:", ["Barras (Agrupadas)", "Linhas", "Área", "Dispersão"])
        
        with c2:
            eixo_x = st.selectbox("Eixo X (Base):", colunas_todas)
        
        with c3:
            # AQUI ESTÁ A MÁGICA: O usuário pode adicionar quantos eixos Y quiser
            eixo_y = st.multiselect("Eixo Y (Adicione Múltiplos):", colunas_numericas, default=[colunas_numericas[0]] if colunas_numericas else [])
            
        with c4:
            # AQUI ADICIONAMOS A COR/LEGENDA
            cor = st.selectbox("Dividir por Cor (Opcional):", ["Nenhum"] + colunas_texto)

        # --- RENDERIZAÇÃO ---
        if eixo_y:
            st.markdown("---")
            
            try:
                # Lógica de agrupamento para a matemática ficar correta no gráfico
                if cor != "Nenhum":
                    # Agrupa pelo X e pela Cor
                    df_agrupado = df_filtrado.groupby([eixo_x, cor])[eixo_y].sum().reset_index()
                    param_cor = cor
                else:
                    df_agrupado = df_filtrado.groupby(eixo_x)[eixo_y].sum().reset_index()
                    param_cor = None

                # Gerando os gráficos com base na escolha
                if tipo_grafico == "Barras (Agrupadas)":
                    fig = px.bar(df_agrupado, x=eixo_x, y=eixo_y, color=param_cor, barmode="group")
                
                elif tipo_grafico == "Linhas":
                    fig = px.line(df_agrupado, x=eixo_x, y=eixo_y, color=param_cor, markers=True)
                
                elif tipo_grafico == "Área":
                    fig = px.area(df_agrupado, x=eixo_x, y=eixo_y, color=param_cor)
                
                elif tipo_grafico == "Dispersão":
                    # Dispersão não agrupa, mostra os pontos brutos
                    fig = px.scatter(df_filtrado, x=eixo_x, y=eixo_y, color=param_cor if cor != "Nenhum" else None)

                # Deixa o gráfico mais limpo e profissional
                fig.update_layout(hovermode="x unified")
                st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.warning("⚠️ Os dados selecionados não combinam perfeitamente para este formato. Tente remover a 'Cor' ou alterar o Eixo X.")

        with st.expander("Ver Tabela de Dados Atualizada"):
            st.dataframe(df_filtrado)

    except Exception as e:
        st.error(f"Erro ao ler a planilha: {e}")
