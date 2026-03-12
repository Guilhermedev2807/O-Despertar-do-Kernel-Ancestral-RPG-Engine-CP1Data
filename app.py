import os
import oracledb
from flask import Flask, render_template_string

# Força o modo THIN (Leve) antes de qualquer outra coisa
# Isso resolve o erro DPI-1047 na Vercel
oracledb.defaults.thin = True

app = Flask(__name__)

def get_connection():
    # Pega as credenciais das variáveis de ambiente da Vercel
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
        cursor.execute("SELECT nome, classe, hp_atual, hp_max, status FROM TB_HEROIS ORDER BY nome")
        herois = cursor.fetchall()
        cursor.close()
        conn.close()

        html = """
        <body style="font-family: sans-serif; padding: 20px;">
            <h1>Mestre do Jogo - SQLgard</h1>
            <hr>
            <h3>Estado dos Heróis:</h3>
            <ul>
            {% for h in herois %}
                <li>{{ h[0] }} ({{ h[1] }}) - HP: {{ h[2] }}/{{ h[3] }} - <b>{{ h[4] }}</b></li>
            {% endfor %}
            </ul>
            <form action="/processar" method="post"><button type="submit">Próximo Turno</button></form>
        </body>
        """
        return render_template_string(html, herois=herois)
    except Exception as e:
        return f"<h3>Erro de Conexão:</h3><p>{str(e)}</p>"

@app.route('/processar', methods=['POST'])
def processar():
    try:
        conn = get_connection()
        cursor = conn.cursor()
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
        return "Turno Processado! <a href='/'>Voltar</a>"
    except Exception as e:
        return f"Erro no PL/SQL: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
