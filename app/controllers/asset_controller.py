from flask import request, jsonify
from app.services.asset_service import AssetService
import time


class AssetController:
    @staticmethod
    def list_assets():
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        offset = (page - 1) * limit

        # filters
        symbol = request.args.get('symbol')
        name = request.args.get('name')
        asset_type = request.args.get('asset_type')
        sector = request.args.get('sector')

        # sorting: use `sort` for field and `order` for direction (asc|desc)
        sort = request.args.get('sort')
        order = request.args.get('order', 'asc')

        data = AssetService.list_assets(
            offset=offset,
            limit=limit,
            symbol=symbol,
            name=name,
            asset_type=asset_type,
            sector=sector,
            order_by=sort,
            order_dir=order,
        )
        return jsonify(data), 200

    @staticmethod
    def create_asset():
        payload = request.get_json() or {}
        try:
            created = AssetService.create_asset(payload)
            return jsonify(created), 201
        except AttributeError:
            return jsonify({'error': 'invalid_json'}), 400
        except AssetService.ValidationError as e:
            return jsonify({'error': str(e)}), 400
        except AssetService.DuplicateError as e:
            return jsonify({'error': str(e)}), 409

    @staticmethod
    def get_asset(asset_id: int):
        item = AssetService.get_asset(asset_id)
        if not item:
            return jsonify({'message': 'Not found'}), 404
        return jsonify(item), 200

    @staticmethod
    def update_asset(asset_id: int):
        payload = request.get_json() or {}
        try:
            updated = AssetService.update_asset(asset_id, payload)
            if not updated:
                return jsonify({'message': 'Not found'}), 404
            return jsonify(updated), 200
        except AssetService.ValidationError as e:
            return jsonify({'error': str(e)}), 400
        except AssetService.DuplicateError as e:
            return jsonify({'error': str(e)}), 409

    @staticmethod
    def delete_asset(asset_id: int):
        try:
            ok = AssetService.delete_asset(asset_id)
        except AssetService.DeletionError as e:
            return jsonify({'error': str(e)}), 409
        except Exception:
            return jsonify({'error': 'internal_server_error'}), 500

        if not ok:
            return jsonify({'message': 'Not found'}), 404
        return '', 204

    @staticmethod
    def sync_asset(asset_id: int):
        # Trigger an asynchronous sync for the asset (best-effort placeholder)
        item = AssetService.get_asset(asset_id)
        if not item:
            return jsonify({'message': 'Not found'}), 404

        # In a real implementation this would enqueue a background job.
        job_id = f"sync-{asset_id}-{int(time.time())}"
        return jsonify({'message': 'sync_started', 'job_id': job_id}), 202
