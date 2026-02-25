from odoo import models, fields

class Vehicle(models.Model):
    _name = 'vehicle.fuel.vehicle'
    _description = 'Vehicle'

    name = fields.Char(string='Name', required=True)
    license_plate = fields.Char(string='License Plate', required=True)
    model = fields.Char(string='Model')
    driver_id = fields.Many2one('res.partner', string='Driver/Owner')
    active = fields.Boolean(default=True)