# Solo actúa si el stock disponible es menor a 5
if record.qty_available < 5:
    # 1. Crear mensaje en el Chatter
    mensaje = f"⚠️ Atención Compras: Stock crítico de '{record.name}'. Quedan {record.qty_available} unidades."
    record.message_post(body=mensaje)

    # 2. Modificación visual: añadir prefijo [REPOSICIÓN] si no existe
    if not record.name.startswith("[REPOSICIÓN]"):
        record.name = "[REPOSICIÓN] " + record.name

    # 3. (Opcional) Añadir etiqueta técnica
    etiqueta = env['product.tag'].search([('name','=','Stock Crítico')], limit=1)
    if not etiqueta:
        etiqueta = env['product.tag'].create({'name': 'Stock Crítico'})
    if etiqueta not in record.tag_ids:
        record.tag_ids = [(4, etiqueta.id)]
