import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd

# Configuração da página para ocupar a tela toda
st.set_page_config(page_title="Analisador de Glosas TISS", page_icon="🏥", layout="wide")

st.title("🏥 Analisador de Glosas TISS e Gerador de Recursos")
st.markdown("Faça o upload do seu arquivo XML (Bradesco, SulAmérica ou outras operadoras) para analisar as glosas e gerar recursos instantaneamente.")

# Função de extração unificada (a mesma lógica inteligente que já aprovamos)
def extrair_glosas_tiss(caminho_xml):
    tree = ET.parse(caminho_xml)
    root = tree.getroot()
    ns = {'ans': 'http://www.ans.gov.br/padroes/tiss/schemas'}

    dados_glosa = []

    # ==========================================
    # FORMATO DEMONSTRATIVO DE PAGAMENTO (Ex: SulAmérica)
    # ==========================================
    demonstrativos = root.findall('.//ans:demonstrativoPagamento', ns)
    if not demonstrativos:
        demonstrativos = root.findall('.//{*}demonstrativoPagamento')

    if demonstrativos:
        for demo in demonstrativos:
            nome_op = demo.find('.//ans:nomeOperadora', ns) or demo.find('.//{*}nomeOperadora')
            nome_operadora = nome_op.text if nome_op is not None else "SUL AMERICA / OUTRA"

            num_demo = demo.find('.//ans:numeroDemonstrativo', ns) or demo.find('.//{*}numeroDemonstrativo')
            numero_demonstrativo = num_demo.text if num_demo is not None else ""

            protocolos = demo.findall('.//ans:relacaoProtocolos', ns)
            if not protocolos:
                protocolos = demo.findall('.//{*}relacaoProtocolos')

            for prot in protocolos:
                num_prot = prot.find('ans:numeroProtocolo', ns) or prot.find('{*}numeroProtocolo')
                protocolo_num = num_prot.text if num_prot is not None else ""

                num_lote = prot.find('ans:numeroLote', ns) or prot.find('{*}numeroLote')
                lote_num = num_lote.text if num_lote is not None else ""

                guias = prot.findall('ans:guiasDoLote', ns)
                if not guias:
                    guias = prot.findall('{*}guiasDoLote')

                for guia in guias:
                    g_prest = guia.find('ans:numeroGuiaPrestador', ns) or guia.find('{*}numeroGuiaPrestador')
                    num_guia_prestador = g_prest.text if g_prest is not None else ""

                    g_op = guia.find('ans:numeroGuiaOperadora', ns) or guia.find('{*}numeroGuiaOperadora')
                    num_guia_op = g_op.text if g_op is not None else ""

                    s_guia = guia.find('ans:senha', ns) or guia.find('{*}senha')
                    senha_num = s_guia.text if s_guia is not None else ""

                    v_proc = guia.find('ans:valorProcessadoGuia', ns) or guia.find('{*}valorProcessadoGuia')
                    v_lib = guia.find('ans:valorLiberadoGuia', ns) or guia.find('{*}valorLiberadoGuia')
                    v_glo = guia.find('ans:valorGlosaGuia', ns) or guia.find('{*}valorGlosaGuia')

                    valor_processado = float(v_proc.text) if v_proc is not None and v_proc.text else 0.0
                    valor_liberado = float(v_lib.text) if v_lib is not None and v_lib.text else 0.0
                    valor_glosa = float(v_glo.text) if v_glo is not None and v_glo.text else 0.0

                    dados_glosa.append({
                        "Operadora": nome_operadora,
                        "Demonstrativo/Lote": f"{numero_demonstrativo} / Lote: {lote_num}",
                        "Protocolo": protocolo_num,
                        "Guia Prestador": num_guia_prestador,
                        "Guia Operadora": num_guia_op,
                        "Senha": senha_num,
                        "Seq. Item": "-",
                        "Cód. Procedimento": "-",
                        "Descrição Procedimento": "Consolidado por Guia (Lote)",
                        "Valor Informado (R$)": valor_processado,
                        "Valor Liberado (R$)": valor_liberado,
                        "Valor Glosado (R$)": valor_glosa,
                        "Código Glosa": "Verificar Lote" if valor_glosa > 0 else "Sem Glosa"
                    })
        
        if dados_glosa:
            return pd.DataFrame(dados_glosa)

    # ==========================================
    # FORMATO DETALHADO POR GUIA/PROCEDIMENTO (Ex: Bradesco)
    # ==========================================
    nome_op = root.find('.//ans:nomeOperadora', ns) or root.find('.//{*}nomeOperadora')
    nome_operadora = nome_op.text if nome_op is not None else "BRADESCO / OUTRA"
    
    num_demo = root.find('.//ans:numeroDemonstrativo', ns) or root.find('.//{*}numeroDemonstrativo')
    numero_demonstrativo = num_demo.text if num_demo is not None else ""

    guias_detalhe = root.findall('.//ans:relacaoGuias', ns)
    if not guias_detalhe:
        guias_detalhe = root.findall('.//{*}relacaoGuias')

    for guia in guias_detalhe:
        num_guia_prestador = guia.find('ans:numeroGuiaPrestador', ns) or guia.find('{*}numeroGuiaPrestador')
        num_guia = num_guia_prestador.text if num_guia_prestador is not None else ""
        
        carteira = guia.find('ans:numeroCarteira', ns) or guia.find('{*}numeroCarteira')
        carteira_num = carteira.text if carteira is not None else ""
        
        senha = guia.find('ans:senha', ns) or guia.find('{*}senha')
        senha_num = senha.text if senha is not None else ""

        detalhes = guia.findall('ans:detalhesGuia', ns)
        if not detalhes:
            detalhes = guia.findall('{*}detalhesGuia')

        for detalhe in detalhes:
            seq = detalhe.find('ans:sequencialItem', ns) or detalhe.find('{*}sequencialItem')
            seq_item = seq.text if seq is not None else ""
            
            dt = detalhe.find('ans:dataRealizacao', ns) or detalhe.find('{*}dataRealizacao')
            data_realizacao = dt.text if dt is not None else ""

            proc = detalhe.find('ans:procedimento', ns) or detalhe.find('{*}procedimento')
            cod_proc = desc_proc = ""
            if proc is not None:
                cp = proc.find('ans:codigoProcedimento', ns) or proc.find('{*}codigoProcedimento')
                dp = proc.find('ans:descricaoProcedimento', ns) or proc.find('{*}descricaoProcedimento')
                cod_proc = cp.text if cp is not None else ""
                desc_proc = dp.text if dp is not None else ""

            v_info = detalhe.find('ans:valorInformado', ns) or detalhe.find('{*}valorInformado')
            v_lib = detalhe.find('ans:valorLiberado', ns) or detalhe.find('{*}valorLiberado')
            
            valor_info = float(v_info.text) if v_info is not None and v_info.text else 0.0
            valor_lib = float(v_lib.text) if v_lib is not None and v_lib.text else 0.0

            rel_glosa = detalhe.find('ans:relacaoGlosa', ns) or detalhe.find('{*}relacaoGlosa')
            if rel_glosa is not None:
                v_glosa = rel_glosa.find('ans:valorGlosa', ns) or rel_glosa.find('{*}valorGlosa')
                t_glosa = rel_glosa.find('ans:tipoGlosa', ns) or rel_glosa.find('{*}tipoGlosa')
                valor_glosa = float(v_glosa.text) if v_glosa is not None and v_glosa.text else 0.0
                tipo_glosa = t_glosa.text if t_glosa is not None else ""
            else:
                valor_glosa = 0.0
                tipo_glosa = ""

            dados_glosa.append({
                "Operadora": nome_operadora,
                "Demonstrativo": numero_demonstrativo,
                "Guia Prestador": num_guia,
                "Carteira": carteira_num,
                "Senha": senha_num,
                "Seq. Item": seq_item,
                "Cód. Procedimento": cod_proc,
                "Descrição Procedimento": desc_proc,
                "Valor Informado (R$)": valor_info,
                "Valor Liberado (R$)": valor_lib,
                "Valor Glosado (R$)": valor_glosa,
                "Código Glosa": tipo_glosa
            })

    return pd.DataFrame(dados_glosa)

# --- UPLOAD DO ARQUIVO NA TELA ---
arquivo_submetido = st.file_uploader("Selecione o arquivo XML da operadora", type=["xml"])

if arquivo_submetido is not None:
    try:
        # Processa o XML diretamente do arquivo enviado
        df = extrair_glosas_tiss(arquivo_submetido)

        if df.empty:
            st.warning("O arquivo foi lido, mas nenhum dado compatível foi encontrado.")
        else:
            st.success("Arquivo processado com sucesso!")

            # --- MÉTRICAS / RESUMO ---
            total_inf = df["Valor Informado (R$)"].sum()
            total_lib = df["Valor Liberado (R$)"].sum()
            total_glo = df["Valor Glosado (R$)"].sum()

            col1, col2, col3 = st.columns(3)
            col1.metric("Valor Informado / Processado", f"R$ {total_inf:,.2f}")
            col2.metric("Valor Liberado", f"R$ {total_lib:,.2f}")
            col3.metric("Valor Glosado", f"R$ {total_glo:,.2f}")

            st.divider()

            # --- TABELA INTERATIVA ---
            st.subheader("📋 Dados Extraídos do XML")
            st.dataframe(df, use_container_width=True)

            # --- BOTÃO DE EXPORTAR EXCEL ---
            from io import BytesIO
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            excel_data = output.getvalue()

            st.download_button(
                label="📥 Baixar Planilha em Excel (.xlsx)",
                data=excel_data,
                file_name="relatorio_glosas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.divider()

            # --- GERADOR DE RECURSOS ---
            st.subheader("✍️ Gerador de Recurso de Glosa por Guia")
            
            # Cria uma lista de opções baseada nas guias encontradas
            lista_guias = df["Guia Prestador"].unique().tolist()
            guia_escolhida = st.selectbox("Selecione o número da Guia/Prestador para gerar o recurso:", lista_guias)

            if guia_escolhida:
                # Pega a primeira linha correspondente à guia escolhida
                linha_dados = df[df["Guia Prestador"] == guia_escolhida].iloc[0]

                operadora = linha_dados.get("Operadora", "Operadora de Saúde")
                senha = linha_dados.get("Senha", "N/D")
                carteira = linha_dados.get("Carteira", "N/D")
                procedimento = linha_dados.get("Descrição Procedimento", "N/D")
                cod_glosa = linha_dados.get("Código Glosa", "N/D")
                valor_glosado = linha_dados.get("Valor Glosado (R$)", 0.0)

                texto_recurso = f"""À Operadora: {operadora}
Assunto: RECURSO DE GLOSA - SOLICITAÇÃO DE REVISÃO
--------------------------------------------------------------------------------
Prezados Senhores,

Venho por meio deste solicitar formalmente a revisão e reversão da glosa aplicada no atendimento abaixo especificado:

• Número da Guia (Prestador): {guia_escolhida}
• Número da Senha de Autorização: {senha}
• Número da Carteira do Beneficiário: {carteira}
• Procedimento / Item: {procedimento}
• Código da Glosa Informada: {cod_glosa}
• Valor Glosado: R$ {valor_glosado:,.2f}

JUSTIFICATIVA:
O procedimento em questão foi executado em estrita conformidade com as diretrizes técnicas e contratuais estabelecidas, amparado pela respectiva autorização prévia (senha informada acima). A retenção ou glosa do valor não se justifica, uma vez que toda a documentação comprobatória e a prestação do serviço ocorreram regular e tempestivamente.

Diante do exposto, solicitamos o cancelamento da referida glosa e a consequente liberação/pagamento do valor retido de R$ {valor_glosado:,.2f}.

Atenciosamente,
[Nome da Clínica / Prestador]
"""

                st.text_area("Minuta do Recurso:", value=texto_recurso, height=300)

                st.download_button(
                    label="📄 Baixar Texto do Recurso (.txt)",
                    data=texto_recurso,
                    file_name=f"Recurso_Guia_{guia_escolhida}.txt",
                    mime="text/plain"
                )

    except Exception as e:
        st.error(f"Erro ao processar o arquivo XML: {e}")