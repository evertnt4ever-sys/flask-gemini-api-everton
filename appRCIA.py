import os
import google.generativeai as genai
from flask import Flask, request, jsonify

app = Flask(__name__)

# Modelo atual e suportado pelo Google
MODEL_NAME = 'gemini-1.5-flash'

def get_api_key():
    # Busca a chave em diferentes nomes comuns de variáveis
    key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY') or os.environ.get('API_KEY')
    if key:
        return key.strip().strip('"').strip("'") # Remove aspas e espaços acidentais
    return None

@app.route('/ask', methods=['POST'])
def ask_gemini():
    current_key = get_api_key()
    
    # Se a chave não existir no Render, avisa com erro claro
    if not current_key:
        error_msg = "ERRO NO SERVIDOR: A variável de ambiente GEMINI_API_KEY não foi encontrada no Render."
        print(error_msg)
        return jsonify({"error": error_msg}), 500

    # Configura a API key
    genai.configure(api_key=current_key)

    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({"error": "Nenhuma pergunta fornecida ('question')."}), 400

    question = data.get('question')

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(question)
        
        if hasattr(response, 'text') and response.text:
            return jsonify({"answer": response.text}), 200
        else:
            return jsonify({"error": "O Gemini retornou uma resposta vazia."}), 500

    except Exception as e:
        print(f"Erro ao chamar Gemini: {e}")
        return jsonify({"error": f"Erro do Gemini: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health():
    key_exists = get_api_key() is not None
    return jsonify({
        "status": "ok",
        "model": MODEL_NAME,
        "api_key_configurada": key_exists
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)