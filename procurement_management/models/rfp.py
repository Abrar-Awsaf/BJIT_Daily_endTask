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
    expiry_date = fields.Date(string='Expiry Date', default=lambda self: fields.Date.today() + timedelta(days=7))
    
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
    recommended_rfq_line_ids = fields.One2many(
        'purchase.order', 'rfp_id',
        string='Recommended RFQs',
        compute='_compute_recommended_rfq_lines',
        store=False
    )
    selected_rfq_id = fields.Many2one(
        'purchase.order',
        string='Selected RFQ for PO',
        domain="[('rfp_id', '=', id), ('recommended', '=', True)]",
        help="The RFQ selected by the approver for purchase order creation."
    )

    @api.depends('rfq_line_ids.recommended')
    def _compute_recommended_rfq_lines(self):
        """ Compute only recommended RFQs """
        for rfp in self:
            rfp.recommended_rfq_line_ids = rfp.rfq_line_ids.filtered(lambda rfq: rfq.recommended)

    
    @api.model
    def create(self, vals):
        """
        Override create method to generate sequence number for RFP.
        """
        if self.env.user.has_group('procurement_management.group_supplier_approver'):
            raise UserError(_("Approvers cannot create RFPs. Only Reviewers can create them."))
        if vals.get('rfp_number', _("New")) == _("New"):
            vals['rfp_number'] = self.env['ir.sequence'].next_by_code(
                'parent.id.sequence') or _("New")
        return super(RFP, self).create(vals)
    
    @api.depends('selected_rfq_id.amount_total')
    def _compute_total_amount(self):
        """
        Compute the total amount based only on the selected RFQ.
        """
        for rfp in self:
            # If a final RFQ is selected, use its total amount; otherwise, default to 0.0.
            rfp.total_amount = rfp.selected_rfq_id.amount_total if rfp.selected_rfq_id else 0.0
    
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
        if not self.selected_rfq_id:
            raise exceptions.UserError("Please select one RFQ to accept.")
        self.selected_rfq_id.write({'state': 'purchase'})
        # Set the approved supplier field properly
        self.write({
            'status': 'accepted',
            'approved_supplier_id': self.selected_rfq_id.partner_id.id
        })
        
    




