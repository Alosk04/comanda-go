from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Vendas & Estoque</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-color: #f4f6f9;
            --card-bg: #ffffff;
            --primary: #2563eb;
            --success: #16a34a;
            --warning: #d97706;
            --danger: #dc2626;
            --text-dark: #1e293b;
            --text-muted: #64748b;
            --border: #e2e8f0;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: sans-serif; }
        body { background-color: var(--bg-color); color: var(--text-dark); padding: 15px; max-width: 1200px; margin: 0 auto; }
        header { margin-bottom: 20px; text-align: center; }
        header h1 { font-size: 22px; color: var(--text-dark); }
        
        .grid-forms { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .form-card { background: var(--card-bg); padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
        .form-card h2 { font-size: 15px; margin-bottom: 12px; color: var(--primary); }
        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; }
        .form-group { display: flex; flex-direction: column; }
        .form-group label { font-size: 11px; font-weight: bold; margin-bottom: 4px; }
        .form-group input, .form-group select { padding: 8px; border: 1px solid var(--border); border-radius: 6px; font-size: 13px; }
        .btn-submit { grid-column: 1 / -1; background-color: var(--primary); color: white; border: none; padding: 10px; border-radius: 6px; font-size: 14px; font-weight: bold; cursor: pointer; margin-top: 5px; }

        .kpi-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 20px; }
        .kpi-card { background: var(--card-bg); padding: 12px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 4px solid var(--primary); }
        .kpi-card.green { border-left-color: var(--success); }
        .kpi-card.amber { border-left-color: var(--warning); }
        .kpi-card.red { border-left-color: var(--danger); }
        .kpi-card h3 { font-size: 11px; text-transform: uppercase; color: var(--text-muted); }
        .kpi-card .value { font-size: 18px; font-weight: bold; margin-top: 4px; }

        .dashboard-content { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .chart-card, .table-card { background: var(--card-bg); padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
        .card-header { font-size: 14px; font-weight: bold; margin-bottom: 10px; }
        
        .table-responsive { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; text-align: left; font-size: 13px; }
        th, td { padding: 8px; border-bottom: 1px solid var(--border); }
        .badge { padding: 3px 6px; border-radius: 8px; font-size: 10px; font-weight: bold; }
        .badge-paid { background: #dcfce7; color: var(--success); }
        .badge-pending { background: #fef3c7; color: var(--warning); }
        .badge-low { background: #fee2e2; color: var(--danger); }
        .badge-ok { background: #dcfce7; color: var(--success); }
        .btn-action { background: none; border: none; color: var(--danger); cursor: pointer; }
    </style>
</head>
<body>

    <header>
        <h1>📊 Vendas & Controle de Estoque</h1>
    </header>

    <div class="grid-forms">
        <!-- Cadastrar Novo Produto no Estoque -->
        <div class="form-card">
            <h2>📦 Adicionar/Atualizar Estoque</h2>
            <form id="stockForm" class="form-grid">
                <div class="form-group">
                    <label>Nome do Produto</label>
                    <input type="text" id="stockProductName" placeholder="Ex: Camiseta" required>
                </div>
                <div class="form-group">
                    <label>Qtd em Estoque</label>
                    <input type="number" id="stockQuantity" min="0" value="10" required>
                </div>
                <button type="submit" class="btn-submit" style="background-color: var(--success);">Salvar no Estoque</button>
            </form>
        </div>

        <!-- Lançar Venda -->
        <div class="form-card">
            <h2>🛒 Registrar Venda</h2>
            <form id="saleForm" class="form-grid">
                <div class="form-group">
                    <label>Selecione o Produto</label>
                    <select id="saleProductSelect" required></select>
                </div>
                <div class="form-group">
                    <label>Quantidade Vendida</label>
                    <input type="number" id="saleQuantity" min="1" value="1" required>
                </div>
                <div class="form-group">
                    <label>Valor Unitário (R$)</label>
                    <input type="number" id="unitPrice" step="0.01" min="0" placeholder="0.00" required>
                </div>
                <div class="form-group">
                    <label>Status</label>
                    <select id="paymentStatus">
                        <option value="Pago">Pago</option>
                        <option value="Pendente">Pendente</option>
                    </select>
                </div>
                <button type="submit" class="btn-submit">Dar Baixa e Vender</button>
            </form>
        </div>
    </div>

    <!-- Indicadores -->
    <div class="kpi-grid">
        <div class="kpi-card green">
            <h3>Recebido</h3>
            <div class="value" id="kpiReceived">R$ 0,00</div>
        </div>
        <div class="kpi-card amber">
            <h3>Pendente</h3>
            <div class="value" id="kpiPending">R$ 0,00</div>
        </div>
        <div class="kpi-card">
            <h3>Total de Vendas</h3>
            <div class="value" id="kpiTotalSales">0</div>
        </div>
        <div class="kpi-card red">
            <h3>Alertas de Estoque Baixo</h3>
            <div class="value" id="kpiLowStock">0 prod.</div>
        </div>
    </div>

    <!-- Tabela de Estoque -->
    <div class="table-card" style="margin-bottom: 20px;">
        <div class="card-header">📦 Posição Atual do Estoque</div>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr>
                        <th>Produto</th>
                        <th>Qtd Restante</th>
                        <th>Status Estoque</th>
                        <th>Ação</th>
                    </tr>
                </thead>
                <tbody id="stockTableBody"></tbody>
            </table>
        </div>
    </div>

    <!-- Gráficos -->
    <div class="dashboard-content">
        <div class="chart-card">
            <div class="card-header">Status Financeiro</div>
            <canvas id="statusChart"></canvas>
        </div>
        <div class="chart-card">
            <div class="card-header">Faturamento por Produto</div>
            <canvas id="productChart"></canvas>
        </div>
    </div>

    <!-- Tabela de Vendas -->
    <div class="table-card">
        <div class="card-header">📋 Histórico de Vendas</div>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr>
                        <th>Produto</th>
                        <th>Qtd.</th>
                        <th>Total</th>
                        <th>Status</th>
                        <th>Excluir</th>
                    </tr>
                </thead>
                <tbody id="salesTableBody"></tbody>
            </table>
        </div>
    </div>

    <script>
        let inventory = JSON.parse(localStorage.getItem('my_inventory')) || [
            { product: 'Camiseta', qty: 15 },
            { product: 'Calça Jeans', qty: 3 }
        ];

        let sales = JSON.parse(localStorage.getItem('my_dashboard_sales')) || [
            { id: 1, product: 'Camiseta', qty: 2, price: 50.0, status: 'Pago' }
        ];

        let statusChart, productChart;

        function saveAndRender() {
            localStorage.setItem('my_inventory', JSON.stringify(inventory));
            localStorage.setItem('my_dashboard_sales', JSON.stringify(sales));
            
            updateSelectOptions();
            updateKPIs();
            renderStockTable();
            renderSalesTable();
            renderCharts();
        }

        function formatCurrency(val) {
            return val.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
        }

        function updateSelectOptions() {
            const select = document.getElementById('saleProductSelect');
            select.innerHTML = '';
            if (inventory.length === 0) {
                select.innerHTML = '<option value="">Cadastre um produto no estoque primeiro</option>';
                return;
            }
            inventory.forEach(item => {
                const opt = document.createElement('option');
                opt.value = item.product;
                opt.innerText = `${item.product} (${item.qty} em estoque)`;
                select.appendChild(opt);
            });
        }

        function updateKPIs() {
            let received = 0, pending = 0;
            sales.forEach(s => {
                const total = s.qty * s.price;
                if (s.status === 'Pago') received += total;
                else pending += total;
            });

            let lowStockCount = inventory.filter(i => i.qty <= 3).length;

            document.getElementById('kpiReceived').innerText = formatCurrency(received);
            document.getElementById('kpiPending').innerText = formatCurrency(pending);
            document.getElementById('kpiTotalSales').innerText = sales.length;
            document.getElementById('kpiLowStock').innerText = lowStockCount + ' prod.';
        }

        function renderStockTable() {
            const tbody = document.getElementById('stockTableBody');
            tbody.innerHTML = '';
            inventory.forEach((item, index) => {
                const badgeClass = item.qty <= 3 ? 'badge-low' : 'badge-ok';
                const badgeText = item.qty <= 3 ? 'Estoque Baixo ⚠️' : 'OK';
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${item.product}</strong></td>
                    <td><strong>${item.qty} unid.</strong></td>
                    <td><span class="badge ${badgeClass}">${badgeText}</span></td>
                    <td><button class="btn-action" onclick="deleteStock(${index})">❌</button></td>
                `;
                tbody.appendChild(tr);
            });
        }

        function renderSalesTable() {
            const tbody = document.getElementById('salesTableBody');
            tbody.innerHTML = '';
            sales.forEach((s, index) => {
                const total = s.qty * s.price;
                const badgeClass = s.status === 'Pago' ? 'badge-paid' : 'badge-pending';
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${s.product}</strong></td>
                    <td>${s.qty}</td>
                    <td>${formatCurrency(total)}</td>
                    <td>
                        <span class="badge ${badgeClass}" style="cursor:pointer;" onclick="toggleStatus(${index})">
                            ${s.status} 🔄
                        </span>
                    </td>
                    <td><button class="btn-action" onclick="deleteSale(${index})">❌</button></td>
                `;
                tbody.appendChild(tr);
            });
        }

        function toggleStatus(index) {
            sales[index].status = sales[index].status === 'Pago' ? 'Pendente' : 'Pago';
            saveAndRender();
        }

        function deleteSale(index) {
            sales.splice(index, 1);
            saveAndRender();
        }

        function deleteStock(index) {
            inventory.splice(index, 1);
            saveAndRender();
        }

        function renderCharts() {
            let received = 0, pending = 0;
            let productTotals = {};

            sales.forEach(s => {
                const total = s.qty * s.price;
                if (s.status === 'Pago') received += total;
                else pending += total;
                productTotals[s.product] = (productTotals[s.product] || 0) + total;
            });

            const ctxStatus = document.getElementById('statusChart').getContext('2d');
            if (statusChart) statusChart.destroy();
            statusChart = new Chart(ctxStatus, {
                type: 'doughnut',
                data: {
                    labels: ['Pago (R$)', 'Pendente (R$)'],
                    datasets: [{ data: [received, pending], backgroundColor: ['#16a34a', '#d97706'] }]
                },
                options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
            });

            const ctxProd = document.getElementById('productChart').getContext('2d');
            if (productChart) productChart.destroy();
            productChart = new Chart(ctxProd, {
                type: 'bar',
                data: {
                    labels: Object.keys(productTotals),
                    datasets: [{ label: 'Faturamento (R$)', data: Object.values(productTotals), backgroundColor: '#2563eb' }]
                },
                options: { responsive: true, plugins: { legend: { display: false } } }
            });
        }

        document.getElementById('stockForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const name = document.getElementById('stockProductName').value;
            const qty = parseInt(document.getElementById('stockQuantity').value);

            let existing = inventory.find(i => i.product.toLowerCase() === name.toLowerCase());
            if (existing) {
                existing.qty = qty;
            } else {
                inventory.push({ product: name, qty: qty });
            }

            saveAndRender();
            this.reset();
        });

        document.getElementById('saleForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const productName = document.getElementById('saleProductSelect').value;
            const qty = parseInt(document.getElementById('saleQuantity').value);
            const price = parseFloat(document.getElementById('unitPrice').value);
            const status = document.getElementById('paymentStatus').value;

            if (!productName) {
                alert('Cadastre um produto no estoque antes de vender!');
                return;
            }

            let itemInStock = inventory.find(i => i.product === productName);
            if (!itemInStock || itemInStock.qty < qty) {
                alert(`Estoque insuficiente! Você só tem ${itemInStock ? itemInStock.qty : 0} unidades de ${productName}.`);
                return;
            }

            itemInStock.qty -= qty;

            sales.unshift({ id: Date.now(), product: productName, qty, price, status });
            saveAndRender();

            this.reset();
            document.getElementById('saleQuantity').value = 1;
        });

        saveAndRender();
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8501)
