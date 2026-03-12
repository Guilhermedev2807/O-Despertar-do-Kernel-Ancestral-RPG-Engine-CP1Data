import os
import oracledb
from flask import Flask, render_template_string

# Força o modo Thin para a Vercel
oracledb.defaults.thin = True

app = Flask(__name__)

# COLOQUE SEU RM AQUI EM MAIÚSCULO (Ex: RM12345)
MEU_USUARIO = "RM566087" 

def get_connection():
    return oracledb.connect(
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        dsn=os.environ.get("DB_DSN")
    )

@app.route('/')
def index():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Tentamos selecionar usando o prefixo do seu RM para não ter erro
        sql = f"SELECT nome, classe, hp_atual, hp_max, status FROM {MEU_USUARIO}.TB_HEROIS ORDER BY nome"
        cursor.execute(sql)
        herois = cursor.fetchall()
        
        cursor.close()
        conn.close()

        html = """
        <body style="font-family: sans-serif; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 500px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <h1 style="color: #2c3e50; text-align: center;">⚔️ RPG - SQLgard</h1>
                <hr>
                {% for h in herois %}
                <div style="border-bottom: 1px solid #eee; padding: 10px 0;">
                    <strong>{{ h[0] }}</strong> ({{ h[1] }})<br>
                    HP: {{ h[2] }}/{{ h[3] }} - <span style="color: {{ 'red' if h[4] == 'CAÍDO' else 'green' }}">{{ h[4] }}</span>
                </div>
                {% endfor %}
                <form action="/processar" method="post" style="margin-top: 20px; text-align: center;">
                    <button type="submit" style="background: #e74c3c; color: white; border: none; padding: 10px 20px; cursor: pointer; border-radius: 5px;">
                        Atacar Heróis (PL/SQL)
                    </button>
                </form>
            </div>
        </body>
        """
        return render_template_string(html, herois=herois)
    except Exception as e:
        return f"<div style='color:red; padding:20px;'><h3>Erro no Banco:</h3>{str(e)}<br><br>Dica: Verifique se a tabela foi criada no RM correto.</div>"

@app.route('/processar', methods=['POST'])
def processar():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # PL/SQL ajustado com o seu usuário
        plsql = f"""
        DECLARE
            v_dano NUMBER := 10;
        BEGIN
            FOR r IN (SELECT id_heroi, hp_atual FROM {MEU_USUARIO}.TB_HEROIS WHERE status = 'ATIVO') LOOP
                IF r.hp_atual - v_dano <= 0 THEN
                    UPDATE {MEU_USUARIO}.TB_HEROIS SET hp_atual = 0, status = 'CAÍDO' WHERE id_heroi = r.id_heroi;
                ELSE
                    UPDATE {MEU_USUARIO}.TB_HEROIS SET hp_atual = hp_atual - v_dano WHERE id_heroi = r.id_heroi;
                END IF;
            END LOOP;
            COMMIT;
        END;
        """
        cursor.execute(plsql)
        cursor.close()
        conn.close()
        return "<h3>Dano aplicado com sucesso!</h3><a href='/'>Voltar</a>"
    except Exception as e:
        return f"<h3>Erro no Processamento:</h3>{str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
