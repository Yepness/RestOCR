from flask import Flask, jsonify, request
import os
import sys
import cv2
import pytesseract

app = Flask(__name__)

@app.route('/rest_tessdata', methods=['POST'])
def rest_tessdata():
    app.logger.info("Rota '/rest_tessdata' acessada.")

    try:
        # Verifica se a solicitação contém um arquivo chamado 'imagem'
        if 'imagem' not in request.files:
            return jsonify({"error": "Nenhum arquivo enviado"}), 400

        imagem = request.files['imagem']

        # Verifica se o nome do arquivo está vazio
        if imagem.filename == '':
            return jsonify({"error": "Nome do arquivo vazio"}), 400

        # Cria um diretório temporário para cada solicitação
        upload_folder = os.path.join(os.getcwd(), 'uploads')
        os.makedirs(upload_folder, exist_ok=True)

        # Salva o arquivo no diretório temporário
        caminho_imagem = os.path.join(upload_folder, imagem.filename)
        imagem.save(caminho_imagem)

        # Baixar e configurar o Tesseract no Heroku
        pytesseract.pytesseract.tesseract_cmd = '/app/.apt/usr/bin/tesseract'
        tessdata_dir_config = '--tessdata-dir "/app/.apt/usr/share/tesseract-ocr/4.00/tessdata"'

        #
        config_tesseract = '--psm 1'  # Configuração de Page Segmentation Mode a ser utilizada.

        # Realizar a leitura da imagem pelo OpenCV
        img = cv2.imread(caminho_imagem)

        # Transformar a imagem em texto tendo a saída em modo de string.
        resultStr = pytesseract.image_to_string(img, config=config_tesseract, lang="eng")

        # Remover espaços em branco e imprimir o resultado
        resultStr = resultStr.replace(" ", "").replace("\n", "")
        print(f'Tess: {resultStr}')

        app.logger.info(f"{resultStr}")
        return jsonify({"message": f"{resultStr}"})
    
    except Exception as e:
        app.logger.error("Erro ao executar o script rest_tessdata: " + str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
