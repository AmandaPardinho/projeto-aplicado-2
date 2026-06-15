/* ============================================================
   api.js — só conversa com o backend.
   Análogo aos seus repositories no Python: zero lógica de UI.
   ============================================================ */

// URL base do backend. Se mudar a porta, mexe SÓ aqui.
const API_BASE = "http://127.0.0.1:8000";

/**
 * Helper genérico — faz QUALQUER requisição HTTP pro backend.
 * @param {string} method - "GET" | "POST" | "PUT" | "DELETE"
 * @param {string} route  - ex.: "/clients" ou "/clients/abc-123"
 * @param {object|null} body - objeto JS que vira JSON (null em GET/DELETE)
 */
async function request(method, route, body = null) {
    const options = {
        method: method,
        headers: { "Content-Type": "application/json" },
    };
    if (body !== null) options.body = JSON.stringify(body);

    const response = await fetch(`${API_BASE}${route}`, options);

    // 204 No Content (caso típico do DELETE) — não tem corpo pra ler
    if (response.status === 204) {
        return { _info: "Excluído com sucesso (204 No Content)" };
    }

    // Lê o corpo como JSON
    const data = await response.json();

    // Se não foi 2xx, lança um erro que CARREGA o status e o corpo inteiro.
    // (Antes a gente jogava fora tudo menos o detail — mas o 409 de CPF
    // repetido traz o `conflict_with`, que o app.js usa pra oferecer reativar.)
    if (!response.ok) {
        const message = typeof data.detail === "string"
            ? data.detail
            : JSON.stringify(data.detail, null, 2);
        const error = new Error(message);
        error.status = response.status;
        error.body = data;
        throw error;
    }

    return data;
}

/* ===== CRUD genérico =====
   As 5 operações agora recebem o `endpoint` da entidade (ex.: "/clients").
   É a mesma ideia de antes, mas servindo as 4 entidades em vez de só Client. */
const api = {
    create: (endpoint, data) => request("POST", endpoint, data),
    list: (endpoint) => request("GET", endpoint),
    get: (endpoint, id) => request("GET", `${endpoint}/${id}`),
    update: (endpoint, id, data) => request("PUT", `${endpoint}/${id}`, data),
    remove: (endpoint, id) => request("DELETE", `${endpoint}/${id}`),
    // Busca de cliente por CPF (só o Client tem). encodeURIComponent cuida da
    // pontuação do CPF na URL.
    getByCpf: (cpf) => request("GET", `/clients/by-cpf/${encodeURIComponent(cpf)}`),
};
