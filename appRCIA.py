import os
import google.generativeai as genai
from flask import Flask, request, jsonify

app = Flask(__name__)

# Lista de reserva caso a busca dinâmica falhe
PREFERRED_MODELS = [
    'gemini-2.0-flash-exp',
    'gemini-1.5-flash-8b',
    'gemini-1.5-flash',
    'gemini-2.0-flash',
    'gemini-2.5-flash',
    'gemini-3.6-flash',
    'gemini-1.5-pro'
]

def get_api_key():
    key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY') or os.environ.get('API_KEY')
    if key:
        return key.strip().strip('"').strip("'")
    return None

def find_available_models():
    """Consulta a API do Google para listar quais modelos aceitam perguntas nesta chave"""
    try:
        available = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                clean_name = m.name.replace('models/', '')
                available.append(clean_name)
        return available
    except Exception as e:
        print(f"Erro ao listar modelos do Gemini: {e}")
        return []

@app.route('/ask', methods=['POST'])
def ask_gemini():
    current_key = get_api_key()
    if not current_key:
        return jsonify({"error": "ERRO NO SERVIDOR: A variável GEMINI_API_KEY não foi configurada no Render."}), 500

    genai.configure(api_key=current_key)

    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({"error": "Nenhuma pergunta fornecida ('question')."}), 400

    question = data.get('question')

    # 1. Busca os modelos disponíveis para esta chave de API
    available_models = find_available_models()
    models_to_test = available_models if available_models else PREFERRED_MODELS

    last_error = None
    for model_name in models_to_test:
        try:
            print(f"Tentando modelo: {model_name}")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(question)
            if hasattr(response, 'text') and response.text:
                return jsonify({"answer": response.text}), 200
        except Exception as e:
            last_error = e
            print(f"Falha no modelo {model_name}: {e}")
            continue

    return jsonify({
        "error": f"Erro do Gemini: {str(last_error)}. Modelos testados: {models_to_test}"
    }), 500

@app.route('/health', methods=['GET'])
def health():
    key = get_api_key()
    available = []
    if key:
        try:
            genai.configure(api_key=key)
            available = find_available_models()
        except Exception as e:
            available = [f"Erro: {e}"]

    return jsonify({
        "status": "ok",
        "api_key_configurada": key is not None,
        "modelos_disponiveis_para_sua_chave": available
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)
