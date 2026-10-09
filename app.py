import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from flask import Flask, request, jsonify

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("COMANDA_DB", BASE_DIR / "comanda_go.db"))
INDEX_HTML = (BASE_DIR / "index.html").read_text(encoding="utf-8")
MAX_CENTS = 10**11  # limite de segurança (R$ 1 bilhão)
PAYMENT_METHODS = {"PIX", "Dinheiro", "Débito", "Crédito"}


@contextmanager
def db():
    """Abre a conexão, faz commit/rollback e SEMPRE fecha ao final."""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with db() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'Geral',
            price_cents INTEGER NOT NULL CHECK(price_cents >= 0),
            active INTEGER NOT NULL DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'open',
            created_at TEXT NOT NULL,
            closed_at TEXT
        );
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL REFERENCES orders(id),
            product_id INTEGER REFERENCES products(id) ON DELETE SET NULL,
            description TEXT NOT NULL,
            unit_price_cents INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL REFERENCES orders(id),
            amount_cents INTEGER NOT NULL CHECK(amount_cents > 0),
            method TEXT NOT NULL,
            received_cents INTEGER NOT NULL,
            change_cents INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS cash_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            opening_cents INTEGER NOT NULL DEFAULT 0,
            opened_at TEXT NOT NULL,
            closed_at TEXT,
            closing_cents INTEGER
        );
        CREATE TABLE IF NOT EXISTS cash_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL REFERENCES cash_sessions(id),
            kind TEXT NOT NULL,
            description TEXT NOT NULL,
            amount_cents INTEGER NOT NULL CHECK(amount_cents > 0),
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_items_order ON order_items(order_id);
        CREATE INDEX IF NOT EXISTS idx_payments_order ON payments(order_id);
        CREATE INDEX IF NOT EXISTS idx_movements_session ON cash_movements(session_id);
        """)
        count = c.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if count == 0:
            c.executemany(
                "INSERT INTO products(name, category, price_cents) VALUES (?, ?, ?)",
                [
                    ("Água", "Bebidas", 300),
                    ("Refrigerante", "Bebidas", 600),
                    ("Cerveja", "Bebidas", 800),
                    ("Hambúrguer", "Comidas", 1800),
                    ("Batata frita", "Porções", 1600),
                ],
            )


def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def today():
    """Data local de hoje (YYYY-MM-DD), compatível com o início de created_at."""
    return datetime.now().astimezone().date().isoformat()


def body():
    """Lê o JSON da requisição sem derrubar a API se vier inválido."""
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def cents(value):
    try:
        d = Decimal(str(value).replace(",", "."))
        if not d.is_finite() or d < 0:
            raise ValueError
        result = int((d * 100).quantize(Decimal("1")))
        if result > MAX_CENTS:
            raise ValueError
        return result
    except (InvalidOperation, ValueError):
        raise ValueError("Informe um valor válido e não negativo.")


def money(n):
    return f"R$ {n / 100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def row_dict(row):
    return dict(row) if row is not None else None


def order_total(c, order_id):
    items = c.execute(
        "SELECT COALESCE(SUM(unit_price_cents * quantity),0) FROM order_items WHERE order_id=?",
        (order_id,),
    ).fetchone()[0]
    paid = c.execute(
        "SELECT COALESCE(SUM(amount_cents),0) FROM payments WHERE order_id=?",
        (order_id,),
    ).fetchone()[0]
    return items, paid


@app.get("/api/init")
def api_init():
    with db() as c:
        products = [row_dict(r) for r in c.execute(
            "SELECT id,name,category,price_cents FROM products WHERE active=1 ORDER BY category,name"
        )]
        orders = c.execute("""
            SELECT o.*,
            COALESCE((SELECT SUM(i.unit_price_cents*i.quantity) FROM order_items i WHERE i.order_id=o.id),0) AS total_cents,
            COALESCE((SELECT SUM(p.amount_cents) FROM payments p WHERE p.order_id=o.id),0) AS paid_cents
            FROM orders o WHERE o.status='open' ORDER BY o.id DESC
        """).fetchall()
        result_orders = []
        for r in orders:
            d = row_dict(r)
            d["balance_cents"] = max(0, d["total_cents"] - d["paid_cents"])
            d["items"] = [row_dict(i) for i in c.execute(
                "SELECT id,description,unit_price_cents,quantity FROM order_items WHERE order_id=? ORDER BY id DESC",
                (d["id"],)
            )]
            result_orders.append(d)
        session = c.execute(
            "SELECT * FROM cash_sessions WHERE closed_at IS NULL ORDER BY id DESC LIMIT 1"
        ).fetchone()
        # created_at é ISO com fuso (ex.: 2026-10-08T22:41:00-03:00). Usar date() do SQLite
        # converteria para UTC e jogaria vendas da noite para o "dia seguinte";
        # por isso comparamos os 10 primeiros caracteres (data local).
        summary = c.execute("""
            SELECT
            COALESCE((SELECT SUM(amount_cents) FROM payments WHERE substr(created_at,1,10)=?),0) received,
            COALESCE((SELECT SUM((SELECT COALESCE(SUM(i.unit_price_cents*i.quantity),0) FROM order_items i WHERE i.order_id=o.id) -
                                  (SELECT COALESCE(SUM(p.amount_cents),0) FROM payments p WHERE p.order_id=o.id))
                      FROM orders o WHERE o.status='open'),0) pending,
            (SELECT COUNT(*) FROM orders WHERE status='open') open_count
        """, (today(),)).fetchone()
        return jsonify(products=products, orders=result_orders, session=row_dict(session),
                       summary=row_dict(summary), methods=sorted(PAYMENT_METHODS))


@app.post("/api/products")
def add_product():
    data = body()
    name = str(data.get("name", "")).strip()
    category = str(data.get("category", "Geral")).strip() or "Geral"
    if not name:
        return jsonify(error="Informe o nome do produto."), 400
    try:
        price = cents(data.get("price", ""))
    except ValueError as e:
        return jsonify(error=str(e)), 400
    with db() as c:
        cur = c.execute("INSERT INTO products(name,category,price_cents) VALUES (?,?,?)",
                        (name[:100], category[:50], price))
        return jsonify(id=cur.lastrowid), 201


@app.delete("/api/products/<int:pid>")
def delete_product(pid):
    with db() as c:
        c.execute("UPDATE products SET active=0 WHERE id=?", (pid,))
    return jsonify(ok=True)


@app.post("/api/orders")
def create_order():
    data = body()
    customer = str(data.get("customer", "")).strip()
    if not customer:
        return jsonify(error="Informe a mesa ou o nome do cliente."), 400
    with db() as c:
        cur = c.execute("INSERT INTO orders(customer,created_at) VALUES (?,?)", (customer[:100], now()))
        return jsonify(id=cur.lastrowid), 201


@app.post("/api/orders/<int:oid>/items")
def add_item(oid):
    data = body()
    try:
        qty = int(data.get("quantity", 1))
        if qty < 1 or qty > 999:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify(error="Quantidade deve ser entre 1 e 999."), 400
    with db() as c:
        order = c.execute("SELECT status FROM orders WHERE id=?", (oid,)).fetchone()
        if not order or order["status"] != "open":
            return jsonify(error="Comanda não encontrada ou já encerrada."), 404
        product_id = data.get("product_id")
        if product_id:
            product = c.execute("SELECT * FROM products WHERE id=? AND active=1", (product_id,)).fetchone()
            if not product:
                return jsonify(error="Produto não encontrado."), 404
            desc, price = product["name"], product["price_cents"]
            pid = product["id"]
        else:
            desc = str(data.get("description", "")).strip()
            try:
                price = cents(data.get("price", ""))
            except ValueError as e:
                return jsonify(error=str(e)), 400
            if not desc:
                return jsonify(error="Informe a descrição do item."), 400
            desc, pid = desc[:100], None
        c.execute("""INSERT INTO order_items(order_id,product_id,description,unit_price_cents,quantity,created_at)
                     VALUES (?,?,?,?,?,?)""", (oid, pid, desc, price, qty, now()))
    return jsonify(ok=True), 201


@app.delete("/api/items/<int:item_id>")
def remove_item(item_id):
    with db() as c:
        item = c.execute("""SELECT i.*,o.status FROM order_items i JOIN orders o ON o.id=i.order_id
                            WHERE i.id=?""", (item_id,)).fetchone()
        if not item or item["status"] != "open":
            return jsonify(error="Item não encontrado ou comanda encerrada."), 404
        paid = c.execute("SELECT COALESCE(SUM(amount_cents),0) FROM payments WHERE order_id=?",
                         (item["order_id"],)).fetchone()[0]
        if paid:
            return jsonify(error="Não é possível remover itens após um pagamento parcial. Ajuste a conta pelo atendimento."), 409
        c.execute("DELETE FROM order_items WHERE id=?", (item_id,))
    return jsonify(ok=True)


@app.post("/api/orders/<int:oid>/payments")
def pay_order(oid):
    data = body()
    method = str(data.get("method", "")).strip()
    if method not in PAYMENT_METHODS:
        return jsonify(error="Forma de pagamento inválida."), 400
    with db() as c:
        order = c.execute("SELECT * FROM orders WHERE id=?", (oid,)).fetchone()
        if not order or order["status"] != "open":
            return jsonify(error="Comanda não encontrada ou já encerrada."), 404
        total, paid = order_total(c, oid)
        balance = total - paid
        if balance <= 0:
            return jsonify(error="Esta comanda já está totalmente paga."), 400
        try:
            amount = cents(data.get("amount", balance / 100))
        except ValueError as e:
            return jsonify(error=str(e)), 400
        if amount <= 0 or amount > balance:
            return jsonify(error=f"O pagamento deve ser maior que zero e não pode ultrapassar o saldo de {money(balance)}."), 400
        change = 0
        received = amount
        if method == "Dinheiro":
            # "recebido" só é lido (e validado) quando o pagamento é em dinheiro
            try:
                received = cents(data.get("received", amount / 100))
            except ValueError as e:
                return jsonify(error=str(e)), 400
            if received < amount:
                return jsonify(error="O dinheiro recebido é menor que o valor do pagamento."), 400
            change = received - amount
        c.execute("""INSERT INTO payments(order_id,amount_cents,method,received_cents,change_cents,created_at)
                     VALUES (?,?,?,?,?,?)""", (oid, amount, method, received, change, now()))
        new_paid = paid + amount
        if new_paid >= total:
            c.execute("UPDATE orders SET status='paid',closed_at=? WHERE id=?", (now(), oid))
    return jsonify(ok=True, change_cents=change, balance_cents=max(0, balance - amount))


@app.post("/api/cash/open")
def open_cash():
    data = body()
    try:
        opening = cents(data.get("opening", 0))
    except ValueError as e:
        return jsonify(error=str(e)), 400
    with db() as c:
        existing = c.execute("SELECT id FROM cash_sessions WHERE closed_at IS NULL LIMIT 1").fetchone()
        if existing:
            return jsonify(error="Já existe um caixa aberto."), 409
        cur = c.execute("INSERT INTO cash_sessions(opening_cents,opened_at) VALUES (?,?)", (opening, now()))
        return jsonify(id=cur.lastrowid), 201


@app.post("/api/cash/movements")
def cash_movement():
    data = body()
    kind = str(data.get("kind", "")).lower()
    description = str(data.get("description", "")).strip()
    if kind not in {"expense", "withdrawal", "reinforcement"}:
        return jsonify(error="Tipo de movimentação inválido."), 400
    if not description:
        return jsonify(error="Informe a descrição."), 400
    try:
        amount = cents(data.get("amount", ""))
    except ValueError as e:
        return jsonify(error=str(e)), 400
    if amount <= 0:
        return jsonify(error="O valor precisa ser maior que zero."), 400
    with db() as c:
        session = c.execute("SELECT id FROM cash_sessions WHERE closed_at IS NULL ORDER BY id DESC LIMIT 1").fetchone()
        if not session:
            return jsonify(error="Abra o caixa antes de registrar movimentações."), 409
        c.execute("""INSERT INTO cash_movements(session_id,kind,description,amount_cents,created_at)
                     VALUES (?,?,?,?,?)""", (session["id"], kind, description[:150], amount, now()))
    return jsonify(ok=True), 201


@app.get("/api/cash/report")
def cash_report():
    with db() as c:
        session = c.execute("SELECT * FROM cash_sessions WHERE closed_at IS NULL ORDER BY id DESC LIMIT 1").fetchone()
        payments = c.execute("""
            SELECT method, SUM(amount_cents) total FROM payments
            WHERE substr(created_at,1,10)=? GROUP BY method
        """, (today(),)).fetchall()
        movements = []
        expected = 0
        if session:
            movements = [row_dict(r) for r in c.execute(
                "SELECT * FROM cash_movements WHERE session_id=? ORDER BY id DESC", (session["id"],))]
            ins = sum(r["amount_cents"] for r in movements if r["kind"] == "reinforcement")
            outs = sum(r["amount_cents"] for r in movements if r["kind"] in ("expense", "withdrawal"))
            cash_received = c.execute("""
                SELECT COALESCE(SUM(amount_cents),0) FROM payments
                WHERE method='Dinheiro' AND created_at>=?
            """, (session["opened_at"],)).fetchone()[0]
            expected = session["opening_cents"] + cash_received + ins - outs
        return jsonify(session=row_dict(session), payments=[row_dict(r) for r in payments],
                       movements=movements, expected_cents=expected)


@app.post("/api/cash/close")
def close_cash():
    data = body()
    try:
        counted = cents(data.get("counted", 0))
    except ValueError as e:
        return jsonify(error=str(e)), 400
    with db() as c:
        session = c.execute("SELECT * FROM cash_sessions WHERE closed_at IS NULL ORDER BY id DESC LIMIT 1").fetchone()
        if not session:
            return jsonify(error="Não há caixa aberto."), 409
        c.execute("UPDATE cash_sessions SET closed_at=?,closing_cents=? WHERE id=?",
                  (now(), counted, session["id"]))
    return jsonify(ok=True)


@app.get("/")
def index():
    # HTML puro (sem Jinja), lido do arquivo index.html
    return INDEX_HTML


init_db()

if __name__ == "__main__":
    # Debug desligado por padrão (o debugger do Flask permite executar código remotamente).
    # Para desenvolvimento local: FLASK_DEBUG=1 python app.py
    app.run(
        debug=os.environ.get("FLASK_DEBUG") == "1",
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
    )
