import streamlit as st
import os
from fpdf import FPDF
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
# ==========================================

MESES = {
    1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
    5: "maio", 6: "junho", 7: "julho", 8: "agosto",
    9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
}

def formatar_moeda(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def processar_texto(texto):
    """Garante que acentos em português funcionem perfeitamente no PDF"""
    return str(texto).encode('latin-1', 'replace').decode('latin-1')

# ==========================================
# FORMULÁRIO DO APLICATIVO
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
        local = st.text_input("Local (Making of)", placeholder="Ex: Hotel Jatiúca")
        cidade_evento = st.text_input("Cidade / Município", value="Maceió/AL")

    st.markdown("---")
    st.header("💄 Pacote e Valores")
    
    pacote = st.selectbox("Pacote Escolhido", [
        "I – CLASSIC BRIDE", 
        "II – COMPLETE BRIDE", 
        "III – EXCLUSIVE BRIDE"
    ])
    
    horas_acompanhamento = st.text_input("Horas de Acompanhamento (Apenas p/ Exclusive)", value="02 (duas) horas")
    valor_total = st.number_input("Valor Total (R$)", min_value=0.0, value=0.0, step=100.0)
    
    sinal_calc = valor_total * 0.30
    saldo_calc = valor_total * 0.70
    
    col5, col6 = st.columns(2)
    with col5:
        st.info(f"**Sinal (30%):** R$ {formatar_moeda(sinal_calc)}")
    with col6:
        st.info(f"**Saldo (70%):** R$ {formatar_moeda(saldo_calc)}")
        
    observacoes = st.text_area("Observações Específicas", value="Nenhum adicional.")

    submit_button = st.form_submit_button(label="Gerar Contrato (PDF Direto) 📝")

# ==========================================
# LÓGICA DE CRIAÇÃO DO PDF (FPDF)
# ==========================================
class PDFContrato(FPDF):
    def header(self):
        if self.page_no() == 1 and os.path.exists("logo_marca.png"):
            self.image("logo_marca.png", x=85, y=8, w=40)
            self.ln(25)
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

if submit_button:
    if not nome_noiva or not cpf:
        st.error("⚠️ Preencha pelo menos o Nome e o CPF da noiva.")
    else:
        try:
            hoje = datetime.now()
            data_emissao = f"{hoje.day} de {MESES[hoje.month]} de {hoje.year}"
            
            pdf = PDFContrato()
            pdf.add_page()
            
            # Título
            pdf.set_font("Arial", 'B', 12)
            pdf.multi_cell(0, 8, processar_texto("CONTRATO DE PRESTAÇÃO DE SERVIÇOS DE BELEZA PARA NOIVA"), align='C')
            pdf.ln(5)
            
            pdf.set_font("Arial", '', 10)
            # Qualificação
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(32, 6, "CONTRATADA: ", ln=0)
            pdf.set_font("Arial", '', 10)
            pdf.multi_cell(0, 6, processar_texto("Maria Laura Toledo Montenegro de Moraes Sampaio, pessoa jurídica de direito privado, CNPJ/MF nº 66.400.716/0001-94, sede na Av. Fernandes Lima, nº 8 - Empresarial Centenário Office, sala 204, Farol, Maceió/AL."))
            pdf.ln(2)
            
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(32, 6, "CONTRATANTE: ", ln=0)
            pdf.set_font("Arial", '', 10)
            qualificacao = f"{nome_noiva}, {nacionalidade}, {estado_civil}, {profissao}, CPF nº {cpf}, e-mail: {email}, telefone: {telefone}, residente no endereço: {endereco}."
            pdf.multi_cell(0, 6, processar_texto(qualificacao))
            pdf.ln(5)
            
            # Cláusulas
            clausulas = [
                ("CLÁUSULA 1ª – DO OBJETO",
                 "1.1. A CONTRATADA compromete-se a prestar serviços profissionais especializados de visagismo e embelezamento ('dia da noiva').\n"
                 "1.2. Todos os produtos e equipamentos utilizados são de exclusiva responsabilidade da CONTRATADA.\n"
                 "1.3. Os robes padronizados fornecidos para o making of são cedidos em comodato e devem ser devolvidos ao término do atendimento, sob pena de indenização de R$ 150,00 por peça em caso de extravio ou dano."),
                
                ("CLÁUSULA 2ª – DO DIA, HORÁRIO E LOCAL",
                 f"2.1. O serviço será realizado no dia {data_casamento}, no local {local}, município de {cidade_evento}.\n"
                 f"2.2. A produção será concluída até o início da cerimônia, previsto para as {horario}.\n"
                 "2.3. Tolerância máxima de 15 minutos de atraso para o início do atendimento. Atrasos superiores poderão reduzir ou cancelar serviços.\n"
                 f"2.4. Os valores contemplam o atendimento ajustado para o município de {cidade_evento}. Mudanças de município dependem de aprovação e taxa logística.\n"
                 "2.5. Atendimentos que exijam início antes das 06h30min (ou término após as 22h00) acarretarão taxa adicional de madrugada."),
                
                ("CLÁUSULA 3ª – DO PACOTE DE SERVIÇOS CONTRATADO",
                 f"3.1. A CONTRATANTE opta expressamente pelo pacote {pacote}, ajustado pelo valor final de R$ {formatar_moeda(valor_total)}. Observações adicionais: {observacoes}.\n"
                 "§1º Inclusão de acompanhantes extras requer aviso de 15 dias e disponibilidade de agenda.\n"
                 f"3.2. LIMITE DE ACOMPANHAMENTO: No pacote Exclusive Bride, o tempo limite de acompanhamento pós-cerimônia é de {horas_acompanhamento}. Horas excedentes terão taxa extra de R$ 100,00/hora.\n"
                 "3.3. TESTE/PRÉVIA: Realizado no estúdio (segunda a quinta-feira). Falta ou remarcação com menos de 48h gera perda da gratuidade. O pacote é indivisível e a não realização da prévia não gera abatimento."),
                
                ("CLÁUSULA 4ª – DO PAGAMENTO",
                 f"4.1. Sinal/Arras: 30% correspondente a R$ {formatar_moeda(sinal_calc)} no ato da assinatura.\n"
                 f"4.2. Saldo Remanescente: 70% correspondente a R$ {formatar_moeda(saldo_calc)} quitado até o dia da prévia ou até 10 dias antes do evento."),
                
                ("CLÁUSULA 5ª – DO CANCELAMENTO",
                 "5.1. Direito de arrependimento (7 dias da contratação) com devolução integral.\n"
                 "5.2. Cancelamento imotivado acarretará retenção sobre o valor total do contrato: a) Mais de 90 dias: 30%; b) De 45 a 90 dias: 50%; c) De 15 a 44 dias: 70%; d) Menos de 15 dias: 100%. Devoluções ocorrem de forma parcelada.\n"
                 "5.3. Remarcação com menos de 60 dias incide taxa de 20% do valor total."),
                
                ("CLÁUSULA 6ª – BIOSSEGURANÇA E ESTRUTURA",
                 "6.1. Proibido realizar procedimentos estéticos abrasivos (peeling/laser) nos 10 dias anteriores ao evento.\n"
                 "6.2. ALIMENTAÇÃO: Em produções a partir de 04 horas, a CONTRATANTE deve fornecer refeição completa à equipe, sob pena de multa de R$ 150,00 por membro.\n"
                 "6.3. Concluída a produção e aprovada, cessa a responsabilidade técnica da equipe sobre efeitos externos (chuva, calor, lágrimas). O ambiente deve permanecer restrito à equipe e foto/vídeo."),
                 
                ("CLÁUSULA 7ª E 8ª – DIREITOS DE IMAGEM E FORO",
                 "7.1. A CONTRATANTE autoriza o uso gratuito de sua imagem pela marca. Publicações em tempo real ocorrerão apenas após o início da cerimônia, preservando o sigilo. Revogações não terão efeito retroativo.\n"
                 "8.1. Fica eleito o Foro da Comarca de Maceió/AL.")
            ]

            for titulo, texto in clausulas:
                pdf.set_font("Arial", 'B', 10)
                pdf.multi_cell(0, 6, processar_texto(titulo))
                pdf.set_font("Arial", '', 10)
                pdf.multi_cell(0, 5, processar_texto(texto))
                pdf.ln(3)

            # Assinaturas
            pdf.ln(10)
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 5, processar_texto(f"Maceió/AL, {data_emissao}."), align='C', ln=True)
            pdf.ln(15)

            y_assinaturas = pdf.get_y()
            pdf.line(20, y_assinaturas, 90, y_assinaturas)
            pdf.line(120, y_assinaturas, 190, y_assinaturas)
            
            pdf.set_y(y_assinaturas + 2)
            pdf.set_x(20)
            pdf.cell(70, 5, processar_texto("CONTRATANTE"), align="C")
            pdf.set_x(120)
            pdf.cell(70, 5, processar_texto("CONTRATADA"), align="C")
            
            pdf.ln(5)
            pdf.set_x(20)
            pdf.set_font("Arial", 'B', 9)
            pdf.cell(70, 5, processar_texto(nome_noiva), align="C")
            pdf.set_x(120)
            pdf.cell(70, 5, processar_texto("Laura Moraes Beauty"), align="C")
            
            pdf.ln(4)
            pdf.set_font("Arial", '', 8)
            pdf.set_x(20)
            pdf.cell(70, 5, processar_texto(f"CPF nº {cpf}"), align="C")
            pdf.set_x(120)
            pdf.cell(70, 5, processar_texto("CNPJ nº 66.400.716/0001-94"), align="C")

            # Gerar arquivo para download em memória (Evita erros na nuvem)
            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            
            st.success("✅ Contrato gerado em PDF com sucesso!")
            st.download_button(
                label="⬇️ Baixar Contrato (PDF)",
                data=pdf_bytes,
                file_name=f"Contrato_Laura_Moraes_{nome_noiva.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
            
        except Exception as e:
            st.error(f"❌ Ocorreu um erro ao gerar o PDF: {e}")
            st.info("Verifique se o arquivo logo_marca.png está na pasta correta.")
# --- FIM DO CÓDIGO ---
