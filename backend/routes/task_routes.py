from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from tasks import AsyncResult  # Adjust import based on your task location

def register_task_routes(app):
    @app.route('/task-status/<task_id>', methods=['GET'])
    @jwt_required()
    def get_task_status(task_id):
        current_user = get_jwt_identity()

        # Check user permissions
        if current_user['role'] not in ['Administrator', 'Security Staff']:
            return jsonify({'message': 'Unauthorized'}), 403

        # Retrieve task information using Celery's AsyncResult
        task_result = AsyncResult(task_id)

        if task_result.state == 'PENDING':
            response = {
                'state': task_result.state,
                'status': 'Pending...'
            }
        elif task_result.state != 'FAILURE':
            response = {
                'state': task_result.state,
                'status': task_result.info.get('status', ''),
                'results': task_result.info.get('results'),
                'image_path': task_result.info.get('image_path')
            }
        else:
            response = {
                'state': task_result.state,
                'status': str(task_result.info),  # Error message from task
            }

        return jsonify(response)
