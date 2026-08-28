from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Vendas & Caixa Pro</title>
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

        body.dark-mode {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-dark: #f8fafc;
            --text-muted: #94a3b8;
            --border: #334155;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, -apple-system, sans-serif; }
        body { background-color: var(--bg-color); color: var(--text-dark); padding: 15px; max-width: 1200px; margin: 0 auto; transition: background 0.3s, color 0.3s; }
        
        header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        header h1 { font-size: 20px; }
        .btn-theme { background: var(--border); border: none; padding: 8px 12px; border-radius: 20px; cursor: pointer; color: var(--text-dark); font-size: 12px; font-weight: bold; }

        .grid-forms { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .form-card { background: var(--card-bg); padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
        .form-card h2 { font-size: 14px; margin-bottom: 12px; color: var(--primary); }
        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; }
        .form-group { display: flex; flex-direction: column; }
        .form-group label { font-size: 11px; font-weight: bold; margin-bottom: 4px; color: var(--text-muted); }
        .form-group input, .form-group select { padding: 8px; border: 1px solid var(--border); border-radius: 6px; font-size: 13px; background: var(--card-bg); color: var(--text-dark); }
        .btn-submit { grid-column: 1 / -1; background-color: var(--primary); color: white; border: none; padding: 10px; border-radius: 6px; font-size: 14px; font-weight: bold; cursor: pointer; margin-top: 5px; }

        .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; margin-bottom: 20px; }
        .kpi-card { background: var(--card-bg); padding: 12px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 4px solid var(--primary); }
        .kpi-card.green { border-left-color: var(--success); }
        .kpi-card.amber { border-left-color: var(--warning); }
        .kpi-card.red { border-left-color: var(--danger); }
        .kpi-card h3 { font-size: 11px; text-transform: uppercase; color: var(--text-muted); }
        .kpi-card .value { font-size: 18px; font-weight: bold; margin-top: 4px; }

        .dashboard-content { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .chart-card, .table-card { background: var(--card-bg); padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
        .card-header-flex { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px; }
        .card-header { font-size: 14px; font-weight: bold; }
        
        .search-input { padding: 6px 10px; border: 1px solid var(--border); border-radius: 6px; font-size: 12px; background: var(--card-bg); color: var(--text-dark); }

        .table-responsive { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; text-align: left; font-size: 13px; }
        th, td { padding: 10px 8px; border-bottom: 1px solid var(--border); white-space: nowrap; }
        .badge { padding: 3px 6px; border-radius: 8px; font-size: 10px; font-weight: bold; }
        .badge-paid { background: #dcfce7; color: var(--success); }
        .badge-pending { background: #fef3c7; color: var(--warning); }
        .badge-low { background: #fee2e2; color: var(--danger); }
        .badge-ok { background: #dcfce7; color: var(--success); }
        .btn-action { background: none; border: none; cursor: pointer; font-size: 14px; margin-right: 4px; }

        .summary-box { background: var(--card-bg); padding: 15px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
        .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; margin-top: 10px; }
        .summary-item { background: var(--bg-color); padding: 10px; border-radius: 8px; text-align: center; }
        .summary-item label { font-size: 10px; text-transform: uppercase; color: var(--text-muted); display: block; }
        .summary-item span { font-weight: bold; font-size: 14px; }

        footer { text-align: center; padding: 20px 10px; margin-top: 30px; border-top: 1px solid var(--border); font-size: 13px; color: var(--text-muted); }
        .insta-link { display: inline-flex; align-items: center; gap: 6px; margin-top: 6px; color: #e1306c; text-decoration: none; font-weight: bold; }
        .insta-link:hover { text-decoration: underline; }
    </style>
</head>
<body>

    <header>
        <h1>📊 Gestão de Vendas & Caixa Pro</h1>
        <button class="btn-theme" onclick="toggleDarkMode()">🌙 Tema</button>
    </header>

    <div class="grid-forms">
        <!-- FORMULARIO DE ESTOQUE COM PREÇO DE CUSTO -->
        <div class="form-card">
            <h2>📦 Cadastrar / Atualizar Estoque</h2>
            <form id="stockForm" class="form-grid">
                <div class="form-group" style="grid-column: 1 / -1;">
                    <label>Produto</label>
                    <input type="text" id="stockProductName" placeholder="Ex: Camiseta Nike" required>
                </div>
                <div class="form-group">
                    <label>Qtd em Estoque</label>
                    <input type="number" id="stockQuantity" min="0" value="10" required>
                </div>
                <div class="form-group">
                    <label>Preço Custo (R$)</label>
                    <input type="number" id="costPrice" step="0.01" min="0" placeholder="0.00" required>
                </div>
                <button type="submit" class="btn-submit" style="background-color: var(--success);">Salvar Produto</button>
            </form>
        </div>

        <!-- FORMULARIO DE VENDA AVANÇADO -->
        <div class="form-card">
            <h2>🛒 Registrar Venda</h2>
            <form id="saleForm" class="form-grid">
                <div class="form-group" style="grid-column: 1 / -1;">
                    <label>Cliente (Nome / WhatsApp)</label>
                    <input type="text" id="customerName" placeholder="Ex: João (99) 99999-9999">
                </div>
                <div class="form-group" style="grid-column: 1 / -1;">
                    <label>Produto</label>
                    <select id="saleProductSelect" required></select>
                </div>
                <div class="form-group">
                    <label>Qtd Vendida</label>
                    <input type="number" id="saleQuantity" min="1" value="1" required>
                </div>
                <div class="form-group">
                    <label>Valor Unit. (R$)</label>
                    <input type="number" id="unitPrice" step="0.01" min="0" placeholder="0.00" required>
                </div>
                <div class="form-group">
                    <label>Desconto (R$)</label>
                    <input type="number" id="discount" step="0.01" min="0" value="0.00">
                </div>
                <div class="form-group">
                    <label>Taxas/Frete (R$)</label>
                    <input type="number" id="fees" step="0.01" min="0" value="0.00">
                </div>
                <div class="form-group">
                    <label>Pagamento</label>
                    <select id="paymentMethod">
                        <option value="Pix">Pix</option>
                        <option value="Dinheiro">Dinheiro</option>
                        <option value="Cartão de Crédito">Cartão de Crédito</option>
                        <option value="Cartão de Débito">Cartão de Débito</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Status</label>
                    <select id="paymentStatus">
                        <option value="Pago">Pago</option>
                        <option value="Pendente">Pendente</option>
                    </select>
                </div>
                <button type="submit" class="btn-submit">Finalizar e Baixar Estoque</button>
            </form>
        </div>
    </div>

    <!-- PAINEL DE KPIS COM LUCRO REAL -->
    <div class="kpi-grid">
        <div class="kpi-card green">
            <h3>Faturamento</h3>
            <div class="value" id="kpiReceived">R$ 0,00</div>
        </div>
        <div class="kpi-card green">
            <h3>Lucro Liquido</h3>
            <div class="value" id="kpiProfit">R$ 0,00</div>
        </div>
        <div class="kpi-card amber">
            <h3>A Receber (Pendente)</h3>
            <div class="value" id="kpiPending">R$ 0,00</div>
        </div>
        <div class="kpi-card">
            <h3>Total de Vendas</h3>
            <div class="value" id="kpiTotalSales">0</div>
        </div>
        <div class="kpi-card red">
            <h3>Estoque Baixo</h3>
            <div class="value" id="kpiLowStock">0 prod.</div>
        </div>
    </div>

    <!-- FECHAMENTO DE CAIXA POR FORMA DE PAGAMENTO -->
    <div class="summary-box">
        <div class="card-header">💵 Resumo de Caixa por Método de Pagamento</div>
        <div class="summary-grid">
            <div class="summary-item">
                <label>Pix</label>
                <span id="sumPix">R$ 0,00</span>
            </div>
            <div class="summary-item">
                <label>Dinheiro</label>
                <span id="sumMoney">R$ 0,00</span>
            </div>
            <div class="summary-item">
                <label>Crédito</label>
                <span id="sumCredit">R$ 0,00</span>
            </div>
            <div class="summary-item">
                <label>Débito</label>
                <span id="sumDebit">R$ 0,00</span>
            </div>
        </div>
    </div>

    <!-- TABELA DE ESTOQUE -->
    <div class="table-card" style="margin-bottom: 20px;">
        <div class="card-header-flex">
            <div class="card-header">📦 Posição do Estoque</div>
            <input type="text" id="searchStock" class="search-input" placeholder="Buscar produto..." onkeyup="renderStockTable()">
        </div>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr>
                        <th>Produto</th>
                        <th>Custo Unit.</th>
                        <th>Qtd. Restante</th>
                        <th>Status</th>
                        <th>Ação</th>
                    </tr>
                </thead>
                <tbody id="stockTableBody"></tbody>
            </table>
        </div>
    </div>

    <!-- GRÁFICOS -->
    <div class="dashboard-content">
        <div class="chart-card">
            <div class="card-header">Recebido vs Pendente</div>
            <canvas id="statusChart"></canvas>
        </div>
        <div class="chart-card">
            <div class="card-header">Vendas por Meio de Pagamento</div>
            <canvas id="methodChart"></canvas>
        </div>
    </div>

    <!-- HISTÓRICO DE VENDAS COMPLETO -->
    <div class="table-card">
        <div class="card-header-flex">
            <div class="card-header">📋 Histórico de Vendas</div>
            <input type="text" id="searchSales" class="search-input" placeholder="Buscar venda ou cliente..." onkeyup="renderSalesTable()">
        </div>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr>
                        <th>Cliente</th>
                        <th>Produto</th>
                        <th>Qtd.</th>
                        <th>Total Final</th>
                        <th>Lucro</th>
                        <th>Método</th>
                        <th>Status</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody id="salesTableBody"></tbody>
            </table>
        </div>
    </div>

    <footer>
        <p>Desenvolvido por <strong>Alison Freitas</strong></p>
        <a href="https://instagram.com/alisonfreitas__" target="_blank" class="insta-link">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path d="M8 0C5.829 0 5.556.01 4.703.048 3.85.088 3.269.222 2.76.42a3.917 3.917 0 0 0-1.417.923A3.927 3.927 0 0 0 .42 2.76C.222 3.268.087 3.85.048 4.7.01 5.555 0 5.827 0 8.001c0 2.172.01 2.444.048 3.297.04.852.174 1.433.372 1.942.205.526.478.972.923 1.417.444.445.89.719 1.416.923.51.198 1.09.333 1.942.372C5.555 15.99 5.827 16 8 16s2.444-.01 3.298-.048c.851-.04 1.434-.174 1.943-.372a3.916 3.916 0 0 0 1.416-.923c.445-.445.718-.891.923-1.417.197-.509.332-1.09.372-1.942C15.99 10.445 16 10.173 16 8s-.01-2.445-.048-3.299c-.04-.851-.175-1.433-.372-1.941a3.926 3.926 0 0 0-.923-1.417A3.911 3.911 0 0 0 13.24.42c-.51-.198-1.092-.333-1.943-.372C10.443.01 10.172 0 7.998 0h.003zm-.717 1.442h.718c2.136 0 2.389.007 3.232.046.78.035 1.204.166 1.486.275.373.145.64.319.92.599.28.28.453.546.598.92.11.281.24.705.275 1.485.039.843.047 1.096.047 3.231s-.008 2.389-.047 3.232c-.035.78-.166 1.203-.275 1.485a2.47 2.47 0 0 1-.599.919c-.28.28-.546.453-.92.598-.28.11-.704.24-1.485.276-.843.038-1.096.047-3.232.047s-2.39-.009-3.233-.047c-.78-.036-1.203-.166-1.485-.276a2.478 2.478 0 0 1-.92-.598 2.48 2.48 0 0 1-.6-.92c-.109-.281-.24-.705-.275-1.485-.038-.843-.046-1.096-.046-3.233 0-2.136.008-2.388.046-3.231.036-.78.166-1.204.276-1.486.145-.373.319-.64.599-.92.28-.28.546-.453.92-.598.282-.11.705-.24 1.485-.276.738-.034 1.024-.044 2.515-.045v.002zm4.988 1.328a.96.96 0 1 0 0 1.92.96.96 0 0 0 0-1.92zm-4.27 1.252a4.001 4.001 0 1 0 0 8.001 4.001 4.001 0 0 0 0-8.001zm0 1.442a2.559 2.559 0 1 1 0 5.118 2.559 2.559 0 0 1 0-5.118z"/>
            </svg>
            @alisonfreitas__
        </a>
    </footer>

    <script>
        let inventory = JSON.parse(localStorage.getItem('my_inventory')) || [
            { product: 'Camiseta Nike', qty: 15, cost: 30.0 },
            { product: 'Calça Jeans', qty: 3, cost: 60.0 }
        ];

        let sales = JSON.parse(localStorage.getItem('my_dashboard_sales')) || [
            { id: 1, customer: 'João', product: 'Camiseta Nike', qty: 2, price: 60.0, discount: 0, fees: 0, cost: 30.0, method: 'Pix', status: 'Pago' }
        ];

        let statusChart, methodChart;

        function toggleDarkMode() {
            document.body.classList.toggle('dark-mode');
        }

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
                select.innerHTML = '<option value="">Cadastre um produto primeiro</option>';
                return;
            }
            inventory.forEach(item => {
                const opt = document.createElement('option');
                opt.value = item.product;
                opt.innerText = `${item.product} (${item.qty} un.) - Custo: R$ ${item.cost.toFixed(2)}`;
                select.appendChild(opt);
            });
        }

        function updateKPIs() {
            let received = 0, pending = 0, profit = 0;
            let sumPix = 0, sumMoney = 0, sumCredit = 0, sumDebit = 0;

            sales.forEach(s => {
                const totalSale = (s.qty * s.price) - (s.discount || 0) + (s.fees || 0);
                const totalCost = s.qty * (s.cost || 0);
                const saleProfit = totalSale - totalCost;

                if (s.status === 'Pago') {
                    received += totalSale;
                    profit += saleProfit;

                    if (s.method === 'Pix') sumPix += totalSale;
                    else if (s.method === 'Dinheiro') sumMoney += totalSale;
                    else if (s.method === 'Cartão de Crédito') sumCredit += totalSale;
                    else if (s.method === 'Cartão de Débito') sumDebit += totalSale;
                } else {
                    pending += totalSale;
                }
            });

            let lowStockCount = inventory.filter(i => i.qty <= 3).length;

            document.getElementById('kpiReceived').innerText = formatCurrency(received);
            document.getElementById('kpiProfit').innerText = formatCurrency(profit);
            document.getElementById('kpiPending').innerText = formatCurrency(pending);
            document.getElementById('kpiTotalSales').innerText = sales.length;
            document.getElementById('kpiLowStock').innerText = lowStockCount + ' prod.';

            document.getElementById('sumPix').innerText = formatCurrency(sumPix);
            document.getElementById('sumMoney').innerText = formatCurrency(sumMoney);
            document.getElementById('sumCredit').innerText = formatCurrency(sumCredit);
            document.getElementById('sumDebit').innerText = formatCurrency(sumDebit);
        }

        function renderStockTable() {
            const tbody = document.getElementById('stockTableBody');
            const query = document.getElementById('searchStock').value.toLowerCase();
            tbody.innerHTML = '';

            inventory.filter(i => i.product.toLowerCase().includes(query)).forEach((item, index) => {
                const badgeClass = item.qty <= 3 ? 'badge-low' : 'badge-ok';
                const badgeText = item.qty <= 3 ? 'Baixo ⚠️' : 'OK';
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${item.product}</strong></td>
                    <td>${formatCurrency(item.cost || 0)}</td>
                    <td>${item.qty} unid.</td>
                    <td><span class="badge ${badgeClass}">${badgeText}</span></td>
                    <td><button class="btn-action" onclick="deleteStock(${index})">❌</button></td>
                `;
                tbody.appendChild(tr);
            });
        }

        function renderSalesTable() {
            const tbody = document.getElementById('salesTableBody');
            const query = document.getElementById('searchSales').value.toLowerCase();
            tbody.innerHTML = '';

            sales.filter(s => 
                s.product.toLowerCase().includes(query) || 
                (s.customer && s.customer.toLowerCase().includes(query))
            ).forEach((s, index) => {
                const totalSale = (s.qty * s.price) - (s.discount || 0) + (s.fees || 0);
                const totalCost = s.qty * (s.cost || 0);
                const profit = totalSale - totalCost;
                const badgeClass = s.status === 'Pago' ? 'badge-paid' : 'badge-pending';
                
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${s.customer || 'Geral'}</td>
                    <td><strong>${s.product}</strong></td>
                    <td>${s.qty}</td>
                    <td><strong>${formatCurrency(totalSale)}</strong></td>
                    <td style="color:${profit >= 0 ? 'var(--success)' : 'var(--danger)'}">${formatCurrency(profit)}</td>
                    <td>${s.method}</td>
                    <td>
                        <span class="badge ${badgeClass}" style="cursor:pointer;" onclick="toggleStatus(${index})">
                            ${s.status} 🔄
                        </span>
                    </td>
                    <td>
                        <button class="btn-action" title="Enviar WhatsApp" onclick="sendWhatsApp(${index})">📲</button>
                        <button class="btn-action" title="Excluir" onclick="deleteSale(${index})">❌</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        function sendWhatsApp(index) {
            const s = sales[index];
            const totalSale = (s.qty * s.price) - (s.discount || 0) + (s.fees || 0);
            
            let text = "";
            if (s.status === 'Pago') {
                text = `*Comprovante de Compra*\n\n` +
                       `Cliente: ${s.customer || 'Cliente'}\n` +
                       `Produto: ${s.product} (x${s.qty})\n` +
                       `Valor Total: ${formatCurrency(totalSale)}\n` +
                       `Forma de Pagamento: ${s.method}\n` +
                       `Status: Pago ✅\n\nObrigado pela preferência!`;
            } else {
                text = `*Lembrete de Pagamento*\n\n` +
                       `Olá ${s.customer || ''}, passando para lembrar referente ao pedido:\n` +
                       `Produto: ${s.product} (x${s.qty})\n` +
                       `Valor em Aberto: ${formatCurrency(totalSale)}\n\n` +
                       `Por favor, entre em contato para combinar o acerto.`;
            }

            window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`, '_blank');
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
            let methodTotals = { 'Pix': 0, 'Dinheiro': 0, 'Cartão de Crédito': 0, 'Cartão de Débito': 0 };

            sales.forEach(s => {
                const totalSale = (s.qty * s.price) - (s.discount || 0) + (s.fees || 0);
                if (s.status === 'Pago') {
                    received += totalSale;
                    if (methodTotals[s.method] !== undefined) methodTotals[s.method] += totalSale;
                } else {
                    pending += totalSale;
                }
            });

            const ctxStatus = document.getElementById('statusChart').getContext('2d');
            if (statusChart) statusChart.destroy();
            statusChart = new Chart(ctxStatus, {
                type: 'doughnut',
                data: {
                    labels: ['Pago', 'Pendente'],
                    datasets: [{ data: [received, pending], backgroundColor: ['#16a34a', '#d97706'] }]
                },
                options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
            });

            const ctxMethod = document.getElementById('methodChart').getContext('2d');
            if (methodChart) methodChart.destroy();
            methodChart = new Chart(ctxMethod, {
                type: 'bar',
                data: {
                    labels: Object.keys(methodTotals),
                    datasets: [{ label: 'Total (R$)', data: Object.values(methodTotals), backgroundColor: '#2563eb' }]
                },
                options: { responsive: true, plugins: { legend: { display: false } } }
            });
        }

        document.getElementById('stockForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const name = document.getElementById('stockProductName').value;
            const qty = parseInt(document.getElementById('stockQuantity').value);
            const cost = parseFloat(document.getElementById('costPrice').value);

            let existing = inventory.find(i => i.product.toLowerCase() === name.toLowerCase());
            if (existing) {
                existing.qty = qty;
                existing.cost = cost;
            } else {
                inventory.push({ product: name, qty: qty, cost: cost });
            }

            saveAndRender();
            this.reset();
        });

        document.getElementById('saleForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const customer = document.getElementById('customerName').value;
            const productName = document.getElementById('saleProductSelect').value;
            const qty = parseInt(document.getElementById('saleQuantity').value);
            const price = parseFloat(document.getElementById('unitPrice').value);
            const discount = parseFloat(document.getElementById('discount').value) || 0;
            const fees = parseFloat(document.getElementById('fees').value) || 0;
            const method = document.getElementById('paymentMethod').value;
            const status = document.getElementById('paymentStatus').value;

            if (!productName) {
                alert('Cadastre um produto no estoque antes!');
                return;
            }

            let itemInStock = inventory.find(i => i.product === productName);
            if (!itemInStock || itemInStock.qty < qty) {
                alert(`Estoque insuficiente! Apenas ${itemInStock ? itemInStock.qty : 0} em estoque.`);
                return;
            }

            itemInStock.qty -= qty;

            sales.unshift({
                id: Date.now(),
                customer: customer,
                product: productName,
                qty: qty,
                price: price,
                discount: discount,
                fees: fees,
                cost: itemInStock.cost || 0,
                method: method,
                status: status
            });
            saveAndRender();

            this.reset();
            document.getElementById('saleQuantity').value = 1;
            document.getElementById('discount').value = '0.00';
            document.getElementById('fees').value = '0.00';
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
