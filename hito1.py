import xmlrpc.client
import csv

url = "https://sgempresarial1.odoo.com"
db = "sgempresarial1"
username = "896846@alu.murciaeduca.es"
password = "Archenaignacio2025"

common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})

if not uid:
    raise Exception("Error de autenticación.")

models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

print("✅ Conectado correctamente a Odoo Online")

def get_or_create_category(category_name):
    category = models.execute_kw(
        db, uid, password,
        'product.category', 'search',
        [[('name', '=', category_name)]],
        {'limit': 1}
    )
    if category:
        return category[0]
    else:
        return models.execute_kw(
            db, uid, password,
            'product.category', 'create',
            [{'name': category_name}]
        )

def get_internal_location():
    location = models.execute_kw(
        db, uid, password,
        'stock.location', 'search',
        [[('usage', '=', 'internal')]],
        {'limit': 1}
    )
    if not location:
        raise Exception("No se encontró ubicación interna.")
    return location[0]

location_id = get_internal_location()

with open("catalogo_hardware.csv", newline='', encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:

        referencia = row['Referencia interna']
        nombre = row['Nombre']
        precio = float(row['Precio de venta'])
        coste = float(row['Coste'])
        categoria_nombre = row['Categoría']
        cantidad = float(row['Cantidad'])

        categoria_id = get_or_create_category(categoria_nombre)

        existing_product = models.execute_kw(
            db, uid, password,
            'product.product', 'search',
            [[('default_code', '=', referencia)]],
            {'limit': 1}
        )

        if existing_product:
            product_id = existing_product[0]
            print(f"🔄 Producto ya existe: {nombre}")
        else:
            template_id = models.execute_kw(
                db, uid, password,
                'product.template', 'create',
                [{
                    'name': nombre,
                    'default_code': referencia,
                    'list_price': precio,
                    'standard_price': coste,
                    'categ_id': categoria_id,
                    'type': 'product'   # <-- CORRECCIÓN
                }]
            )

            product_variant = models.execute_kw(
                db, uid, password,
                'product.product', 'search',
                [[('product_tmpl_id', '=', template_id)]],
                {'limit': 1}
            )

            product_id = product_variant[0]
            print(f"🆕 Producto creado: {nombre}")

        quant = models.execute_kw(
            db, uid, password,
            'stock.quant', 'search',
            [[('product_id', '=', product_id),
              ('location_id', '=', location_id)]],
            {'limit': 1}
        )

        if quant:
            models.execute_kw(
                db, uid, password,
                'stock.quant', 'write',
                [quant, {'inventory_quantity': cantidad}]
            )
        else:
            models.execute_kw(
                db, uid, password,
                'stock.quant', 'create',
                [{
                    'product_id': product_id,
                    'location_id': location_id,
                    'inventory_quantity': cantidad
                }]
            )

        print(f"📦 Stock ajustado: {nombre} → {cantidad} unidades")

print("🎯 Proceso completado correctamente.")
