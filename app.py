from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comanda Go! - Controle de Comandas</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
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
                <button onclick="gerarPdfCaixa()" class="w-full bg-red-600 hover:bg-red-700 text-white py-3.5 rounded-xl font-bold text-xs shadow-lg shadow-red-600/30">📄 Baixar PDF do Caixa do Dia</button>
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
            <h3 class="text-xs font
