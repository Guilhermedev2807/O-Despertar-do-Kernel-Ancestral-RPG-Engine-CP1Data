import os
import oracledb
from flask import Flask, render_template_string

# --- FORÇA O MODO THIN (LEVE) LOGO NO INÍCIO ---
# Isso impede o erro DPI-1047 de acontecer na Vercel
oracledb.defaults.thin = True

app = Flask(__name__)

def get_connection():
    # Coleta as variáveis configuradas na Vercel
    user = os.environ.get("DB_USER")
    password = os.environ.get("DB_PASSWORD")
    dsn = os.environ.get("DB_DSN")
    
    return oracledb.connect(
        user=user,
        password=password,
        dsn=dsn
    )

@app.route('/')
def index():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Seleciona os heróis da tabela que você criou no SQL Developer
       # Exemplo: se seu RM for RM99999

        cursor.execute("SELECT nome, classe, hp_atual, hp_max, status FROM RM566087.TB_HEROIS ORDER BY nome")
        herois = cursor.fetchall()
        cursor.close()
        conn.close()

        html = """
        <body style="font-family: sans-serif; padding: 20px; background-color: #f0f2f5;">
            <div style="max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 10px; shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h1 style="color: #1a73e8; text-align: center;">⚔️ Mestre do Jogo - SQLgard</h1>
                <hr>
                <ul style="list-style: none; padding: 0;">
                {% for h in herois %}
                    <li style="padding: 10px; border-bottom: 1px solid #eee;">
                        <strong>{{ h[0] }}</strong> ({{ h[1] }}) <br>
                        HP: {{ h[2] }}/{{ h[3] }} | 
                        <span style="color: {{ 'red' if h[4] == 'CAÍDO' else 'green' }}; font-weight: bold;">{{ h[4] }}</span>
                    </li>
                {% endfor %}
                </ul>
                <form action="/processar" method="post" style="text-align: center; margin-top: 20px;">
                    <button type="submit" style="background: #d93025; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 16px;">
                        Próximo Turno (PL/SQL)
                    </button>
                </form>
            </div>
        </body>
        """
        return render_template_string(html, herois=herois)
    except Exception as e:
        return f"<div style='color:red; padding:20px;'><h3>Erro de Conexão:</h3>{str(e)}</div>"

@app.route('/processar', methods=['POST'])
def processar():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # O seu Bloco PL/SQL exigido pelo professor
        plsql = """
        DECLARE
            v_dano NUMBER := 10;
        BEGIN
            FOR r IN (SELECT id_heroi, hp_atual FROM TB_HEROIS WHERE status = 'ATIVO') LOOP
                IF r.hp_atual - v_dano <= 0 THEN
                    UPDATE TB_HEROIS SET hp_atual = 0, status = 'CAÍDO' WHERE id_heroi = r.id_heroi;
                ELSE
                    UPDATE TB_HEROIS SET hp_atual = hp_atual - v_dano WHERE id_heroi = r.id_heroi;
                END IF;
            END LOOP;
            COMMIT;
        END;
        """
        cursor.execute(plsql)
        cursor.close()
        conn.close()
        return "<h3>Turno Processado com Sucesso!</h3><a href='/'>Voltar para a arena</a>"
    except Exception as e:
        return f"<div style='color:red;'>Erro no Processamento: {str(e)}</div>"

if __name__ == '__main__':
    app.run(debug=True)

