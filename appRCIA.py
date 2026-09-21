import os
import google.generativeai as genai
from flask import Flask, request, jsonify

# 1. Configura a API Key do Gemini.
# A chave é lida de uma variável de ambiente, por segurança.
try:
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    genai.configure(api_key=GEMINI_API_KEY)
    print("API Key do Gemini configurada com sucesso!")
except Exception as e:
    print(f"Erro na configuração da API Key: {e}")
    # Em um ambiente de produção, o aplicativo deve sair se a chave não estiver configurada.
    # raise e

# 2. Cria a instância do aplicativo Flask.
app = Flask(__name__)

# 3. Cria o modelo do Gemini.
model = genai.GenerativeModel('gemini-pro')

# 4. Cria o endpoint para a nossa API.
@app.route('/ask', methods=['POST'])
def ask_gemini():
    # Adiciona um log no console do servidor para cada requisição recebida.
    print("Requisição recebida no endpoint /ask.")

    data = request.get_json()
    question = data.get('question')

    if not question:
        print("Erro: Nenhuma pergunta fornecida na requisição.")
        return jsonify({"error": "No question provided"}), 400

    try:
        print(f"Gerando conteúdo para a pergunta: '{question}'")
        response = model.generate_content(question)
        answer = response.text
        print(f"Resposta gerada pelo Gemini: '{answer}'")
        return jsonify({"answer": answer})
    except Exception as e:
        print(f"Erro ao gerar conteúdo com o Gemini: {e}")
        return jsonify({"error": str(e)}), 500

# 5. Roda o servidor.
# O host '0.0.0.0' permite que o servidor seja acessado de outros dispositivos na mesma rede.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)

