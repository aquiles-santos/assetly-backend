from flask import Blueprint, jsonify, request

from app.services.asset_service import AssetService

bp = Blueprint('assets', __name__)


@bp.route('/assets', methods=['GET'])
def list_assets():
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        offset = (page - 1) * limit

        data = AssetService.list_assets(
                offset=offset,
                limit=limit,
                symbol=request.args.get('symbol'),
                name=request.args.get('name'),
                asset_type=request.args.get('asset_type'),
                sector=request.args.get('sector'),
                order_by=request.args.get('sort'),
                order_dir=request.args.get('order', 'asc'),
        )
        return jsonify(data), 200


@bp.route('/assets', methods=['POST'])
def create_asset():
        try:
                created = AssetService.create_asset(request.get_json() or {})
                return jsonify(created), 201
        except AttributeError:
                return jsonify({'error': 'invalid_json'}), 400
        except AssetService.ValidationError as exc:
                return jsonify({'error': str(exc)}), 400
        except AssetService.DuplicateError as exc:
                return jsonify({'error': str(exc)}), 409


@bp.route('/assets/<int:asset_id>', methods=['GET'])
def get_asset(asset_id: int):
        asset = AssetService.get_asset(asset_id)
        if not asset:
                return jsonify({'message': 'Not found'}), 404
        return jsonify(asset), 200


@bp.route('/assets/<int:asset_id>', methods=['PUT'])
def update_asset(asset_id: int):
        try:
                updated = AssetService.update_asset(asset_id, request.get_json() or {})
                if not updated:
                        return jsonify({'message': 'Not found'}), 404
                return jsonify(updated), 200
        except AssetService.ValidationError as exc:
                return jsonify({'error': str(exc)}), 400
        except AssetService.DuplicateError as exc:
                return jsonify({'error': str(exc)}), 409


@bp.route('/assets/<int:asset_id>', methods=['PATCH'])
def patch_asset(asset_id: int):
        try:
                updated = AssetService.patch_asset(asset_id, request.get_json() or {})
                if not updated:
                        return jsonify({'message': 'Not found'}), 404
                return jsonify(updated), 200
        except AssetService.ValidationError as exc:
                return jsonify({'error': str(exc)}), 400
        except AssetService.DuplicateError as exc:
                return jsonify({'error': str(exc)}), 409


@bp.route('/assets/<int:asset_id>', methods=['DELETE'])
def delete_asset(asset_id: int):
        if not AssetService.delete_asset(asset_id):
                return jsonify({'message': 'Not found'}), 404
        return '', 204


@bp.route('/assets/<int:asset_id>/sync', methods=['POST'])
def sync_asset(asset_id: int):
        try:
                result = AssetService.sync_asset(asset_id)
                if not result:
                        return jsonify({'message': 'Not found'}), 404
                return jsonify(result), 200
        except AssetService.SyncError as exc:
                return jsonify({'error': str(exc)}), 502
