import streamlit as st
from docx import Document
import os
import re
import subprocess

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Contratos | Laura Moraes Beauty",
    page_icon=":sparkles:", 
    layout="centered"
)

# --- 2. ESTÉTICA PREMIUM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Montserrat:wght@300;400;500&display=swap');
    
    .stApp { background-color: #FCFBF9; }
    html, body, [class*="css"] { font-family: 'Montserrat', sans-serif; color: #4A3B39; }
    h1, h2, h3, h4 { font-family: 'Playfair Display', serif !important; color: #3D2C2A !important; }
    
    [data-testid="stForm"] {
        background-color: #FFFFFF; border: 1px solid #EBE4E2;
        border-radius: 12px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04); padding: 2rem;
    }
    
    div.stButton > button:first-child {
        background-color: #C2A39E; color: white; border-radius: 8px;
        border: none; padding: 12px 24px; font-weight: 500; width: 100%;
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover { background-color: #A68782; color: white; }
    .stTextInput input, .stSelectbox select { background-color: #FAFAFA; border: 1px solid #E0DCDA; border-radius: 6px; }
    </style>
""", unsafe_allow_html=True)

# --- 3. IDENTIDADE VISUAL ---
# Logomarca ampliada (proporção 1 : 3 : 1)
col_logo1, col_logo2, col_logo3 = st.columns([1, 3, 1])
with col_logo2:
    try:
        st.image("logo_marca.png", use_container_width=True)
    except FileNotFoundError:
        pass

# Foto de Produção
try:
    st.image("capa_noiva.png", use_container_width=True)
except FileNotFoundError:
    st.info("Dica: Salve uma foto da sua produção como 'capa_noiva.png' e sua logo como 'logo_marca.png' na mesma pasta deste arquivo.")

st.markdown("<h2 style='text-align: center; margin-top: 10px;'>Gerador de Contratos</h2>", unsafe_allow_html=True)
st.write("") 

# --- FUNÇÕES DE PROCESSAMENTO ---
def remover_caracteres_estranhos(texto):
    if isinstance(texto, str):
        return re.sub(r'[\ud800-\udfff]', '', texto)
    return texto

def preencher_contrato(template_path, dados):
    doc = Document(template_path)
    for p in doc.paragraphs:
        texto_paragrafo = p.text
        tem_tag = any(key in texto_paragrafo for key in dados.keys())
        if tem_tag:
            texto_limpo = remover_caracteres_estranhos(texto_paragrafo)
            for key, value in dados.items():
                if key in texto_limpo:
                    texto_limpo = texto_limpo.replace(key, remover_caracteres_estranhos(value))
            p.text = texto_limpo
    return doc

# --- FORMULÁRIO ---
with st.form("form_contrato"):
    st.markdown("#### 📋 Dados da Noiva")
    nome = st.text_input("Nome completo")
    colA, colB = st.columns(2)
    with colA:
        cpf = st.text_input("CPF")
        telefone = st.text_input("Telefone")
    with colB:
        profissao = st.text_input("Profissão")
        email = st.text_input("E-mail")
    endereco = st.text_input("Endereço Completo")
    
    st.markdown("---")
    st.markdown("#### 💍 Dados do Evento")
    colC, colD = st.columns(2)
    with colC:
        data_casamento = st.text_input("Data (ex: 15/01/2028)")
    with colD:
        horario = st.text_input("Horário (ex: 14h00)")
    local = st.text_input("Local da Produção")
    pacote = st.selectbox("Pacote Escolhido", ["Exclusive Bride", "Complete Bride", "Classic Bride"])
    
    st.markdown("---")
    st.markdown("#### 💰 Financeiro")
    valor_total = st.text_input("Valor Total (ex: 3.600,00)")
    colE, colF = st.columns(2)
    with colE:
        sinal = st.text_input("Sinal - 30% (ex: 1.080,00)")
    with colF:
        saldo = st.text_input("Saldo Restante - 70% (ex: 2.520,00)")
        
    st.markdown("---")
    st.markdown("#### 📄 Formato de Exportação")
    formato_arquivo = st.radio("Como deseja baixar o contrato final?", ["PDF", "Word (.docx)"], horizontal=True)
    
    st.write("")
    submit = st.form_submit_button("Gerar Contrato")

# --- GERAÇÃO ---
if submit:
    if not nome or not cpf:
        st.error("Preencha Nome e CPF.")
    else:
        dados_noiva = {
            "{{NOME_NOIVA}}": nome,
            "{{CPF}}": cpf,
            "{{PROFISSAO}}": profissao,
            "{{EMAIL}}": email,
            "{{TELEFONE}}": telefone,
            "{{ENDERECO}}": endereco,
            "{{DATA_CASAMENTO}}": data_casamento,
            "{{LOCAL}}": local,
            "{{HORARIO}}": horario,
            "{{PACOTE}}": pacote,
            "{{VALOR_TOTAL}}": valor_total,
            "{{SINAL}}": sinal,
            "{{SALDO}}": saldo
        }
        
        try:
            with st.spinner(f"Processando contrato em {formato_arquivo}..."):
                # 1. Gera o Word base sempre
                doc_preenchido = preencher_contrato("template_contrato.docx", dados_noiva)
                nome_arquivo = nome.replace(' ', '_')
                temp_docx = f"temp_{nome_arquivo}.docx"
                doc_preenchido.save(temp_docx)
                
                # 2. Lógica baseada na escolha
                if formato_arquivo == "PDF":
                    temp_pdf = f"Contrato_{nome_arquivo}.pdf"
                    
                    # Comando específico para converter PDF na nuvem (usando LibreOffice nativo do servidor)
                    subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf', temp_docx])
                    
                    with open(temp_pdf, "rb") as pdf_file:
                        file_bytes = pdf_file.read()
                        
                    st.success(f"Contrato de {nome} gerado com sucesso em PDF!")
                    st.download_button(
                        label="⬇️ Baixar Contrato (PDF)", 
                        data=file_bytes, 
                        file_name=temp_pdf, 
                        mime="application/pdf"
                    )
                    
                    if os.path.exists(temp_pdf): 
                        os.remove(temp_pdf)
                    
                else: 
                    with open(temp_docx, "rb") as docx_file:
                        file_bytes = docx_file.read()
                        
                    st.success(f"Contrato de {nome} gerado com sucesso em Word!")
                    st.download_button(
                        label="⬇️ Baixar Contrato (Word)", 
                        data=file_bytes, 
                        file_name=f"Contrato_{nome_arquivo}.docx", 
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                
                # Limpa o arquivo docx temporário em ambos os casos
                if os.path.exists(temp_docx): 
                    os.remove(temp_docx)
                    
        except Exception as e:
            st.error(f"Erro ao processar: {e}")