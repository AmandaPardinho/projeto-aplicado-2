/* ============================================================
   api.js — só conversa com o backend.
   Análogo aos seus repositories no Python: zero lógica de UI.
   ============================================================ */

// URL base do backend. Se mudar a porta, mexe SÓ aqui.
const API_BASE = "http://127.0.0.1:8000";

/**
 * Helper genérico — faz QUALQUER requisição HTTP pro backend.
 * @param {string} metodo - "GET" | "POST" | "PUT" | "DELETE"
 * @param {string} rota   - ex.: "/clients" ou "/clients/abc-123"
 * @param {object|null} corpo - objeto JS que vira JSON (null em GET/DELETE)
 */
async function request(metodo, rota, corpo = null) {
    const opcoes = {
        method: metodo,
        headers: { "Content-Type": "application/json" },
    };
    if (corpo !== null) opcoes.body = JSON.stringify(corpo);

    const resposta = await fetch(`${API_BASE}${rota}`, opcoes);

    // 204 No Content (caso típico do DELETE) — não tem corpo pra ler
    if (resposta.status === 204) {
        return { _info: "Excluído com sucesso (204 No Content)" };
    }

    // Lê o corpo como JSON
    const dados = await resposta.json();

    // Se não foi 2xx, lança erro com a mensagem do backend
    if (!resposta.ok) {
        throw new Error(JSON.stringify(dados.detail, null, 2));
    }

    return dados;
}

// ===== 5 funções de 1 linha — cada uma é uma operação CRUD =====
const criarAluno     = (dados)     => request("POST",   "/clients", dados);
const listarAlunos   = ()          => request("GET",    "/clients");
const buscarAluno    = (id)        => request("GET",    `/clients/${id}`);
const atualizarAluno = (id, dados) => request("PUT",    `/clients/${id}`, dados);
const excluirAluno   = (id)        => request("DELETE", `/clients/${id}`);
