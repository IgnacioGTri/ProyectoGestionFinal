import xmlrpc.client
import csv

# Configuración de conexión
url = "https://sgempresarial1.odoo.com"
db = "sgempresarial1"
username = "896846@alu.murciaeduca.es"
password = "Archenaignacio2025"

# ---------------- CONEXIÓN ----------------
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})

if uid:
    print("Conexión exitosa. UID:", uid)
else:
    print("Error en la autenticación.")

# ---------------- OPERACIONES ----------------
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

# Obtener productos
products = models.execute_kw(db, uid, password,
    'product.template', 'search_read',
    [[]], {'fields': ['name', 'list_price', 'standard_price']})

# Guardar en CSV
csv_file = 'catalogo_hardware.csv'

with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Escribir encabezados
    writer.writerow(['Producto', 'Precio de venta', 'Coste'])
    # Escribir cada producto
    for product in products:
        writer.writerow([product['name'], product['list_price'], product['standard_price']])

print(f"Datos guardados en {csv_file}")
