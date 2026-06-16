/* ============================================================
   app.js — lógica de UI.
   Mexe no DOM, escuta eventos, lê o ENTITIES (entities.js)
   e chama o api.js. Não conhece HTTP nem regras de negócio.
   ============================================================ */

// As 5 ações padrão (toda entidade tem). Entidades podem somar `extraActions`.
const BASE_ACTIONS = [
    { value: "create", label: "Cadastrar novo" },
    { value: "list", label: "Listar todos" },
    { value: "get", label: "Buscar por ID" },
    { value: "update", label: "Atualizar" },
    { value: "delete", label: "Excluir" },
];

// Texto que o botão exibe pra cada ação
const BUTTON_LABEL = {
    create: "Cadastrar",
    list: "Listar todos",
    get: "Buscar",
    update: "Atualizar",
    delete: "Excluir",
    "find-cpf": "Buscar por CPF",
};

// Ícones SVG inline (estilo Lucide). O container leva aria-hidden — o rótulo ao lado já informa.
const ICON = {
    idle: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/></svg>',
    loading: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>',
    ok: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.8 10A10 10 0 1 1 17 3.34"/><path d="m9 11 3 3L22 4"/></svg>',
    error: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
    moon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>',
    sun: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>',
};

// Rótulo padrão de cada estado da saída do servidor
const STATUS_LABEL = { idle: "Aguardando ação", loading: "Enviando…", ok: "Sucesso", error: "Erro" };

// ===== Estado da tela =====
let currentEntityKey = "clients"; // qual entidade está selecionada
let currentAction = "create";     // qual ação está selecionada

// ===== Referências de elementos fixos da página =====
const nav = document.querySelector("#nav");
const entityTitle = document.querySelector("#entity-title");
const form = document.querySelector("#crud-form");
const actionSelect = document.querySelector("#action");
const formFields = document.querySelector("#form-fields");
const formHint = document.querySelector("#form-hint");
const submitButton = form.querySelector("button[type='submit']");
const output = document.querySelector("#output");           // o <pre> com o corpo (JSON)
const outputWrap = document.querySelector("#server-output"); // wrapper que leva o data-state
const statusIcon = outputWrap.querySelector(".status-icon");
const statusLabel = outputWrap.querySelector(".status-label");
const tableCard = document.querySelector("#table-card");
const tableHead = document.querySelector("#table-head");
const tableBody = document.querySelector("#table-body");
const tableTitle = document.querySelector("#table-title");
const modeToggle = document.querySelector("#mode-toggle");
const actionPrompt = document.querySelector("#action-prompt");

/* ============================================================
   1. Barra lateral — uma entrada por entidade do ENTITIES
   ============================================================ */
function renderNav() {
    nav.innerHTML = "";
    Object.entries(ENTITIES).forEach(([key, entity]) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "nav-item" + (key === currentEntityKey ? " is-active" : "");
        btn.textContent = entity.label;
        btn.addEventListener("click", () => selectEntity(key));
        nav.appendChild(btn);
    });
}

function selectEntity(key) {
    currentEntityKey = key;
    renderNav();
    entityTitle.textContent = ENTITIES[key].label;
    renderActionOptions(ENTITIES[key]);
    hideTable();
    clearPrompt();
    clearOutput();
    renderForm();
}

// Monta o <select> de ações: as 5 padrão + as extras da entidade (ex.: Buscar por CPF).
function renderActionOptions(entity) {
    // ordem alfabética pelo rótulo que a usuária lê (pt-BR cuida dos acentos)
    const all = [...BASE_ACTIONS, ...(entity.extraActions || [])]
        .sort((a, b) => a.label.localeCompare(b.label, "pt-BR"));
    actionSelect.innerHTML = all
        .map((a) => `<option value="${a.value}">${a.label}</option>`)
        .join("");
    // se a ação atual não existe nessa entidade (ex.: troquei de entidade), volta pro create
    if (!all.some((a) => a.value === currentAction)) currentAction = "create";
    actionSelect.value = currentAction;
}

/* ============================================================
   2. Formulário dinâmico — monta os campos da entidade + ação
   ============================================================ */
function fieldToHtml(field) {
    const id = `f-${field.name}`;
    // "*" sempre que o campo for obrigatório e a ação não for atualizar (no PUT tudo é parcial).
    // aria-required avisa o leitor de tela; o "*" visual fica aria-hidden pra não duplicar.
    const required = field.required && currentAction !== "update";
    const star = required ? ' <span class="req" aria-hidden="true">*</span>' : "";
    const ariaReq = required ? ' aria-required="true"' : "";

    if (field.type === "checkbox") {
        const checked = field.default ? "checked" : "";
        return `
            <div class="field field--check">
                <label class="check">
                    <input id="${id}" name="${field.name}" type="checkbox" ${checked}>
                    <span>${field.label}</span>
                </label>
            </div>`;
    }

    if (field.type === "select") {
        const opts = field.options
            .map((o) => `<option value="${o.value}">${o.label}</option>`)
            .join("");
        return `
            <div class="field">
                <label for="${id}">${field.label}${star}</label>
                <select id="${id}" name="${field.name}"${ariaReq}>${opts}</select>
            </div>`;
    }

    // text | email | date | number
    const attrs = [
        `type="${field.type}"`,
        field.placeholder ? `placeholder="${field.placeholder}"` : "",
        field.min !== undefined ? `min="${field.min}"` : "",
        field.step ? `step="${field.step}"` : "",
    ].filter(Boolean).join(" ");

    return `
        <div class="field">
            <label for="${id}">${field.label}${star}</label>
            <input id="${id}" name="${field.name}" ${attrs}${ariaReq}>
        </div>`;
}

// Campo de ID (UUID) — aparece em buscar/atualizar/excluir
function idFieldHtml() {
    return `
        <div class="field">
            <label for="f-id">ID (UUID) <span class="req" aria-hidden="true">*</span></label>
            <input id="f-id" name="id" type="text" aria-required="true" placeholder="cole o UUID aqui">
        </div>`;
}

function renderForm() {
    const entity = ENTITIES[currentEntityKey];
    let html = "";

    // get/update/delete precisam do ID
    if (["get", "update", "delete"].includes(currentAction)) {
        html += idFieldHtml();
    }

    // qualquer campo cujo `actions` inclua a ação atual (create, update, find-cpf...)
    entity.fields
        .filter((f) => f.actions.includes(currentAction))
        .forEach((f) => { html += fieldToHtml(f); });

    formFields.innerHTML = html;
    applyMasks();

    submitButton.textContent = BUTTON_LABEL[currentAction] || "Enviar";

    // dica contextual
    if (currentAction === "list") {
        formHint.textContent = `Clique em "${BUTTON_LABEL.list}" para ver todos os registros.`;
    } else if (currentAction === "delete") {
        formHint.textContent = "Atenção: a exclusão é um soft-delete (desativa o registro).";
    } else if (currentAction === "find-cpf") {
        formHint.textContent = "A busca acha a aluna mesmo se ela estiver inativa.";
    } else {
        formHint.textContent = "";
    }
}

// Máscaras visuais (CPF e WhatsApp). Recriadas a cada render porque
// o formulário é reconstruído do zero quando muda entidade/ação.
function applyMasks() {
    const cpf = formFields.querySelector('[name="cpf"]');
    if (cpf) IMask(cpf, { mask: "000.000.000-00" });

    const whatsapp = formFields.querySelector('[name="whatsapp_number"]');
    if (whatsapp) IMask(whatsapp, { mask: "(00) 00000-0000" });
}

/* ============================================================
   3. Coleta dos campos preenchidos
   ============================================================ */
function collectFields() {
    const data = {};
    formFields.querySelectorAll("input, select").forEach((input) => {
        const name = input.name;
        if (!name) return;
        const value = input.type === "checkbox" ? input.checked : input.value.trim();
        if (value === "") return; // ignora vazios (essencial pro PUT parcial)
        data[name] = value;
    });
    return data;
}

/* ============================================================
   4. Saída do servidor (#output) com estados visuais
   ============================================================ */
// state pinta o ícone+rótulo+moldura; body é o JSON cru (some quando vazio); label sobrescreve o padrão.
function setOutput(state, body = "", label) {
    outputWrap.dataset.state = state;
    statusIcon.innerHTML = ICON[state] || "";
    statusLabel.textContent = label || STATUS_LABEL[state] || "";
    output.textContent = body;
    output.classList.toggle("hidden", !body); // sem corpo, esconde o <pre>
}
function clearOutput() {
    setOutput("idle");
}

/* ============================================================
   4.5. Prompt de decisão — quando um CPF já existe (reativar × cancelar)
   A reativação NUNCA é automática: quem decide é a recepção (a aluna pode
   ter passado o CPF pra pedir exclusão por LGPD, não pra voltar).
   ============================================================ */
function clearPrompt() {
    actionPrompt.innerHTML = "";
    actionPrompt.classList.add("hidden");
}

/**
 * Mostra o aviso de cliente já existente, com a decisão na mão da recepção.
 * @param {{id:string, name:string, is_active:boolean}} found
 * @param {{reactivateLabel:string, onReactivate:Function}} opts
 */
function showClientFoundPrompt(found, opts) {
    actionPrompt.innerHTML = "";

    const msg = document.createElement("p");
    msg.className = "prompt-msg";
    const situacao = found.is_active ? "ativa" : "inativa";
    // o nome entra por textContent (sem risco de injeção de HTML)
    msg.append("Esse CPF já é de ");
    const strong = document.createElement("strong");
    strong.textContent = found.name;
    msg.append(strong, `, que está ${situacao}.`);
    if (found.is_active) {
        msg.append(" Confira se é a mesma pessoa antes de cadastrar de novo.");
    }

    const actions = document.createElement("div");
    actions.className = "prompt-actions";

    // botão de reativar só faz sentido se ela está INATIVA
    if (!found.is_active && opts.onReactivate) {
        const yes = document.createElement("button");
        yes.type = "button";
        yes.className = "btn-primary btn-sm";
        yes.textContent = opts.reactivateLabel;
        yes.addEventListener("click", () => opts.onReactivate(found));
        actions.append(yes);
    }

    const no = document.createElement("button");
    no.type = "button";
    no.className = "btn-ghost btn-sm";
    no.textContent = found.is_active ? "Fechar" : "Cancelar";
    no.addEventListener("click", clearPrompt);
    actions.append(no);

    actionPrompt.append(msg, actions);
    actionPrompt.classList.remove("hidden");
}

// Reativa (PUT is_active=true; o service limpa o deleted_at). `extra` permite
// mandar junto os dados que a recepção digitou (reativa E atualiza).
async function reactivateClient(endpoint, id, extra, successPrefix) {
    try {
        const result = await api.update(endpoint, id, { ...extra, is_active: true });
        clearPrompt();
        hideTable();
        setOutput("ok", JSON.stringify(result, null, 2), successPrefix);
    } catch (err) {
        setOutput("error", err.message, "Erro ao reativar");
    }
}

/* ============================================================
   5. Tabela de listagem — montada a partir das colunas do ENTITIES
   ============================================================ */
function formatCpf(value) {
    const d = String(value).replace(/\D/g, "");
    if (d.length !== 11) return value;
    return d.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");
}

function formatWhatsapp(value) {
    const d = String(value).replace(/\D/g, "");
    // Banco guarda com o 55 na frente (5511987654321). Tira o código do país pra exibir.
    const national = d.length === 13 && d.startsWith("55") ? d.slice(2) : d;
    if (national.length !== 11) return value;
    return national.replace(/(\d{2})(\d{5})(\d{4})/, "($1) $2-$3");
}

function formatBRL(value) {
    const n = Number(value);
    if (Number.isNaN(n)) return String(value);
    return n.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function formatDateTime(value) {
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return String(value);
    return d.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

// Traduz o valor de um enum (ex.: "prospect") para o label em PT ("Prospecto"),
// usando as próprias options definidas no ENTITIES.
function enumLabel(entity, key, value) {
    const field = entity.fields.find((f) => f.name === key && f.type === "select");
    if (!field) return String(value);
    const opt = field.options.find((o) => o.value === value);
    return opt ? opt.label : String(value);
}

function formatValue(value, col, entity) {
    if (value === null || value === undefined || value === "") return "—";
    switch (col.format) {
        case "cpf": return formatCpf(value);
        case "whatsapp": return formatWhatsapp(value);
        case "brl": return formatBRL(value);
        case "bool": return value ? "Sim" : "Não";
        case "datetime": return formatDateTime(value);
        case "enum": return enumLabel(entity, col.key, value);
        default: return String(value);
    }
}

function renderTable(items) {
    const entity = ENTITIES[currentEntityKey];

    tableHead.innerHTML =
        "<tr>" + entity.columns.map((c) => `<th>${c.label}</th>`).join("") + "</tr>";
    tableBody.innerHTML = "";

    if (!Array.isArray(items) || items.length === 0) {
        tableBody.innerHTML = `<tr><td class="empty" colspan="${entity.columns.length}">Nenhum registro ainda.</td></tr>`;
    } else {
        items.forEach((item) => {
            const tr = document.createElement("tr");
            entity.columns.forEach((col) => {
                const td = document.createElement("td");
                // textContent (não innerHTML) evita injeção de HTML pelos dados do banco
                td.textContent = formatValue(item[col.key], col, entity);
                tr.appendChild(td);
            });
            tableBody.appendChild(tr);
        });
    }

    tableTitle.textContent = `${entity.label} cadastrados`;
    tableCard.classList.remove("hidden");
}

function hideTable() {
    tableCard.classList.add("hidden");
}

/* ============================================================
   6. Eventos
   ============================================================ */
actionSelect.addEventListener("change", () => {
    currentAction = actionSelect.value;
    hideTable();
    clearPrompt();
    renderForm();
});

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const entity = ENTITIES[currentEntityKey];
    const data = collectFields();
    const id = data.id; // pode estar undefined
    delete data.id;     // o id vai pela URL, não no corpo

    clearPrompt();
    setOutput("loading");
    submitButton.disabled = true; // trava o botão enquanto a requisição está no ar

    try {
        let response;
        switch (currentAction) {
            case "create":
                response = await api.create(entity.endpoint, data);
                break;
            case "list":
                response = await api.list(entity.endpoint);
                renderTable(response);
                break;
            case "get":
                if (!id) throw new Error("Informe o ID para buscar.");
                response = await api.get(entity.endpoint, id);
                break;
            case "update":
                if (!id) throw new Error("Informe o ID para atualizar.");
                response = await api.update(entity.endpoint, id, data);
                break;
            case "delete":
                if (!id) throw new Error("Informe o ID para excluir.");
                response = await api.remove(entity.endpoint, id);
                break;
            case "find-cpf":
                if (!data.cpf) throw new Error("Informe o CPF para buscar.");
                response = await api.getByCpf(data.cpf);
                // achou: se inativa, oferece reativar (sem dados novos — é só busca)
                showClientFoundPrompt(response, {
                    reactivateLabel: `Reativar ${response.name}`,
                    onReactivate: (found) =>
                        reactivateClient(entity.endpoint, found.id, {}, "Cliente reativado"),
                });
                break;
        }
        setOutput("ok", JSON.stringify(response, null, 2));
    } catch (error) {
        // 409 com conflict_with = CPF repetido. Em vez de só barrar, oferece a
        // decisão de reativar (reativa E atualiza com os dados recém-digitados).
        const conflict = (error.status === 409 && error.body) ? error.body.conflict_with : null;
        if (conflict) {
            setOutput("error", error.message);
            showClientFoundPrompt(conflict, {
                reactivateLabel: `Reativar e atualizar ${conflict.name}`,
                onReactivate: (found) =>
                    reactivateClient(entity.endpoint, found.id, data, "Cliente reativado e atualizado"),
            });
        } else {
            setOutput("error", error.message);
        }
    } finally {
        submitButton.disabled = false; // libera o botão de volta (deu certo ou não)
    }
});

/* ============================================================
   7. Modo claro/escuro (a paleta é fixa: Ametista, definida no <html>)
   ============================================================ */
const prefersDark = matchMedia("(prefers-color-scheme: dark)");

function applyMode(mode) {
    document.documentElement.dataset.mode = mode;
    // o botão mostra a AÇÃO (pra onde vai ao clicar), não o estado atual
    const goingToLight = mode === "dark";
    modeToggle.innerHTML =
        (goingToLight ? ICON.sun : ICON.moon) +
        `<span>${goingToLight ? "Modo claro" : "Modo escuro"}</span>`;
    modeToggle.setAttribute("aria-pressed", mode === "dark");
}

modeToggle.addEventListener("click", () => {
    const next = document.documentElement.dataset.mode === "dark" ? "light" : "dark";
    localStorage.setItem("studio-mode", next); // a partir do 1º clique, escolha manual
    applyMode(next);
});

// Enquanto NÃO houver escolha manual salva, acompanha o sistema em tempo real
prefersDark.addEventListener("change", (event) => {
    if (!localStorage.getItem("studio-mode")) applyMode(event.matches ? "dark" : "light");
});

/* ============================================================
   8. Boot — o <head> já definiu mode/theme (sem flash); aqui só sincronizamos
   ============================================================ */
applyMode(document.documentElement.dataset.mode || "light");
renderNav();
selectEntity("clients");
