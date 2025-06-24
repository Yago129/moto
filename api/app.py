from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

static_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

app = Flask(__name__, static_folder=static_folder_path)
CORS(app)

entregas = []
next_id = 1

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/nova_entrega', methods=['POST'])
def nova_entrega():
    global next_id
    try:
        data = request.json
        nova_entrega = {
            "id": next_id,
            "caixa_nome": data.get('caixa_nome', 'Desconhecido'),
            "nota": data.get('nota', ''),
            "taxa_entrega": data.get('taxa_entrega', 0.0),
            "data_hora": "Agora"
        }
        entregas.append(nova_entrega)
        next_id += 1
        return jsonify({"message": "Entrega registrada com sucesso", "entrega": nova_entrega}), 201
    except Exception as e:
        return jsonify({"error": f"Erro ao registrar entrega: {str(e)}"}), 500

@app.route('/relatorio', methods=['GET'])
def relatorio():
    try:
        total = sum(entrega['taxa_entrega'] for entrega in entregas)
        return jsonify({"entregas": entregas, "total": total}), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao gerar relatório: {str(e)}"}), 500

# Editar entrega pelo ID
@app.route('/editar_entrega/<int:id>', methods=['PUT'])
def editar_entrega(id):
    try:
        data = request.json
        for entrega in entregas:
            if entrega['id'] == id:
                entrega['caixa_nome'] = data.get('caixa_nome', entrega['caixa_nome'])
                entrega['nota'] = data.get('nota', entrega['nota'])
                entrega['taxa_entrega'] = data.get('taxa_entrega', entrega['taxa_entrega'])
                return jsonify({"message": "Entrega atualizada com sucesso", "entrega": entrega}), 200
        return jsonify({"error": "Entrega não encontrada"}), 404
    except Exception as e:
        return jsonify({"error": f"Erro ao atualizar entrega: {str(e)}"}), 500

# Excluir entrega pelo ID
@app.route('/excluir_entrega/<int:id>', methods=['DELETE'])
def excluir_entrega(id):
    try:
        global entregas
        entregas = [e for e in entregas if e['id'] != id]
        return jsonify({"message": "Entrega excluída com sucesso"}), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao excluir entrega: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
