from odoo import models, fields, api, exceptions, _
from datetime import timedelta

class RFP(models.Model):
    _name = 'rfp.management'  # Creating a custom RFP model
    _description = 'Request for Purchase (RFP)'
    _rec_name = 'rfp_number'
    _order = 'create_date desc'

    # Auto-generated RFP Number using Odoo's sequence
    rfp_number = fields.Char(string='RFP Number', required=True, copy=False, readonly=True, default='New')
    
    # Status field with required workflow
    status = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('closed', 'Closed'),
        ('recommendation', 'Recommendation'),
        ('accepted', 'Accepted')
    ], string='Status', default='draft', tracking=True,)
    
    # RFP Expiry Date: After this date, suppliers cannot submit RFQs
    expiry_date = fields.Date(string='Expiry Date', required=True, default=lambda self: fields.Date.today() + timedelta(days=7))
    
    # Total Amount: Computed from accepted RFQ lines
    total_amount = fields.Monetary(string='Total Amount', compute='_compute_total_amount', store=True)
    
    # Approved Supplier: Can only be set by Approver
    approved_supplier_id = fields.Many2one('res.partner', string='Approved Supplier', domain=[('supplier_rank', '>', 0)], readonly=True)
    
    # Currency field (inherited from company settings)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    
    # Chatter log for tracking changes
    message_ids = fields.One2many('mail.message', 'res_id', domain=[('model', '=', 'rfp.management')], string='Messages')
    message_follower_ids = fields.One2many('mail.followers', 'res_id', domain=[('res_model', '=', 'rfp.management')], string='Followers')
    
    # Product Lines: One2many field for listing required products
    product_line_ids = fields.One2many('rfp.product.line', 'rfp_id', string='Product Lines')
    
    # RFQ Lines: One2many field for submitted supplier quotations
    rfq_line_ids = fields.One2many('purchase.order', 'rfp_id', string='RFQ Lines')
    
    @api.model
    def create(self, vals):
        """
        Override create method to generate sequence number for RFP.
        """
        if vals.get('rfp_number', _("New")) == _("New"):
            vals['rfp_number'] = self.env['ir.sequence'].next_by_code(
                'parent.id.sequence') or _("New")
        return super(RFP, self).create(vals)
    
    @api.depends('rfq_line_ids.amount_total')
    def _compute_total_amount(self):
        """
        Compute total amount based on the accepted RFQ lines.
        """
        for rfp in self:
            accepted_rfq = rfp.rfq_line_ids.filtered(lambda rfq: rfq.state == 'approved')
            rfp.total_amount = sum(accepted_rfq.mapped('amount_total'))
    
    # Reviewer Actions
    def action_submit(self):
        """
        Submit RFP for approval.
        """
        self.write({'status': 'submitted'})
        # Notify Approvers (Email Notification Logic to be added later)
    
    def action_return_to_draft(self):
        """
        Return RFP to Draft for modifications.
        """
        self.write({'status': 'draft'})
    
    def action_recommend(self):
        """
        Mark RFP as recommended.
        """
        if not self.rfq_line_ids.filtered(lambda rfq: rfq.recommended):
            raise exceptions.UserError("At least one RFQ must be recommended before recommendation.")
        self.write({'status': 'recommendation'})
        
        
    # Approver Actions
    
    def action_approve(self):
        """ Approve RFP """
        self.write({'status': 'approved'})

    def action_reject(self):
        """ Reject RFP """
        self.write({'status': 'rejected'})

    def action_close(self):
        """ Close RFP """
        self.write({'status': 'closed'})

    def action_accept(self):
        """ Accept RFP and create PO from Approved RFQ """
        if not self.approved_supplier_id:
            raise exceptions.UserError("No approved supplier selected.")

        # Create PO
        self.env['purchase.order'].create({
            'partner_id': self.approved_supplier_id.id,
            'rfp_id': self.id,
            'order_line': [(0, 0, {
                'product_id': line.product_id.id,
                'name': line.description,
                'product_qty': line.quantity,
                'price_unit': line.unit_price,
                'date_planned': fields.Date.today(),
            }) for line in self.rfq_line_ids]
        })
        self.write({'status': 'accepted'})
