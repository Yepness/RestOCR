from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import cv2
import pytesseract
import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route('/v1/RestOCR', methods=['POST'])
def rest_tessdata():
    app.logger.info("Rota '/v1/RestOCR' acessada.")

    keys_hg = ['image', 'type'] # Lista de parâmetros obrigatórios
    types_hg = ['data', 'string'] # Lista de possiveis valores type

    config_tesseract = '--psm 6'  # Configuração de Page Segmentation Mode a ser utilizada.

    try:
        # Verificação geral dos parâmetros obrigatórios:
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
            
            # Cria um diretório temporário para cada solicitação e salva o arquivo de imagem recebido:
            upload_folder = os.path.join(os.getcwd(), 'uploads')
            os.makedirs(upload_folder, exist_ok=True)

            image_path = os.path.join(upload_folder, image.filename)
            image.save(image_path)

            img = cv2.imread(image_path) # Realizar a leitura da imagem pelo OpenCV
            processGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # Converter a imagem para formato de cores na escala de cinza.

            # Transformar a imagem em texto tendo a saída em modo de dados.
            data = pytesseract.image_to_data(processGray, config=config_tesseract, lang="por")

            # Conversão da saída do Tesseract para um DataFrame
            dataList = list(map(lambda x: x.split('\t'),data.split('\n')))
            df = pd.DataFrame(dataList[1:],columns=dataList[0])
            df.dropna(inplace=True)
            df['conf'] = df['conf'].apply(pd.to_numeric, errors='coerce', downcast='integer')  # Converter para inteiros, permitindo valores NaN

            useFulData = df.query(f'conf >= {conf}') # Definir dados que serão utilizados com base na confiabilidade da extração

            text_values = []

            # Dataframe:
            File_DM = pd.DataFrame()
            File_DM['text'] = useFulData['text']

            for UsefulText in File_DM['text']:
                text_values.append(UsefulText)

            app.logger.info("Solicitação data, finalizado com sucesso!")

            # Excluir imagem do diretório temporário 
            if os.path.exists(image_path):
                os.remove(image_path)

            # Definir o tipo de conteúdo como json
            return jsonify(text_values), 200
        
        elif type.lower() == 'string':
            # Cria um diretório temporário para cada solicitação e salva o arquivo de imagem recebido:
            upload_folder = os.path.join(os.getcwd(), 'uploads')
            os.makedirs(upload_folder, exist_ok=True)

            image_path = os.path.join(upload_folder, image.filename)
            image.save(image_path)

            img = cv2.imread(image_path) # Realizar a leitura da imagem pelo OpenCV
            processGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # Converter a imagem para formato de cores na escala de cinza.

            # Transformar a imagem em texto tendo a saída em modo de dados.
            string = pytesseract.image_to_string(processGray, config=config_tesseract, lang="por")

            app.logger.info("Solicitação string, finalizado com sucesso!")

            # Excluir imagem do diretório temporário 
            if os.path.exists(image_path):
                os.remove(image_path)

            # Definir o tipo de conteúdo como text
            return (string), 200
    
    except Exception as e:
        app.logger.error("Erro ao executar o script rest_tessdata: " + str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
