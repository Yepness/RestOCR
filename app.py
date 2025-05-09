import os

import cv2
import pandas as pd
import pytesseract
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/v1/RestOCR', methods=['POST'])
def rest_tessdata():
    app.logger.info("Rota '/v1/RestOCR' acessada.")

    keys_hg = ['image', 'type']
    types_hg = ['data', 'string']

    config_tesseract = '--psm 6'

    try:
        for key in keys_hg:
            if key not in request.files:
                if key not in request.form:
                    return jsonify({"error": f"Parâmetro obrigatório '{key}' faltando!"}), 400

        image = request.files['image']
        type = request.form['type']

        if image.filename == '':
            return jsonify({"error": "Nome do arquivo vazio"}), 400
        if type == '':
            return jsonify({"error": "valor de type vazio"}), 400
        elif type.lower() not in types_hg:
            return jsonify({"error": f"valor de type '{type}' não é um valor válido!"}), 400

        if type.lower() == 'data':

            if 'conf' not in request.form:
                return jsonify({"error": f"Parâmetro obrigatório conf faltando!"}), 400

            conf = request.form['conf']

            if conf == '':
                return jsonify({"error": "valor de conf vazio"}), 400
            elif conf.isdigit():
                conf_value = int(conf)
                if conf_value < 0 or conf_value > 100:
                    return jsonify({"error": f"valor de conf '{conf}' não é um valor válido!"}), 400

            upload_folder = os.path.join(os.getcwd(), 'uploads')
            os.makedirs(upload_folder, exist_ok=True)

            image_path = os.path.join(upload_folder, image.filename)
            image.save(image_path)

            img = cv2.imread(image_path)
            processGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            data = pytesseract.image_to_data(
                processGray, config=config_tesseract, lang="por")

            dataList = list(map(lambda x: x.split('\t'), data.split('\n')))
            df = pd.DataFrame(dataList[1:], columns=dataList[0])
            df.dropna(inplace=True)
            df['conf'] = df['conf'].apply(
                pd.to_numeric, errors='coerce', downcast='integer')

            useFulData = df.query(f'conf >= {conf}')

            text_values = []

            File_DM = pd.DataFrame()
            File_DM['text'] = useFulData['text']

            for UsefulText in File_DM['text']:
                text_values.append(UsefulText)

            app.logger.info("Solicitação data, finalizado com sucesso!")

            if os.path.exists(image_path):
                os.remove(image_path)

            return jsonify(text_values), 200

        elif type.lower() == 'string':
            upload_folder = os.path.join(os.getcwd(), 'uploads')
            os.makedirs(upload_folder, exist_ok=True)

            image_path = os.path.join(upload_folder, image.filename)
            image.save(image_path)

            img = cv2.imread(image_path)
            processGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            string = pytesseract.image_to_string(
                processGray, config=config_tesseract, lang="por")

            app.logger.info("Solicitação string, finalizado com sucesso!")

            if os.path.exists(image_path):
                os.remove(image_path)

            return (string), 200

    except Exception as e:
        app.logger.error("Erro ao executar o script rest_tessdata: " + str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run()
