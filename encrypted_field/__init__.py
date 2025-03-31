"""Import files (models)."""

from odoo import fields
from .encrypted_field import Encrypted

fields.Encrypted = Encrypted
