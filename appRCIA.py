import os
import google.generativeai as genai
from flask import Flask, request, jsonify

# Configura a API Key
API_KEY = "AIzaSyD0V0Kp2AD7x903s-hIhyTFKiRUHoKC86M"
genai.configure(api_key=API_KEY)

# Cria a instância do Flask
app = Flask(__name__)

# Cria o modelo
model = genai.GenerativeModel('gemini-2.0-flash-001')

@app.route('/ask', methods=['POST'])
def ask_gemini():
    try:
        # Pega os dados da requisição
        data = request.get_json()
        question = data.get('question')
        
        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        # Gera a resposta com instruções para formato limpo
        clean_instructions = "Responda de forma clara e direta, sem usar formatação markdown (sem **, *, #, etc.). Use apenas texto simples e limpo."
        full_question = f"{clean_instructions}\n\n{question}"
        
        response = model.generate_content(full_question)
        answer = response.text
        
        return jsonify({"answer": answer})
        
    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "model": "gemini-2.0-flash-001"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
