"""
Extend Odoo's ir.module.module model to include the category full name.

:version: 1.0
"""

from odoo import fields, models


class Module(models.Model):
    """
    Extends ir.module.module to include category full name.

    :ivar category_name: The full name of the category, defaults to None
    """

    _inherit = "ir.module.module"

    category_name = fields.Char(
        related="category_id.display_name",
        string="Category Full Name",
        store=True,
        readonly=True,
    )
