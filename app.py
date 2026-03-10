import streamlit as st
from db import get_connection

st.title("⚔️ SQLgard - Mestre do Jogo")

conn = get_connection()
cursor = conn.cursor()

cursor.execute("SELECT nome, classe, hp_atual, hp_max, status FROM TB_HEROIS")

herois = cursor.fetchall()

st.subheader("Heróis do Reino")

for h in herois:
    st.write(f"{h[0]} | {h[1]} | HP: {h[2]}/{h[3]} | Status: {h[4]}")

if st.button("Próximo Turno"):

    plsql = """
    DECLARE
        v_dano_nevoa NUMBER := 10;

        CURSOR c_herois IS
            SELECT id_heroi, hp_atual
            FROM TB_HEROIS
            WHERE status = 'ATIVO'
            FOR UPDATE;

    BEGIN

        FOR r IN c_herois LOOP

            UPDATE TB_HEROIS
            SET hp_atual = hp_atual - v_dano_nevoa
            WHERE id_heroi = r.id_heroi;

            UPDATE TB_HEROIS
            SET status = 'CAIDO'
            WHERE id_heroi = r.id_heroi
            AND hp_atual - v_dano_nevoa <= 0;

        END LOOP;

        COMMIT;

    END;
    """

    cursor.execute(plsql)
    conn.commit()

    st.success("Turno processado! A névoa causou dano nos heróis.")