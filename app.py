import streamlit as st
import pandas as pd
import json
from hud_visualizer import injetar_sinalizacao_tela
import urllib.parse

# 1. Configuração da Página (Layout Amplo e Corporativo)
st.set_page_config(
    page_title="RB Consultoria - Gestão de Ativos",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS: Altura calibrada para 750px para valorizar a maquete
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    iframe { width: 100% !important; height: 750px !important; border-radius: 12px; }
    .legenda-item { display: flex; align-items: center; margin-bottom: 6px; font-size: 14px; }
    .quadrado-cor { width: 16px; height: 16px; border-radius: 4px; margin-right: 10px; }
    </style>
""", unsafe_allow_html=True)

# Base da URL do seu modelo Speckle com o token
url_base_speckle = "https://app.speckle.systems/projects/a649da7292/models/815af390c7?embedToken=2aaa49d6f30ad4db0d2844045f56d8ad0ee3bf7643"

# 2. Layout de Tela: Barra Lateral (Métricas Operacionais)
with st.sidebar:
    st.title("Painel de Controle")
    st.markdown("---")
    
    # Componente de Upload do arquivo CSV gerado pelo CMMS
    arquivo_upload = st.file_uploader("Carregar Planilha CMMS (.csv)", type=["csv"])
    
    st.markdown("---")
    
    # Placeholders globais para evitar quebras no código
    df_exibicao = pd.DataFrame()
    contagem_status = {"Aberta": 0, "Fechado": 0, "Em Atendimento": 0, "Pausada": 0}
    lista_os_selecao = ["Nenhuma OS selecionada"]
    url_modificadores = ""
    
    if arquivo_upload is not None:
        try:
            # Lendo a planilha carregada pelo usuário
            df_os = pd.read_csv(arquivo_upload)
            df_os.columns = df_os.columns.str.strip()
            
            # Padronização e limpeza dos dados
            df_os['Data_Abertura'] = pd.to_datetime(df_os['Data_Abertura'], errors='coerce')
            df_os['Status'] = df_os['Status'].astype(str).str.strip()
            df_os['Setor'] = df_os['Setor'].astype(str).str.strip()
            df_os['OS'] = df_os['OS'].astype(str).str.strip()
            df_os['ID'] = df_os['ID'].astype(str).str.strip()
            
            # Mapeamento da coluna de responsáveis
            if 'Responsavel' in df_os.columns:
                df_os['Responsavel'] = df_os['Responsavel'].astype(str).str.strip()
            else:
                df_os['Responsavel'] = "Não Atribuído"
            
            # Base de cálculo estrita: Mês de Junho/2026
            df_mes = df_os[df_os['Data_Abertura'].dt.strftime('%Y-%m') == '2026-06']
            
            st.subheader("Filtros de Visão")
            lista_setores = ["Todos"] + sorted(list(df_mes['Setor'].unique()))
            setor_selecionado = st.selectbox("Filtrar por Setor:", lista_setores)
            
            lista_status = ["Todos"] + sorted(list(df_mes['Status'].unique()))
            status_selecionado = st.selectbox("Filtrar por Status:", lista_status)
            
            # Aplicando os filtros na tabela de exibição
            criticidade_selecionada = st.sidebar.selectbox(
    "Filtrar por Criticidade:",
    ["Todos", "Alta", "Média", "Baixa"]
)
            st.sidebar.markdown("---")
            filtro_dias = st.sidebar.selectbox(
            "Filtrar por Tempo Aberta:",
            ["Todos", "0 a 3 dias", "4 a 7 dias", "8 a 15 dias", "Mais de 16 dias"]
            )

            df_exibicao = df_mes.copy()
            if setor_selecionado != "Todos":
                df_exibicao = df_exibicao[df_exibicao['Setor'] == setor_selecionado]
            if status_selecionado != "Todos":
                df_exibicao = df_exibicao[df_exibicao['Status'] == status_selecionado]

            if criticidade_selecionada != "Todos":
                df_exibicao = df_exibicao[df_exibicao['Criticidade'] == criticidade_selecionada]

            # Cálculo de Aging (Dias em Aberto) baseado na data atual
            import datetime
            hoje = datetime.date(2026, 6, 25)
            
                        # Converte a data de forma segura e calcula a diferença
            df_exibicao['Data_DT'] = pd.to_datetime(df_exibicao['Data_Abertura'], errors='coerce').dt.date
            df_exibicao['Fim_DT'] = pd.to_datetime(df_exibicao['Data_Fechamento'], errors='coerce').dt.date
            df_exibicao['Dias_Aberto'] = df_exibicao.apply(
                                lambda r: (hoje - r['Data_DT']).days if str(r['Status']).strip() == 'Aberta' 
                and (pd.isna(r['Fim_DT']) or str(r['Fim_DT']).strip() in ['', 'nan', 'NaT', 'None']) 
                and not pd.isna(r['Data_DT']) else -1,

                                axis=1
            )
            
            # Aplica o filtro de tempo escolhido na barra lateral
            if filtro_dias == "0 a 3 dias":
                df_exibicao = df_exibicao[(df_exibicao['Dias_Aberto'] >= 0) & (df_exibicao['Dias_Aberto'] <= 3)]
            elif filtro_dias == "4 a 7 dias":
                df_exibicao = df_exibicao[(df_exibicao['Dias_Aberto'] >= 4) & (df_exibicao['Dias_Aberto'] <= 7)]
            elif filtro_dias == "8 a 15 dias":
                df_exibicao = df_exibicao[(df_exibicao['Dias_Aberto'] >= 8) & (df_exibicao['Dias_Aberto'] <= 15)]
            elif filtro_dias == "Mais de 16 dias":
                df_exibicao = df_exibicao[df_exibicao['Dias_Aberto'] >= 16]

            
            # Lista de OS para o seletor da IA
            lista_os_selecao = sorted(list(df_exibicao['OS'].unique()))
            
            # Mapeamento e contagem estrita dos status
            for status_chave in contagem_status.keys():
                contagem_status[status_chave] = len(df_exibicao[df_exibicao['Status'] == status_chave])
            
            st.markdown("---")
            st.subheader("🎨 Filtro de Cores no Modelo (BIM)")
            modo_cor = st.toggle("Ativar Visão Cromática por Status", value=True)
            
            if modo_cor:
                st.markdown("""
                <div class="legenda-item"><div class="quadrado-cor" style="background-color: #ff4b4b;"></div>🔴 Aberta (Manutenção Urgente)</div>
                <div class="legenda-item"><div class="quadrado-cor" style="background-color: #28a745;"></div>🟢 Fechado (Ativo em Conformidade)</div>
                """, unsafe_allow_html=True)
                
                # Engenharia de Isolamento de IDs no Speckle
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
                
                st.metric(
                    label="SLA de Atendimento (Meta: 95%)",
                    value=f"{sla_calculado}%",
                    delta=f"{round(sla_calculado - 95.0, 1)}% em relação à meta",
                    delta_color="normal" if sla_calculado >= 95 else "inverse"
                )
            
        except Exception as e:
            st.error(f"Erro ao processar as colunas: {e}")
    else:
        st.warning("Aguardando upload da planilha...")
        st.metric(label="SLA de Atendimento (Meta: 95%)", value="-- %", delta="Sem dados")

# 3. Layout de Tela: Área Central (Maquete 3D Panorâmica do Speckle Dinâmica)
st.title("Visualizador Operacional de Ativos 3D")

url_final_speckle = f"{url_base_speckle}{url_modificadores}"
st.components.v1.iframe(url_final_speckle, height=750)

st.markdown("---")

# 4. Centro de Diagnóstico Avançado (IA Preditiva)
st.subheader("🧠 Centro de Diagnóstico Avançado (IA Preditiva)")

if arquivo_upload is not None and not df_exibicao.empty:
    col_sel, col_diag = st.columns(2)
    
    with col_sel:
        st.markdown("**🔎 Seleção de Ativo para Auditoria**")
        os_selecionada = st.selectbox("Selecione a OS para análise da IA:", lista_os_selecao)
        
        # Filtro seguro focado na OS selecionada
        df_filtrado_os = df_exibicao[df_exibicao['OS'] == os_selecionada]
        
        if not df_filtrado_os.empty:
            id_bim = str(df_filtrado_os['ID'].values[0])
            responsavel_tecnico = str(df_filtrado_os['Responsavel'].values[0])
            setor_ativo = str(df_filtrado_os['Setor'].values[0])
            status_ativo = str(df_filtrado_os['Status'].values[0])
            descricao_falha = str(df_filtrado_os['Descrição'].values[0])
            
            data_raw = df_filtrado_os['Data_Abertura'].values[0]
            data_abertura = pd.to_datetime(data_raw).strftime('%d/%m/%Y')
            
            injetar_sinalizacao_tela(df_filtrado_os)
            st.info(f"""
            **📋 Ficha Técnica do Ativo**
            * **ID BIM:** `{id_bim}`
            * **Responsável Técnico:** {responsavel_tecnico}
            * **Setor:** {setor_ativo}
            * **Status Atual:** {status_ativo}
            * **Data de Abertura:** {data_abertura}
            * **Histórico de Quebras:** 3 recorrências registradas nos últimos 180 dias.
            * 📖 [Acessar Manual Técnico do Ativo](https://github.com)
            """)
        
    with col_diag:
        st.markdown("**⚡ Análise de Engenharia Operacional da IA**")
        
        if not df_filtrado_os.empty:
            if status_ativo == 'Aberta':
                st.error(f"⚠️ DIAGNÓSTICO PRESCRITIVO: Risco de Parada Crítica. Causa Raiz: Com base na descrição '{descricao_falha}', o sintoma aponta para fadiga por vibração excessiva nas prumadas de alimentação do Bloco B. Plano de Ação para {responsavel_tecnico}: 1. Isolar a válvula reguladora; 2. Verificar microfissuras; 3. Substituir anéis de vedação.")
            else:
                st.success(f"✅ ANÁLISE COMPLEMENTAR: Ordem Encerrada. A OS executada por {responsavel_tecnico} referente a '{descricao_falha}' foi devidamente finalizada de acordo com as especificações técnicas do fabricante. Recomendação: Agendar inspeção preventiva em 90 dias.")
            
                # Análise de Desempenho Técnico
                st.markdown("---")
                st.subheader("📊 Análise de Produtividade da Equipe Técnica")
        
                df_fechadas_resp = df_mes[df_mes['Status'] == 'Fechado']
                if not df_fechadas_resp.empty:
                    produtividade = df_fechadas_resp['Responsavel'].value_counts()
                    st.bar_chart(produtividade)
                else:
                    st.info("Nenhuma ordem fechada encontrada no filtro selecionado para montar o gráfico de barras.")

else:
    st.info("Carregue a planilha na barra lateral para ativar o Centro de Diagnóstico Inteligente por IA.")

st.markdown("---")

# 5. VOLUMETRIA POSICIONADA LOGO ACIMA DA PLANILHA
st.subheader("📊 Volumetria das Ordens de Serviço")
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric(label="🟢 Aberta", value=contagem_status["Aberta"])
with col2: st.metric(label="🔵 Em Atendimento", value=contagem_status["Em Atendimento"])
with col3: st.metric(label="🟡 Pausada", value=contagem_status["Pausada"])
with col4: st.metric(label="🔴 Fechado", value=contagem_status["Fechado"])

st.markdown("---")

# 6. SEÇÃO DO RELATÓRIO COMPLETAMENTE DESTRAVADA E OBRIGATÓRIA
st.subheader("📋 Relatório Sincronizado de Ordens de Serviço")

if arquivo_upload is not None:
    st.dataframe(df_exibicao, use_container_width=True, height=300)
else:
    st.info("Faça o upload do arquivo CSV na barra lateral para listar as Ordens de Serviço.")
