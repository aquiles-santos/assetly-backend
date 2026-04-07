from flask import Blueprint
from app.controllers.asset_controller import AssetController

bp = Blueprint('assets', __name__)


@bp.route('/assets', methods=['GET'])
def list_assets():
    return AssetController.list_assets()


@bp.route('/assets', methods=['POST'])
def create_asset():
    return AssetController.create_asset()


@bp.route('/assets/<int:asset_id>', methods=['GET'])
def get_asset(asset_id: int):
    return AssetController.get_asset(asset_id)


@bp.route('/assets/<int:asset_id>', methods=['PUT'])
def update_asset(asset_id: int):
    return AssetController.update_asset(asset_id)


@bp.route('/assets/<int:asset_id>', methods=['DELETE'])
def delete_asset(asset_id: int):
    return AssetController.delete_asset(asset_id)
