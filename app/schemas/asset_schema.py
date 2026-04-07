from app import ma
from marshmallow import fields


class AssetSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    ticker = fields.Str(required=True)
    name = fields.Str()
    exchange = fields.Str()
    currency = fields.Str()
    sector = fields.Str()
    price = fields.Float()
    market_cap = fields.Float()
    last_price_update = fields.DateTime()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


asset_schema = AssetSchema()
assets_schema = AssetSchema(many=True)
