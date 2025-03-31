"""
Extend the functionality of the Odoo module category.

Provides support for a computed display name, automatically incorporating parent category names
if available, and to allow navigation and identification of categories within the Odoo interface.

:version: 1.0
"""

from typing import NoReturn

from odoo import api, fields, models


class ModuleCategory(models.Model):
    """
    Extends ir.module.category to add a computed, translatable display name.

    :ivar display_name: The computed, translatable display name of the category, defaults to None
    """

    _inherit = "ir.module.category"

    display_name = fields.Char(
        translate=True,
        compute="_compute_display_name",
        store=True,
    )

    @api.depends("name", "parent_id")
    def _compute_display_name(self) -> NoReturn:
        """Compute the display name of the category based on its name and its parent's."""
        for record in self:
            record.display_name = self._build_display_name(record)

    @api.model_create_multi
    def create(self, vals_list):
        """Override create method to set display_name."""
        recs = super().create(vals_list)
        for record in recs:
            record.display_name = self._build_display_name(record)
        return recs

    @api.model
    def _build_display_name(self, record):
        if not record.parent_id:
            return f"{record.name}"
        parent_path = self._build_display_name(record.parent_id)
        return f"{parent_path}/{record.name}"
