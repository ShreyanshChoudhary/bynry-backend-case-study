# corrected_app.py — Flask API with validation, transactions, error handling

from flask import Flask, request, jsonify
from decimal import Decimal
import psycopg2, psycopg2.extras, logging

app = Flask(__name__)
log = logging.getLogger(__name__)

DB_DSN = 'postgresql://user:password@localhost:5432/inventory_db'


def get_conn():
    return psycopg2.connect(
        DB_DSN,
        cursor_factory=psycopg2.extras.RealDictCursor
    )


def validate_product_payload(data):
    errors = []

    if not data.get('name') or not str(data['name']).strip():
        errors.append('name is required and must be non-empty')

    if data.get('price') is None:
        errors.append('price is required')
    else:
        try:
            if Decimal(str(data['price'])) < 0:
                errors.append('price must be non-negative')
        except:
            errors.append('price must be a valid number')

    if data.get('warehouse_id') is None:
        errors.append('warehouse_id is required')

    qty = data.get('quantity', 0)
    if not isinstance(qty, int) or qty < 0:
        errors.append('quantity must be a non-negative integer')

    return errors


@app.route('/product', methods=['POST'])
def create_product():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({'error': 'Request body must be valid JSON'}), 400

    errors = validate_product_payload(data)
    if errors:
        return jsonify({'errors': errors}), 400

    name = str(data['name']).strip()
    price = Decimal(str(data['price']))
    warehouse_id = int(data['warehouse_id'])
    quantity = int(data.get('quantity', 0))
    sku = data.get('sku', '').strip() or None

    conn = None

    try:
        conn = get_conn()

        # psycopg2: this manages transaction, not connection closing
        with conn:
            with conn.cursor() as cur:

                # Check duplicate product
                cur.execute(
                    'SELECT id FROM products WHERE name = %s AND is_active = TRUE',
                    (name,)
                )
                if cur.fetchone():
                    return jsonify({'error': f'Product "{name}" already exists'}), 409

                # Validate warehouse
                cur.execute(
                    'SELECT id FROM warehouses WHERE id = %s',
                    (warehouse_id,)
                )
                if not cur.fetchone():
                    return jsonify({'error': f'Warehouse {warehouse_id} not found'}), 404

                # Insert product
                cur.execute(
                    '''INSERT INTO products (name, sku, price, is_active)
                       VALUES (%s, %s, %s, TRUE)
                       RETURNING id''',
                    (name, sku, price)
                )
                product_id = cur.fetchone()['id']

                # Insert / update inventory
                cur.execute(
                    '''INSERT INTO inventory (product_id, warehouse_id, quantity)
                       VALUES (%s, %s, %s)
                       ON CONFLICT (product_id, warehouse_id)
                       DO UPDATE SET quantity = inventory.quantity + EXCLUDED.quantity''',
                    (product_id, warehouse_id, quantity)
                )

                # 🔥 Audit log (IMPORTANT FIX)
                cur.execute(
                    '''INSERT INTO inventory_transactions 
                       (product_id, warehouse_id, transaction_type, quantity_delta, quantity_before, quantity_after)
                       VALUES (%s, %s, 'INITIAL_LOAD', %s, 0, %s)''',
                    (product_id, warehouse_id, quantity, quantity)
                )

        log.info('Product created: id=%s name=%s warehouse=%s', product_id, name, warehouse_id)

        return jsonify({
            'id': product_id,
            'name': name,
            'sku': sku,
            'price': float(price),
            'warehouse_id': warehouse_id,
            'quantity': quantity,
        }), 201

    except psycopg2.IntegrityError as e:
        log.warning('Integrity error: %s', e)
        return jsonify({'error': 'Data integrity violation'}), 409

    except Exception as e:
        log.exception('Unexpected error')
        return jsonify({'error': 'Internal server error'}), 500

    finally:
        # Explicit connection close (important)
        if conn:
            conn.close()