import streamlit as st

def injetar_sinalizacao_tela(dados_os):
    """
    Injeta um marcador visual HUD (Heads-Up Display) flutuante na tela.
    Lê dinamicamente o casamento de Status + Criticidade da planilha Sheets.
    """
    try:
        status = str(dados_os['Status'].values[0]).strip()
        criticidade = str(dados_os['Criticidade'].values[0]).strip()
        id_bim = str(dados_os['ID'].values[0]).strip()
        sintoma = str(dados_os['Sintoma_detalhado'].values[0]).strip()
        responsavel = str(dados_os['Responsavel'].values[0]).strip()
        os_codigo = str(dados_os['OS'].values[0]).strip()
    except Exception:
        return

    if status == "Aberta":
        if criticidade == "Alta":
            cor_alerta = "#FF1F1F"      
            cor_borda = "#9B1C1C"       
            texto_hud = "🚨 ALERTA CRÍTICO: RISCO DE PARADA"
            animacao_css = "pulse 1.5s infinite"
        elif criticidade == "Média":
            cor_alerta = "#FF9F1C"      
            cor_borda = "#92400E"       
            texto_hud = "⚠️ ATENÇÃO: MANUTENÇÃO PREVENTIVA"
            animacao_css = "none"
        else:
            cor_alerta = "#2563EB"      
            cor_borda = "#1E429F"       
            texto_hud = "🔧 ROTINA: AJUSTE ESTÉTICO/VISUAL"
            animacao_css = "none"

        html_hud = f"""
        <div style="
            background: rgba(15, 23, 42, 0.95);
            color: #F8FAFC;
            padding: 16px;
            border-radius: 10px;
            border-left: 6px solid {cor_alerta};
            border-top: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            margin-bottom: 20px;
            animation: {animacao_css};">
            
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="color: {cor_alerta}; font-weight: 700; font-size: 13px; letter-spacing: 0.05em;">{texto_hud}</span>
                <span style="background: {cor_borda}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">{os_codigo}</span>
            </div>
            
            <div style="font-size: 15px; font-weight: 600; margin-bottom: 4px; color: #FFFFFF;">
                Ativo BIM: <span style="font-family: monospace; color: #CBD5E1;">{id_bim}</span>
            </div>
            
            <div style="font-size: 13px; color: #94A3B8; margin-top: 6px;">
                <b>Sintoma:</b> {sintoma} | <b>Técnico:</b> {responsavel}
            </div>
        </div>

        <style>
        @keyframes pulse {{
            0% {{ box-shadow: 0 0 0 0 rgba(255, 31, 31, 0.6); }}
            70% {{ box-shadow: 0 0 0 12px rgba(255, 31, 31, 0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(255, 31, 31, 0); }}
        }}
        </style>
        """
        st.components.v1.html(html_hud, height=120)
