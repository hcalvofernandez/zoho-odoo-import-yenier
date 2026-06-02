# -*- coding: utf-8 -*-
"""
DoorAndDoor - Botón de Entrega desde Ventas
Modelo: stock.picking
"""

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # -------------------------------------------------------------------------
    # CAMPOS
    # -------------------------------------------------------------------------

    sale_id = fields.Many2one(
        'sale.order',
        string='Pedido de Venta',
        index=True,
        ondelete='set null',
        help='Pedido de venta relacionado con esta operación de almacén',
        copy=False,
    )

    # -------------------------------------------------------------------------
    # MÉTODOS HEREDADOS
    # -------------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        """
        Sobrescribe create para vincular automáticamente el picking con la venta
        cuando el origin coincide con un sale.order.name y sale_id no está establecido.
        """
        pickings = super(StockPicking, self).create(vals_list)

        for picking in pickings:
            # Solo sincronizar si sale_id está vacío y origin tiene valor
            if not picking.sale_id and picking.origin:
                # Buscar si el origin coincide con un sale.order
                sale_order = self.env['sale.order'].search([
                    ('name', '=', picking.origin),
                ], limit=1)
                if sale_order:
                    picking.sale_id = sale_order.id

        return pickings

    def write(self, vals):
        """
        Sobrescribe write para mantener sincronizado sale_id con origin
        solo cuando sale_id no está establecido manualmente.
        """
        res = super(StockPicking, self).write(vals)

        # Solo sincronizar si origin cambió y sale_id sigue vacío
        if 'origin' in vals:
            for picking in self:
                if picking.origin and not picking.sale_id:
                    sale_order = self.env['sale.order'].search([
                        ('name', '=', picking.origin),
                    ], limit=1)
                    if sale_order:
                        picking.sale_id = sale_order.id

        return res
