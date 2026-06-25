import streamlit as st
import pandas as pd
import json
import urllib.parse

# 1. Configuração da Página (Layout Amplo e Corporativo)
st.set_page_config(
    page_title="RB Consultoria - Gestão de Ativos",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS: Altura do 3D ajustada para 550px para máxima compactação vertical
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    iframe { width: 100% !important; height: 550px !important; border-radius: 12px; }
    .legenda-item { display: flex; align-items: center; margin-bottom: 6px; font-size: 14px; }
    .quadrado-cor { width: 16px; height: 16px; border-radius: 4px; margin-right: 10px; }
    </style>
""", unsafe_allow_html=True)

# Base da URL do seu modelo Speckle com o token
url_base_speckle = "https://speckle.systems"

# 2. Layout de Tela: Barra Lateral (Métricas Operacionais)
with st.sidebar:
    st.title("Painel de Controle")
    st.markdown("---")
    
    arquivo_upload = st.file_uploader("Carregar Planilha CMMS (.csv)", type=["csv"])
    st.markdown("---")
    
    df_exibicao = pd.DataFrame()
    contagem_status = {"Aberta": 0, "Fechado": 0, "Em Atendimento": 0, "Pausada": 0}
    lista_os_selecao = ["Nenhuma OS selecionada"]
    url_modificadores = ""
    
    if arquivo_upload is not None:
        try:
            df_os = pd.read_csv(arquivo_upload)
            df_os.columns = df_os.columns.str.strip()
            
            df_os['Data_Abertura'] = pd.to_datetime(df_os['Data_Abertura'], errors='coerce')
            df_os['Status'] = df_os['Status'].astype(str).str.strip()
            df_os['Setor'] = df_os['Setor'].astype(str).str.strip()
            df_os['OS'] = df_os['OS'].astype(str).str.strip()
            df_os['ID'] = df_os['ID'].astype(str).str.strip()
            
            if 'Responsavel' in df_os.columns:
                df_os['Responsavel'] = df_os['Responsavel'].astype(str).str.strip()
            else:
                df_os['Responsavel'] = "Não Atribuído"
            
            df_mes = df_os[df_os['Data_Abertura'].dt.strftime('%Y-%m') == '2026-06']
            
            st.subheader("Filtros de Visão")
            lista_setores = ["Todos"] + sorted(list(df_mes['Setor'].unique()))
            setor_selecionado = st.selectbox("Filtrar por Setor:", lista_setores)
            
            lista_status = ["Todos"] + sorted(list(df_mes['Status'].unique()))
            status_selecionado = st.selectbox("Filtrar por Status:", lista_status)
            
            df_exibicao = df_mes.copy()
            if setor_selecionado != "Todos":
                df_exibicao = df_exibicao[df_exibicao['Setor'] == setor_selecionado]
            if status_selecionado != "Todos":
                df_exibicao = df_exibicao[df_exibicao['Status'] == status_selecionado]
            
            lista_os_selecao = sorted(list(df_exibicao['OS'].unique()))
            
            for status_chave in contagem_status.keys():
                contagem_status[status_chave] = len(df_exibicao[df_exibicao['Status'] == status_chave])
            
            st.markdown("---")
            st.subheader("🎨 Filtro de Cores no Modelo (BIM)")
            modo_cor = st.toggle("Ativar Visão Cromática por Status", value=True)
            
            if modo_cor:
                st.markdown("""
                <div class="legenda-item"><div class="quadrado-cor" style="background-color: #ff4b4b;"></div>🔴 Aberta (Urgente)</div>
                <div class="legenda-item"><div class="quadrado-cor" style="background-color: #28a745;"></div>🟢 Fechado (Concluída)</div>
                """, unsafe_allow_html=True)
                
                ids_abertos = df_exibicao[df_exibicao['Status'] == 'Aberta']['ID'].dropna().tolist()
                opcoes_visualizador = {"ghostOthers": True}
                if ids_abertos:
                    opcoes_visualizador["filter"] = {"objectIds": ids_abertos}
                
                string_json = json.dumps(opcoes_visualizador)
                url_modificadores = f"#embed={urllib.parse.quote(string_json)}"
            
            st.markdown("---")
            st.subheader("Métricas de Manutenção")
            total_abertas_mes = len(df_mes)
            if total_abertas_mes > 0:
                total_fechadas_filtradas = len(df_exibicao[df_exibicao['Status'] == 'Fechado'])
                sla_calculado = round((total_fechadas_filtradas / total_abertas_mes) * 100, 1)
                st.metric(label="SLA de Atendimento (Meta: 95%)", value=f"{sla_calculado}%", delta=f"{round(sla_calculado - 95.0, 1)}%")
            
        except Exception as e:
            st.error(f"Erro ao processar as colunas: {e}")
    else:
        st.warning("Aguardando upload da planilha...")

# 3. Layout de Tela: Área Central (Maquete 3D Panorâmica)
st.title("Visualizador Operacional de Ativos 3D")
url_final_speckle = f"{url_base_speckle}{url_modificadores}"
st.components.v1.iframe(url_final_speckle, height=550)

st.markdown("---")

# 4. Volumetria das Ordens de Serviço (KPIs)
st.subheader("📊 Volumetria das Ordens de Serviço")
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric(label="🟢 Aberta", value=contagem_status["Aberta"])
with col2: st.metric(label="🔵 Em Atendimento", value=contagem_status["Em Atendimento"])
with col3: st.metric(label="🟡 Pausada", value=contagem_status["Pausada"])
with col4: st.metric(label="🔴 Fechado", value=contagem_status["Fechado"])

st.markdown("---")

# 5. DIVISÃO EM COLUNAS LADO A LADO: CENTRO DE IA + GRÁFICO DE PRODUTIVIDADE
if arquivo_upload is not None and not df_exibicao.empty:
    col_esquerda, col_direita = st.columns(2)
    
    with col_esquerda:
        st.subheader("🧠 Centro de Diagnóstico Avançado")
        os_selecionada = st.selectbox("Selecione a OS para análise da IA:", lista_os_selecao)
        linha_os = df_exibicao[df_exibicao['OS'] == os_selecionada].iloc[0]
        
        st.info(f"""
        **📋 Ficha Técnica**
        * **ID BIM:** `{linha_os['ID']}`
        * **Responsável:** {linha_os['Responsavel']} | **Setor:** {linha_os['Setor']}
        * **Status:** {linha_os['Status']} | **Abertura:** {linha_os['Data_Abertura'].strftime('%d/%m/%Y')}
        """)
        
        if linha_os['Status'] == 'Aberta':
            st.error(f"⚠️ DIAGNÓSTICO PRESCRITIVO: Risco de Parada Crítica\n\nCausa Raiz: Fadiga por vibração excessiva.\nPlano de Ação: Isolar válvula reguladora (Seção 4.2 do manual).")
        else:
            st.success(f"✅ ANÁLISE COMPLEMENTAR: OS Concluída por {linha_os['Responsavel']}.\n\nRecomendação: Agendar inspeção preventiva em 90 dias.")
            
    with col_direita:
        st.subheader("👥 Produtividade da Equipe")
        df_fechadas_resp = df_exibicao[df_exibicao['Status'] == 'Fechado']
        if not df_fechadas_resp.empty:
            produtividade = df_fechadas_resp['Responsavel'].value_counts()
            st.bar_chart(produtividade, height=260)
        else:
            st.info("Nenhuma ordem fechada encontrada no filtro selecionado.")
else:
    st.info("Carregue a planilha na barra lateral para ativar o Centro de Diagnóstico Inteligente por IA.")

# 6. RELATÓRIO SINCRONIZADO NA BASE DA TELA PRINCIPAL
st.markdown("---")
st.subheader("📋 Relatório Sincronizado de Ordens de Serviço")

if arquivo_upload is not None and not df_exibicao.empty:
    st.dataframe(df_exibicao, use_container_width=True, height=250)
else:
    st.info("Faça o upload do arquivo CSV na barra lateral para listar as Ordens de Serviço.")
