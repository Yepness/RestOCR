from flask import Flask, jsonify, request
import subprocess
import os
import sys

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

        # Agora, você pode passar o caminho do arquivo para o subprocesso
        app.logger.info("Executando o script rest_tessdata")

        # Dentro da rota /rest_tessdata
        subprocess.Popen(['python', 'rest_tessdata.py', caminho_imagem], stdout=sys.stdout, stderr=sys.stderr)
        app.logger.info("rest_tessdata em execução.")

        return jsonify({"message": "Executando o script rest_tessdata"})
    except Exception as e:
        app.logger.error("Erro ao executar o script rest_tessdata: " + str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
