import os
import traceback

import cv2
import pandas as pd
import pytesseract
from flask import Flask, jsonify, request
from flask_cors import CORS
from paddleocr import PaddleOCR

app = Flask(__name__)
CORS(app)

ocr_paddle = PaddleOCR()


def extract_paddle_texts(result):
    texts = []
    try:
        app.logger.info(f"Resultado PaddleOCR tipo: {type(result)}")
        if result and len(result) > 0:
            page_result = result[0]
            app.logger.info(
                f"Page result keys: {page_result.keys() if isinstance(page_result, dict) else 'Não é dict'}")

            if 'rec_texts' in page_result:
                texts = page_result['rec_texts']
                app.logger.info(
                    f"Encontrados {len(texts)} textos em rec_texts")
            else:
                app.logger.info(
                    "rec_texts não encontrado, tentando formato alternativo")
                for item in page_result:
                    if len(item) > 1:
                        texts.append(item[1][0])

        valid_texts = []
        for text in texts:
            if text is not None and str(text).strip():
                valid_texts.append(str(text).strip())

        app.logger.info(f"Textos válidos extraídos: {len(valid_texts)}")
        return valid_texts
    except Exception as e:
        app.logger.error(f"Erro ao extrair textos do PaddleOCR: {e}")
        app.logger.error(f"Traceback: {traceback.format_exc()}")
        return []


def format_paddle_string(paddle_texts, paddle_result):
    try:
        if not paddle_texts or not paddle_result or len(paddle_result) == 0:
            return ""

        page_result = paddle_result[0]

        if 'rec_boxes' in page_result:
            boxes = page_result['rec_boxes']
            app.logger.info(f"Usando {len(boxes)} boxes para formatação")

            text_positions = []
            for i, (text, box) in enumerate(zip(paddle_texts, boxes)):
                if text.strip():
                    y_avg = (box[1] + box[3]) / 2
                    x_avg = (box[0] + box[2]) / 2
                    text_positions.append((y_avg, x_avg, text))

                    # app.logger.debug(f"Texto '{text}': box={box}, y_avg={y_avg}, x_avg={x_avg}")

            text_positions.sort(key=lambda x: (x[0], x[1]))

            formatted_text = ""
            prev_y = None
            current_line_texts = []

            for y, x, text in text_positions:
                if prev_y is not None:
                    if abs(y - prev_y) > 30:
                        if current_line_texts:
                            formatted_text += " ".join(
                                current_line_texts) + "\n"
                            current_line_texts = []

                current_line_texts.append(text)
                prev_y = y

            if current_line_texts:
                formatted_text += " ".join(current_line_texts)

            return formatted_text.strip()

        else:
            app.logger.info("rec_boxes não encontrado, usando fallback")
            return " ".join(paddle_texts)

    except Exception as e:
        app.logger.error(f"Erro ao formatar string do PaddleOCR: {e}")
        app.logger.error(f"Traceback: {traceback.format_exc()}")
        return " ".join(paddle_texts) if paddle_texts else ""


@app.route('/v1/RestOCR', methods=['POST'])
def rest_ocr_combined():
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
        type_param = request.form['type']

        if image.filename == '':
            return jsonify({"error": "Nome do arquivo vazio"}), 400
        if type_param == '':
            return jsonify({"error": "valor de type vazio"}), 400
        elif type_param.lower() not in types_hg:
            return jsonify({"error": f"valor de type '{type_param}' não é um valor válido!"}), 400

        upload_folder = os.path.join(os.getcwd(), 'uploads')
        os.makedirs(upload_folder, exist_ok=True)

        image_path = os.path.join(upload_folder, image.filename)
        image.save(image_path)

        try:
            app.logger.info("Processando com PaddleOCR...")
            paddle_result = ocr_paddle.predict(image_path)
            app.logger.info(
                f"PaddleOCR processado. Tipo do resultado: {type(paddle_result)}")

            app.logger.info("Processando com Tesseract...")
            img = cv2.imread(image_path)
            process_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            if type_param.lower() == 'data':
                if 'conf' not in request.form:
                    return jsonify({"error": "Parâmetro obrigatório conf faltando!"}), 400

                conf = request.form['conf']
                if conf == '':
                    return jsonify({"error": "valor de conf vazio"}), 400
                elif conf.isdigit():
                    conf_value = int(conf)
                    if conf_value < 0 or conf_value > 100:
                        return jsonify({"error": f"valor de conf '{conf}' não é um valor válido!"}), 400
                else:
                    return jsonify({"error": f"valor de conf '{conf}' deve ser um número!"}), 400

                tesseract_data = pytesseract.image_to_data(
                    process_gray, config=config_tesseract, lang="por")

                data_list = list(map(lambda x: x.split(
                    '\t'), tesseract_data.split('\n')))
                df = pd.DataFrame(data_list[1:], columns=data_list[0])
                df.dropna(inplace=True)
                df['conf'] = df['conf'].apply(
                    pd.to_numeric, errors='coerce', downcast='integer')

                useful_data = df.query(f'conf >= {conf_value}')
                tesseract_texts = useful_data['text'].tolist()

                paddle_texts = extract_paddle_texts(paddle_result)
                app.logger.info(
                    f"PaddleOCR extraiu {len(paddle_texts)} textos")

                response = {
                    "tesseract": tesseract_texts,
                    "paddle": paddle_texts
                }

                app.logger.info("Solicitação data, finalizado com sucesso!")
                return jsonify(response), 200

            elif type_param.lower() == 'string':
                app.logger.info("Extraindo string do Tesseract...")
                tesseract_string = pytesseract.image_to_string(
                    process_gray, config=config_tesseract, lang="por")
                app.logger.info(
                    f"Tesseract string extraída: {len(tesseract_string)} caracteres")

                app.logger.info("Extraindo textos do PaddleOCR para string...")
                paddle_texts = extract_paddle_texts(paddle_result)
                app.logger.info(
                    f"PaddleOCR extraiu {len(paddle_texts)} textos para string")

                paddle_string = format_paddle_string(
                    paddle_texts, paddle_result)
                app.logger.info(
                    f"PaddleOCR string formatada: {len(paddle_string)} caracteres")

                response = {
                    "tesseract": tesseract_string.strip() if tesseract_string else "",
                    "paddle": paddle_string if paddle_string else ""
                }

                app.logger.info("Solicitação string, finalizado com sucesso!")
                return jsonify(response), 200

        finally:
            if os.path.exists(image_path):
                os.remove(image_path)

    except Exception as e:
        app.logger.error(
            "Erro ao executar o script rest_ocr_combined: " + str(e))
        app.logger.error("Traceback completo:")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
