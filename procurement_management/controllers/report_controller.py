from odoo import http
from odoo.http import request

class RFPReportController(http.Controller):
    @http.route('/report/rfp_report/', type='http', auth='user', website=True)
    def generate_rfp_report(self, **kwargs):
        wizard = request.env['rfp.report.wizard'].browse(int(kwargs.get('wizard_id')))
        supplier = wizard.supplier_id
        start_date = wizard.start_date
        end_date = wizard.end_date

        # Get the approved RFPs based on the supplier and date range
        approved_rfps = request.env['rfp.management'].search([
            ('state', '=', 'accepted'),
            ('supplier_id', '=', supplier.id),
            ('required_date', '>=', start_date),
            ('required_date', '<=', end_date)
        ])

        # Get product lines for the approved RFPs
        product_lines = []
        for rfp in approved_rfps:
            for line in rfp.rfp_product_line_ids:
                product_lines.append(line)

        # Get company details
        company = request.env.user.company_id

        # Render the QWeb report template
        return request.render('procurement_management.rfp_report_html_template', {
            'supplier': supplier,
            'approved_rfps': approved_rfps,
            'product_lines': product_lines,
            'company': company,
        })
