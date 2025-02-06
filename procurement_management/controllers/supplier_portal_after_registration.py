from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from datetime import date

class RFQPortal(CustomerPortal):
    
    @http.route(['/my/rfp'], type='http', auth='user', website=True)
    def view_rfp_list(self, **kwargs):
        """
        Display a list of approved RFPs that are not closed (expiry date not passed).
        """
        rfp_domain = [('status', '=', 'approved'), ('expiry_date', '>=', date.today())]
        
        rfp_list = request.env['rfp.management'].sudo().search(rfp_domain)
        return request.render('procurement_management.rfp_list_template', {'rfps': rfp_list})
    
    @http.route(['/my/rfp/submit/<int:rfp_id>'], type='http', auth='user', website=True)
    def submit_rfq_form(self, rfp_id, **kwargs):
        """
        Render RFQ submission form for a selected RFP.
        """
        rfp = request.env['rfp.management'].sudo().browse(rfp_id)
        if not rfp or rfp.status != 'approved' or rfp.expiry_date < date.today():
            return request.render('website.404')
        return request.render('procurement_management.rfq_submission_template', {'rfp': rfp})
    
    @http.route(['/my/rfp/submit'], type='http', auth='user', website=True, methods=['POST'])
    def submit_rfq(self, **post):
        """
        Handle RFQ submission by suppliers with validation.
        """
        supplier = request.env.user.partner_id
        rfp_id = int(post.get('rfp_id'))
        rfp = request.env['rfp.management'].sudo().browse(rfp_id)
        
        if not rfp or rfp.status != 'approved' or rfp.expiry_date < date.today():
            return request.render('website.404')
        
        # Validation
        if not post.get('expected_delivery_date'):
            return request.render('procurement_management.rfq_submission_template', {
                'rfp': rfp,
                'error_message': 'Expected delivery date is required.'
            })
        
        if not post.get('terms_conditions'):
            return request.render('procurement_management.rfq_submission_template', {
                'rfp': rfp,
                'error_message': 'Terms and Conditions are required.'
            })
        
        if not post.get('warranty_period').isdigit():
            return request.render('procurement_management.rfq_submission_template', {
                'rfp': rfp,
                'error_message': 'Warranty period must be a valid number.'
            })
        
        # Create RFQ linked to the RFP
        rfq_vals = {
            'rfp_id': rfp.id,
            'partner_id': supplier.id,
            'expected_delivery_date': post.get('expected_delivery_date'),
            'terms_conditions': post.get('terms_conditions'),
            'warranty_period': int(post.get('warranty_period', 0)),
            'state': 'draft',
        }
        new_rfq = request.env['purchase.order'].sudo().create(rfq_vals)
        
        return request.render('procurement_management.rfq_submission_template', {
            'rfp': rfp,
            'success_message': 'RFQ submitted successfully.'
        })

    @http.route(['/my'], type='http', auth='user', website=True)
    def portal_my_home(self, **kw):
        """
        Extend the portal home menu to include RFP menu.
        """
        values = super(RFQPortal, self).portal_my_home(**kw)
        values.update({
            'rfp_menu': True
        })
        return request.render("portal.portal_my_home", values)
