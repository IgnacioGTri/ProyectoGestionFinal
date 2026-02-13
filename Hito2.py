# Solo actúa si el stock disponible es menor a 5
if record.qty_available < 5:
    # 1. Crear mensaje en el Chatter (sin f-string)
    mensaje = "⚠️ Atención Compras: Stock crítico de '%s'. Quedan %d unidades." % (record.name, record.qty_available)
    record.message_post(body=mensaje)

    # 2. Modificación visual: añadir prefijo [REPOSICIÓN] si no existe
    if not record.name.startswith("[REPOSICIÓN]"):
        record.name = "[REPOSICIÓN] " + record.name

    # 3. Añadir etiqueta técnica (Stock Crítico)
    tag_obj = env['product.tag']
    etiqueta = tag_obj.search([('name','=','Stock Crítico')], limit=1)
    if not etiqueta:
        etiqueta = tag_obj.create({'name': 'Stock Crítico'})
    if etiqueta.id not in record.tag_ids.ids:
        record.tag_ids = [(4, etiqueta.id)]

