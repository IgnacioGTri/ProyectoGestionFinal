import xmlrpc.client
import csv

# -----------------------------
# CONFIGURACIÓN DE CONEXIÓN
# -----------------------------
url = "https://sgempresarial1.odoo.com/odoo"
db = "sgempresarial1"
username = "Ignacio Trigueros"
password = "Huarke2026"

# -----------------------------
# CONEXIÓN A ODOO
# -----------------------------
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})

if not uid:
    raise Exception("Error de autenticación")

models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

print("Conectado correctamente a Odoo")

# -----------------------------
# FUNCIÓN: OBTENER O CREAR CATEGORÍA
# -----------------------------
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

# -----------------------------
# FUNCIÓN: OBTENER UBICACIÓN INTERNA
# -----------------------------
def get_internal_location():
    location = models.execute_kw(
        db, uid, password,
        'stock.location', 'search',
        [[('usage', '=', 'internal')]],
        {'limit': 1}
    )
    return location[0]

location_id = get_internal_location()

# -----------------------------
# PROCESO DE IMPORTACIÓN
# -----------------------------
with open("catalogo_hardware.csv", newline='', encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:

        referencia = row['Referencia interna']
        nombre = row['Nombre']
        precio = float(row['Precio de venta'])
        coste = float(row['Coste'])
        categoria_nombre = row['Categoría']
        cantidad = float(row['Cantidad'])

        # Obtener o crear categoría
        categoria_id = get_or_create_category(categoria_nombre)

        # Verificar si el producto ya existe
        existing_product = models.execute_kw(
            db, uid, password,
            'product.product', 'search',
            [[('default_code', '=', referencia)]],
            {'limit': 1}
        )

        if existing_product:
            product_id = existing_product[0]
            print(f"Producto ya existe: {nombre}")
        else:
            # Crear producto (tipo almacenable)
            template_id = models.execute_kw(
                db, uid, password,
                'product.template', 'create',
                [{
                    'name': nombre,
                    'default_code': referencia,
                    'list_price': precio,
                    'standard_price': coste,
                    'categ_id': categoria_id,
                    'type': 'product'
                }]
            )

            # Obtener variante creada automáticamente
            product_variant = models.execute_kw(
                db, uid, password,
                'product.product', 'search',
                [[('product_tmpl_id', '=', template_id)]],
                {'limit': 1}
            )

            product_id = product_variant[0]
            print(f"Producto creado: {nombre}")

        # -----------------------------
        # AJUSTE INICIAL DE INVENTARIO
        # -----------------------------
        models.execute_kw(
            db, uid, password,
            'stock.quant', 'create',
            [{
                'product_id': product_id,
                'location_id': location_id,
                'inventory_quantity': cantidad
            }]
        )

        print(f"Stock ajustado: {nombre} → {cantidad} unidades")

print("Proceso completado correctamente.")
