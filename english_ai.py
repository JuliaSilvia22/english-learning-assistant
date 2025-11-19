import os
import json
from flask import Flask, render_template, request, redirect, url_for
from openai import OpenAI
from openai import APIError # Importa para tratamento de erros específicos

# Configuração do Flask
app = Flask(__name__, template_folder='templates')

# --- VARIÁVEIS DE CONFIGURAÇÃO (OpenAI) ---
# A chave da API será lida da variável de ambiente OPENAI_API_KEY.
API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Inicializa o cliente da OpenAI
try:
    client = OpenAI(api_key=API_KEY)
except Exception as e:
    print(f"Erro ao inicializar o cliente OpenAI: {e}")
    client = None # Define como None se a inicialização falhar

# A persona da Teacher Ju (FLUIDA, CONVERSACIONAL E COM GÍRIAS)
SYSTEM_PERSONA = """
Você é a Teacher Ju, a sua best friend de inglês! Seu jeito de falar é super descontraído, usa GÍRIAS (tipo "mano", "tipo", "uau", "rolou um errinho"), muitos emojis e fala como uma amiga próxima. Seu objetivo é dar o feedback de forma rápida, pouca formalidade e muito motivacional.

Sua resposta deve ser um ÚNICO fluxo de conversa sempre que possível, super natural e que flua como um bate-papo:
1. Comece com uma introdução muito animada e informal, usando gírias.
2. Integre a CORREÇÃO (em inglês) e a EXPLICAÇÃO (em português) na conversa, explicando o que rolou de forma bem simplificada e com gírias.
3. Termine com uma pergunta em INGLÊS para manter o papo rolando.

Mantenha a resposta o mais CONCISA e divertida possível. Não use numeração, bullet points, títulos ou qualquer formalidade.
"""

# Função para chamar a API da OpenAI
def get_correction_from_openai(prompt):
    if not client:
        return "Erro: O cliente OpenAI não foi inicializado. Verifique se a chave da API está configurada (OPENAI_API_KEY)."
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # Modelo rápido e eficiente para esta tarefa
            messages=[
                {"role": "system", "content": SYSTEM_PERSONA},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
        )
        
        # Extrai o texto da resposta
        text_content = response.choices[0].message.content
        
        return text_content
        
    except APIError as e:
        # Tratamento de erros de API, como chave inválida ou limite de taxa
        print(f"Erro da API OpenAI: {e}")
        return f"Erro: Houve um problema com a API da OpenAI. Verifique sua chave ou saldo. Detalhe: {e.status_code} - {e.response.text}"
    except Exception as e:
        # Tratamento de erros gerais
        print(f"Erro inesperado na aplicação: {e}")
        return f"Erro: Ocorreu um erro inesperado na aplicação. Detalhe: {e}"


# --- ROTAS DO FLASK ---

@app.route('/')
def index():
    return render_template("index.html", correction=None, user_input="")

@app.route('/answer', methods=['POST'])
def answer():
    user_input = request.form.get('user_answer', '').strip()

    if not user_input:
        return redirect(url_for('index'))

    prompt = f"Corrija e responda este texto: '{user_input}'"
    correction = get_correction_from_openai(prompt)

    return render_template("index.html", correction=correction, user_input=user_input)

# --- INICIALIZAÇÃO DO SERVIDOR (COM CORREÇÃO PARA ACESSO EXTERNO) ---
if __name__ == '__main__':
    # Roda o servidor em 0.0.0.0 para que ele seja acessível pela rede local (Wi-Fi)
    app.run(debug=True, host='0.0.0.0') 
