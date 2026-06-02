# -*- coding: utf-8 -*-
"""
DoorAndDoor - Estado de Entrega en Picking
Modelo: stock.move

CORRECCIÓN Odoo 18:
- En Odoo 18, el campo quantity_done fue renombrado/ movido.
- La cantidad entregada en un stock.move se calcula sumando las cantidades 
  de sus stock.move.line (qty_done en move_line_ids).
- Usamos qty_delivered_this como campo compute que suma las qty_done de las líneas.
"""

from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    # -------------------------------------------------------------------------
    # CAMPOS
    # -------------------------------------------------------------------------

    qty_ordered = fields.Float(
        string='Cantidad Pedida',
        compute='_compute_qty_ordered',
        store=False,
        readonly=True,
        help='Cantidad original pedida en la venta (desde sale.order.line)',
        digits='Product Unit of Measure',
    )

    qty_delivered_this = fields.Float(
        string='Entregado',
        compute='_compute_qty_delivered_this',
        store=False,
        readonly=True,
        help='Cantidad entregada en ESTE picking específico (suma de move_line_ids.qty_done)',
        digits='Product Unit of Measure',
    )

    qty_pending = fields.Float(
        string='Pendiente',
        compute='_compute_qty_pending',
        store=False,
        readonly=True,
        help='Cantidad pendiente por entregar = Pedida - Entregado (este picking)',
        digits='Product Unit of Measure',
    )

    has_sale_order = fields.Boolean(
        string='Tiene Venta',
        compute='_compute_has_sale_order',
        store=False,
        help='Indica si este movimiento está vinculado a una venta',
    )

    # -------------------------------------------------------------------------
    # MÉTODOS COMPUTE
    # -------------------------------------------------------------------------

    @api.depends('sale_line_id', 'sale_line_id.product_uom_qty')
    def _compute_qty_ordered(self):
        """
        Calcula la cantidad pedida original desde la línea de venta.
        Si no hay venta relacionada, muestra 0.
        """
        for move in self:
            if move.sale_line_id:
                move.qty_ordered = move.sale_line_id.product_uom_qty
            else:
                move.qty_ordered = 0.0

    @api.depends('move_line_ids', 'move_line_ids.qty_done')
    def _compute_qty_delivered_this(self):
        """
        Calcula la cantidad entregada en ESTE picking.
        En Odoo 18, la cantidad realizada está en stock.move.line.qty_done.
        Sumamos todas las qty_done de las líneas de este movimiento.
        """
        for move in self:
            if move.move_line_ids:
                # Sumar qty_done de todas las move_lines
                move.qty_delivered_this = sum(
                    line.qty_done or 0.0 for line in move.move_line_ids
                )
            else:
                # Fallback: si no hay move_lines, usar product_uom_qty como aproximación
                # (esto ocurre cuando el picking está en borrador y no se han creado líneas)
                move.qty_delivered_this = 0.0

    @api.depends('qty_ordered', 'qty_delivered_this')
    def _compute_qty_pending(self):
        """
        Calcula la cantidad pendiente: Pedida - Entregado (este picking).
        Si no hay venta, muestra 0.
        """
        for move in self:
            if move.sale_line_id:
                move.qty_pending = move.qty_ordered - move.qty_delivered_this
            else:
                move.qty_pending = 0.0

    @api.depends('picking_id.sale_id')
    def _compute_has_sale_order(self):
        """
        Indica si el movimiento está vinculado a una venta.
        """
        for move in self:
            move.has_sale_order = bool(move.picking_id.sale_id)
