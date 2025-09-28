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
except Exception as e:
    # Em um ambiente de produção, você pode usar um logger.
    print(f"Erro na configuração da API Key: {e}")
    # O script pode parar aqui se a chave for essencial.
    # raise e

# 2. Cria a instância do aplicativo Flask.
app = Flask(__name__)

# 3. Cria o modelo do Gemini.
# 'gemini-2.0-flash-001' é o modelo estável disponível na API v1beta.
model = genai.GenerativeModel('gemini-2.0-flash-001')

# 4. Cria o endpoint para a nossa API.
# Este é o caminho que o seu aplicativo Android vai chamar.
@app.route('/ask', methods=['POST'])
def ask_gemini():
    # Pega os dados da requisição JSON que o app Android enviou.
    data = request.get_json()
    question = data.get('question')

    # Se a pergunta não foi fornecida, retorna um erro.
    if not question:
        return jsonify({"error": "No question provided"}), 400

    try:
        # Usa o modelo do Gemini para gerar uma resposta.
        response = model.generate_content(question)
        answer = response.text
        # Retorna a resposta em formato JSON para o app Android.
        return jsonify({"answer": answer})
    except Exception as e:
        # Se algo der errado, retorna um erro genérico.
        # Imprime o erro no console para depuração
        print(f"Erro ao gerar conteúdo com o Gemini: {e}")
        return jsonify({"error": str(e)}), 500

# 5. Roda o servidor.
# O host '0.0.0.0' permite que o servidor seja acessado de outros dispositivos na mesma rede.
if __name__ == '__main__':
    # Obtém a porta do Railway ou usa 5000 como padrão
    port = int(os.environ.get('PORT', 5000))
    
    # Adiciona a opção threaded=True para lidar com múltiplas requisições,
    # caso o app Android tente fazer mais de uma chamada ao mesmo tempo.
    app.run(host='0.0.0.0', port=port, threaded=True)
