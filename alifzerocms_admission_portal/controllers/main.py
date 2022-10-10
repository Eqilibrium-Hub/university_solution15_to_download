
import logging
from odoo.http import request
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.exceptions import UserError
from odoo import _
import odoo
from odoo import http
from odoo.service import db, security
import pdb
import werkzeug
from odoo.addons.auth_signup.models.res_users import SignupError

_logger = logging.getLogger(__name__)


class AuthSignupHome(Home):

	@http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
	def web_auth_signup(self, *args, **kw):

		qcontext = self.get_auth_signup_qcontext()
		if not qcontext.get('token') and not qcontext.get('signup_enabled'):
			raise werkzeug.exceptions.NotFound()

		if 'error' not in qcontext and request.httprequest.method == 'POST':
			try:
				self.do_signup(qcontext)
				# Send an account creation confirmation email
				#if qcontext.get('token'):
				user_sudo = request.env['res.users'].sudo().search([('login', '=', qcontext.get('login'))])
				template = request.env.ref('alifzerocms_admission_portal.mail_template_user_signup_account_created', raise_if_not_found=False)
				if user_sudo and template:
					template.sudo().with_context(
						lang=user_sudo.lang,
						auth_login=werkzeug.url_encode({'auth_login': user_sudo.email}),
					).send_mail(user_sudo.id, force_send=True)

				return self.web_login(*args, **kw)
			except UserError as e:
				qcontext['error'] = e.name or e.value
			except (SignupError, AssertionError) as e:
				if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
					qcontext["error"] = _("Another user is already registered using this email address.")
				else:
					_logger.error("%s", e)
					qcontext['error'] = _("Could not create a new account.")

		response = request.render('auth_signup.signup', qcontext)
		response.headers['X-Frame-Options'] = 'DENY'

		return response

	def do_signup(self, qcontext):
		if not qcontext.get('token'):  # our custom function should not be called if user go for reset password. So, we have added this statement
			""" Shared helper that creates a res.partner out of a token """
			values = { key: qcontext.get(key) for key in ('login', 'name', 'password', 'email' ,'mobile') }
			if not values:
				raise UserError(_("The form was not properly filled in."))
			
			# get all user and check if the email already exist or not
			user = request.env["res.users"].sudo().search([])
			count = 0
			for rec in user:
				if (rec.login).upper() == (qcontext.get("login")).upper():
					count += 1
			
			if values.get('password') != qcontext.get('confirm_password'):
				raise UserError(_("Passwords do not match; please retype them."))
			supported_langs = [lang['code'] for lang in request.env['res.lang'].sudo().search_read([], ['code'])]
			if request.lang in supported_langs:
				values['lang'] = request.lang

			if count > 0:
				raise UserError(_("Another user is already registered with same CNIC."))
			elif request.env["res.users"].sudo().search(['|' ,("email", "=", qcontext.get("email")) ,("mobile", "=", qcontext.get("mobile"))]):
				raise UserError(_("Another user is already registered with same Email or Mobile."))

			self._signup_with_values(qcontext.get('token'), values)
			request.env.cr.commit()
		else:
			res = super(AuthSignupHome, self).do_signup \
				(qcontext)  # default will be called if you do have token---> means come here by clicking on reset password




