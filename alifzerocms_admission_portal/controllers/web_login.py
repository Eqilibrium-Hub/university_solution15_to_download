# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import odoo
import odoo.modules.registry
from odoo.tools.translate import _
from odoo import http
from odoo.http import content_disposition, dispatch_rpc, request
import pdb

import odoo.addons.web.controllers.main as main
from odoo.addons.portal.controllers.web import Home

class Home(Home):
	# @http.route('/web/login', type='http', auth="none", sitemap=False) #default funcation is with auth="none" but its changed in website module. So, we added auth="public" and added website inherited code below
	@http.route('/web/login', type='http', auth="public", sitemap=False)
	def web_login(self, redirect=None, **kw):
		main.ensure_db()
		request.params['login_success'] = False
		if request.httprequest.method == 'GET' and redirect and request.session.uid:
			return http.redirect_with_hash(redirect)

		if not request.uid:
			request.uid = odoo.SUPERUSER_ID

		values = request.params.copy()
		try:
			values['databases'] = http.db_list()
		except odoo.exceptions.AccessDenied:
			values['databases'] = None

		if request.httprequest.method == 'POST':
			old_uid = request.uid
			try:
				uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
				request.params['login_success'] = True
				current_user = request.env['res.users'].search([('id','=',uid)])

				student_application = request.env['alifzerocms.application'].sudo().search([('cnic', '=', current_user.login)])
				student = request.env['alifzerocms.student'].sudo().search([('partner_id', '=', current_user.partner_id.id)])
				faculty = request.env['alifzerocms.faculty.staff'].sudo().search([('partner_id', '=', current_user.partner_id.id)])

				if not student and not faculty and request.env.ref('base.group_portal') in current_user.groups_id:
					return request.redirect('/admission/registration')
				return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))

			except odoo.exceptions.AccessDenied as e:
				request.uid = old_uid
				if e.args == odoo.exceptions.AccessDenied().args:
					values['error'] = _("Wrong login/password")
				else:
					values['error'] = e.args[0]
		else:
			if 'error' in request.params and request.params.get('error') == 'access':
				values['error'] = _('Only employee can access this database. Please contact the administrator.')

		if 'login' not in values and request.session.get('auth_login'):
			values['login'] = request.session.get('auth_login')

		if not odoo.tools.config['list_db']:
			values['disable_database_manager'] = True

		# otherwise no real way to test debug mode in template as ?debug =>
		# values['debug'] = '' but that's also the fallback value when
		# missing variables in qweb
		if 'debug' in values:
			values['debug'] = True

		response = request.render('web.login', values)
		response.headers['X-Frame-Options'] = 'DENY'

		#website web_login function
		if not redirect and request.params['login_success']:
			if request.env['res.users'].browse(request.uid).has_group('base.group_user'):
				redirect = b'/web?' + request.httprequest.query_string
			else:
				redirect = '/my'
			return http.redirect_with_hash(redirect)

		# auth_signup web_login function
		response.qcontext.update(self.get_auth_signup_config())
		if request.httprequest.method == 'GET' and request.session.uid and request.params.get('redirect'):
			# Redirect if already logged in and redirect param is present
			return http.redirect_with_hash(request.params.get('redirect'))

		return response

