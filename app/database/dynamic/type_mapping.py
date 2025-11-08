from sqlalchemy import String, Float, Date

from app.common.enums import SupportedFieldTypes

"""
Mapping between form field types and SQLAlchemy column types.
"""
SQLALCHEMY_TYPE_MAPPING = {
    SupportedFieldTypes.TEXT: String,
    SupportedFieldTypes.STRING: String,
    SupportedFieldTypes.EMAIL: String,
    SupportedFieldTypes.PASSWORD: String,
    SupportedFieldTypes.NUMBER: Float,
    SupportedFieldTypes.DATE: Date,
    SupportedFieldTypes.DROPDOWN: String,
}
