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

    // Se não foi 2xx, lança erro com a mensagem do backend
    if (!response.ok) {
        throw new Error(JSON.stringify(data.detail, null, 2));
    }

    return data;
}

// ===== 5 funções de 1 linha — cada uma é uma operação CRUD =====
const createClient = (data)     => request("POST",   "/clients", data);
const listClients  = ()         => request("GET",    "/clients");
const getClient    = (id)       => request("GET",    `/clients/${id}`);
const updateClient = (id, data) => request("PUT",    `/clients/${id}`, data);
const deleteClient = (id)       => request("DELETE", `/clients/${id}`);
