# -*- coding: utf-8 -*-
{
    'name': "Procurement_management",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'portal', 'web', 'mail', 'purchase'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/ir_sequence.xml',
        'views/email_templates.xml',
        'views/supplier_portal.xml',
        'views/supplier_registration.xml',
        'views/supplier_purchase_view.xml',
        'views/supplier_purchase_after_reviewed_view.xml',
        'views/reviewer_rfp.xml',
        'views/approver_rfp.xml',
        'views/rfp_list_template.xml',
        'views/rfq_submission_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

