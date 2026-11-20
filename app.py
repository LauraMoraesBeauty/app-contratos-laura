import streamlit as st
from docx import Document
from io import BytesIO
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Gerador de Contratos - Laura Moraes Beauty", page_icon="✨", layout="centered")

# Dicionário de meses para a data automática em português
MESES = {
    1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
    5: "maio", 6: "junho", 7: "julho", 8: "agosto",
    9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
}

def formatar_moeda(valor):
    """Formata número para o padrão de moeda brasileiro (ex: 2.500,00)"""
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def substituir_tags(doc, dicionario_tags):
    """Substitui as tags no documento preservando a formatação (parágrafos e tabelas)"""
    # Substituir em parágrafos normais
    for p in doc.paragraphs:
        for tag, valor in dicionario_tags.items():
            if tag in p.text:
                # O replace direto no text perde formatação fina, mas para tags inteiras 
                # costuma funcionar bem. Para garantir, substituímos no texto do parágrafo.
                p.text = p.text.replace(tag, str(valor))
                
    # Substituir em tabelas (como a tabela de assinaturas)
    for tabela in doc.tables:
        for linha in tabela.rows:
            for celula in linha.cells:
                for p in celula.paragraphs:
                    for tag, valor in dicionario_tags.items():
                        if tag in p.text:
                            p.text = p.text.replace(tag, str(valor))

# Cabeçalho do App
st.title("✨ Emissor de Contratos")
st.subheader("Laura Moraes Beauty")
st.markdown("---")

# Formulário de Preenchimento
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
        local = st.text_input("Local da Produção (Making of)", placeholder="Ex: Hotel Jatiúca, Quarto 201")
        cidade_evento = st.text_input("Cidade / Município do Evento", value="Maceió/AL")

    st.markdown("---")
    st.header("💄 Pacote e Valores")
    
    pacote = st.selectbox("Pacote Escolhido", [
        "I – CLASSIC BRIDE", 
        "II – COMPLETE BRIDE", 
        "III – EXCLUSIVE BRIDE"
    ])
    
    horas_acompanhamento = st.text_input(
        "Horas de Acompanhamento (Apenas para Exclusive Bride)", 
        value="02 (duas) horas",
        help="Altere apenas se negociar um tempo diferente."
    )
    
    # Valores
    valor_total = st.number_input("Valor Total (R$)", min_value=0.0, value=0.0, step=100.0)
    
    # Cálculo automático do Sinal (30%) e Saldo (70%)
    sinal_calc = valor_total * 0.30
    saldo_calc = valor_total * 0.70
    
    col5, col6 = st.columns(2)
    with col5:
        st.info(f"**Sinal (30%):** R$ {formatar_moeda(sinal_calc)}")
    with col6:
        st.info(f"**Saldo (70%):** R$ {formatar_moeda(saldo_calc)}")
        
    observacoes = st.text_area(
        "Observações / Adicionais Específicos", 
        value="Nenhum adicional contratado.",
        help="Ex: Inclui taxa de deslocamento para São Miguel dos Milagres."
    )

    submit_button = st.form_submit_button(label="Gerar Contrato 📝")

# Lógica de Geração do Documento
if submit_button:
    if not nome_noiva or not cpf:
        st.error("⚠️ Por favor, preencha pelo menos o Nome e o CPF da noiva.")
    else:
        try:
            # Puxar a data automática do dia da geração do contrato
            hoje = datetime.now()
            data_emissao_formatada = f"{hoje.day} de {MESES[hoje.month]} de {hoje.year}"
            
            # Mapeamento das tags que estão no Word
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

            # Carregar o documento Word base
            doc = Document("template_contrato.docx")
            
            # Substituir as tags
            substituir_tags(doc, tags)
            
            # Salvar em memória (BytesIO) para download
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            
            st.success("✅ Contrato gerado com sucesso!")
            
            # Botão de Download
            st.download_button(
                label="⬇️ Baixar Contrato Preenchido (Word)",
                data=buffer,
                file_name=f"Contrato_Laura_Moraes_{nome_noiva.replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
        except Exception as e:
            st.error(f"❌ Erro ao gerar o documento: {e}")
            st.info("Verifique se o arquivo 'template_contrato.docx' está na mesma pasta do aplicativo.")
