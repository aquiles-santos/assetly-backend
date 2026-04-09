from flask import Blueprint
from app.controllers.asset_controller import AssetController

bp = Blueprint('assets', __name__)


@bp.route('/assets', methods=['GET'])
def list_assets():
        """List assets (delegates to AssetService). See docs/openapi.yaml for full spec."""
        return AssetController.list_assets()


@bp.route('/assets', methods=['POST'])
def create_asset():
        """Create an asset. See `docs/openapi.yaml` for request/response examples."""
        return AssetController.create_asset()


@bp.route('/assets/<int:asset_id>', methods=['GET'])
def get_asset(asset_id: int):
        """Get asset by ID. See `docs/openapi.yaml` for full response example."""
        return AssetController.get_asset(asset_id)


@bp.route('/assets/<int:asset_id>', methods=['PUT'])
def update_asset(asset_id: int):
        """Update asset. See `docs/openapi.yaml` for expected request/response and errors."""
        return AssetController.update_asset(asset_id)


@bp.route('/assets/<int:asset_id>', methods=['PATCH'])
def patch_asset(asset_id: int):
        """Partially update asset. Accepts partial fields and only updates provided ones."""
        return AssetController.patch_asset(asset_id)


@bp.route('/assets/<int:asset_id>', methods=['DELETE'])
def delete_asset(asset_id: int):
        """Delete asset. See `docs/openapi.yaml` for errors like `pending_syncs`."""
        return AssetController.delete_asset(asset_id)


@bp.route('/assets/<int:asset_id>/sync', methods=['POST'])
def sync_asset(asset_id: int):
        """Sync market data for an asset and return the updated asset, snapshot, and sync log."""
        return AssetController.sync_asset(asset_id)
