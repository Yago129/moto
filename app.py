from flask import Flask, request, jsonify
from flask_cors import CORS  # Importar suporte ao CORS
import sqlite3

app = Flask(__name__)
CORS(app)  # Habilitar CORS para permitir conexões externas

# Função para conectar ao banco de dados
def db_connection():
    conn = sqlite3.connect('entregas.db')
    conn.row_factory = sqlite3.Row
    return conn

# Criar a tabela se não existir
def criar_tabela():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entregas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            caixa_nome TEXT NOT NULL,
            nota TEXT NOT NULL,
            taxa_entrega REAL NOT NULL,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Endpoint para editar entrega pelo id
@app.route('/editar_entrega/<int:id>', methods=['PUT'])
def editar_entrega(id):
    try:
        data = request.json
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE entregas
            SET caixa_nome = ?, nota = ?, taxa_entrega = ?
            WHERE id = ?
        ''', (data['caixa_nome'], data['nota'], data['taxa_entrega'], id))
        conn.commit()
        conn.close()
        return jsonify({"message": "Entrega atualizada com sucesso"})
    except Exception as e:
        return jsonify({"error": f"Erro ao atualizar entrega: {str(e)}"}), 500

# Endpoint para excluir entrega pelo id
@app.route('/excluir_entrega/<int:id>', methods=['DELETE'])
def excluir_entrega(id):
    try:
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM entregas WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Entrega excluída com sucesso"})
    except Exception as e:
        return jsonify({"error": f"Erro ao excluir entrega: {str(e)}"}), 500

# Endpoint para registrar nova entrega
@app.route('/nova_entrega', methods=['POST'])
def nova_entrega():
    try:
        data = request.json
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO entregas (caixa_nome, nota, taxa_entrega)
            VALUES (?, ?, ?)
        ''', (data['caixa_nome'], data['nota'], data['taxa_entrega']))
        conn.commit()
        conn.close()
        return jsonify({"message": "Entrega registrada com sucesso"}), 201
    except Exception as e:
        return jsonify({"error": f"Erro ao registrar entrega: {str(e)}"}), 500

# Endpoint para gerar relatório (com filtro e incluindo id)
@app.route('/relatorio', methods=['GET'])
def relatorio():
    try:
        data_inicial = request.args.get('data_inicial')
        data_final = request.args.get('data_final')
        caixa_nome = request.args.get('caixa_nome')

        query = '''
            SELECT id, caixa_nome, nota, taxa_entrega, data_hora
            FROM entregas
            WHERE 1=1
        '''
        params = []

        if data_inicial:
            query += ' AND date(data_hora) >= ?'
            params.append(data_inicial)

        if data_final:
            query += ' AND date(data_hora) <= ?'
            params.append(data_final)

        if caixa_nome:
            query += ' AND caixa_nome = ?'
            params.append(caixa_nome)

        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        entregas = cursor.fetchall()
        total = sum([e['taxa_entrega'] for e in entregas])

        return jsonify({"entregas": [dict(e) for e in entregas], "total": total})
    except Exception as e:
        return jsonify({"error": f"Erro ao gerar relatório: {str(e)}"}), 500

if __name__ == '__main__':
    criar_tabela()
    app.run(debug=True, host='0.0.0.0')
