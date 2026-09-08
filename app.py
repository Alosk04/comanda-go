from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comanda Go! - Controle de Comandas</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
        }
    </script>
</head>
<body class="bg-gray-50 dark:bg-slate-900 text-gray-800 dark:text-gray-100 font-sans pt-40 pb-44 flex flex-col min-h-screen select-none transition-colors duration-200">

    <!-- Notificação Flutuante Toast -->
    <div id="toast" class="fixed top-36 right-4 left-4 md:left-auto md:w-96 bg-gray-900 dark:bg-slate-800 text-white px-4 py-3.5 rounded-2xl shadow-2xl z-50 opacity-0 pointer-events-none transition-opacity duration-300 flex items-center gap-3 text-sm font-bold border border-gray-700">
        <span id="toast-icon" class="text-xl">💡</span>
        <div>
            <p id="toast-title" class="text-[10px] text-red-400 uppercase tracking-wider">Aviso Comanda Go</p>
            <span id="toast-msg" class="text-xs">Ação realizada com sucesso!</span>
        </div>
    </div>

    <!-- TOPO FIXO -->
    <header class="fixed top-0 left-0 right-0 bg-white/95 dark:bg-slate-900/95 backdrop-blur-md border-b border-gray-200 dark:border-slate-800 p-3 shadow-lg z-40">
        <div class="max-w-6xl mx-auto space-y-2.5">
            <!-- Barra Superior -->
            <div class="flex justify-between items-center">
                <h1 class="text-base font-extrabold flex items-center gap-1 text-red-600 dark:text-red-500">🚀 Comanda Go!</h1>
                <div class="flex items-center gap-2">
                    <button onclick="alternarTelaCheia()" id="btn-fullscreen" class="bg-gray-100 dark:bg-slate-800 hover:bg-gray-200 px-3 py-2 rounded-xl text-xs font-bold border dark:border-slate-700 shadow-sm" title="Tela Cheia">⛶ Full</button>
                    <button onclick="abrirModalProdutos()" class="bg-gray-100 dark:bg-slate-800 hover:bg-gray-200 text-gray-700 dark:text-gray-200 font-semibold px-3 py-2 rounded-xl shadow-sm transition text-xs border dark:border-slate-700">
                        ⚙️ Produtos
                    </button>
                    <button onclick="alternarModoDark()" id="btn-tema" class="bg-gray-100 dark:bg-slate-800 px-3 py-2 rounded-xl text-xs font-bold border dark:border-slate-700 shadow-sm">🌙</button>
                </div>
            </div>

            <!-- Resumo Rápido -->
            <div class="grid grid-cols-2 gap-2.5">
                <div class="bg-emerald-600 text-white px-3.5 py-2.5 rounded-2xl shadow flex justify-between items-center">
                    <div>
                        <p class="text-[10px] uppercase font-bold text-emerald-100">Recebido (Pago)</p>
                        <h3 id="total-recebido" class="text-base font-extrabold">R$ 0,00</h3>
                    </div>
                    <span class="text-lg">💵</span>
                </div>
                <div class="bg-rose-600 text-white px-3.5 py-2.5 rounded-2xl shadow flex justify-between items-center">
                    <div>
                        <p class="text-[10px] uppercase font-bold text-rose-100">Pendente (Aberto)</p>
                        <h3 id="total-pendente" class="text-base font-extrabold">R$ 0,00</h3>
                    </div>
                    <span class="text-lg">⏳</span>
                </div>
            </div>

            <!-- Filtros Rápidos -->
            <div class="flex gap-2 w-full">
                <button onclick="filtrarStatus('todas')" id="btn-filtro-todas" class="flex-1 py-2 rounded-xl font-black text-xs shadow transition bg-gray-900 text-white dark:bg-slate-700">Todas</button>
                <button onclick="filtrarStatus('abertas')" id="btn-filtro-abertas" class="flex-1 py-2 rounded-xl font-black text-xs shadow transition bg-white dark:bg-slate-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-slate-700">Em Aberto</button>
                <button onclick="filtrarStatus('pagas')" id="btn-filtro-pagas" class="flex-1 py-2 rounded-xl font-black text-xs shadow transition bg-white dark:bg-slate-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-slate-700">Pagas</button>
            </div>
        </div>
    </header>

    <!-- Conteúdo Principal -->
    <main class="max-w-6xl mx-auto px-4 flex-grow w-full mt-2" id="area-swipe">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4" id="lista-comandas">
            <!-- Comandas aqui -->
        </div>
    </main>

    <!-- RODAPÉ FIXO PARA O POLEGAR -->
    <div class="fixed bottom-0 left-0 right-0 bg-white/95 dark:bg-slate-900/95 backdrop-blur-md border-t border-gray-200 dark:border-slate-800 p-3.5 shadow-2xl z-40">
        <div class="max-w-6xl mx-auto space-y-2.5">
            <div class="flex gap-2.5 w-full">
                <button onclick="abrirBalcaoExpresso()" class="flex-1 bg-amber-500 hover:bg-amber-600 text-white font-extrabold py-3.5 px-3 rounded-2xl shadow-lg transition text-xs flex items-center justify-center gap-1.5 active:scale-95">
                    ⚡ Balcão
                </button>
                <button onclick="abrirModalNovoPedido()" class="flex-1 bg-red-600 hover:bg-red-700 text-white font-extrabold py-3.5 px-3 rounded-2xl shadow-lg shadow-red-600/30 transition text-xs flex items-center justify-center gap-1.5 active:scale-95">
                    + Nova Comanda
                </button>
                <button onclick="abrirResumoCaixa()" class="bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-3.5 px-4 rounded-2xl shadow-lg shadow-emerald-600/30 transition text-xs flex items-center justify-center gap-1.5 active:scale-95">
                    📊 Caixa
                </button>
            </div>
            
            <div class="text-center text-[10px] text-gray-500 dark:text-gray-400 pt-1.5 border-t border-gray-100 dark:border-slate-800/60">
                &copy; 2026 Comanda Go! • Desenvolvido por <a href="https://instagram.com/alisonfreitas__" target="_blank" class="text-red-600 dark:text-red-400 font-bold hover:underline">Alison Freitas</a>
            </div>
        </div>
    </div>

    <!-- Modais -->
    <div id="modal-tutorial" class="fixed inset-0 bg-black bg-opacity-60 hidden flex justify-center items-center p-4 z-50">
        <div class="bg-white dark:bg-slate-800 rounded-3xl shadow-2xl max-w-md w-full p-6 transition-colors border border-gray-100 dark:border-slate-700">
            <div class="text-center mb-4">
                <span class="text-4xl">👋</span>
                <h2 class="text-xl font-black text-gray-800 dark:text-gray-100 mt-2">Bem-vindo ao Comanda Go!</h2>
                <p class="text-xs text-red-600 dark:text-red-400 font-bold mt-1">Dicas rápidas para começar:</p>
            </div>
            <div class="space-y-3 mb-6 text-xs text-gray-600 dark:text-gray-300">
                <div class="flex items-start gap-2.5 bg-gray-50 dark:bg-slate-900 p-3 rounded-2xl border dark:border-slate-700">
                    <span class="text-base">⛶</span>
                    <div><strong class="text-gray-800 dark:text-gray-200 block mb-0.5">Modo Tela Cheia</strong>Use o botão "Full" no topo para ocultar as barras do navegador.</div>
                </div>
            </div>
            <div class="flex gap-2">
                <button onclick="fecharTutorial(true)" class="w-1/2 bg-gray-200 dark:bg-slate-700 text-gray-700 dark:text-gray-200 py-3.5 rounded-2xl font-bold text-xs">Não mostrar hoje</button>
                <button onclick="fecharTutorial(false)" class="w-1/2 bg-red-600 text-white py-3.5 rounded-2xl font-bold text-xs shadow-lg shadow-red-600/30">Começar 🚀</button>
            </div>
        </div>
    </div>

    <!-- Modal Nova Comanda -->
    <div id="modal-pedido" class="fixed inset-0 bg-black bg-opacity-50 hidden flex justify-center items-center p-4 z-50">
        <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl max-w-md w-full p-6 transition-colors">
            <h2 class="text-lg font-bold mb-4 text-gray-800 dark:text-gray-100">Abrir Nova Comanda</h2>
            <div class="mb-4">
                <label class="block text-xs font-bold uppercase text-gray-600 dark:text-gray-400 mb-1">Mesa ou Nome do Cliente</label>
                <input type="text" id="nome-cliente" placeholder="Ex: Mesa 03 ou João" class="w-full border-2 border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-gray-800 dark:text-gray-100 rounded-xl p-3.5 text-base focus:border-red-500 focus:outline-none">
            </div>
            <div class="flex space-x-2">
                <button onclick="fecharModalNovoPedido()" class="w-1/2 bg-gray-200 dark:bg-slate-700 text-gray-700 dark:text-gray-200 py-3.5 rounded-xl font-bold">Cancelar</button>
                <button onclick="salvarPedido()" class="w-1/2 bg-red-600 text-white py-3.5 rounded-xl font-bold hover:bg-red-700">Criar Comanda</button>
            </div>
        </div>
    </div>

    <!-- Modal Pagamento -->
    <div id="modal-pagamento" class="fixed inset-0 bg-black bg-opacity-50 hidden flex justify-center items-center p-4 z-50">
        <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl max-w-md w-full p-6 transition-colors">
            <h2 class="text-lg font-bold mb-1 text-gray-800 dark:text-gray-100">Receber Pagamento</h2>
            <p id="pag-info-cliente" class="text-xs text-gray-500 dark:text-gray-400 mb-4 font-bold uppercase"></p>
            <input type="hidden" id="pag-id-comanda">
            <div class="bg-gray-50 dark:bg-slate-900 p-4 rounded-xl mb-4 border dark:border-slate-700">
                <div class="flex justify-between mb-3 items-center">
                    <span class="text-sm font-bold text-gray-600 dark:text-gray-400">Total a Pagar:</span>
                    <span id="pag-valor-total" class="text-xl font-extrabold text-gray-800 dark:text-gray-100">R$ 0,00</span>
                </div>
                <div class="mb-3">
                    <label class="block text-xs font-bold uppercase text-gray-700 dark:text-gray-300 mb-1">Dinheiro Recebido (R$)</label>
                    <input type="number" step="0.01" id="valor-recebido" oninput="calcularTroco()" placeholder="0.00" class="w-full border-2 border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-800 dark:text-gray-100 rounded-xl p-3.5 text-lg font-extrabold focus:border-emerald-500 focus:outline-none">
                </div>
                <div class="grid grid-cols-5 gap-1.5 mb-3">
                    <button onclick="setarValorRecebido(0)" class="bg-white dark:bg-slate-800 border dark:border-slate-700 rounded-xl py-2.5 text-xs font-bold text-gray-700 dark:text-gray-200 shadow-sm">Exato</button>
                    <button onclick="setarValorRecebido(10)" class="bg-white dark:bg-slate-800 border dark:border-slate-700 rounded-xl py-2.5 text-xs font-bold text-gray-700 dark:text-gray-200 shadow-sm">10</button>
                    <button onclick="setarValorRecebido(20)" class="bg-white dark:bg-slate-800 border dark:border-slate-700 rounded-xl py-2.5 text-xs font-bold text-gray-700 dark:text-gray-200 shadow-sm">20</button>
                    <button onclick="setarValorRecebido(50)" class="bg-white dark:bg-slate-800 border dark:border-slate-700 rounded-xl py-2.5 text-xs font-bold text-gray-700 dark:text-gray-200 shadow-sm">50</button>
                    <button onclick="setarValorRecebido(100)" class="bg-white dark:bg-slate-800 border dark:border-slate-700 rounded-xl py-2.5 text-xs font-bold text-gray-700 dark:text-gray-200 shadow-sm">100</button>
                </div>
                <div class="flex justify-between items-center bg-emerald-50 dark:bg-emerald-950/40 p-3.5 rounded-xl border border-emerald-200 dark:border-emerald-800">
                    <span class="text-xs font-bold text-emerald-800 dark:text-emerald-300 uppercase">Troco:</span>
                    <span id="troco-calculado" class="text-lg font-black text-emerald-700 dark:text-emerald-400">R$ 0,00</span>
                </div>
            </div>
            <div class="flex space-x-2">
                <button onclick="fecharModalPagamento()" class="w-1/2 bg-gray-200 dark:bg-slate-700 text-gray-700 dark:text-gray-200 py-3.5 rounded-xl font-bold text-sm">Cancelar</button>
                <button onclick="confirmarRecebimento()" class="w-1/2 bg-emerald-600 text-white py-3.5 rounded-xl font-bold text-sm hover:bg-emerald-700 shadow-lg shadow-emerald-600/30">Baixar Conta</button>
            </div>
        </div>
    </div>

    <!-- Modal Caixa -->
    <div id="modal-caixa" class="fixed inset-0 bg-black bg-opacity-50 hidden flex justify-center items-center p-4 z-50">
        <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl max-w-lg w-full p-6 max-h-[90vh] flex flex-col transition-colors">
            <h2 class="text-lg font-bold mb-3 text-gray-800 dark:text-gray-100">📊 Fechamento e Extrato de Caixa</h2>
            
            <div id="conteudo-relatorio-caixa" class="space-y-2 mb-4 text-xs text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-slate-900 p-3.5 rounded-xl border dark:border-slate-700"></div>

            <h3 class="text-xs font-bold uppercase text-gray-500 dark:text-gray-400 mb-1.5">🧾 Via Detalhada (Consumo por Mesa):</h3>
            <div id="via-detalhada-mesas" class="space-y-2 mb-4 overflow-y-auto max-h-52 pr-1 border dark:border-slate-700 p-2.5 rounded-xl bg-gray-50 dark:bg-slate-900"></div>

            <div class="space-y-2 mt-auto">
                <button onclick="limparCaixaDoDia()" class="w-full bg-rose-100 dark:bg-rose-950/40 text-rose-700 dark:text-rose-300 py-3.5 rounded-xl font-bold text-xs">🗑️ Limpar Contas Pagas do Dia</button>
                <button onclick="fecharResumoCaixa()" class="w-full bg-gray-800 dark:bg-slate-700 text-white py-3.5 rounded-xl font-bold text-xs">Fechar</button>
            </div>
        </div>
    </div>

    <!-- Modal Adicionar Consumo -->
    <div id="modal-adicionar" class="fixed inset-0 bg-black bg-opacity-50 hidden flex justify-center items-center p-4 z-50">
        <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl max-w-lg w-full p-6 max-h-[90vh] flex flex-col transition-colors">
            <!-- Cabeçalho do Modal -->
            <div class="mb-3 bg-emerald-50 dark:bg-emerald-950/40 p-3 rounded-xl border border-emerald-200 dark:border-emerald-800">
                <h2 class="text-sm font-extrabold text-emerald-900 dark:text-emerald-200">Lançar Consumo</h2>
                <p id="titulo-cliente-add" class="text-xs text-emerald-700 dark:text-emerald-400 font-bold uppercase"></p>
            </div>
            
            <input type="hidden" id="add-id-comanda">
            
            <div class="bg-gray-50 dark:bg-slate-900 p-3.5 rounded-xl mb-3 border dark:border-slate-700 space-y-2.5">
                <div class="flex items-center justify-between">
                    <label class="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase">Qtd por clique:</label>
                    <div class="flex items-center gap-1.5">
                        <button onclick="alterarQtdLote(-1)" class="bg-white dark:bg-slate-800 border-2 dark:border-slate-700 font-bold w-10 h-10 rounded-xl shadow-sm">-</button>
                        <input type="number" id="input-qtd-lote" value="1" min="1" onclick="this.select()" class="w-16 text-center font-black bg-white dark:bg-slate-800 border-2 dark:border-slate-700 rounded-xl p-1.5 text-base focus:outline-none">
                        <button onclick="alterarQtdLote(1)" class="bg-white dark:bg-slate-800 border-2 dark:border-slate-700 font-bold w-10 h-10 rounded-xl shadow-sm">+</button>
                    </div>
                </div>
                <div>
                    <input type="text" id="busca-produto" oninput="filtrarProdutosModal()" placeholder="🔍 Buscar produto..." class="w-full border-2 border-gray-200 dark:border-slate-700 rounded-xl p-3 text-sm focus:outline-none bg-white dark:bg-slate-800 text-gray-800 dark:text-gray-100">
                </div>
                <div class="flex gap-1.5 overflow-x-auto pb-1" id="abas-categorias"></div>
            </div>

            <div id="botoes-produtos-rapidos" class="grid grid-cols-2 gap-2.5 overflow-y-auto max-h-56 mb-3 pr-1"></div>

            <div class="border-t dark:border-slate-700 pt-3 mt-auto space-y-2">
                <div class="flex gap-2">
                    <input type="text" id="manual-desc" placeholder="Item avulso" class="w-1/2 border-2 dark:border-slate-700 bg-white dark:bg-slate-900 rounded-xl p-3 text-xs focus:outline-none">
                    <input type="number" step="0.01" id="manual-valor" placeholder="Valor (R$)" class="w-1/4 border-2 dark:border-slate-700 bg-white dark:bg-slate-900 rounded-xl p-3 text-xs focus:outline-none">
                    <button onclick="adicionarItemManual()" class="w-1/4 bg-gray-800 dark:bg-slate-700 text-white rounded-xl text-xs font-bold py-3">+ Adicionar</button>
                </div>
                <!-- Botão Pronto Movido para Baixo -->
                <button onclick="fecharModalAdicionar()" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-3.5 rounded-xl text-sm shadow-lg shadow-emerald-600/30 transition">✓ Pronto (Concluir)</button>
            </div>
        </div>
    </div>

    <!-- Modal Gerenciar Produtos -->
    <div id="modal-produtos" class="fixed inset-0 bg-black bg-opacity-50 hidden flex justify-center items-center p-4 z-50">
        <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl max-w-md w-full p-6 max-h-[90vh] overflow-y-auto transition-colors">
            <h2 class="text-lg font-bold mb-3 text-gray-800 dark:text-gray-100">⚙️ Gerenciar Produtos</h2>
            <div class="bg-gray-50 dark:bg-slate-900 p-3.5 rounded-xl mb-4 border dark:border-slate-700 space-y-2.5">
                <div>
                    <label class="block text-xs font-bold uppercase text-gray-600 dark:text-gray-400 mb-1">Nome do Produto</label>
                    <input type="text" id="prod-nome" placeholder="Ex: Cerveja" class="w-full border-2 dark:border-slate-700 rounded-xl p-3 text-sm focus:outline-none bg-white dark:bg-slate-800 text-gray-800 dark:text-gray-100">
                </div>
                <div class="flex gap-2">
                    <div class="w-1/2">
                        <label class="block text-xs font-bold uppercase text-gray-600 dark:text-gray-400 mb-1">Preço (R$)</label>
                        <input type="number" step="0.01" id="prod-preco" placeholder="0.00" class="w-full border-2 dark:border-slate-700 rounded-xl p-3 text-sm focus:outline-none bg-white dark:bg-slate-800 text-gray-800 dark:text-gray-100">
                    </div>
                    <div class="w-1/2">
                        <label class="block text-xs font-bold uppercase text-gray-600 dark:text-gray-400 mb-1">Categoria</label>
                        <input type="text" id="prod-cat" placeholder="Ex: Bebida" class="w-full border-2 dark:border-slate-700 rounded-xl p-3 text-sm focus:outline-none bg-white dark:bg-slate-800 text-gray-800 dark:text-gray-100 uppercase">
                    </div>
                </div>
                <button onclick="salvarNovoProduto()" class="w-full bg-red-600 text-white py-3.5 rounded-xl text-sm font-bold hover:bg-red-700 shadow-lg shadow-red-600/30">+ Cadastrar Produto</button>
            </div>
            <h3 class="text-xs font-bold uppercase text-gray-500 mb-2">Cadastrados:</h3>
            <div id="lista-produtos-cadastrados" class="space-y-2 mb-4 max-h-40 overflow-y-auto pr-1"></div>
            <div class="flex justify-end">
                <button onclick="fecharModalProdutos()" class="w-full bg-gray-200 dark:bg-slate-700 text-gray-700 dark:text-gray-200 py-3.5 rounded-xl font-bold text-sm">Fechar</button>
            </div>
        </div>
    </div>

    <!-- Script Principal -->
    <script>
        let produtos = JSON.parse(localStorage.getItem('produtos_comandago')) || [
            { id: 1, nome: "Espeto de Carne", preco: 9.00, cat: "COMIDA" },
            { id: 2, nome: "Skol (Litrão)", preco: 14.00, cat: "BEBIDA" }
        ];
        let comandas = JSON.parse(localStorage.getItem('comandas_comandago')) || [];
        let filtroAtual = 'todas';
        let categoriaModalAtual = 'TODOS';
        let toastTimeout = null;

        function alternarTelaCheia() {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen().catch(err => {
                    alert(`Erro ao ativar tela cheia: ${err.message}`);
                });
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                }
            }
        }

        document.addEventListener('fullscreenchange', () => {
            const btn = document.getElementById('btn-fullscreen');
            if (document.fullscreenElement) {
                btn.innerText = '⛶ Sair';
                btn.classList.add('bg-red-600', 'text-white');
            } else {
                btn.innerText = '⛶ Full';
                btn.classList.remove('bg-red-600', 'text-white');
            }
        });

        let touchStartX = 0;
        let touchEndX = 0;
        const ordemFiltros = ['todas', 'abertas', 'pagas'];
        const areaSwipe = document.getElementById('area-swipe');

        areaSwipe.addEventListener('touchstart', e => { touchStartX = e.changedTouches[0].screenX; }, {passive: true});
        areaSwipe.addEventListener('touchend', e => {
            touchEndX = e.changedTouches[0].screenX;
            const diff = touchEndX - touchStartX;
            if (Math.abs(diff) < 50) return;
            let idx = ordemFiltros.indexOf(filtroAtual);
            if (diff < 0) idx = (idx + 1) % ordemFiltros.length;
            else idx = (idx - 1 + ordemFiltros.length) % ordemFiltros.length;
            filtrarStatus(ordemFiltros[idx]);
        }, {passive: true});

        function verificarPrimeiroAcesso() {
            const hoje = new Date().toLocaleDateString();
            if (localStorage.getItem('ultimo_acesso_comandago') !== hoje) {
                document.getElementById('modal-tutorial').classList.remove('hidden');
            }
        }

        function fecharTutorial(naoMostrarHoje) {
            if (naoMostrarHoje) localStorage.setItem('ultimo_acesso_comandago', new Date().toLocaleDateString());
            document.getElementById('modal-tutorial').classList.add('hidden');
        }

        function inicializarTema() {
            const isDark = localStorage.getItem('dark_mode_comandago') === 'true';
            if (isDark) {
                document.documentElement.classList.add('dark');
                document.getElementById('btn-tema').innerText = '☀️';
            } else {
                document.documentElement.classList.remove('dark');
                document.getElementById('btn-tema').innerText = '🌙';
            }
        }
        function alternarModoDark() {
            const isDark = document.documentElement.classList.toggle('dark');
            localStorage.setItem('dark_mode_comandago', isDark);
            document.getElementById('btn-tema').innerText = isDark ? '☀️' : '🌙';
        }
        inicializarTema();

        function mostrarToast(msg, icone = '✔️', titulo = 'Aviso') {
            const t = document.getElementById('toast');
            document.getElementById('toast-msg').innerText = msg;
            document.getElementById('toast-icon').innerText = icone;
            document.getElementById('toast-title').innerText = titulo;
            
            t.classList.remove('opacity-0', 'pointer-events-none');
            t.classList.add('opacity-100');

            if (toastTimeout) clearTimeout(toastTimeout);

            toastTimeout = setTimeout(() => {
                t.classList.remove('opacity-100');
                t.classList.add('opacity-0', 'pointer-events-none');
            }, 2500);
        }

        function salvarStorage() {
            localStorage.setItem('produtos_comandago', JSON.stringify(produtos));
            localStorage.setItem('comandas_comandago', JSON.stringify(comandas));
            atualizarTotaisTopo();
            renderizarComandas();
        }

        function atualizarTotaisTopo() {
            let rec = 0, pend = 0;
            comandas.forEach(c => { if (c.pago) rec += c.valor; else pend += c.valor; });
            document.getElementById('total-recebido').innerText = `R$ ${rec.toFixed(2)}`;
            document.getElementById('total-pendente').innerText = `R$ ${pend.toFixed(2)}`;
        }

        function abrirBalcaoExpresso() {
            const num = 'Balcão ' + Math.floor(Math.random() * 900 + 100);
            comandas.push({ id: Date.now(), cliente: num, itens: [], valor: 0, pago: false, timestamp: Date.now() });
            salvarStorage();
            abrirModalAdicionar(comandas[comandas.length - 1].id);
        }

        function filtrarStatus(status) {
            filtroAtual = status;
            const estiloInativo = "bg-white dark:bg-slate-800 text-gray-500 dark:text-gray-400 border border-gray-200 dark:border-slate-700";
            document.getElementById('btn-filtro-todas').className = `flex-1 py-2 rounded-xl font-black text-xs shadow transition ${status === 'todas' ? 'bg-gray-900 text-white dark:bg-slate-600' : estiloInativo}`;
            document.getElementById('btn-filtro-abertas').className = `flex-1 py-2 rounded-xl font-black text-xs shadow transition ${status === 'abertas' ? 'bg-rose-600 text-white shadow-lg' : estiloInativo}`;
            document.getElementById('btn-filtro-pagas').className = `flex-1 py-2 rounded-xl font-black text-xs shadow transition ${status === 'pagas' ? 'bg-emerald-600 text-white shadow-lg' : estiloInativo}`;
            renderizarComandas();
        }

        function abrirModalProdutos() { renderizarListaProdutosCadastrados(); document.getElementById('modal-produtos').classList.remove('hidden'); }
        function fecharModalProdutos() { document.getElementById('modal-produtos').classList.add('hidden'); }

        function salvarNovoProduto() {
            const nome = document.getElementById('prod-nome').value.trim();
            const preco = parseFloat(document.getElementById('prod-preco').value);
            const cat = document.getElementById('prod-cat').value.trim().toUpperCase() || 'GERAL';
            if (!nome || isNaN(preco)) { alert('Preencha nome e preço!'); return; }
            produtos.push({ id: Date.now(), nome, preco, cat });
            salvarStorage();
            document.getElementById('prod-nome').value = '';
            document.getElementById('prod-preco').value = '';
            document.getElementById('prod-cat').value = '';
            renderizarListaProdutosCadastrados();
            mostrarToast('Produto cadastrado!');
        }

        function excluirProduto(id) {
            produtos = produtos.filter(p => p.id !== id);
            salvarStorage();
            renderizarListaProdutosCadastrados();
        }

        function renderizarListaProdutosCadastrados() {
            const container = document.getElementById('lista-produtos-cadastrados');
            container.innerHTML = '';
            if (produtos.length === 0) { container.innerHTML = `<p class="text-xs text-gray-400 text-center py-2">Nenhum produto.</p>`; return; }
            produtos.forEach(p => {
                const item = document.createElement('div');
                item.className = "flex justify-between items-center bg-gray-50 dark:bg-slate-900 p-3 rounded-xl border dark:border-slate-700 text-sm";
                item.innerHTML = `<span><b>${p.nome}</b> - R$ ${p.preco.toFixed(2)} <span class="text-[10px] bg-gray-200 dark:bg-slate-800 px-1.5 py-0.5 rounded uppercase">${p.cat}</span></span> <button onclick="excluirProduto(${p.id})" class="text-rose-500 font-bold px-2 py-1">✕</button>`;
                container.appendChild(item);
            });
        }

        function abrirModalNovoPedido() { document.getElementById('modal-pedido').classList.remove('hidden'); }
        function fecharModalNovoPedido() { document.getElementById('modal-pedido').classList.add('hidden'); document.getElementById('nome-cliente').value = ''; }
        function salvarPedido() {
            const cliente = document.getElementById('nome-cliente').value.trim();
            if (!cliente) { alert('Informe a mesa ou cliente!'); return; }
            comandas.push({ id: Date.now(), cliente, itens: [], valor: 0, pago: false, timestamp: Date.now() });
            salvarStorage();
            fecharModalNovoPedido();
        }

        function abrirModalAdicionar(id) {
            const comanda = comandas.find(c => c.id === id);
            if (!comanda) return;
            document.getElementById('add-id-comanda').value = id;
            document.getElementById('titulo-cliente-add').innerText = `Mesa: ${comanda.cliente}`;
            document.getElementById('input-qtd-lote').value = '1';
            document.getElementById('busca-produto').value = '';
            document.getElementById('manual-desc').value = '';
            document.getElementById('manual-valor').value = '';
            categoriaModalAtual = 'TODOS';
            atualizarAbasCategorias();
            renderizarBotoesRapidos(id);
            document.getElementById('modal-adicionar').classList.remove('hidden');
        }

        function fecharModalAdicionar() {
            document.getElementById('modal-adicionar').classList.add('hidden');
            renderizarComandas();
        }

        function alterarQtdLote(v) {
            const inp = document.getElementById('input-qtd-lote');
            let at = parseInt(inp.value) || 1;
            at += v;
            if (at < 1) at = 1;
            inp.value = at;
        }

        function filtrarCategoria(cat) {
            categoriaModalAtual = cat;
            atualizarAbasCategorias();
            renderizarBotoesRapidos(parseInt(document.getElementById('add-id-comanda').value));
        }

        function atualizarAbasCategorias() {
            const containerAbas = document.getElementById('abas-categorias');
            containerAbas.innerHTML = '';
            let cats = ['TODOS'];
            produtos.forEach(p => { let c = (p.cat || 'GERAL').toUpperCase(); if (!cats.includes(c)) cats.push(c); });
            cats.forEach(cat => {
                const btn = document.createElement('button');
                const ativo = (cat === categoriaModalAtual);
                btn.className = `px-3.5 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition ${ativo ? 'bg-red-600 text-white shadow' : 'bg-white dark:bg-slate-800 text-gray-600 dark:text-gray-300 border dark:border-slate-700'}`;
                btn.innerText = cat;
                btn.onclick = () => filtrarCategoria(cat);
                containerAbas.appendChild(btn);
            });
        }

        function filtrarProdutosModal() { renderizarBotoesRapidos(parseInt(document.getElementById('add-id-comanda').value)); }

        function renderizarBotoesRapidos(idComanda) {
            const container = document.getElementById('botoes-produtos-rapidos');
            container.innerHTML = '';
            const termo = document.getElementById('busca-produto').value.toLowerCase();
            let filtrados = produtos.filter(p => {
                let matchCat = (categoriaModalAtual === 'TODOS' || (p.cat || 'GERAL').toUpperCase() === categoriaModalAtual);
                let matchNome = p.nome.toLowerCase().includes(termo);
                return matchCat && matchNome;
            });
            if (filtrados.length === 0) { container.innerHTML = `<p class="text-xs text-gray-400 col-span-2 text-center py-4">Nenhum produto.</p>`; return; }
            filtrados.forEach(p => {
                const btn = document.createElement('button');
                btn.className = "bg-red-50 dark:bg-slate-900 border-2 border-red-100 dark:border-slate-700 text-red-700 dark:text-red-400 font-semibold p-3.5 rounded-2xl text-xs hover:bg-red-100 dark:hover:bg-slate-800 flex flex-col items-center justify-center transition shadow-sm active:scale-95";
                btn.innerHTML = `<span class="font-bold text-center">${p.nome}</span><span class="text-gray-500 dark:text-gray-400 text-xs mt-1 font-bold">R$ ${p.preco.toFixed(2)}</span>`;
                btn.onclick = () => {
                    const qtd = parseInt(document.getElementById('input-qtd-lote').value) || 1;
                    adicionarItemComandaMultiplo(idComanda, p.nome, p.preco, qtd);
                    mostrarToast(`+${qtd}x ${p.nome} adicionado!`);
                };
                container.appendChild(btn);
            });
        }

        function adicionarItemComandaMultiplo(idComanda, nomeItem, valorUnitario, quantidade) {
            comandas = comandas.map(c => {
                if (c.id === idComanda) {
                    for (let i = 0; i < quantidade; i++) {
                        c.itens.push({ idItem: Date.now() + Math.random(), nome: nomeItem, preco: valorUnitario });
                        c.valor += valorUnitario;
                    }
                }
                return c;
            });
            salvarStorage();
            document.getElementById('input-qtd-lote').value = '1';
        }

        function adicionarItemManual() {
            const idComanda = parseInt(document.getElementById('add-id-comanda').value);
            const desc = document.getElementById('manual-desc').value.trim();
            const valor = parseFloat(document.getElementById('manual-valor').value);
            const qtd = parseInt(document.getElementById('input-qtd-lote').value) || 1;
            if (!desc || isNaN(valor)) { alert('Informe nome e valor!'); return; }
            adicionarItemComandaMultiplo(idComanda, desc, valor, qtd);
            document.getElementById('manual-desc').value = '';
            document.getElementById('manual-valor').value = '';
            mostrarToast(`+${qtd}x ${desc} avulso adicionado!`);
        }

        function removerItemComanda(idComanda, idItem) {
            comandas = comandas.map(c => {
                if (c.id === idComanda) {
                    const idx = c.itens.findIndex(i => i.idItem === idItem);
                    if (idx !== -1) { c.valor -= c.itens[idx].preco; c.itens.splice(idx, 1); }
                }
                return c;
            });
            salvarStorage();
        }

        function iniciarPagamento(id) {
            const comanda = comandas.find(c => c.id === id);
            if (!comanda) return;
            document.getElementById('pag-id-comanda').value = id;
            document.getElementById('pag-info-cliente').innerText = `Mesa: ${comanda.cliente}`;
            document.getElementById('pag-valor-total').innerText = `R$ ${comanda.valor.toFixed(2)}`;
            document.getElementById('valor-recebido').value = '';
            document.getElementById('troco-calculado').innerText = 'R$ 0,00';
            document.getElementById('modal-pagamento').classList.remove('hidden');
        }

        function setarValorRecebido(quantia) {
            const id = parseInt(document.getElementById('pag-id-comanda').value);
            const comanda = comandas.find(c => c.id === id);
            let val = quantia === 0 ? comanda.valor : quantia;
            document.getElementById('valor-recebido').value = val.toFixed(2);
            calcularTroco();
        }

        function calcularTroco() {
            const id = parseInt(document.getElementById('pag-id-comanda').value);
            const comanda = comandas.find(c => c.id === id);
            const recebido = parseFloat(document.getElementById('valor-recebido').value);
            if (isNaN(recebido) || recebido < comanda.valor) {
                document.getElementById('troco-calculado').innerText = 'R$ 0,00';
                return;
            }
            document.getElementById('troco-calculado').innerText = `R$ ${(recebido - comanda.valor).toFixed(2)}`;
        }

        function confirmarRecebimento() {
            const id = parseInt(document.getElementById('pag-id-comanda').value);
            comandas = comandas.map(c => { if (c.id === id) c.pago = true; return c; });
            salvarStorage();
            fecharModalPagamento();
            mostrarToast('Conta baixada com sucesso!');
        }

        function reabrirComanda(id) {
            comandas = comandas.map(c => { if (c.id === id) c.pago = false; return c; });
            salvarStorage();
            mostrarToast('Comanda reaberta!', '🔄');
        }

        function fecharModalPagamento() { document.getElementById('modal-pagamento').classList.add('hidden'); }

        function abrirResumoCaixa() {
            let totalRecebido = 0, totalPendente = 0, pagas = 0, abertas = 0;
            comandas.forEach(c => {
                if (c.pago) { totalRecebido += c.valor; pagas++; }
                else { totalPendente += c.valor; abertas++; }
            });
            
            document.getElementById('conteudo-relatorio-caixa').innerHTML = `
                <div class="flex justify-between py-1 border-b dark:border-slate-700"><span>Comandas Pagas:</span> <b>${pagas}</b></div>
                <div class="flex justify-between py-1 border-b dark:border-slate-700"><span>Comandas Abertas:</span> <b>${abertas}</b></div>
                <div class="flex justify-between py-1 border-b dark:border-slate-700 text-emerald-600 dark:text-emerald-400"><span>Entrada Total (Caixa):</span> <b>R$ ${totalRecebido.toFixed(2)}</b></div>
                <div class="flex justify-between py-1 text-rose-600 dark:text-rose-400"><span>A Receber nas Mesas:</span> <b>R$ ${totalPendente.toFixed(2)}</b></div>
            `;

            const containerVia = document.getElementById('via-detalhada-mesas');
            containerVia.innerHTML = '';
            if (comandas.length === 0) {
                containerVia.innerHTML = `<p class="text-xs text-gray-400 text-center py-4">Nenhuma comanda registrada.</p>`;
            } else {
                comandas.forEach(c => {
                    let contagemItens = {};
                    c.itens.forEach(i => {
                        contagemItens[i.nome] = (contagemItens[i.nome] || 0) + 1;
                    });

                    let itensStr = Object.entries(contagemItens)
                        .map(([nome, qtd]) => `<span class="text-[11px] bg-white dark:bg-slate-800 px-2 py-0.5 rounded border dark:border-slate-700 inline-block m-0.5">${qtd}x ${nome}</span>`)
                        .join(' ');

                    if (c.itens.length === 0) {
                        itensStr = '<span class="text-[11px] text-gray-400 italic">Nenhum item lançado</span>';
                    }

                    const cardMesa = document.createElement('div');
                    cardMesa.className = `p-2.5 rounded-xl border text-xs bg-white dark:bg-slate-800 ${c.pago ? 'border-emerald-200 dark:border-emerald-900' : 'border-rose-200 dark:border-rose-900'}`;
                    cardMesa.innerHTML = `
                        <div class="flex justify-between items-center mb-1.5 font-bold">
                            <span class="text-gray-800 dark:text-gray-200">${c.cliente}</span>
                            <span class="${c.pago ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}">${c.pago ? '✓ PAGO' : '⏳ ABERTO'} — R$ ${c.valor.toFixed(2)}</span>
                        </div>
                        <div class="flex flex-wrap gap-1">${itensStr}</div>
                    `;
                    containerVia.appendChild(cardMesa);
                });
            }

            document.getElementById('modal-caixa').classList.remove('hidden');
        }
        function fecharResumoCaixa() { document.getElementById('modal-caixa').classList.add('hidden'); }

        function limparCaixaDoDia() {
            if (confirm('Deseja excluir todas as comandas PAGAS?')) {
                comandas = comandas.filter(c => !c.pago);
                salvarStorage();
                fecharResumoCaixa();
                mostrarToast('Histórico de pagas limpo.');
            }
        }

        function excluirComanda(id) {
            if (confirm('Deseja apagar esta comanda?')) {
                comandas = comandas.filter(c => c.id !== id);
                salvarStorage();
            }
        }

        function renderizarComandas() {
            const container = document.getElementById('lista-comandas');
            container.innerHTML = '';
            let filtradas = comandas.filter(c => {
                if (filtroAtual === 'abertas') return !c.pago;
                if (filtroAtual === 'pagas') return c.pago;
                return true;
            });

            if (filtradas.length === 0) {
                container.innerHTML = `<p class="text-gray-400 col-span-3 text-center py-10 font-medium">Nenhuma comanda encontrada.</p>`;
                return;
            }

            const agora = Date.now();
            filtradas.forEach(c => {
                const diffMinutos = Math.floor((agora - (c.timestamp || agora)) / 60000);
                let corTempoBg = 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/30 dark:text-emerald-400 dark:border-emerald-800';
                let txtTempo = `${diffMinutos} min`;
                if (diffMinutos >= 60) {
                    corTempoBg = 'bg-rose-100 text-rose-800 border-rose-300 font-bold dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-800';
                    txtTempo = `${Math.floor(diffMinutos/60)}h ${diffMinutos%60}m`;
                } else if (diffMinutos >= 30) {
                    corTempoBg = 'bg-amber-100 text-amber-800 border-amber-300 font-bold dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800';
                }

                const card = document.createElement('div');
                card.className = `bg-white dark:bg-slate-800 rounded-2xl shadow-md p-4 border-l-8 ${c.pago ? 'border-emerald-500' : 'border-rose-500'} flex flex-col justify-between transition-colors relative mt-4`;

                let listaItensHtml = '';
                if (c.itens && c.itens.length > 0) {
                    listaItensHtml = '<ul class="text-xs text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-slate-900 p-3 rounded-xl mb-3 space-y-2 max-h-36 overflow-y-auto">';
                    c.itens.forEach(item => {
                        listaItensHtml += `<li class="flex justify-between items-center bg-white dark:bg-slate-800 p-2.5 rounded-xl border dark:border-slate-700 shadow-sm">
                            <span>• ${item.nome}</span>
                            <div class="flex items-center gap-3">
                                <span class="font-bold">R$ ${item.preco.toFixed(2)}</span>
                                ${!c.pago ? `<button onclick="removerItemComanda(${c.id}, ${item.idItem})" class="text-rose-500 hover:text-rose-700 font-bold px-2 py-1 text-sm">✕</button>` : ''}
                            </div>
                        </li>`;
                    });
                    listaItensHtml += '</ul>';
                } else {
                    listaItensHtml = '<p class="text-xs text-gray-400 bg-gray-50 dark:bg-slate-900 p-3 rounded-xl mb-3 italic">Nenhum item lançado.</p>';
                }

                card.innerHTML = `
                    <div>
                        <div class="absolute -top-3 left-4">
                            <span class="inline-block text-[11px] font-bold px-3.5 py-1 rounded-full border shadow-sm ${c.pago ? 'bg-emerald-100 text-emerald-800 border-emerald-200 dark:bg-emerald-950 dark:text-emerald-300 dark:border-emerald-800' : corTempoBg}">
                                ${c.pago ? '✓ CONTA PAGA' : '⏱️ Há ' + txtTempo}
                            </span>
                        </div>
                        <div class="flex justify-between items-start mb-2 pt-2">
                            <div><h3 class="font-black text-lg text-gray-800 dark:text-gray-100">${c.cliente}</h3></div>
                            <span class="text-xs font-bold px-3.5 py-1.5 rounded-xl ${c.pago ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300' : 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300'}">
                                ${c.pago ? 'PAGO' : 'ABERTO'}
                            </span>
                        </div>
                        ${listaItensHtml}
                    </div>
                    <div>
                        <div class="flex justify-between items-center mb-3.5 pt-2 border-t dark:border-slate-700">
                            <span class="text-xs font-bold uppercase text-gray-400">Total:</span>
                            <span class="text-xl font-black text-gray-800 dark:text-gray-100">R$ ${c.valor.toFixed(2)}</span>
                        </div>
                        <div class="space-y-2.5">
                            ${!c.pago ? `<button onclick="abrirModalAdicionar(${c.id})" class="w-full bg-rose-600 hover:bg-rose-700 text-white py-3.5 rounded-xl text-sm font-bold shadow-sm transition">+ Adicionar Consumo</button>` : ''}
                            <div class="flex space-x-2">
                                <button onclick="${c.pago ? `reabrirComanda(${c.id})` : `iniciarPagamento(${c.id})`}" class="flex-1 py-3.5 text-sm rounded-xl font-bold ${c.pago ? 'bg-amber-500 text-white hover:bg-amber-600' : 'bg-emerald-600 text-white hover:bg-emerald-700'} shadow-sm transition">
                                    ${c.pago ? 'Reabrir Comanda' : 'Receber Conta'}
                                </button>
                                <button onclick="excluirComanda(${c.id})" class="bg-gray-100 dark:bg-slate-700 text-gray-600 dark:text-gray-200 px-4 py-3.5 rounded-xl hover:bg-gray-200 text-sm font-bold">🗑️</button>
                            </div>
                        </div>
                    </div>
                `;
                container.appendChild(card);
            });
        }

        atualizarTotaisTopo();
        renderizarComandas();
        verificarPrimeiroAcesso();
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8501)

