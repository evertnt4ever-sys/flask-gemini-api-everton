import os
import re
import google.generativeai as genai
from flask import Flask, request, jsonify

app = Flask(__name__)

# Instrução do Sistema para proibir o modelo de exibir rascunhos ou pensamentos em inglês
SYSTEM_INSTRUCTION = """Você é um assistente virtual em português do Brasil (pt-BR).
REGRAS RÍGIDAS:
1. Responda SEMPRE E EXCLUSIVAMENTE em português do Brasil (pt-BR).
2. NUNCA inclua seu raciocínio interno, pensamentos, análises do prompt, planejamentos ou anotações em inglês.
3. Não mostre etapas como 'The user wants...', 'Option A:', 'Greeting:'.
4. Responda DIRETAMENTE com a resposta final limpa, educada e bem formatada para o usuário."""

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
    try:
        available = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                clean_name = m.name.replace('models/', '')
                available.append(clean_name)
        return available
    except Exception as e:
        print(f"Erro ao listar modelos: {e}")
        return []

def clean_thought_process(text: str) -> str:
    """Remove blocos de raciocínio interno se o modelo os gerar por acidente"""
    if "The user" in text or "Option A" in text or "Greeting:" in text or "Language:" in text:
        match = re.search(r'(Perfeito|Olá|Com certeza|Entendido|Vamos|Para |Aqui está|Como você|Se você|1\.|2\.|3\.)', text, re.IGNORECASE)
        if match:
            return text[match.start():].strip()
    return text.strip()

@app.route('/ask', methods=['POST'])
def ask_gemini():
    current_key = get_api_key()
    if not current_key:
        return jsonify({"error": "ERRO NO SERVIDOR: GEMINI_API_KEY não encontrada no Render."}), 500

    genai.configure(api_key=current_key)

    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({"error": "Nenhuma pergunta fornecida ('question')."}), 400

    question = data.get('question')

    available_models = find_available_models()
    models_to_test = available_models if available_models else PREFERRED_MODELS

    last_error = None
    for model_name in models_to_test:
        try:
            # Passa a system_instruction para forçar resposta direta em português
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=SYSTEM_INSTRUCTION
            )
            response = model.generate_content(question)
            if hasattr(response, 'text') and response.text:
                cleaned_text = clean_thought_process(response.text)
                return jsonify({"answer": cleaned_text}), 200
        except Exception as e:
            last_error = e
            print(f"Falha no modelo {model_name}: {e}")
            continue

    return jsonify({"error": f"Erro do Gemini: {str(last_error)}"}), 500

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
        "modelos_disponiveis": available
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)
