import sys
import cv2
import pytesseract

#
caminho_imagem = sys.argv[1]

# pytesseract on Heroku
pytesseract.pytesseract.tesseract_cmd = "/app/.apt/usr/bin/tesseract"

#
config_tesseract = '--psm 1'  # Configuração de Page Segmentation Mode a ser utilizada.

# Realizar a leitura da imagem pelo OpenCV
img = cv2.imread(caminho_imagem)

# Transformar a imagem em texto tendo a saída em modo de string.
resultStr = pytesseract.image_to_string(img, config=config_tesseract, lang="eng")

# Remover espaços em branco e imprimir o resultado
resultStr = resultStr.replace(" ", "").replace("\n", "")
print(f'Tess: {resultStr}')