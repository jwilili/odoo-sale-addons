# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class AssignSalespersonByAreaWizard(models.Model):
    _name = "assign.salesperson.by.area.wizard"
    _description = "Assign Salesperson By Area Wizard"

    available_territory_ids = fields.Many2many(comodel_name="res.territory")
    available_salesperson_ids = fields.Many2many(comodel_name="res.users")
    is_several_salespersons = fields.Boolean()
    salesperson_id = fields.Many2one(comodel_name="res.users")
    wizard_msg = fields.Text(compute="_compute_wizard_msg")

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)

        active_record = self.get_active_record()
        territories = active_record.territory_ids
        salespersons = territories.mapped("salesperson_id")
        vals = {
            "available_territory_ids": [(6, 0, territories.ids)],
            "available_salesperson_ids": [(6, 0, salespersons.ids)],
            "is_several_salespersons": len(salespersons) > 1,
        }
        if len(salespersons) == 1:
            vals["salesperson_id"] = salespersons.id
        res.update(vals)
        return res

    @api.onchange("available_salesperson_ids")
    def _onchange_available_salesperson_ids(self):
        return {
            "domain": {
                "salesperson_id": [("id", "in", self.available_salesperson_ids.ids)]
            }
        }

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        if not self.salesperson_id:
            raise AssertionError("There is no salesperson")

        active_record = self.get_active_record()
        active_record["user_id"] = self.salesperson_id

    @api.multi
    def get_active_record(self):
        context = self._context
        active_model = context.get("active_model")
        active_id = context.get("active_id")
        if not (active_model and active_id):
            raise AssertionError("Missing active_model or active_id context.")

        active_record = self.env[context.get("active_model")].browse(
            context.get("active_id")
        )
        if not active_record.exists():
            raise AssertionError(
                "Cannot find any record with model '%s' and id '%s'." %
                (active_model, active_id)
            )
        return active_record

    @api.depends("available_territory_ids", "available_salesperson_ids")
    def _compute_wizard_msg(self):
        for wizard in self:
            wizard.wizard_msg = wizard._get_wizard_msg()

    def _get_wizard_msg(self):
        if len(self.available_salesperson_ids) == 1:
            related_territories = self.available_territory_ids.filtered(
                lambda r: r.salesperson_id == self.available_salesperson_ids
            )
            related_territories_names = ", ".join(
                related_territories.mapped("display_name")
            )
            return _(
                "%s will be assigned to the record. Do you want to continue?"
            ) % (
                "{} ({})".format(
                    self.available_salesperson_ids[0].display_name,
                    related_territories_names,
                )
            )
        elif len(self.available_salesperson_ids) > 1:
            return _(
                "Several salespersons could be assigned depending on the partner's "
                "territories. Please choose the right seller."
            )
        else:
            return _(
                "There is no salesperson to assign. The partner's territories "
                "might not be linked to any salesperson."
            )
