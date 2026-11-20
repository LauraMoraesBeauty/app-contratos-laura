import streamlit as st
import os
import base64
import requests
from docx import Document
from io import BytesIO
from datetime import datetime

# ==========================================
# 🔑 SEU TOKEN DA ZAPSIGN VAI AQUI
# ==========================================
ZAPSIGN_TOKEN = "1b8a8326-6440-469b-b8dc-f96308fab22701bf3f9a-4cde-43c9-90f3-f8ee4da18142"

# Configuração da página
st.set_page_config(page_title="Gerador de Contratos - Laura Moraes", page_icon="✨", layout="centered")

# ==========================================
# CABEÇALHO E LOGOMARCA
# ==========================================
col_logo, col_titulo = st.columns([1, 3])
with col_logo:
    if os.path.exists("logo_marca.png"):
        st.image("logo_marca.png", use_column_width=True)
    else:
        st.info("📌 Logo não encontrada.")
with col_titulo:
    st.title("✨ Gerador de Contratos")
    st.subheader("Laura Moraes Beauty")
st.markdown("---")

with st.sidebar:
    st.header("📸 Portfólio / Inspirações")
    if os.path.exists("capa_noiva.png"):
        st.image("capa_noiva.png", caption="Laura Moraes Beauty")

MESES = {1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril", 5: "maio", 6: "junho", 7: "julho", 8: "agosto", 9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"}

def formatar_moeda(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def substituir_tags(doc, dicionario_tags):
    for p in doc.paragraphs:
        for run in p.runs:
            for tag, valor in dicionario_tags.items():
                if tag in run.text:
                    run.text = run.text.replace(tag, str(valor))
    for tabela in doc.tables:
        for linha in tabela.rows:
            for celula in linha.cells:
                for p in celula.paragraphs:
                    for run in p.runs:
                        for tag, valor in dicionario_tags.items():
                            if tag in run.text:
                                run.text = run.text.replace(tag, str(valor))

def enviar_para_zapsign(buffer_docx, nome_arquivo, nome_noiva):
    """Envia o documento para a ZapSign via API"""
    url = f"https://api.zapsign.com.br/api/v1/docs/?api_token={ZAPSIGN_TOKEN}"
    
    # Converte o documento Word para Base64 (formato que a API entende)
    b64_file = base64.b64encode(buffer_docx.getvalue()).decode('utf-8')
    b64_string = f"data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64_file}"
    
    # Monta o pacote de informações
    payload = {
        "name": nome_arquivo,
        "base64_pdf": b64_string, # ZapSign aceita word aqui também
        "signers": [
            {
                "name": nome_noiva,
                "auth_mode": "assinatura_tela" # Noiva assina desenhando na tela
            },
            {
                "name": "Laura Moraes Beauty",
                "auth_mode": "assinatura_tela" # Você assina desenhando na tela
            }
        ]
    }
    
    headers = {"Content-Type": "application/json"}
    resposta = requests.post(url, json=payload, headers=headers)
    return resposta

# ==========================================
# FORMULÁRIO DE PREENCHIMENTO
# ==========================================
with st.form("form_contrato"):
    st.header("👰 Dados da Contratante")
    col1, col2 = st.columns(2)
    with col1:
        nome_noiva = st.text_input("Nome da Noiva", placeholder="Ex: Ana Carolina Silva")
        nacionalidade = st.text_input("Nacionalidade", value="brasileira")
        estado_civil = st.selectbox("Estado Civil", ["solteira", "casada", "divorciada", "viúva"])
        profissao = st.text_input("Profissão")
    with col2:
        cpf = st.text_input("CPF")
        email = st.text_input("E-mail")
        telefone = st.text_input("Telefone / WhatsApp")
        endereco = st.text_input("Endereço Completo")

    st.markdown("---")
    st.header("📍 Dados do Evento")
    col3, col4 = st.columns(2)
    with col3:
        data_casamento = st.text_input("Data do Casamento", placeholder="Ex: 15 de novembro de 2027")
        horario = st.text_input("Horário da Cerimônia", placeholder="Ex: 15:30")
    with col4:
        local = st.text_input("Local da Produção", placeholder="Ex: Hotel Jatiúca")
        cidade_evento = st.text_input("Cidade / Município do Evento", value="Maceió/AL")

    st.markdown("---")
    st.header("💄 Pacote e Valores")
    pacote = st.selectbox("Pacote Escolhido", ["I – CLASSIC BRIDE", "II – COMPLETE BRIDE", "III – EXCLUSIVE BRIDE"])
    horas_acompanhamento = st.text_input("Horas de Acompanhamento (Apenas p/ Exclusive)", value="02 (duas) horas")
    valor_total = st.number_input("Valor Total (R$)", min_value=0.0, value=0.0, step=100.0)
    
    sinal_calc = valor_total * 0.30
    saldo_calc = valor_total * 0.70
    
    col5, col6 = st.columns(2)
    with col5:
        st.info(f"**Sinal (30%):** R$ {formatar_moeda(sinal_calc)}")
    with col6:
        st.info(f"**Saldo (70%):** R$ {formatar_moeda(saldo_calc)}")
        
    observacoes = st.text_area("Observações Específicas", value="Nenhum adicional contratado.")

    st.markdown("---")
    enviar_zapsign = st.checkbox("✍️ Enviar contrato automaticamente para a ZapSign", value=True)

    submit_button = st.form_submit_button(label="Gerar Contrato 📝")

# ==========================================
# LÓGICA DE GERAÇÃO
# ==========================================
if submit_button:
    if not nome_noiva or not cpf:
        st.error("⚠️ Por favor, preencha pelo menos o Nome e o CPF da noiva.")
    else:
        try:
            hoje = datetime.now()
            data_emissao_formatada = f"{hoje.day} de {MESES[hoje.month]} de {hoje.year}"
            
            tags = {
                "{{NOME_NOIVA}}": nome_noiva.strip(),
                "{{NACIONALIDADE}}": nacionalidade.strip(),
                "{{ESTADO_CIVIL}}": estado_civil.strip(),
                "{{PROFISSAO}}": profissao.strip(),
                "{{CPF}}": cpf.strip(),
                "{{EMAIL}}": email.strip(),
                "{{TELEFONE}}": telefone.strip(),
                "{{ENDERECO}}": endereco.strip(),
                "{{DATA_CASAMENTO}}": data_casamento.strip(),
                "{{HORARIO}}": horario.strip(),
                "{{LOCAL}}": local.strip(),
                "{{CIDADE_EVENTO}}": cidade_evento.strip(),
                "{{PACOTE}}": pacote,
                "{{HORAS_ACOMPANHAMENTO}}": horas_acompanhamento.strip(),
                "{{VALOR_TOTAL}}": formatar_moeda(valor_total),
                "{{SINAL}}": formatar_moeda(sinal_calc),
                "{{SALDO}}": formatar_moeda(saldo_calc),
                "{{OBSERVACOES}}": observacoes.strip(),
                "{{DATA_EMISSAO}}": data_emissao_formatada
            }

            doc = Document("template_contrato.docx")
            substituir_tags(doc, tags)
            
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            
            nome_arquivo_base = f"Contrato_Laura_{nome_noiva.replace(' ', '_')}"
            
            st.success("✅ Contrato Word gerado com sucesso!")
            
            st.download_button(
                label="⬇️ Baixar Contrato (Word)",
                data=buffer,
                file_name=f"{nome_arquivo_base}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

            # --- INTEGRAÇÃO ZAPSIGN ---
            if enviar_zapsign:
                if ZAPSIGN_TOKEN == "5d5f2747-a445-45aa-8ccc-3b9a3a880ec712170f78-6c66-48e7-8d0d-89525cd119bf":
                    st.warning("⚠️ Você marcou para enviar à ZapSign, mas esqueceu de colar o seu Token no código (Linha 9).")
                else:
                    with st.spinner("Enviando contrato para a ZapSign..."):
                        resposta = enviar_para_zapsign(buffer, nome_arquivo_base, nome_noiva)
                        
                        if resposta.status_code == 200:
                            dados = resposta.json()
                            link_noiva = dados['signers'][0]['sign_url']
                            link_laura = dados['signers'][1]['sign_url']
                            
                            st.markdown("---")
                            st.header("✍️ Links de Assinatura (ZapSign)")
                            
                            st.success("Documento criado na ZapSign com sucesso!")
                            
                            st.text_input("🔗 Link para mandar no WhatsApp da NOIVA:", value=link_noiva)
                            st.markdown(f"[➡️ Clique aqui para abrir o link da Noiva]({link_noiva})")
                            
                            st.text_input("🔗 Link para VOCÊ assinar:", value=link_laura)
                            st.markdown(f"[➡️ Clique aqui para abrir o seu link]({link_laura})")
                            
                        else:
                            st.error(f"Erro ao integrar com ZapSign. Código: {resposta.status_code}")
                            st.json(resposta.json())

        except Exception as e:
            st.error(f"❌ Erro ao gerar o documento: {e}")
