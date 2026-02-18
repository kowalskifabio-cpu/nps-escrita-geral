import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 1. Configurações da Página
st.set_page_config(page_title="NPS Escrita Geral", page_icon="📊")

# 2. CSS Personalizado
st.markdown("""
<style>
    .stApp { background-color: #F4F6F8; }
    .header-container {
        background-color: #0E3A5D;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .header-title { color: #FFFFFF; font-weight: bold; margin-top: 10px; }
    .header-subtitle { color: #B79A5B; font-size: 1.1rem; }
    div.stButton > button {
        background-color: #1F5E8C !important;
        color: white !important;
        border: 2px solid #B79A5B !important;
        font-weight: bold;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# 3. Função de Conexão
def get_gsheet_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_info = st.secrets["gcp_service_account"]
    credentials = Credentials.from_service_account_info(creds_info, scopes=scope)
    return gspread.authorize(credentials)

# 4. Cabeçalho
with st.container():
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    try:
        st.image("Logo Escrita.png", width=200)
    except:
        st.write("---")
    st.markdown('<h1 class="header-title">Pesquisa de Satisfação Geral</h1>', unsafe_allow_html=True)
    st.markdown('<p class="header-subtitle">Escrita Contabilidade</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 5. Lógica do App
if 'passo' not in st.session_state:
    st.session_state.passo = 1
    st.session_state.respostas = {}

# PASSO 1: IDENTIFICAÇÃO E GERAL
if st.session_state.passo == 1:
    with st.form("form_geral"):
        nome = st.text_input("Seu nome ou empresa:", placeholder="Ex: João Silva")
        st.markdown("### De 0 a 10, o quanto você recomendaria a Escrita Contabilidade para um amigo?")
        nota_geral = st.select_slider("Nota Geral:", options=list(range(11)), value=10)
        
        proximo = st.form_submit_button("Próxima etapa")
        if proximo:
            if not nome:
                st.error("Por favor, identifique-se.")
            else:
                st.session_state.respostas['cliente'] = nome
                st.session_state.respostas['nota_geral'] = nota_geral
                st.session_state.passo = 2
                st.rerun()

# PASSO 2: DEPARTAMENTOS (Incluindo Financeiro)
elif st.session_state.passo == 2:
    st.info("Dê uma nota para cada setor que te atende:")
    with st.form("form_setores"):
        n_contabil = st.select_slider("Setor Contábil:", options=list(range(11)), value=10)
        n_fiscal = st.select_slider("Setor Fiscal:", options=list(range(11)), value=10)
        n_rh = st.select_slider("Setor RH / Pessoal:", options=list(range(11)), value=10)
        n_legal = st.select_slider("Setor Legal / Societário:", options=list(range(11)), value=10)
        n_financeiro = st.select_slider("Setor Financeiro:", options=list(range(11)), value=10) # NOVO
        
        proximo_2 = st.form_submit_button("Último passo")
        if proximo_2:
            st.session_state.respostas.update({
                'nota_contabil': n_contabil,
                'nota_fiscal': n_fiscal,
                'nota_rh': n_rh,
                'nota_legal': n_legal,
                'nota_financeiro': n_financeiro
            })
            st.session_state.passo = 3
            st.rerun()

# PASSO 3: COMENTÁRIO E ENVIO
elif st.session_state.passo == 3:
    with st.form("form_final"):
        st.markdown("### Algum comentário adicional? (Opcional)")
        comentario = st.text_area("Sua opinião:", placeholder="Opcional...", max_chars=500)
        
        enviar = st.form_submit_button("Enviar Resposta")
        if enviar:
            try:
                client = get_gsheet_client()
                sh = client.open_by_key(st.secrets["SHEET_ID"])
                wks = sh.worksheet("respostas")
                
                # Dados na ordem exata das colunas da planilha (A até K)
                dados = [
                    datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    st.session_state.respostas['cliente'],
                    st.session_state.respostas['nota_geral'],
                    st.session_state.respostas['nota_contabil'],
                    st.session_state.respostas['nota_fiscal'],
                    st.session_state.respostas['nota_rh'],
                    st.session_state.respostas['nota_legal'],
                    st.session_state.respostas['nota_financeiro'], # NOVO
                    comentario,
                    "streamlit_app",
                    "v2_financeiro"
                ]
                
                wks.append_row(dados)
                st.session_state.passo = 4
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

# PASSO 4: SUCESSO
elif st.session_state.passo == 4:
    st.balloons()
    st.success("Obrigado! Sua resposta foi registrada.")
    if st.button("Enviar nova resposta"):
        st.session_state.passo = 1
        st.session_state.respostas = {}
        st.rerun()
