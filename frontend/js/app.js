/* ============================================================
   app.js — lógica de UI.
   Mexe em DOM, escuta eventos, chama o api.js.
   ============================================================ */

// Texto que o botão exibe pra cada ação
const BUTTON_LABEL = {
    create: "Cadastrar",
    list:   "Listar",
    get:    "Buscar",
    update: "Atualizar",
    delete: "Excluir",
};

// 1. Pega referências dos elementos da página que vamos usar
const form         = document.querySelector("form");
const output       = document.querySelector("#output");
const actionSelect = document.querySelector("#action");
const submitButton = form.querySelector("button[type='submit']");

// 2. Função que mostra/esconde campos conforme a ação selecionada
function applyAction() {
    const action = actionSelect.value;

    // Atualiza o texto do botão
    submitButton.textContent = BUTTON_LABEL[action];

    // Para cada .field, decide se mostra ou esconde
    document.querySelectorAll(".field").forEach((field) => {
        const allowedActions = (field.dataset.actions || "").split(" ");
        if (allowedActions.includes(action)) {
            field.classList.remove("hidden");
        } else {
            field.classList.add("hidden");
        }
    });
}

// 3. Liga o evento "mudou o select" → reaplica
actionSelect.addEventListener("change", applyAction);
applyAction(); // roda uma vez ao carregar pra estado inicial

// 3.5. Máscaras de input (IMask).
// São puramente VISUAIS: o backend já normaliza (joga fora pontuação),
// então mandar "(11) 98765-4321" ou "5511987654321" dá no mesmo lá no servidor.
// Os inputs continuam no DOM mesmo quando ocultos, então basta aplicar uma vez.
IMask(document.querySelector("#client-cpf"), {
    mask: "000.000.000-00",
});
IMask(document.querySelector("#client-whatsapp"), {
    mask: "(00) 00000-0000",
});

// 4. Função que coleta os campos VISÍVEIS e PREENCHIDOS do form
function collectFields() {
    const data = {};
    document.querySelectorAll(".field:not(.hidden)").forEach((field) => {
        const input = field.querySelector("input, select");
        if (!input) return;
        const fieldName = input.name;
        const value = input.type === "checkbox" ? input.checked : input.value.trim();
        if (value === "") return; // ignora vazios (importante pro PUT parcial)
        data[fieldName] = value;
    });
    return data;
}

// 4.5. Formatação para EXIBIÇÃO (o banco guarda só dígitos; aqui deixamos bonito).
//      Se o valor vier fora do formato esperado, devolvemos como veio (não quebra a tela).
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

// 4.6. Monta a tabela de clientes a partir da lista que o backend devolve.
function renderTable(clients) {
    const tableBody = document.querySelector("#table-body");
    tableBody.innerHTML = ""; // limpa render anterior

    clients.forEach((client) => {
        const tr = document.createElement("tr");

        const tdName = document.createElement("td");
        tdName.textContent = client.name; // textContent (não innerHTML) evita injeção de HTML pelo nome

        const tdCpf = document.createElement("td");
        tdCpf.textContent = formatCpf(client.cpf);

        const tdWhatsapp = document.createElement("td");
        tdWhatsapp.textContent = formatWhatsapp(client.whatsapp_number);

        tr.append(tdName, tdCpf, tdWhatsapp);
        tableBody.appendChild(tr);
    });

    document.querySelector("#table-block").classList.remove("hidden");
}

// 5. Submit — escolhe o método HTTP conforme a ação selecionada
form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const action = actionSelect.value;
    const data   = collectFields();
    const id     = data.id;     // pode estar undefined
    delete data.id;             // id vai pela URL, não no body

    output.textContent = "⏳ Enviando...";

    try {
        let response;
        switch (action) {
            case "create":
                response = await createClient(data);
                break;
            case "list":
                response = await listClients();
                renderTable(response); // além do JSON cru no #output, monta a tabela bonita
                break;
            case "get":
                if (!id) throw new Error("Informe o ID para buscar.");
                response = await getClient(id);
                break;
            case "update":
                if (!id) throw new Error("Informe o ID para atualizar.");
                response = await updateClient(id, data);
                break;
            case "delete":
                if (!id) throw new Error("Informe o ID para excluir.");
                response = await deleteClient(id);
                break;
        }
        output.textContent = "✅ Sucesso:\n" + JSON.stringify(response, null, 2);
    } catch (error) {
        output.textContent = "❌ Erro:\n" + error.message;
    }
});
