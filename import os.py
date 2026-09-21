import os
import requests
import json

def test_with_your_api_key():
    """Testa o servidor com sua API key"""
    
    # Substitua pela sua API key real
    API_KEY = "AIzaSyD_nOC60ph6A08Qy-wx4coZ-1ULBNxf6IE"  # ← COLE SUA CHAVE AQUI
    
    if API_KEY == "SUA_API_KEY_AQUI":
        print("❌ ERRO: Você precisa colar sua API key real no código!")
        print("1. Acesse: https://aistudio.google.com/app/apikey")
        print("2. Crie uma API key")
        print("3. Substitua 'SUA_API_KEY_AQUI' pela chave real")
        return False
    
    # Configura a API key
    os.environ['GEMINI_API_KEY'] = API_KEY
    
    # Inicia o servidor em background
    import subprocess
    import time
    
    print("🔄 Iniciando servidor Flask...")
    server_process = subprocess.Popen(['python', 'appRCIA.py'], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE)
    
    # Aguarda o servidor iniciar
    time.sleep(3)
    
    # Testa o servidor
    url = "http://127.0.0.1:5000/ask"
    data = {"question": "Olá, você está funcionando?"}
    
    try:
        print("🔄 Testando comunicação...")
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCESSO! Servidor funcionando!")
            print(f"📝 Resposta: {result.get('answer', 'N/A')}")
            return True
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"❌ Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    finally:
        # Para o servidor
        server_process.terminate()
        print("🛑 Servidor parado")

if __name__ == "__main__":
    test_with_your_api_key()