# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class PayrollPreparationLine(models.Model):
    _inherit = "payroll.preparation.line"

    commission_target_id = fields.Many2one("commission.target", index=True)
