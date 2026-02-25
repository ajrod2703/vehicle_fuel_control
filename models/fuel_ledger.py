from odoo import models, fields, api

class FuelLedger(models.Model):
    _name = 'vehicle.fuel.ledger'
    _description = 'Fuel Ledger'
    _order = 'date desc, id desc'

    name = fields.Char(string='Reference', default='New', readonly=True)
    vehicle_id = fields.Many2one('vehicle.fuel.vehicle', string='Vehicle', required=True)
    date = fields.Datetime(string='Date', default=fields.Datetime.now, required=True)
    liters = fields.Float(string='Liters', required=True, digits=(16, 2))
    odometer = fields.Float(string='Odometer', digits=(16, 2))
    cost = fields.Float(string='Cost', digits=(16, 2))
    request_id = fields.Many2one('vehicle.fuel.request', string='Source Request', readonly=True, ondelete='restrict')
    user_id = fields.Many2one('res.users', string='Processed by', default=lambda self: self.env.user, required=True)
    notes = fields.Text(string='Notes')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('vehicle.fuel.ledger') or 'New'
        return super().create(vals_list)