from odoo import models, fields, api
from odoo.exceptions import UserError

class MassApproveWizard(models.TransientModel):
    _name = 'vehicle.fuel.mass.approve.wizard'
    _description = 'Mass Approve Fuel Requests'

    request_ids = fields.Many2many('vehicle.fuel.request', string='Requests to Process')
    action = fields.Selection([
        ('approve', 'Approve'),
        ('done', 'Mark as Done'),
        ('cancel', 'Cancel')
    ], string='Action', required=True, default='approve')

    def action_apply(self):
        if not self.request_ids:
            raise UserError('Please select at least one request.')

        if self.action == 'approve':
            self.request_ids.action_approve()
        elif self.action == 'done':
            # Only approved requests can be done
            invalid = self.request_ids.filtered(lambda r: r.state != 'approved')
            if invalid:
                raise UserError('Only approved requests can be marked as done.')
            self.request_ids.action_done()
        elif self.action == 'cancel':
            self.request_ids.action_cancel()

        return {'type': 'ir.actions.act_window_close'}