import os
import oracledb
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)


def get_connection():
    return oracledb.connect(
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        dsn=os.environ.get("DB_DSN")
    )

# Rota principal para mostrar os heróis
@app.route('/')
def index():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nome, classe, hp_atual, hp_max, status FROM TB_HEROIS")
    herois = cursor.fetchall()
    cursor.close()
    conn.close()

    # HTML simples para exibir os dados
    html = """
    <h1>Mestre do Jogo - SQLgard</h1>
    <ul>
    {% for h in herois %}
        <li>{{ h[0] }} ({{ h[1] }}) - HP: {{ h[2] }}/{{ h[3] }} - Status: {{ h[4] }}</li>
    {% endfor %}
    </ul>
    <form action="/processar" method="post"><button type="submit">Próximo Turno</button></form>
    """
    return render_template_string(html, herois=herois)


# Rota exigida pelo professor
@app.route('/processar', methods=['POST'])
def processar():
    conn = get_connection()
    cursor = conn.cursor()

    # O seu bloco PL/SQL que você já fez
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


if __name__ == '__main__':
    app.run(debug=True)