const API_URL = "http://127.0.0.1:8000";

// ==========================================
// FUNÇÕES DO MODAL CUSTOMIZADO
// ==========================================
function mostrarAlerta(titulo, mensagem, tipo = 'success') {
    const modal = document.getElementById('customModal');
    const modalBox = modal.querySelector('.modal-box');
    
    document.getElementById('modalTitle').innerText = titulo;
    document.getElementById('modalMessage').innerHTML = mensagem;

    modalBox.className = `modal-box ${tipo}`; // Define a cor (success ou error)
    modal.classList.remove('hidden');
}

function fecharModal() {
    document.getElementById('customModal').classList.add('hidden');
}

// ==========================================
// RF-001: Cadastrar Encomenda (Admin)
// ==========================================
async function cadastrarEncomenda() {
    const descricao = document.getElementById('novaDescricao').value.trim();
    if (!descricao) return mostrarAlerta("Atenção", "Digite uma descrição para o pacote.", "error");

    try {
        const response = await fetch(`${API_URL}/encomendas`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ descricao: descricao })
        });

        const data = await response.json();

        if (response.ok) {
            mostrarAlerta(
                "✅ Encomenda Criada!",
                `<p>O pacote foi registrado no sistema.</p>
                 <p style="font-size: 18px; background: #f4f7f6; padding: 10px; border-radius: 5px;">
                    <strong>Código:</strong> <span style="color: #007bff;">${data.codigo_rastreio}</span><br>
                    <strong>Status:</strong> ${data.status}
                 </p>`,
                "success"
            );
            
            document.getElementById('novaDescricao').value = ''; 
            document.getElementById('codigoAtribuir').value = data.codigo_rastreio;
        } else {
            mostrarAlerta("❌ Erro", data.detail, "error");
        }
    } catch (error) {
        mostrarAlerta("Erro de Conexão", "Não foi possível conectar com a API.", "error");
    }
}

// ==========================================
// RF-002: Atribuir Entregador (Admin)
// ==========================================
async function atribuirEntregador() {
    const codigo = document.getElementById('codigoAtribuir').value.trim();
    const idEntregador = parseInt(document.getElementById('idAtribuir').value);

    if (!codigo || isNaN(idEntregador)) return mostrarAlerta("Atenção", "Preencha o código e o ID numérico do entregador.", "error");

    try {
        const response = await fetch(`${API_URL}/encomendas/${codigo}/atribuir`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id_entregador: idEntregador })
        });

        const data = await response.json();

        if (response.ok) {
            mostrarAlerta("✅ Sucesso", `Entregador <strong>${idEntregador}</strong> atribuído ao pacote <strong>${codigo}</strong> com sucesso!`, "success");
            document.getElementById('codigoAtribuir').value = '';
            document.getElementById('idAtribuir').value = '';
            
            if (document.getElementById('idEntregador').value == idEntregador) {
                carregarPainel();
            }
        } else {
            mostrarAlerta("❌ Erro", data.detail, "error");
        }
    } catch (error) {
        mostrarAlerta("Erro", "Erro de comunicação com a API ao atribuir entregador.", "error");
    }
}

// ==========================================
// RF-003: Consultar Rastreio Público (Cliente)
// ==========================================
async function rastrearEncomenda() {
    const codigo = document.getElementById('codigoRastreio').value.trim();
    const divResultado = document.getElementById('resultadoRastreio');
    
    if (!codigo) return mostrarAlerta("Atenção", "Digite um código de rastreio válido.", "error");

    try {
        const response = await fetch(`${API_URL}/encomendas/${codigo}`);
        const data = await response.json();

        divResultado.classList.remove('hidden');

        if (response.ok) {
            divResultado.innerHTML = `
                <h3>Status: <span class="badge ${data.status.replace(' ', '-')}">${data.status}</span></h3>
                <p><strong>Código:</strong> ${data.codigo_rastreio}</p>
                <p><strong>Descrição:</strong> ${data.descricao}</p>
            `;
        } else {
            divResultado.innerHTML = `<p style="color: red;">❌ Erro: ${data.detail}</p>`;
        }
    } catch (error) {
        mostrarAlerta("Erro", "Erro ao conectar com o servidor. Verifique se a API está rodando.", "error");
    }
}

// ==========================================
// RF-006: Listar Encomendas do Entregador
// ==========================================
async function carregarPainel() {
    const idEntregador = document.getElementById('idEntregador').value;
    const divLista = document.getElementById('listaEncomendas');

    if (!idEntregador) return mostrarAlerta("Atenção", "Informe seu ID de entregador.", "error");

    try {
        const response = await fetch(`${API_URL}/entregadores/${idEntregador}/encomendas`);
        const encomendas = await response.json();

        divLista.classList.remove('hidden');
        divLista.innerHTML = `<h3>Rotas Ativas (ID: ${idEntregador})</h3>`;

        if (encomendas.length === 0) {
            divLista.innerHTML += `<p>Nenhuma entrega pendente para você.</p>`;
            return;
        }

        encomendas.forEach(enc => {
            let botoesAcao = '';
            if (enc.status === 'Pendente') {
                botoesAcao = `<button onclick="atualizarStatus('${enc.codigo_rastreio}', 'Em Trânsito')">Iniciar Rota</button>`;
            } else if (enc.status === 'Em Trânsito') {
                botoesAcao = `
                    <button class="success" onclick="atualizarStatus('${enc.codigo_rastreio}', 'Entregue')">Entregue</button>
                    <button class="danger" onclick="atualizarStatus('${enc.codigo_rastreio}', 'Falhou')">Falhou</button>
                `;
            }

            divLista.innerHTML += `
                <div class="encomenda-item">
                    <div>
                        <strong>${enc.codigo_rastreio}</strong> - ${enc.descricao} <br>
                        <span class="badge ${enc.status.replace(' ', '-')}">${enc.status}</span>
                    </div>
                    <div>
                        ${botoesAcao}
                    </div>
                </div>
            `;
        });
    } catch (error) {
        mostrarAlerta("Erro", "Erro ao conectar com o servidor ao carregar painel.", "error");
    }
}

// ==========================================
// RF-004 e RF-005: Atualizar Status da Encomenda
// ==========================================
async function atualizarStatus(codigo_rastreio, novo_status) {
    try {
        const response = await fetch(`${API_URL}/encomendas/${codigo_rastreio}/status`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ novo_status: novo_status })
        });

        const data = await response.json();

        if (response.ok) {
            carregarPainel();
        } else {
            mostrarAlerta("❌ Erro", data.detail, "error");
        }
    } catch (error) {
        mostrarAlerta("Erro", "Erro de comunicação com a API ao atualizar status.", "error");
    }
}