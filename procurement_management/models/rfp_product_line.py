from odoo import models, fields, api

class RFPProductLine(models.Model):
    _name = 'rfp.product.line'  # Creating a custom model for RFP Product Lines
    _description = 'RFP Product Line'

    rfp_id = fields.Many2one('rfp.management', string='Related RFP', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    description = fields.Text(string='Description')
    quantity = fields.Integer(string='Quantity', required=True, default=1)
    unit_price = fields.Monetary(string='Unit Price', required=False, readonly=True)
    subtotal_price = fields.Monetary(string='Subtotal', compute='_compute_subtotal', store=True)
    delivery_charges = fields.Monetary(string='Delivery Charges', required=False)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    
    @api.depends('quantity', 'unit_price', 'delivery_charges')
    def _compute_subtotal(self):
        """
        Compute subtotal price as (quantity * unit price) + delivery charges.
        """
        for line in self:
            line.subtotal_price = (line.quantity * line.unit_price) + (line.delivery_charges or 0)