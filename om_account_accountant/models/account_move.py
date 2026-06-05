from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = "account.move"

    def init(self):
        self._normalize_trade_accounts_sql()

    @api.model
    def _normalize_trade_accounts_sql(self):
        trade_account_specs = (
            ('asset_receivable', 'cobrar', '"101"'),
            ('liability_payable', 'pagar', '"102"'),
        )
        for expected_type, keyword, code_hint in trade_account_specs:
            self.env.cr.execute("""
                UPDATE account_account
                   SET account_type = %s
                 WHERE account_type != %s
                   AND (
                       LOWER(name::text) LIKE %s
                       OR code_store::text LIKE %s
                   )
            """, (
                expected_type,
                expected_type,
                f'%{keyword}%',
                f'%{code_hint}%',
            ))

    @api.model
    def _bootstrap_trade_account_types(self, vals_list):
        move_types = {
            vals.get('move_type')
            for vals in vals_list
            if vals.get('move_type')
        }
        if not move_types.intersection({'out_invoice', 'out_refund', 'in_invoice', 'in_refund'}):
            return

        companies = self.env['res.company'].browse({
            vals.get('company_id') or self.env.company.id
            for vals in vals_list
        })
        partners = self.env['res.partner'].browse({
            vals.get('partner_id')
            for vals in vals_list
            if vals.get('partner_id')
        })
        account_model = self.env['account.account'].with_context(active_test=False)

        trade_account_specs = (
            ('property_account_receivable_id', 'asset_receivable', 'cobrar', '"101"'),
            ('property_account_payable_id', 'liability_payable', 'pagar', '"102"'),
        )

        for company in companies:
            company_partner = company.partner_id.with_company(company)
            company_partners = partners.filtered(lambda p: not p.company_id or p.company_id == company)
            for field_name, expected_type, keyword, code_hint in trade_account_specs:
                accounts_to_fix = (
                    company_partner[field_name]
                    | company_partners.with_company(company).mapped(field_name)
                )

                self.env.cr.execute("""
                    SELECT id
                      FROM account_account
                     WHERE account_type IN %s
                       AND (
                           LOWER(name::text) LIKE %s
                           OR code_store::text LIKE %s
                       )
                     ORDER BY id
                     LIMIT 1
                """, (
                    tuple(['asset_current', 'liability_current', expected_type]),
                    f'%{keyword}%',
                    f'%{code_hint}%',
                ))
                fallback_row = self.env.cr.fetchone()
                fallback_account = account_model.browse(fallback_row[0]) if fallback_row else account_model
                accounts_to_fix |= fallback_account

                for account in accounts_to_fix.filtered(lambda acc: acc and acc.account_type != expected_type):
                    account.account_type = expected_type

                if not company_partner[field_name] and fallback_account:
                    company_partner[field_name] = fallback_account

    @api.model
    def _get_invoice_in_payment_state(self):
        return 'in_payment'

    @api.model_create_multi
    def create(self, vals_list):
        self._bootstrap_trade_account_types(vals_list)
        for vals in vals_list:
            move_type = vals.get('move_type')
            if move_type in ('out_invoice', 'out_refund') and not vals.get('invoice_date_due'):
                vals['invoice_date_due'] = vals.get('invoice_date') or fields.Date.context_today(self)
        return super().create(vals_list)

    def write(self, vals):
        if 'invoice_date_due' not in vals:
            pending_moves = self.filtered(
                lambda m: m.move_type in ('out_invoice', 'out_refund') and not m.invoice_date_due
            )
            for move in pending_moves:
                move.invoice_date_due = move.invoice_date or fields.Date.context_today(move)
        return super().write(vals)
