from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class FuelRequest(models.Model):
    _name = 'vehicle.fuel.request'
    _description = 'Fuel Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_request desc, id desc'

    name = fields.Char(string='Reference', default='New', readonly=True)
    vehicle_id = fields.Many2one('vehicle.fuel.vehicle', string='Vehicle', required=True, tracking=True)
    requester_id = fields.Many2one('res.users', string='Requester', default=lambda self: self.env.user, required=True, tracking=True)
    date_request = fields.Datetime(string='Request Date', default=fields.Datetime.now, required=True)
    liters = fields.Float(string='Liters', required=True, digits=(16, 2))
    odometer = fields.Float(string='Odometer', digits=(16, 2))
    notes = fields.Text(string='Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    ledger_id = fields.Many2one('vehicle.fuel.ledger', string='Ledger Entry', readonly=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('vehicle.fuel.request') or 'New'
        return super().create(vals_list)

    @api.constrains('liters')
    def _check_liters_positive(self):
        for record in self:
            if record.liters <= 0:
                raise ValidationError(_('The liters must be greater than zero.'))

    @api.constrains('odometer')
    def _check_odometer_positive(self):
        for record in self:
            if record.odometer and record.odometer < 0:
                raise ValidationError(_('The odometer cannot be negative.'))


    def action_approve(self):
        self.write({'state': 'approved'})

    def action_done(self):
        for record in self:
            if record.state != 'approved':
                raise UserError('Only approved requests can be marked as done.')
            ledger = self.env['vehicle.fuel.ledger'].create({
                'vehicle_id': record.vehicle_id.id,
                'date': fields.Datetime.now(),
                'liters': record.liters,
                'odometer': record.odometer,
                'request_id': record.id,
                'user_id': self.env.user.id,
                'notes': record.notes,
            })
            record.write({'state': 'done', 'ledger_id': ledger.id})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_open_mass_approve_wizard(self):
        """Open the mass approve wizard with the selected requests"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Mass Process',
            'res_model': 'vehicle.fuel.mass.approve.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_request_ids': [(6, 0, self.ids)],
            },
        }    