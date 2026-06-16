/* ============================================================
   entities.js — o "mapa" de cada entidade do sistema.
   É SÓ configuração: zero DOM, zero HTTP.

   Quem lê isto e monta a tela é o app.js.
   Quem fala com a API é o api.js.

   Pra adicionar uma entidade nova no futuro, basta acrescentar
   um bloco aqui — o resto do frontend se vira sozinho.

   Cada campo tem:
     - name   : bate com o campo do schema Pydantic no backend
     - label  : o que a usuária lê
     - type   : text | email | date | number | select | checkbox
     - actions: em quais ações o campo aparece (create / update)
     - mask?  : "cpf" | "whatsapp" (aplica máscara visual)
     - options? (select), default? (checkbox), min/step? (number)
   ============================================================ */

const ENTITIES = {
    clients: {
        label: "Clientes",
        endpoint: "/clients",
        // ações extras só desta entidade (somadas às 5 padrão no app.js)
        extraActions: [
            { value: "find-cpf", label: "Buscar por CPF" },
        ],
        fields: [
            { name: "name", label: "Nome", type: "text", actions: ["create", "update"], required: true, placeholder: "Maria Silva" },
            { name: "cpf", label: "CPF", type: "text", actions: ["create", "find-cpf"], required: true, mask: "cpf", placeholder: "000.000.000-00" },
            { name: "birth_date", label: "Data de nascimento", type: "date", actions: ["create"], required: true },
            { name: "whatsapp_number", label: "WhatsApp", type: "text", actions: ["create", "update"], required: true, mask: "whatsapp", placeholder: "(11) 98765-4321" },
            { name: "email", label: "E-mail", type: "email", actions: ["create", "update"], required: true, placeholder: "maria@exemplo.com" },
            {
                name: "client_status", label: "Status comercial", type: "select", actions: ["create", "update"], options: [
                    { value: "prospect", label: "Prospecto" },
                    { value: "active", label: "Ativo" },
                    { value: "inactive", label: "Inativo" },
                ]
            },
            { name: "marketing_consent", label: "Aceita comunicações de marketing", type: "checkbox", actions: ["create", "update"], default: true },
            { name: "is_active", label: "Aluna ativa (desmarque = desativar)", type: "checkbox", actions: ["update"], default: true },
        ],
        columns: [
            { key: "name", label: "Nome" },
            { key: "cpf", label: "CPF", format: "cpf" },
            { key: "whatsapp_number", label: "WhatsApp", format: "whatsapp" },
            { key: "client_status", label: "Status", format: "enum" },
        ],
    },

    instructors: {
        label: "Instrutores",
        endpoint: "/instructors",
        fields: [
            { name: "name", label: "Nome", type: "text", actions: ["create", "update"], required: true, placeholder: "João Souza" },
            { name: "email", label: "E-mail", type: "email", actions: ["create", "update"], required: true, placeholder: "joao@exemplo.com" },
            { name: "has_credential", label: "Possui credencial (CREFITO)", type: "checkbox", actions: ["create", "update"], default: false },
            { name: "credential_number", label: "Número da credencial", type: "text", actions: ["create", "update"], placeholder: "obrigatório se marcou acima" },
            { name: "specialty", label: "Especialidade", type: "text", actions: ["create", "update"], placeholder: "Pilates clínico" },
            {
                name: "instructor_status", label: "Situação", type: "select", actions: ["create", "update"], options: [
                    { value: "active", label: "Ativo" },
                    { value: "vacation", label: "Férias" },
                    { value: "on_leave", label: "Afastado" },
                    { value: "standby", label: "Banco de vagas" },
                    { value: "inactive", label: "Inativo" },
                ]
            },
            { name: "is_active", label: "Instrutor ativo (desmarque = desativar)", type: "checkbox", actions: ["update"], default: true },
        ],
        columns: [
            { key: "name", label: "Nome" },
            { key: "email", label: "E-mail" },
            { key: "specialty", label: "Especialidade" },
            { key: "instructor_status", label: "Situação", format: "enum" },
        ],
    },

    plans: {
        label: "Planos",
        endpoint: "/plans",
        fields: [
            { name: "name", label: "Nome do plano", type: "text", actions: ["create", "update"], required: true, placeholder: "8 sessões / mês" },
            { name: "sessions_per_month", label: "Sessões por mês", type: "number", actions: ["create", "update"], required: true, min: 1, placeholder: "8" },
            { name: "monthly_fee", label: "Mensalidade (R$)", type: "number", actions: ["create", "update"], required: true, min: 0, step: "0.01", placeholder: "199.90" },
            { name: "is_active", label: "Plano ativo (desmarque = desativar)", type: "checkbox", actions: ["update"], default: true },
        ],
        columns: [
            { key: "name", label: "Nome" },
            { key: "sessions_per_month", label: "Sessões/mês" },
            { key: "monthly_fee", label: "Mensalidade", format: "brl" },
        ],
    },

    client_plans: {
        label: "Matrículas",
        endpoint: "/client_plans",
        fields: [
            { name: "client_id", label: "ID da aluna (UUID)", type: "text", actions: ["create"], required: true, placeholder: "cole o UUID da cliente" },
            { name: "plan_id", label: "ID do plano (UUID)", type: "text", actions: ["create"], required: true, placeholder: "cole o UUID do plano" },
            // start_date é opcional: vazio = hoje (o service preenche). O vencimento é derivado (+1 ano), não aparece aqui.
            { name: "start_date", label: "Início da matrícula", type: "date", actions: ["create"] },
            // renewal_date é manual: vazio na 1ª matrícula; data da rematrícula se a aluna já fazia antes.
            { name: "renewal_date", label: "Data de renovação (rematrícula)", type: "date", actions: ["create", "update"] },
            { name: "is_active", label: "Matrícula ativa (desmarque = desativar)", type: "checkbox", actions: ["update"], default: true },
        ],
        columns: [
            { key: "client_id", label: "Aluna (ID)" },
            { key: "plan_id", label: "Plano (ID)" },
            { key: "start_date", label: "Início", format: "date" },
            { key: "end_date", label: "Vencimento", format: "date" },
            { key: "renewal_date", label: "Renovação", format: "date" },
        ],
    },

    anamneses: {
        label: "Anamneses",
        endpoint: "/anamneses",
        fields: [
            { name: "client_id", label: "ID da aluna (UUID)", type: "text", actions: ["create"], required: true, placeholder: "cole o UUID da cliente" },
            { name: "previous_illness", label: "Possui doença prévia?", type: "checkbox", actions: ["create", "update"], default: false },
            { name: "illness_description", label: "Descrição da doença", type: "text", actions: ["create", "update"] },
            { name: "specific_complaint", label: "Possui queixa específica?", type: "checkbox", actions: ["create", "update"], default: false },
            { name: "complaint_description", label: "Descrição da queixa", type: "text", actions: ["create", "update"] },
            { name: "medication_use", label: "Faz uso de medicação?", type: "checkbox", actions: ["create", "update"], default: false },
            { name: "medication_description", label: "Descrição da medicação", type: "text", actions: ["create", "update"] },
            { name: "physical_restriction", label: "Possui restrição física?", type: "checkbox", actions: ["create", "update"], default: false },
            { name: "restriction_description", label: "Descrição da restrição", type: "text", actions: ["create", "update"] },
            { name: "cleared_for_activity", label: "Liberada para atividade física?", type: "checkbox", actions: ["create", "update"], default: false },
            { name: "is_active", label: "Anamnese ativa (desmarque = desativar)", type: "checkbox", actions: ["update"], default: true },
        ],
        columns: [
            { key: "client_id", label: "Aluna (ID)" },
            { key: "cleared_for_activity", label: "Liberada?", format: "bool" },
            { key: "filled_at", label: "Preenchida em", format: "datetime" },
        ],
    },
};
