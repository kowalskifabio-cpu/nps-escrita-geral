import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 1. Configurações da Página
st.set_page_config(page_title="NPS Escrita Geral", page_icon="📊")

# 2. CSS Personalizado - FOCO EM CONTRASTE E IPHONE
st.markdown("""
<style>
    /* Fundo principal */
    .stApp { background-color: #F4F6F8; }
    
    /* Forçar cor do texto em todos os labels e inputs para evitar branco sobre branco */
    label, p, span, .stMarkdown, .stTextInput label, .stSelectbox label {
        color: #0E3A5D !important;
    }
    
    /* Estilização dos campos de texto e inputs */
    .stTextInput input {
        color: #0E3A5D !important;
        background-color: #FFFFFF !important;
    }

    .header-container { background-color: #0E3A5D; padding: 1.5rem; border-radius: 10px; text-align: center; margin-bottom: 2rem; }
    .header-title { color: #FFFFFF !important; font-weight: bold; margin-top: 10px; }
    .header-subtitle { color: #B79A5B !important; font-size: 1.1rem; }
    
    div.stButton > button { background-color: #1F5E8C !important; color: white !important; border: 2px solid #B79A5B !important; font-weight: bold; width: 100%; }
    
    .section-title { color: #0E3A5D !important; font-weight: bold; border-bottom: 2px solid #B79A5B; margin-bottom: 20px; padding-top: 10px; }
</style>
""", unsafe_allow_html=True)

# 3. Conexão Google com Limpeza de Chave
def get_gsheet_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"].to_dict()
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(credentials)

# 4. Cabeçalho
with st.container():
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    try:
        st.image("Logo Escrita.png", width=200)
    except:
        st.write("---")
    st.markdown('<h1 class="header-title">Pesquisa de Satisfação</h1>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 5. Navegação
if 'passo' not in st.session_state:
    st.session_state.passo = 1
    st.session_state.respostas = {}

# PASSO 1: IDENTIFICAÇÃO
if st.session_state.passo == 1:
    with st.form("f1"):
        nome_contato = st.text_input("Seu nome:", placeholder="Ex: João Silva")
        nome_empresa = st.text_input("Nome da sua empresa:", placeholder="Ex: Empresa ABC")
        st.markdown("### De 0 a 10, o quanto você recomendaria a Escrita Contabilidade para um amigo?")
        n_geral = st.select_slider("Nota:", options=list(range(11)), value=10)
        
        if st.form_submit_button("Próxima Etapa"):
            if not nome_contato or not nome_empresa: 
                st.error("Por favor, preencha seu nome e o nome da empresa.")
            else:
                st.session_state.respostas.update({
                    'cliente': nome_contato, 
                    'empresa': nome_empresa, 
                    'nota_geral': n_geral
                })
                st.session_state.passo = 2
                st.rerun()

# PASSO 2: ATRIBUTOS ESTRATÉGICOS
elif st.session_state.passo == 2:
    st.markdown('<p class="section-title">Avaliação Geral de Serviços</p>', unsafe_allow_html=True)
    with st.form("f2"):
        c1, c2 = st.columns(2)
        with c1:
            clareza = st.select_slider("Clareza nas informações:", options=list(range(11)), value=10)
            comunicacao = st.select_slider("Qualidade da Comunicação:", options=list(range(11)), value=10)
            custo = st.select_slider("Custo-benefício:", options=list(range(11)), value=10)
        with c2:
            prazos = st.select_slider("Cumprimento de Prazos:", options=list(range(11)), value=10)
            atendimento = st.select_slider("Cordialidade no Atendimento:", options=list(range(11)), value=10)
            
        if st.form_submit_button("Avaliar Departamentos"):
            st.session_state.respostas.update({
                'clareza': clareza, 'prazos': prazos, 'comunicacao': comunicacao,
                'atendimento': atendimento, 'custo': custo
            })
            st.session_state.passo = 3
            st.rerun()

# PASSO 3: DEPARTAMENTOS E FINALIZAÇÃO
elif st.session_state.passo == 3:
    st.markdown('<p class="section-title">Avaliação por Setor</p>', unsafe_allow_html=True)
    with st.form("f3"):
        def campo_setor(label, key_n, key_t):
            st.write(f"**{label}**")
            col_n, col_t = st.columns([1, 4])
            n = col_n.selectbox("Nota", list(range(11)), index=10, key=key_n)
            t = col_t.text_input("O que podemos melhorar? (opcional)", key=key_t)
            st.divider()
            return n, t

        # Setores Originais
        n_con, t_con = campo_setor("Setor Contábil", "n_con", "t_con")
        n_fis, t_fis = campo_setor("Setor Fiscal", "n_fis", "t_fis")
        n_rh, t_rh = campo_setor("Setor RH / Pessoal", "n_rh", "t_rh")
        n_leg, t_leg = campo_setor("Setor Legal / Societário", "n_leg", "t_leg")
        n_fin, t_fin = campo_setor("Setor Financeiro", "n_fin", "t_fin")
        n_bpo, t_bpo = campo_setor("Setor BPO Financeiro", "n_bpo", "t_bpo")
        
        # Novos Setores Solicitados
        n_rec, t_rec = campo_setor("Recepção", "n_rec", "t_rec")
        n_est, t_est = campo_setor("Estrutura Física", "n_est", "t_est")
        n_csc, t_csc = campo_setor("Sucesso do Cliente (CS)", "n_csc", "t_csc")

        st.write("**Podemos entrar em contato para falar sobre sua avaliação?**")
        contato_autorizado = st.radio("Selecione uma opção:", ["Sim", "Não"], index=1, horizontal=True)

        if st.form_submit_button("Finalizar e Enviar"):
            try:
                client = get_gsheet_client()
                sh = client.open_by_key(st.secrets["SHEET_ID"])
                wks = sh.worksheet("respostas")
                
                resp = st.session_state.respostas
                # Linha com 28 colunas exatas conforme a tabela passada
                linha = [
                    datetime.now().strftime("%d/%m/%Y %H:%M:%S"), # A
                    resp['cliente'],  # B
                    resp['empresa'],  # C
                    resp['nota_geral'], # D
                    resp['clareza'], resp['prazos'], resp['comunicacao'], resp['atendimento'], resp['custo'], # E, F, G, H, I
                    n_con, t_con, # J, K
                    n_fis, t_fis, # L, M
                    n_rh, t_rh,   # N, O
                    n_leg, t_leg, # P, Q
                    n_fin, t_fin, # R, S
                    n_bpo, t_bpo, # T, U
                    n_rec, t_rec, # V, W
                    n_est, t_est, # X, Y
                    n_csc, t_csc, # Z, AA
                    contato_autorizado # AB
                ]
                wks.append_row(linha)
                st.session_state.passo = 4
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

# PASSO 4: SUCESSO
elif st.session_state.passo == 4:
    st.balloons()
    st.success("Sua avaliação foi enviada com sucesso! A Escrita Contabilidade agradece.")
    if st.button("Enviar outra resposta"):
        st.session_state.passo = 1
        st.session_state.respostas = {}
        st.rerun()
