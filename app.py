import streamlit as st
import os
from docx import Document
from io import BytesIO
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Gerador de Contratos - Laura Moraes", page_icon="✨", layout="centered")

# ==========================================
# 1. CABEÇALHO E LOGOMARCA
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

# ==========================================
# 2. ÁREA DE FOTOS (BARRA LATERAL)
# ==========================================
with st.sidebar:
    st.header("📸 Portfólio / Inspirações")
    if os.path.exists("capa_noiva.png"):
        st.image("capa_noiva.png", caption="Laura Moraes Beauty")
    else:
        st.info("📌 O arquivo 'capa_noiva.png' não foi encontrado.")
# ==========================================

MESES = {
    1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
    5: "maio", 6: "junho", 7: "julho", 8: "agosto",
    9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
}

def formatar_moeda(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def substituir_tags(doc, dicionario_tags):
    for p in doc.paragraphs:
        for tag, valor in dicionario_tags.items():
            if tag in p.text:
                p.text = p.text.replace(tag, str(valor))
                
    for tabela in doc.tables:
        for linha in tabela.rows:
            for celula in linha.cells:
                for p in celula.paragraphs:
                    for tag, valor in dicionario_tags.items():
                        if tag in p.text:
                            p.text = p.text.replace(tag, str(valor))

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
        local = st.text_input("Local da Produção (Making of)", placeholder="Ex: Hotel Jatiúca")
        cidade_evento = st.text_input("Cidade / Município do Evento", value="Maceió/AL")

    st.markdown("---")
    st.header("💄 Pacote e Valores")
    
    pacote = st.selectbox("Pacote Escolhido", [
        "I – CLASSIC BRIDE", 
        "II – COMPLETE BRIDE", 
        "III – EXCLUSIVE BRIDE"
    ])
    
    horas_acompanhamento = st.text_input(
        "Horas de Acompanhamento (Apenas p/ Exclusive)", 
        value="02 (duas) horas"
    )
    
    valor_total = st.number_input("Valor Total (R$)", min_value=0.0, value=0.0, step=100.0)
    
    sinal_calc = valor_total * 0.30
    saldo_calc = valor_total * 0.70
    
    col5, col6 = st.columns(2)
    with col5:
        st.info(f"**Sinal (30%):** R$ {formatar_moeda(sinal_calc)}")
    with col6:
        st.info(f"**Saldo (70%):** R$ {formatar_moeda(saldo_calc)}")
        
    observacoes = st.text_area("Observações Específicas", value="Nenhum adicional.")

    st.markdown("---")
    st.header("⚙️ Formato de Saída")
    formato_saida = st.radio(
        "Como deseja baixar o contrato?", 
        ["Word (.docx)", "PDF (.pdf)"]
    )

    submit_button = st.form_submit_button(label="Gerar Contrato 📝")

if submit_button:
    if not nome_noiva or not cpf:
        st.error("⚠️ Preencha pelo menos o Nome e o CPF da noiva.")
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
            nome_arquivo_base = f"Contrato_Laura_{nome_noiva.replace(' ', '_')}"
            
            if "Word" in formato_saida:
                buffer = BytesIO()
                doc.save(buffer)
                buffer.seek(0)
                
                st.success("✅ Contrato Word gerado com sucesso!")
                st.download_button(
                    label="⬇️ Baixar Contrato (Word)",
                    data=buffer,
                    file_name=f"{nome_arquivo_base}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            
            elif "PDF" in formato_saida:
                try:
                    from docx2pdf import convert
                    
                    temp_docx = "temp_contrato.docx"
                    temp_pdf = "temp_contrato.pdf"
                    
                    doc.save(temp_docx)
                    
                    with st.spinner('Convertendo para PDF... Aguarde.'):
                        convert(temp_docx, temp_pdf)
                    
                    with open(temp_pdf, "rb") as pdf_file:
                        pdf_bytes = pdf_file.read()
                        
                    st.success("✅ Contrato gerado com sucesso em PDF!")
                    st.download_button(
                        label="⬇️ Baixar Contrato (PDF)",
                        data=pdf_bytes,
                        file_name=f"{nome_arquivo_base}.pdf",
                        mime="application/pdf"
                    )
                    
                    if os.path.exists(temp_docx): os.remove(temp_docx)
                    if os.path.exists(temp_pdf): os.remove(temp_pdf)
                    
                except ImportError:
                    st.error("❌ Biblioteca docx2pdf não instalada.")
                except Exception as e:
                    st.error("❌ Erro ao converter PDF (limitação do servidor).")
                    st.warning("Dica: Baixe a versão Word abaixo e salve como PDF no seu PC.")
                    
                    buffer = BytesIO()
                    doc.save(buffer)
                    buffer.seek(0)
                    st.download_button(
                        label="⬇️ Baixar versão Word (Emergência)",
                        data=buffer,
                        file_name=f"{nome_arquivo_base}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

        except Exception as e:
            st.error(f"❌ Erro ao gerar documento: {e}")

# --- FIM DO CÓDIGO ---
