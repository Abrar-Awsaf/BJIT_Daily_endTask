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
    
    amount_total = fields.Monetary(string="Total Amount", compute="_compute_total_price", store=True, currency_field="currency_id")

    @api.depends('order_line.price_unit', 'order_line.product_qty', 'order_line.delivery_charges_supplier')
    def _compute_total_price(self):
        """
        Compute total RFQ price from product lines.
        """
        for order in self:
            total = sum(
                (line.price_unit * line.product_qty) + (line.delivery_charges_supplier or 0)
                for line in order.order_line
            )
            order.amount_total = total

    @api.model
    def create(self, vals):
        """
        Ensure Vendor (partner_id) and Buyer (company_id) are properly set.
        """
        if 'partner_id' not in vals:
            vals['partner_id'] = self.env.user.partner_id.id  # ✅ Set Vendor
        if 'company_id' not in vals and 'rfp_id' in vals:
            rfp = self.env['rfp.management'].browse(vals['rfp_id'])
            vals['company_id'] = rfp.create_uid.company_id.id  # ✅ Set Buyer as RFP creator's company
        return super(RFQ, self).create(vals)

    # def action_recommend_supplier(self):
    #     """
    #     Recommend a supplier and ensure only one recommended per RFP.
    #     """
    #     if self.rfp_id and self.rfp_id.rfq_line_ids.filtered(lambda r: r.recommended):
    #         raise ValidationError("A supplier has already been recommended for this RFP.")
    #     self.recommended = True
    def action_recommend_rfq(self):
        """ ✅ Reviewer Marks the RFQ as Recommended """
        for rfq in self:
            rfq.recommended = True
            
    @api.model
    def _approver_rfq_domain(self):
        """ ✅ Ensure Approver Only Sees Recommended RFQs """
        return [('recommended', '=', True)]

        
    def action_update_score(self):
        """
        Compute RFQ Score Based on:
        - Delivery Date
        - Delivery Charges
        - Warranty Period
        """
        for rfq in self:
            score = 0
            # ✅ Score based on Delivery Date (earlier is better)
            if rfq.expected_delivery_date:
                days_to_delivery = (rfq.expected_delivery_date - fields.Date.today()).days
                score += max(0, 30 - days_to_delivery)  # Higher score for faster delivery

            # ✅ Score based on Delivery Charges (lower cost is better)
            total_delivery_charges = sum(rfq.order_line.mapped('delivery_charges_supplier'))
            if total_delivery_charges < 50:
                score += 20
            elif total_delivery_charges < 100:
                score += 10

            # ✅ Score based on Warranty Period (longer is better)
            if rfq.warranty_period >= 12:
                score += 30
            elif rfq.warranty_period >= 6:
                score += 15
            
            rfq.score = score
            
    def action_approve_rfq(self):
        """ ✅ Approver Can Accept One RFQ Per RFP """
        existing_approved_rfq = self.search([
            ('rfp_id', '=', self.rfp_id.id),
            ('state', '=', 'approved')
        ])
        if existing_approved_rfq:
            raise ValidationError("An RFQ has already been approved for this RFP.")

        # self.state = 'approved' 
        self.rfp_id._compute_total_amount()

class RFQProductLine(models.Model):
    _inherit = 'purchase.order.line'
    
    delivery_charges_supplier = fields.Float(string="Supplier Delivery Charges")