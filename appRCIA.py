import os
import re
import google.generativeai as genai
from flask import Flask, request, jsonify

app = Flask(__name__)

# Instrução do sistema para garantir respostas diretas e em português
SYSTEM_INSTRUCTION = (
    "Você é um assistente virtual prestativo. "
    "Responda sempre em português do Brasil (pt-BR) de forma direta, clara e amigável. "
    "Não inclua análises, rascunhos nem pensamentos em inglês."
)

# Lista prioritária de modelos de texto estáveis
DEFAULT_MODELS = [
    'gemini-1.5-flash',
    'gemini-2.0-flash',
    'gemini-1.5-flash-latest',
    'gemini-1.5-pro'
]

# Cache em memória do modelo ativo (elimina latência nas requisições seguintes)
CACHED_WORKING_MODEL = None

def get_api_key():
    key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY') or os.environ.get('API_KEY')
    if key:
        return key.strip().strip('"').strip("'")
    return None

def find_text_models():
    """Retorna apenas modelos de texto válidos (ignora TTS, áudio e embeddings)"""
    try:
        valid_models = []
        for m in genai.list_models():
            clean_name = m.name.replace('models/', '')
            if 'generateContent' in m.supported_generation_methods:
                # Descarta modelos TTS, áudio, imagens ou embeddings que estouram cota
                if not any(bad in clean_name for bad in ['tts', 'embedding', 'audio', 'imagen', 'realtime']):
                    valid_models.append(clean_name)
        return valid_models if valid_models else DEFAULT_MODELS
    except Exception as e:
        print(f"Aviso ao listar modelos: {e}")
        return DEFAULT_MODELS

def clean_thought_process(text: str) -> str:
    """Remove resquícios de rascunhos em inglês se gerados por acidente"""
    if "The user" in text or "Option A" in text or "Greeting:" in text or "Always/Exclusively" in text:
        match = re.search(r'(Perfeito|Olá|Com certeza|Entendido|Vamos|Para |Aqui está|Como você|Se você|1\.|2\.|3\.)', text, re.IGNORECASE)
        if match:
            return text[match.start():].strip()
    return text.strip()

@app.route('/ask', methods=['POST'])
def ask_gemini():
    global CACHED_WORKING_MODEL
    
    current_key = get_api_key()
    if not current_key:
        return jsonify({"error": "ERRO NO SERVIDOR: GEMINI_API_KEY não encontrada no Render."}), 500

    genai.configure(api_key=current_key)

    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({"error": "Nenhuma pergunta fornecida ('question')."}), 400

    question = data.get('question')

    # 1. USA O MODELO EM CACHE (Resposta ultra rápida instantânea)
    if CACHED_WORKING_MODEL:
        try:
            model = genai.GenerativeModel(
                model_name=CACHED_WORKING_MODEL,
                system_instruction=SYSTEM_INSTRUCTION
            )
            response = model.generate_content(question)
            if hasattr(response, 'text') and response.text:
                return jsonify({"answer": clean_thought_process(response.text)}), 200
        except Exception as e:
            print(f"Modelo em cache {CACHED_WORKING_MODEL} falhou ({e}). Buscando novo modelo...")
            CACHED_WORKING_MODEL = None  # Invalida cache e reavalia

    # 2. SE NÃO HOUVER CACHE, BUSCA APENAS MODELOS DE TEXTO
    candidate_models = find_text_models()
    for m in DEFAULT_MODELS:
        if m not in candidate_models:
            candidate_models.append(m)

    last_error = None
    for model_name in candidate_models:
        try:
            print(f"Testando modelo de texto: {model_name}")
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=SYSTEM_INSTRUCTION
            )
            response = model.generate_content(question)
            if hasattr(response, 'text') and response.text:
                CACHED_WORKING_MODEL = model_name  # Salva o modelo ativo no cache!
                print(f"Sucesso! Modelo '{model_name}' salvo em cache.")
                return jsonify({"answer": clean_thought_process(response.text)}), 200
        except Exception as e:
            last_error = e
            print(f"Falha no modelo {model_name}: {e}")
            continue

    return jsonify({"error": f"Erro do Gemini: {str(last_error)}"}), 500

@app.route('/health', methods=['GET'])
def health():
    key = get_api_key()
    return jsonify({
        "status": "ok",
        "api_key_configurada": key is not None,
        "modelo_em_cache": CACHED_WORKING_MODEL
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)
