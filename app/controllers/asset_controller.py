from flask import request, jsonify
from app.services.asset_service import AssetService


class AssetController:
    @staticmethod
    def list_assets():
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        offset = (page - 1) * limit
        data = AssetService.list_assets(offset=offset, limit=limit)
        return jsonify(data), 200

    @staticmethod
    def create_asset():
        payload = request.get_json() or {}
        created = AssetService.create_asset(payload)
        return jsonify(created), 201

    @staticmethod
    def get_asset(asset_id: int):
        item = AssetService.get_asset(asset_id)
        if not item:
            return jsonify({'message': 'Not found'}), 404
        return jsonify(item), 200

    @staticmethod
    def update_asset(asset_id: int):
        payload = request.get_json() or {}
        updated = AssetService.update_asset(asset_id, payload)
        if not updated:
            return jsonify({'message': 'Not found'}), 404
        return jsonify(updated), 200

    @staticmethod
    def delete_asset(asset_id: int):
        ok = AssetService.delete_asset(asset_id)
        if not ok:
            return jsonify({'message': 'Not found'}), 404
        return '', 204
