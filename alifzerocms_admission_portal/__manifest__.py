# -*- encoding: utf-8 -*-
{
    'name': 'University Admission Portal',
    'summary': 'University Online Admission Application.',
    'category': 'alifzerocms',
    'version': '15.0',
    'license': 'LGPL-3',
    'category': 'alifzerocms',
    'sequence': 4,
    'author': 'Alif Zero',
    'company': 'Alif Zero',
    'website': 'http://www.alifzero.com/',
    'depends': ['website_partner', 'website_mail', 'website', 'base_setup', 'auth_signup', ],
    'data': [
        'security/ir.model.access.csv',
        'views/admission_application/personal_detail.xml',
        'views/admission_application/contact_detail.xml',
        'views/admission_application/guardian_detail.xml',
        'views/admission_application/quota_detail.xml',
        'views/admission_application/program_choices.xml',
        'views/admission_application/test_center.xml',
        'views/admission_application/fee_voucher.xml',
        'views/admission_application/education_detail.xml',
        'views/admission_application/scholarship.xml',
        'views/admission_application/photo_upload.xml',
        'views/admission_application/documents_upload.xml',
        'views/admission_application/final_confirmation.xml',

        'views/alifzerocms_application_view.xml',
        'views/alifzerocms_merit_list.xml',
        # 'views/templates/assets.xml',

        #'views/templates/scholarship.xml',
        'views/templates/registration_form.xml',
        'views/templates/signup_form.xml',
        'views/templates/portal_template.xml',
        'views/templates/merit_info_template.xml',

        'views/inherit_menu.xml',
        'views/res_config_settings_views.xml',
        'views/dashboard_views.xml',


        # 'wizard/alifzerocms_merit_register_wizard_view.xml',
        # 'wizard/alifzerocms_merit_status_view.xml',
        # #
        'report/report.xml',
        'report/report_admission_invoice.xml',
        'report/report_admission_application.xml',
        # 'report/student_admission_invoice.xml',

        'data/admission_mail_template.xml',
        'data/merit_mail_template.xml',
    ],
    'qweb': ["static/src/xml/hrms_dashboard.xml"],
    'images': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
