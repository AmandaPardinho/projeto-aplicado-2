/* ============================================================
   app.js — lógica de UI.
   Mexe em DOM, escuta eventos, chama o api.js.
   ============================================================ */

// Texto que o botão exibe pra cada ação
const TEXTO_BOTAO = {
    criar:     "Cadastrar",
    listar:    "Listar",
    buscar:    "Buscar",
    atualizar: "Atualizar",
    excluir:   "Excluir",
};

// 1. Pega referências dos elementos da página que vamos usar
const form        = document.querySelector("form");
const saida       = document.querySelector("#saida");
const acaoSelect  = document.querySelector("#acao");
const botao       = form.querySelector("button[type='submit']");

// 2. Função que mostra/esconde campos conforme a ação selecionada
function aplicarAcao() {
    const acao = acaoSelect.value;

    // Atualiza o texto do botão
    botao.textContent = TEXTO_BOTAO[acao];

    // Para cada .campo, decide se mostra ou esconde
    document.querySelectorAll(".campo").forEach((campo) => {
        const acoesPermitidas = (campo.dataset.actions || "").split(" ");
        if (acoesPermitidas.includes(acao)) {
            campo.classList.remove("oculto");
        } else {
            campo.classList.add("oculto");
        }
    });
}

// 3. Liga o evento "mudou o select" → reaplica
acaoSelect.addEventListener("change", aplicarAcao);
aplicarAcao(); // roda uma vez ao carregar pra estado inicial

// 4. Função que coleta os campos VISÍVEIS e PREENCHIDOS do form
function coletarCampos() {
    const dados = {};
    document.querySelectorAll(".campo:not(.oculto)").forEach((campo) => {
        const input = campo.querySelector("input, select");
        if (!input) return;
        const nome = input.name;
        const valor = input.type === "checkbox" ? input.checked : input.value.trim();
        if (valor === "") return; // ignora vazios (importante pro PUT parcial)
        dados[nome] = valor;
    });
    return dados;
}

// 5. Submit — escolhe o método HTTP conforme a ação selecionada
form.addEventListener("submit", async (evento) => {
    evento.preventDefault();

    const acao  = acaoSelect.value;
    const dados = coletarCampos();
    const id    = dados.id;     // pode estar undefined
    delete dados.id;            // id vai pela URL, não no body

    saida.textContent = "⏳ Enviando...";

    try {
        let resposta;
        switch (acao) {
            case "criar":
                resposta = await criarAluno(dados);
                break;
            case "listar":
                resposta = await listarAlunos();
                break;
            case "buscar":
                if (!id) throw new Error("Informe o ID para buscar.");
                resposta = await buscarAluno(id);
                break;
            case "atualizar":
                if (!id) throw new Error("Informe o ID para atualizar.");
                resposta = await atualizarAluno(id, dados);
                break;
            case "excluir":
                if (!id) throw new Error("Informe o ID para excluir.");
                resposta = await excluirAluno(id);
                break;
        }
        saida.textContent = "✅ Sucesso:\n" + JSON.stringify(resposta, null, 2);
    } catch (erro) {
        saida.textContent = "❌ Erro:\n" + erro.message;
    }
});
