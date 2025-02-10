from odoo import models, fields, api

class RFPProductLine(models.Model):
    _name = 'rfp.product.line'
    _description = 'RFP Product Line'

    rfp_id = fields.Many2one('rfp.management', string='Related RFP', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    description = fields.Text(string='Description')
    quantity = fields.Integer(string='Quantity', required=True, default=1)
    unit_price = fields.Monetary(string='Unit Price', required=False, readonly=True)
    subtotal_price = fields.Monetary(string='Subtotal', compute='_compute_subtotal', store=True)
    
    product_image = fields.Binary(string="Product Image", related="product_id.image_1920", store=True, readonly=True)
    
    # Fix: Rename supplier_delivery_charges to avoid label conflict
    delivery_charges_supplier = fields.Monetary(string='Supplier Delivery Charges', required=False)
    
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    @api.depends('quantity', 'unit_price', 'delivery_charges_supplier')
    def _compute_subtotal(self):
        """
        Compute subtotal price as (quantity * unit price) + delivery charges.
        """
        for line in self:
            line.subtotal_price = (line.quantity * line.unit_price) + (line.delivery_charges_supplier or 0)

    supplier_unit_price = fields.Float(string='Supplier Unit Price')
    supplier_total_price = fields.Float(string='Total Price', compute='_compute_total_price', store=True)

    @api.depends('supplier_unit_price', 'quantity', 'delivery_charges_supplier')
    def _compute_total_price(self):
        """
        Fix: Replace product_qty with quantity (correct field in this model).
        """
        for line in self:
            line.supplier_total_price = (line.supplier_unit_price * line.quantity) + (line.delivery_charges_supplier or 0)
