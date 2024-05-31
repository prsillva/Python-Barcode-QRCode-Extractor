
# Extrator de Códigos de Barras e QR Code com Python

Este repositório contém um aplicativo web Flask para processar boletos. O aplicativo permite que os usuários insiram o caminho da pasta contendo os boletos, que são então processados para extrair informações relevantes. Este projeto utiliza o Tesseract OCR para a extração de informações adicionais.


## Estrutura do Projeto

O projeto tem a seguinte estrutura de diretórios e arquivos:

```
/
├── templates
│   ├── index.html
│   └── resultado.html
├── static
│   └── style.css
├── uploads
├─ app.py
├─ boleto_processor.py
└─ requirements.txt
```

## Configuração do Ambiente
Para configurar o ambiente, siga as etapas abaixo:

1. Clone o repositório.
2. Crie um ambiente virtual Python. Se você estiver usando o venv, você pode fazer isso com o seguinte comando:

```
python3 -m venv env
```
3. Ative o ambiente virtual. No Windows, use o seguinte comando:
```
.\env\Scripts\activate
```
No Unix ou MacOS, use o seguinte comando:
```
source env/bin/activate
```
4. Instale as dependências do projeto. As dependências estão listadas no arquivo requirements.txt. Você pode instalar as dependências usando pip com o seguinte comando:
```
pip install -r requirements.txt
```
5. Baixe e instale o Tesseract OCR. O Tesseract OCR é uma ferramenta de OCR (Optical Character Recognition) de código aberto que este projeto utiliza para extrair informações adicionais dos boletos. Você pode baixar o instalador do Tesseract OCR para Windows no link oficial do GitHub. Após baixar o instalador, execute-o e siga as instruções para instalar o Tesseract OCR no seu sistema.

6. Configure o caminho do Tesseract OCR no script. No script boleto_processor.py, há uma linha que define o caminho do executável do Tesseract OCR. Você deve ajustar essa linha para que ela aponte para o local onde você instalou o Tesseract OCR. Por exemplo, se você instalou o Tesseract OCR na pasta C:\Program Files\Tesseract-OCR, a linha deve ser:
### Python
```
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

```
## Como usar

1. Execute o script principal com o comando python app.py.

2. Abra um navegador e acesse http://localhost:5000 para ver a interface do usuário.

3. Insira o caminho da pasta contendo os boletos na interface do usuário.

4. Clique em ‘Processar’ para processar os boletos.


## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir uma issue ou enviar um pull request.


## 🚀 Sobre mim
Sou um profissional experiente com quase duas décadas na área de tecnologia, formado em Bacharelado em Ciência de Dados, Ciência da Computação e com MBA em Gestão de Projetos em T.I. Atualmente, estou cursando Pós-graduação em Estatística Aplicada.

