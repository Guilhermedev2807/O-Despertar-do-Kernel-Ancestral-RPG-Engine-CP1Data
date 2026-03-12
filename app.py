import os
import oracledb
from flask import Flask, render_template_string

# 1. Inicializa o Flask
app = Flask(__name__)


# 2. Função de conexão usando Variáveis de Ambiente
def get_connection():
    # O modo "Thin" é obrigatório para a Vercel funcionar com Oracle
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
        cursor.execute("SELECT nome, classe, hp_atual, hp_max, status FROM TB_HEROIS ORDER BY id_heroi")
        herois = cursor.fetchall()
        cursor.close()
        conn.close()

        # HTML simples para exibir os dados
        html = """
        <body style="font-family: sans-serif; padding: 20px;">
            <h1>Mestre do Jogo - SQLgard</h1>
            <hr>
            <h3>Estado atual dos Heróis:</h3>
            <ul>
            {% for h in herois %}
                <li>
                    <strong>{{ h[0] }}</strong> ({{ h[1] }}) - 
                    HP: {{ h[2] }}/{{ h[3] }} - 
                    <span style="color: {{ 'red' if h[4] == 'CAÍDO' else 'green' }}">{{ h[4] }}</span>
                </li>
            {% endfor %}
            </ul>
            <form action="/processar" method="post">
                <button type="submit" style="padding: 10px; cursor: pointer;">Próximo Turno (Drenar HP)</button>
            </form>
        </body>
        """
        return render_template_string(html, herois=herois)
    except Exception as e:
        return f"Erro ao conectar no banco: {str(e)}"


# 4. Rota para processar o PL/SQL (Requisito do professor)
@app.route('/processar', methods=['POST'])
def processar():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Bloco PL/SQL Anônimo conforme solicitado
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
        return "Turno Processado com sucesso via PL/SQL! <br><br> <a href='/'>Voltar para a lista</a>"
    except Exception as e:
        return f"Erro no processamento: {str(e)}"


if __name__ == '__main__':
    app.run(debug=True)

    #versão final