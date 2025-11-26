# Reconhecimento de Placas Veiculares com OCR (OpenCV + Tesseract)

Este projeto implementa um sistema simples e funcional para **leitura de caracteres de placas veiculares** utilizando Python, OpenCV e Tesseract OCR.  
Ele faz captura de vídeo via webcam, pré-processa a imagem, recorta uma área central e aplica OCR apenas nela, aumentando significativamente a precisão da leitura.

---

## 🚀 Funcionalidades

- Captura de vídeo pela webcam em tempo real  
- Conversão automática para escala de cinza  
- Limiarização (threshold) para destacar caracteres  
- Recorte automático de uma **região central fixa de leitura**  
- OCR executado apenas dentro dessa área  
- Retorno do texto reconhecido diretamente no terminal  
- Visualização da área ativa em tempo real na tela

---

## 📂 Estrutura do Projeto

```
projeto-ocr-placas/
│── main.py
│── README.md
```

---

## 🛠 Tecnologias Utilizadas

- **Python 3.10+**
- **OpenCV** – processamento de imagem e captura da webcam  
- **Pytesseract (OCR)** – mecanismo Tesseract para reconhecimento de caracteres  
- **NumPy** – manipulação eficiente de matrizes  

---

## 📥 Instalação

Clone o repositório:

```bash
git clone https://github.com/SEU_USUARIO/ocr-reconhecimento-placas.git
cd ocr-reconhecimento-placas
```

Crie o ambiente virtual (opcional, recomendado):

```bash
python -m venv venv
venv/Scripts/activate  # Windows
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

---

## 📌 Instalando o Tesseract OCR

### Windows  
Baixe o instalador em:  
https://github.com/UB-Mannheim/tesseract/wiki

Após instalar, configure no código:

```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

---

## ▶ Como Executar

```bash
python main.py
```

A webcam abrirá e você verá um retângulo central indicando a área de leitura.  
Coloque uma placa dentro da área e o OCR será exibido diretamente no terminal.

Para encerrar, pressione **Q**.