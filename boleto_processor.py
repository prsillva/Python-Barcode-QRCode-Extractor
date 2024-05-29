import os
import cv2
import pytesseract
from pdf2image import convert_from_path
from pyzbar.pyzbar import decode
import csv
import locale
from datetime import datetime, timedelta
import re

# Configurar o caminho do Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Ajuste conforme o caminho do seu sistema

# Função para extrair códigos de barras de imagens
def extrair_codigos_barras_imagem(caminho_imagem):
    imagem = cv2.imread(caminho_imagem)
    if imagem is not None:
        codigos_barras = decode(imagem)
        return [(codigo, None) for codigo in codigos_barras] if codigos_barras is not None else []
    return []

# Função para extrair códigos de barras de arquivos PDF
def extrair_codigos_barras_pdf(caminho_pdf):
    codigos_barras = []
    imagens_pdf = convert_from_path(caminho_pdf)
    for i, imagem_pdf in enumerate(imagens_pdf):
        imagem_temporaria = f'temp_{i}.jpg'
        imagem_pdf.save(imagem_temporaria)
        codigos_barras.extend([(codigo, i+1) for codigo in decode(cv2.imread(imagem_temporaria))])
        os.remove(imagem_temporaria)  # Remover a imagem temporária após a leitura
    return codigos_barras

# Função para listar arquivos em uma pasta
def listar_arquivos_pasta(pasta):
    arquivos = []
    for diretorio_raiz, _, arquivos_nome in os.walk(pasta):
        for arquivo_nome in arquivos_nome:
            arquivos.append(os.path.join(diretorio_raiz, arquivo_nome))
    return arquivos

# Função para converter código de barras em linha digitável
def converter_para_linha_digitavel(codigo_barras):
    if len(codigo_barras) != 44:
        return "Código de barras inválido"
    
    campo1 = codigo_barras[0:4] + codigo_barras[19:20] + codigo_barras[20:24]
    campo2 = codigo_barras[24:29] + codigo_barras[29:34]
    campo3 = codigo_barras[34:39] + codigo_barras[39:44]
    campo4 = codigo_barras[4:5]
    campo5 = codigo_barras[5:19]

    campo1 = campo1[:9] + str(calcular_dv(campo1))
    campo2 = campo2[:10] + str(calcular_dv(campo2))
    campo3 = campo3[:10] + str(calcular_dv(campo3))

    linha_digitavel = f"{campo1}{campo2}{campo3}{campo4}{campo5}"
    return linha_digitavel.replace(" ", "").replace(".", "")

# Função para calcular dígito verificador
def calcular_dv(campo):
    pesos = [2, 1]
    soma = 0
    for i, char in enumerate(reversed(campo)):
        multiplicacao = int(char) * pesos[i % 2]
        soma += multiplicacao // 10 + multiplicacao % 10
    resto = soma % 10
    dv = 10 - resto if resto != 0 else 0
    return dv

# Função para extrair valor e vencimento do código de barras
def extrair_valor_vencimento(codigo_barras):
    if len(codigo_barras) != 44:
        return "Código de barras inválido", "Data inválida"

    valor = int(codigo_barras[9:19]) / 100.0
    valor_formatado = formatar_valor_real(valor)
    fator_vencimento = int(codigo_barras[5:9])
    data_base = "07/10/1997"
    vencimento = calcular_data_vencimento(data_base, fator_vencimento)
    return valor_formatado, vencimento

# Função para formatar valor em Real brasileiro
def formatar_valor_real(valor):
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    valor_formatado = locale.currency(valor, grouping=True, symbol=None)
    return valor_formatado

# Função para calcular data de vencimento
def calcular_data_vencimento(data_base, fator_vencimento):
    data_base = datetime.strptime(data_base, "%d/%m/%Y")
    data_vencimento = data_base + timedelta(days=fator_vencimento)
    return data_vencimento.strftime("%d/%m/%Y")

# Função para extrair informações adicionais com OCR
def extrair_informacoes_adicionais(caminho_imagem):
    texto = pytesseract.image_to_string(caminho_imagem, lang='por')
    nome, cpf_cnpj = extrair_nome_cpf_cnpj(texto)
    return nome, cpf_cnpj

# Função para extrair o nome e CPF/CNPJ do beneficiário do texto
def extrair_nome_cpf_cnpj(texto):
    linhas = texto.split('\n')
    nome = "Nome não encontrado"
    cpf_cnpj = "CPF/CNPJ não encontrado"
    for linha in linhas:
        # Procurar a linha que contém o nome do beneficiário e possivelmente o CNPJ/CPF
        if any(kw in linha for kw in ['Beneficiário', 'Município', 'Órgão']):
            partes = linha.split(':')
            if len(partes) > 1:
                nome = partes[-1].strip()
            else:
                nome = linha.strip()

            # Tentar extrair o CNPJ/CPF desta linha
            cpf_cnpj_match = re.findall(r'\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b|\b\d{3}\.\d{3}\.\d{3}-\d{2}\b', linha)
            if cpf_cnpj_match:
                cpf_cnpj = cpf_cnpj_match[0]
            break

    # Caso não tenha encontrado o CNPJ/CPF na mesma linha do nome, procurar em linhas próximas
    if cpf_cnpj == "CPF/CNPJ não encontrado":
        for linha in linhas:
            cpf_cnpj_match = re.findall(r'\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b|\b\d{3}\.\d{3}\.\d{3}-\d{2}\b', linha)
            if cpf_cnpj_match:
                cpf_cnpj = cpf_cnpj_match[0]
                break

    return nome, cpf_cnpj

# Função para identificar se é um documento de arrecadação
def eh_documento_arrecadacao(codigo_barras):
    return codigo_barras[0] in ('8', '9')  # Supondo que documentos de arrecadação começam com 8 ou 9

# Função para extrair valor e vencimento de documentos de arrecadação
def extrair_valor_vencimento_arrecadacao(codigo_barras):
    if len(codigo_barras) != 44:
        return "Código de barras inválido", "Data inválida"

    valor = int(codigo_barras[4:15]) / 100.0  # Ajuste conforme o layout específico do código de barras de arrecadação
    valor_formatado = formatar_valor_real(valor)
    data_vencimento = "Data inválida"
    try:
        data_vencimento = codigo_barras[19:27]
        data_vencimento = datetime.strptime(data_vencimento, "%Y%m%d").strftime("%d/%m/%Y")
    except ValueError:
        pass
    return valor_formatado, data_vencimento

# Função para processar boletos
def processar_boletos(pasta):
    boletos = []
    for arquivo in listar_arquivos_pasta(pasta):
        if arquivo.lower().endswith(('.jpg', '.jpeg', '.png')):
            codigos_barras = extrair_codigos_barras_imagem(arquivo)
            nome, cpf_cnpj = extrair_informacoes_adicionais(arquivo)
        elif arquivo.lower().endswith('.pdf'):
            codigos_barras = extrair_codigos_barras_pdf(arquivo)
            nome = None
            cpf_cnpj = None
            imagens_pdf = convert_from_path(arquivo)
            for i, imagem_pdf in enumerate(imagens_pdf):
                imagem_temporaria = f'temp_{i}.jpg'
                imagem_pdf.save(imagem_temporaria)
                pagina_nome, pagina_cpf_cnpj = extrair_informacoes_adicionais(imagem_temporaria)
                if not nome or nome == "Nome não encontrado":
                    nome = pagina_nome
                if not cpf_cnpj or cpf_cnpj == "CPF/CNPJ não encontrado":
                    cpf_cnpj = pagina_cpf_cnpj
                os.remove(imagem_temporaria)
        else:
            continue

        print(f"Códigos de barras encontrados para '{arquivo}': {codigos_barras}")  # Adicionando esta linha
        
        if codigos_barras:
            for codigo, pagina in codigos_barras:
                print(f"Tipo de objeto de código de barras: {type(codigo)}")  # Adicionando esta linha
                codigo_barras_str = codigo.data.decode('utf-8')
                if eh_documento_arrecadacao(codigo_barras_str):
                    valor, vencimento = extrair_valor_vencimento_arrecadacao(codigo_barras_str)
                    linha_digitavel = "Não aplicável para documentos de arrecadação"
                    beneficiario = "Órgão/Município"
                    cpf_cnpj = ""
                else:
                    valor, vencimento = extrair_valor_vencimento(codigo_barras_str)
                    linha_digitavel = converter_para_linha_digitavel(codigo_barras_str)
                    beneficiario = nome
                
                boleto = {
                    'arquivo': arquivo,
                    'tipo': 'Imagem' if arquivo.lower().endswith(('.jpg', '.jpeg', '.png')) else 'PDF',
                    'codigo_barras': codigo_barras_str,
                    'linha_digitavel': linha_digitavel,
                    'valor': valor,
                    'vencimento': vencimento,
                    'pagina': pagina,
                    'nome': nome,
                    'cpf_cnpj': cpf_cnpj,
                    'beneficiario': beneficiario  # Variável para exibição no HTML
                }
                boletos.append(boleto)
        else:
            print(f"Nenhum código de barras detectado em '{arquivo}'.")
    return boletos

# Função para exportar boletos para CSV
def exportar_csv(boletos, caminho_arquivo):
    with open(caminho_arquivo, mode='w', newline='', encoding='utf-8') as arquivo_csv:
        fieldnames = ['arquivo', 'tipo', 'codigo_barras', 'linha_digitavel', 'valor', 'vencimento', 'pagina', 'nome', 'cpf_cnpj', 'beneficiario']
        writer = csv.DictWriter(arquivo_csv, fieldnames=fieldnames)
        writer.writeheader()
        for boleto in boletos:
            writer.writerow(boleto)

# Exemplo de uso
if __name__ == "__main__":
    pasta_boletos = "caminho_para_pasta_com_boletos"
    boletos = processar_boletos(pasta_boletos)
    caminho_arquivo_csv = "boletos_processados.csv"
    exportar_csv(boletos, caminho_arquivo_csv)
    print(f"Boletos exportados para {caminho_arquivo_csv}")
