from flask import Blueprint, render_template, request, jsonify
from app import db
from app.models import Graph

canvas_bp = Blueprint('canvas', __name__)


@canvas_bp.route('/')
def index():
    return render_template('canvas.html')


@canvas_bp.route('/api/list', methods=['GET'])
def list_graphs():
    graphs = Graph.query.order_by(Graph.created_at.desc()).all()
    result = []
    for g in graphs:
        result.append({
            'id': g.id,
            'name': g.name,
            'type': g.type,
            'created_at': g.created_at.strftime('%Y-%m-%d %H:%M') if g.created_at else ''
        })
    return jsonify(result)


@canvas_bp.route('/api/save', methods=['POST'])
def save_graph():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': '名称不能为空'}), 400
    graph = Graph(
        name=data['name'],
        type=data.get('type', 'graph'),
        data_json=data.get('data_json', '')
    )
    db.session.add(graph)
    db.session.commit()
    return jsonify({'id': graph.id, 'name': graph.name, 'message': '保存成功'})


@canvas_bp.route('/api/load/<int:graph_id>', methods=['GET'])
def load_graph(graph_id):
    graph = Graph.query.get_or_404(graph_id)
    return jsonify({
        'id': graph.id,
        'name': graph.name,
        'type': graph.type,
        'data_json': graph.data_json,
        'created_at': graph.created_at.strftime('%Y-%m-%d %H:%M') if graph.created_at else ''
    })


@canvas_bp.route('/api/delete/<int:graph_id>', methods=['DELETE'])
def delete_graph(graph_id):
    graph = Graph.query.get_or_404(graph_id)
    db.session.delete(graph)
    db.session.commit()
    return jsonify({'message': '删除成功'})
