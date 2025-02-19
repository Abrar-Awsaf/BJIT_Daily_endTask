from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import io
import xlsxwriter

class RFPReportWizard(models.TransientModel):
    _name = "rfp.report.wizard"
    _description = "RFP Report Wizard"

    supplier_id = fields.Many2one(
        "res.partner", 
        string="Supplier", 
        required=True, 
        domain=[("supplier_rank", ">", 0)]
    )
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)

    def action_generate_html_report(self):
        if self.start_date > self.end_date:
            raise UserError(_("Start date must be before or equal to end date."))
        # We let the QWeb template handle dynamic filtering.
        return self.env.ref('procurement_management.report_action_rfp_supplier').report_action(self)

    def action_generate_excel_report(self):
        if self.start_date > self.end_date:
            raise UserError(_("Start date must be before or equal to end date."))

        # Section 2: Approved RFPs
        approved_rfps = self.env['rfp.management'].search([
            ('approved_supplier_id', '=', self.supplier_id.id),
            ('status', '=', 'accepted'),
            ('expiry_date', '>=', self.start_date),
            ('expiry_date', '<=', self.end_date),
        ])
        if not approved_rfps:
            raise UserError(_("No approved RFPs found for this supplier within the selected date range."))

        net_total = sum(rfp.total_amount for rfp in approved_rfps)

        # Section 3: Product Lines
        po_lines = self.env['purchase.order.line'].search([
            ('order_id.rfp_id.approved_supplier_id', '=', self.supplier_id.id)
        ])
        grouped_products = {}
        for line in po_lines:
            prod_name = line.product_id.name
            if prod_name not in grouped_products:
                grouped_products[prod_name] = {
                    'quantity': 0,
                    'unit_price': 0,
                    'delivery_charge': 0,
                    'subtotal': 0,
                }
            grouped_products[prod_name]['quantity'] += line.product_qty
            grouped_products[prod_name]['unit_price'] += line.price_unit
            grouped_products[prod_name]['delivery_charge'] += line.delivery_charges_supplier or 0
            grouped_products[prod_name]['subtotal'] += line.price_subtotal

        total_product = sum(item['subtotal'] for item in grouped_products.values())

        # Section 1 & 4: Company and Supplier Information
        company = self.env.user.company_id
        if not company.logo:
            raise UserError(_("The current company does not have a logo. Please add a logo before generating the report."))

        # Create an in-memory Excel file
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet("RFP Report")

        # Define common formats
        title_format = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center'})
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D9D9D9', 'border': 1})
        cell_format = workbook.add_format({'border': 1, 'align': 'left'})
        date_format = workbook.add_format({'border': 1, 'num_format': 'dd/mm/yyyy'})
        currency_format = workbook.add_format({'border': 1, 'num_format': '$#,##0.00'})

        row = 0
        # === Section 1: Company Logo & Supplier Information ===
        worksheet.write(row, 0, "RFP Supplier Report", title_format)
        row += 2

        # Insert company logo at top left
        logo_data = base64.b64decode(company.logo)
        logo_buffer = io.BytesIO(logo_data)
        worksheet.insert_image(row, 0, "company_logo.png", {"image_data": logo_buffer, "x_scale": 1, "y_scale": 1})

        # Write supplier name (title) next to the logo (starting at column D)
        worksheet.write(row, 3, self.supplier_id.name or "Vendor Report", title_format)
        row += 2

        # Supplier information including banking details
        supplier_info = [
            ("Email", self.supplier_id.email or "N/A"),
            ("Phone", self.supplier_id.phone or "N/A"),
            ("Address", self.supplier_id.company_registered_address or "N/A"),
            ("TIN", self.supplier_id.tax_identification_number or "N/A"),
            ("Trade License No.", self.supplier_id.trade_license_number or "N/A"),
        ]
        # Optionally add bank details if available.
        if self.supplier_id.bank_ids:
            bank = self.supplier_id.bank_ids[0]
            supplier_info.extend([
                ("Bank Name", bank.bank_id.name if bank.bank_id else "N/A"),
                ("Account Name", bank.acc_holder_name or "N/A"),
                ("Account Number", bank.acc_number or "N/A"),
                ("IBAN", bank.bank_id.iban if bank.bank_id else "N/A"),
                ("SWIFT Code", bank.bank_id.bank_swift_code if bank.bank_id else "N/A"),
            ])
        else:
            supplier_info.extend([
                ("Bank Name", "N/A"),
                ("Account Name", "N/A"),
                ("Account Number", "N/A"),
                ("IBAN", "N/A"),
                ("SWIFT Code", "N/A"),
            ])

        for label, value in supplier_info:
            worksheet.write(row, 3, label, cell_format)
            worksheet.write(row, 4, value, cell_format)
            row += 1

        row += 1  # Gap before next section

        # === Section 2: Approved RFPs ===
        worksheet.write(row, 0, "Approved RFPs", title_format)
        row += 2
        rfp_headers = ["RFP Number", "Creation Date", "Expiry Date", "Total Amount"]
        for col, header in enumerate(rfp_headers):
            worksheet.write(row, col, header, header_format)
        row += 1
        for rfp in approved_rfps:
            worksheet.write(row, 0, rfp.rfp_number, cell_format)
            worksheet.write(row, 1, rfp.create_date.strftime("%d/%m/%Y"), date_format)
            worksheet.write(row, 2, rfp.expiry_date.strftime("%d/%m/%Y"), date_format)
            worksheet.write(row, 3, rfp.total_amount, currency_format)
            row += 1
        worksheet.write(row, 2, "Net Total:", header_format)
        worksheet.write(row, 3, net_total, header_format)
        row += 2

        # === Section 3: Grouped Product Line Summary ===
        worksheet.write(row, 0, "Product Line Summary", title_format)
        row += 2
        prod_headers = ["Product Name", "Total Quantity", "Unit Price", "Delivery Charge", "Subtotal Price"]
        for col, header in enumerate(prod_headers):
            worksheet.write(row, col, header, header_format)
        row += 1
        for prod, vals in grouped_products.items():
            worksheet.write(row, 0, prod, cell_format)
            worksheet.write(row, 1, vals['quantity'], cell_format)
            worksheet.write(row, 2, vals['unit_price'], currency_format)
            worksheet.write(row, 3, vals['delivery_charge'], currency_format)
            worksheet.write(row, 4, vals['subtotal'], currency_format)
            row += 1
        worksheet.write(row, 3, "Total Price:", header_format)
        worksheet.write(row, 4, total_product, header_format)
        row += 2

        # === Section 4: Company Contact Information ===
        worksheet.write(row, 0, "Company Contact Information", title_format)
        row += 2
        comp_info = [
            ("Email", company.email or "N/A"),
            ("Phone", company.phone or "N/A"),
            ("Address", company.partner_id.contact_address or "N/A")
        ]
        for label, value in comp_info:
            worksheet.write(row, 0, label, cell_format)
            worksheet.write(row, 1, value, cell_format)
            row += 1

        workbook.close()
        output.seek(0)
        attachment = self.env['ir.attachment'].create({
            'name': 'rfp_report.xlsx',
            'datas': base64.b64encode(output.read()),
            'res_model': self._name,
            'res_id': self.id,
            'type': 'binary',
        })
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }