from odoo import http
from odoo.http import request

class RfpDashboardController(http.Controller):
    @http.route('/rfp/dashboard/data', type='json', auth='user')
    def get_dashboard_data(self, supplier_id=None, date_range='last_30_days'):
        domain = []
        if supplier_id:
            domain.append(('approved_supplier_id', '=', int(supplier_id)))
        
        rfps = request.env['rfp.management'].search(domain)
        total_approved_rfqs = len(rfps)
        total_amount = sum(rfps.mapped('total_amount'))

        return {
            'keyMetrics': {
                'totalApprovedRFQs': total_approved_rfqs,
                'totalAmount': total_amount,
            },
            'rfqData': [],
            'productData': [],
        }
