from odoo import models, fields, api

class RFQ(models.Model):
    _inherit = 'purchase.order'  # Ensure correct inheritance from Odoo's built-in purchase.order
    
    rfp_id = fields.Many2one('rfp.management', string='Related RFP', required=False, ondelete='cascade')
    expected_delivery_date = fields.Date(string='Expected Delivery Date', required=True)
    terms_conditions = fields.Html(string='Terms and Conditions')
    warranty_period = fields.Integer(string='Warranty Period (Months)')
    score = fields.Integer(string='Score', default=0)
    recommended = fields.Boolean(string='Recommended')
    
    @api.depends('order_line.price_total')
    def _compute_total_price(self):
        """
        Compute total price from order lines.
        """
        for order in self:
            order.amount_total = sum(order.order_line.mapped('price_total'))
    
    def action_recommend_supplier(self):
        """
        Recommend a supplier and ensure only one recommended per RFP.
        """
        if self.rfp_id and self.rfp_id.rfq_line_ids.filtered(lambda r: r.recommended):
            raise ValidationError("A supplier has already been recommended for this RFP.")
        self.recommended = True
