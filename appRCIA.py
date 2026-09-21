import os
import google.generativeai as genai
from flask import Flask, request, jsonify

app = Flask(__name__)

# Lista de modelos prioritários na ordem de preferência
PREFERRED_MODELS = [
    'gemini-2.0-flash',
    'gemini-2.0-flash-001',
    'gemini-1.5-flash-latest',
    'gemini-1.5-flash'
]

def get_api_key():
    key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY') or os.environ.get('API_KEY')
    if key:
        return key.strip().strip('"').strip("'")
    return None

def get_working_model():
    # Tenta buscar dinamicamente os modelos disponíveis na sua conta do Google
    try:
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                name = model.name.replace('models/', '')
                if 'flash' in name:
                    return name
    except Exception as e:
        print(f"Aviso ao listar modelos: {e}")
    return 'gemini-2.0-flash'

@app.route('/ask', methods=['POST'])
def ask_gemini():
    current_key = get_api_key()
    if not current_key:
        error_msg = "ERRO NO SERVIDOR: A variável de ambiente GEMINI_API_KEY não foi encontrada no Render."
        print(error_msg)
        return jsonify({"error": error_msg}), 500

    genai.configure(api_key=current_key)

    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({"error": "Nenhuma pergunta fornecida ('question')."}), 400

    question = data.get('question')

    # Tenta os modelos prioritários sequencialmente
    last_error = None
    for model_name in PREFERRED_MODELS:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(question)
            if hasattr(response, 'text') and response.text:
                return jsonify({"answer": response.text}), 200
        except Exception as e:
            last_error = e
            print(f"Modelo {model_name} indisponível ({e}). Tentando próximo modelo...")
            continue

    # Tenta modelo detectado dinamicamente caso os prioritários falhem
    try:
        dynamic_model_name = get_working_model()
        model = genai.GenerativeModel(dynamic_model_name)
        response = model.generate_content(question)
        if hasattr(response, 'text') and response.text:
            return jsonify({"answer": response.text}), 200
    except Exception as e:
        last_error = e

    return jsonify({"error": f"Erro do Gemini: {str(last_error)}"}), 500

@app.route('/health', methods=['GET'])
def health():
    key = get_api_key()
    key_exists = key is not None
    active_model = "Não configurado"
    if key_exists:
        try:
            genai.configure(api_key=key)
            active_model = get_working_model()
        except Exception as e:
            active_model = f"Erro ao detectar: {e}"

    return jsonify({
        "status": "ok",
        "model": active_model,
        "api_key_configurada": key_exists
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)