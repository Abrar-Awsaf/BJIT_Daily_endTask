from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo import http
from odoo.http import request

class OTPCustomerPortal(CustomerPortal):
    @http.route(['/my/otp'], type='http', auth='user', website=True)
    def my_otp_verification(self, **kw):
        return request.render('procurement_management.otp_verification_template', {
            'page_name': 'my_otp',
        })

    @http.route(['/my/otp/send'], type='http', auth='user', methods=['POST'], csrf=True, website=True)
    def send_otp(self, **kwargs):
        email = kwargs.get('email')
        if not email:
            return request.render('procurement_management.otp_verification_template', {
                'error': 'Email is required',
            })

        existing_user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
        if existing_user:
            return request.render('procurement_management.otp_verification_template', {
                'error': 'Email is already registered',
            })

        otp_record = request.env['supplier.otp'].sudo().generate_otp(email)
        if not otp_record:
            return request.render('procurement_management.otp_verification_template', {
                'error': 'Failed to generate OTP',
            })

        # Optionally send the OTP via email
        request.env['mail.mail'].sudo().create({
            'email_from': 'shahriar.ahmed@bjitacademy.com',
            'email_to': email,
            'subject': 'Your OTP Code',
            'body_html': f'<p>Your OTP code is: <strong>{otp_record.otp}</strong>. It is valid for 5 minutes.</p>'
        }).send()

        # Render the OTP input form
        return request.render('procurement_management.otp_verification_template', {
            'email': email,
            'show_otp_section': True,
        })

    @http.route(['/my/otp/verify'], type='http', auth='user', methods=['POST'], csrf=True, website=True)
    def verify_otp(self, **kwargs):
        email = kwargs.get('email')
        otp = kwargs.get('otp')

        if not email or not otp:
            return request.render('procurement_management.otp_verification_template', {
                'error': 'Email and OTP are required',
                'show_otp_section': True,
                'email': email,
            })

        valid = request.env['supplier.otp'].sudo().validate_otp(email, otp)
        if valid:
            return request.render('procurement_management.otp_verification_template', {
                'success': 'OTP verified. Proceeding to registration',
            })
        else:
            return request.render('procurement_management.otp_verification_template', {
                'error': 'Invalid OTP. Please try again.',
                'show_otp_section': True,
                'email': email,
            })