import os
import oracledb
from flask import Flask, render_template_string

if os.environ.get('DB_USER'):
    oracledb.defaults.thin = True

# 1. ATIVAÇÃO DO MODO LEVE (THIN MODE) - OBRIGATÓRIO PARA VERCEL
oracledb.defaults.thin = True

app = Flask(__name__)

# 2. Função de conexão usando Variáveis de Ambiente
def get_connection():
    return oracledb.connect(
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        dsn=os.environ.get("DB_DSN")
    )

# 3. Rota principal para listar heróis
@app.route('/')
def index():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Busca os dados da sua tabela
        cursor.execute("SELECT nome, classe, hp_atual, hp_max, status FROM TB_HEROIS ORDER BY id_heroi")
        herois = cursor.fetchall()
        cursor.close()
        conn.close()

        # HTML simples para exibição
        html = """
        <body style="font-family: sans-serif; padding: 20px; background-color: #f4f4f4;">
            <h1 style="color: #2c3e50;">Mestre do Jogo - SQLgard</h1>
            <hr>
            <h3>Estado atual dos Heróis:</h3>
            <table border="1" style="width: 100%; border-collapse: collapse; background: white;">
                <tr style="background: #ecf0f1;">
                    <th>Nome</th><th>Classe</th><th>HP</th><th>Status</th>
                </tr>
                {% for h in herois %}
                <tr>
                    <td>{{ h[0] }}</td><td>{{ h[1] }}</td>
                    <td>{{ h[2] }}/{{ h[3] }}</td>
                    <td style="color: {{ 'red' if h[4] == 'CAÍDO' else 'green' }}; font-weight: bold;">{{ h[4] }}</td>
                </tr>
                {% endfor %}
            </table>
            <br>
            <form action="/processar" method="post">
                <button type="submit" style="padding: 15px; background: #e74c3c; color: white; border: none; cursor: pointer; border-radius: 5px;">
                    ⚔️ Rodar Turno (Executar PL/SQL)
                </button>
            </form>
        </body>
        """
        return render_template_string(html, herois=herois)
    except Exception as e:
        return f"<h2 style='color:red;'>Erro de Conexão:</h2><p>{str(e)}</p><p>Verifique suas Environment Variables na Vercel.</p>"

# 4. Rota para o Processamento (O requisito do seu exercício)
@app.route('/processar', methods=['POST'])
def processar():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Bloco PL/SQL Anônimo
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
        return "<h3>Turno Processado via PL/SQL!</h3><a href='/'>Voltar para o Painel</a>"
    except Exception as e:
        return f"<h2>Erro no PL/SQL:</h2>{str(e)}"

if __name__ == '__main__':
    app.run(debug=True)

