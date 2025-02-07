from odoo import models, fields, api

class RFQ(models.Model):
    _inherit = 'purchase.order'

    rfp_id = fields.Many2one('rfp.management', string='Related RFP', required=False, ondelete='cascade')
    expected_delivery_date = fields.Date(string='Expected Delivery Date', required=True)
    
    # Fix: Rename terms_conditions to supplier_terms_conditions
    # supplier_terms_conditions = fields.Html(string='Supplier Terms and Conditions')
    
    warranty_period = fields.Integer(string='Warranty Period (Months)')
    score = fields.Integer(string='Score', default=0)
    recommended = fields.Boolean(string='Recommended')

    rfq_product_line_ids = fields.One2many('purchase.order.line', 'order_id', string='RFQ Product Lines')

    @api.depends('order_line.price_unit', 'order_line.product_qty', 'order_line.delivery_charges_supplier')
    def _compute_total_price(self):
        """
        Compute total RFQ price from product lines.
        """
        for order in self:
            total = sum((line.price_unit * line.product_qty) + (line.delivery_charges_supplier or 0) for line in order.order_line)
            order.amount_total = total



    def action_recommend_supplier(self):
        """
        Recommend a supplier and ensure only one recommended per RFP.
        """
        if self.rfp_id and self.rfp_id.rfq_line_ids.filtered(lambda r: r.recommended):
            raise ValidationError("A supplier has already been recommended for this RFP.")
        self.recommended = True

class RFQProductLine(models.Model):
    _inherit = 'purchase.order.line'  # Extending RFQ Product Lines
    
    delivery_charges_supplier = fields.Float(string="Supplier Delivery Charges")  # ✅ Corrected