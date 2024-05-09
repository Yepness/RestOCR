# API de Extração de Texto com Tesseract

## Descrição
Esta API fornece um serviço para realizar a extração de texto de imagens usando a biblioteca Tesseract OCR (Optical Character Recognition). Através desta API, os usuários podem enviar uma imagem e escolher entre dois tipos de extração: 'data' para obter os resultados como uma lista de texto com base na confiabilidade especificada, ou 'string' para obter o texto extraído diretamente.

## Uso
### Método
- POST

### URL
- http://127.0.0.1:5000/rest_tessdata

### Parâmetros de Requisição

| Parâmetro | Tipo   | Descrição                                                                                                 |
|-----------|--------|-----------------------------------------------------------------------------------------------------------|
| image     | Arquivo| Imagem contendo o texto a ser extraído.                                                                   |
| type      | String | Tipo de extração desejada. Pode ser 'data' ou 'string'.                                                   |
| conf      | Inteiro| (Obrigatório se type=data) Nível de confiabilidade em porcentagem para a extração de texto. Entre 0 e 100.|

### Respostas

| Código | Descrição                       | Corpo da Resposta                                  |
|--------|---------------------------------|-----------------------------------------------------|
| 200    | Sucesso                         | Lista de strings (se type=data) ou texto (se type=string)  |
| 400    | Requisição inválida             | Mensagem de erro descrevendo o problema encontrado. |
| 500    | Erro interno do servidor        | Mensagem de erro detalhada.                         |


- ### Exemplo de uso (Python)

import requests

url = 'http://127.0.0.1:5000/rest_tessdata'
files = {'image': open('example_image.jpg', 'rb')}
data = {'type': 'data', 'conf': '70'}

response = requests.post(url, files=files, data=data)
print(response.json())


- ### Requisição de Extração de Texto com Confiança Específica (type=data)

POST /rest_tessdata
Content-Type: multipart/form-data

image: [arquivo de imagem]
type: data
conf: 70

Resposta (200 OK):
[
    "Texto extraído 1",
    "Texto extraído 2",
    ...
]


- ### Requisição de Extração de Texto Geral (type=string)

POST /rest_tessdata
Content-Type: multipart/form-data

image: [arquivo de imagem]
type: string

Resposta (200 OK):
"Texto extraído"


- ### Observações

Certifique-se de fornecer os parâmetros obrigatórios corretamente.

A confiabilidade (conf) é uma medida de quão confiável é a extração do texto. Quanto maior o valor, mais restrito será o texto extraído, enquanto valores mais baixos podem resultar em mais texto, incluindo possíveis erros.

