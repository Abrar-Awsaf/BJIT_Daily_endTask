from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo import http, _
from odoo.http import request, route
from odoo import fields
from collections import OrderedDict
import logging
_logger = logging.getLogger(__name__)

class SupplierRegistrationPortal(CustomerPortal):

    # @http.route(['/my/supplier/register'], type='http', auth='user', website=True)
    @http.route(['/my/supplier/register'], type="http", methods=['POST', 'GET'], auth="public", website=True, csrf=True)
    def register_supplier(self, **kw):
        error_list = []
        success_list = []
        if request.httprequest.method == 'POST':
            vals = {}
            keys = [
                'company_name', 'email', 'phone', 'company_registered_address', 'company_alternate_address',
                'company_type_category', 'company_type', 'trade_license_number',
                'tax_identification_number', 'commencement_date', 'expiry_date',
                'contact_person_title', 'contact_email', 'contact_phone',
                'finance_contact_title', 'finance_contact_email', 'finance_contact_phone',
                'authorized_person_name', 'authorized_person_email', 'authorized_person_phone',
                'bank_name', 'bank_address', 'bank_swift_code', 'account_name',
                'account_number', 'iban', 'company_address_as_per_bank', 'client_1_name',
                'client_1_address', 'client_1_contact_email',
                'client_1_contact_phone', 'client_2_name',
                'client_2_contact_email', 'client_2_contact_phone', 'client_3_name',
                'client_3_address', 'client_3_contact_email',
                'client_3_contact_phone', 'certification', 'certificate_number',
                'certifying_body', 'award_date', 'certificate_expiry_date'
            ]
            for key in keys:
                if kw.get(key):
                    vals[key] = kw.get(key)
            if kw.get('tax_identification_number') and (len(kw.get('tax_identification_number')) != 16 or not kw.get(
                    'tax_identification_number').isdigit()):
                error_list.append("Tax Identification Number Should Be Of 16 Digits And All Digits")
            if kw.get('trade_license_number') and (len(kw.get('trade_license_number')) < 8 or len(kw.get('tax_identification_number')) > 20 or not kw.get(
                    'trade_license_number').isdigit()):
                error_list.append("Trade License Number Should Be between 8 to 20 Digits And All Digits")
            if kw.get('expiry_date') and fields.Date.to_date(kw.get('expiry_date')) <= fields.date.today():
                error_list.append("Expiry Date Should Be Greater Than Today")
            if not kw.get('company_name'):
                error_list.append("Company Name is mandatory")
            if not kw.get('email'):
                error_list.append("Company Email is mandatory")
            if kw.get('email'):
                already_exists = request.env['res.partner'].sudo().search([('email', '=', kw.get('email'))])
                if already_exists:
                    error_list.append("Company Email Already Exists In the system. Try with another email")
            file_fields = [
                'trade_license_business_registration', 'certificate_of_incorporation', 'certificate_of_good_standing',
                'establishment_card', 'vat_tax_certificate', 'memorandum_of_association',
                'identification_document_for_authorized_person', 'bank_letter_indicating_bank_account',
                'past_2_years_audited_financial_statements', 'other_certifications'
            ]

            file_vals = {}
            for field in file_fields:
                if kw.get(field):
                    file_vals[field] = kw.get(field).read()
            vals['state'] = 'submitted'
            if not error_list:
                new_supplier = request.env['supplier.registration'].sudo().create(vals)
                # Send email notification to reviewers
                email_template = request.env.ref('procurement_management.email_supplier_registration_notification')
                if email_template:
                    try:
                        reviewer_emails = new_supplier.get_reviewers_emails()
                        if not reviewer_emails:
                            _logger.warning("No reviewer emails found. Email not sent.")
                        else:
                            _logger.info("Sending email to: %s", reviewer_emails)

                            # Email values (recipient and sender)
                            email_values = {
                                'email_to': reviewer_emails,
                                'email_from': 'abrar.awsaf@bjitacademy.com',
                            }

                            # Context for the template
                            ctx = {
                                'default_model': 'supplier.registration',  # Must match your model!
                                'default_res_id': new_supplier.id,  # Ensures the object is passed
                                'default_email_to': reviewer_emails,
                                'default_template_id': email_template.id,
                                'company_name': new_supplier.company_name,  # Pass supplier name
                                'email': new_supplier.email,  # Pass supplier email
                                'phone': new_supplier.phone,  # Pass supplier phone
                                'force_send': True,
                            }

                            # Send email with context and email_values
                            email_template.with_context(**ctx).sudo().send_mail(
                                new_supplier.id, email_values=email_values, force_send=True
                            )

                            _logger.info("Email successfully sent to: %s", reviewer_emails)

                    except Exception as e:
                        _logger.error("Error sending email: %s", str(e))
                if new_supplier:
                    success_list.append("Supplier Registered Successfully")
                if file_vals:
                    new_supplier.write(file_vals)

        return request.render("procurement_management.new_supplier_registration_form_view_portal",
                              {'page_name': 'supplier_registration',
                               'error_list': error_list,
                               'success_list': success_list})