# Projeto Aplicado II — Studio de Pilates 🤸‍♀️

> Este README é o nosso **guia de equipe**. A ideia é que qualquer uma de nós
> consiga entender **o que** o sistema faz, **como** as peças se encaixam e
> **como rodar** o projeto na própria máquina — mesmo quem ainda está começando
> a programar. Sem decoreba: a gente vai construindo a intuição com analogias e
> depois mostra o passo a passo. 💛

---

## 🎯 O que esse sistema faz (a visão lá de cima)

Imagina a **recepção de um studio de Pilates**. Chega aluna nova, alguém anota o
cadastro numa ficha; outra aluna quer trocar de plano; uma terceira pediu pra
sair e meses depois quer voltar. Hoje isso costuma ser feito na mão, em papel ou
planilha — fácil de errar, fácil de perder.

Nosso projeto é a **versão digital dessa recepção**: um sistema que guarda os
dados das alunas, dos instrutores, dos planos e das anamneses (a fichinha de
saúde) de forma organizada, e ainda evita erros bobos (CPF inválido, número de
WhatsApp errado, aluna cadastrada duas vezes).

No futuro, esse mesmo sistema vai responder as alunas **pelo WhatsApp**
automaticamente — mas isso é capítulo lá pra frente. Por enquanto, o foco é a
**base bem feita**: guardar e gerenciar os dados direitinho.

---

## 🧩 As peças do projeto (e pra que serve cada uma)

O sistema tem **três partes**. Pensa num restaurante:

| Peça | No restaurante seria... | No projeto é... |
|---|---|---|
| **Frontend** | O **balcão/salão**, onde a cliente é atendida | A tela bonitinha (`frontend/`) que a recepcionista usa pra clicar e digitar |
| **Backend** | A **cozinha**, onde o pedido vira prato | O programa em Python (`app/`) que recebe os pedidos e decide o que fazer |
| **Banco de dados** | A **despensa/almoxarifado**, onde fica tudo guardado | O **Supabase**, onde os dados ficam salvos de verdade |

A regra de ouro: **o salão não entra na despensa**. A recepcionista (frontend)
faz o pedido, a cozinha (backend) cuida da lógica, e só a cozinha mexe na
despensa (banco). Cada peça tem **um trabalho só** — é isso que deixa o sistema
organizado e fácil de consertar quando algo dá errado.

---

## 🔄 Como um pedido viaja pelo sistema

Quando a recepcionista clica em "salvar aluna", o pedido faz uma viagenzinha. Cada
parada tem um nome técnico (que vai aparecer nos arquivos), mas a ideia é simples:

```
Recepcionista clica   →   API   →   Service   →   Repository   →   Supabase
  (frontend)            (garçom)  (cozinheiro)  (despenseiro)    (despensa)
```

- **API** (`app/api/`) — o **garçom**. Anota o pedido e leva pra cozinha. Não
  cozinha nada, só recebe e entrega.
- **Service** (`app/services/`) — o **cozinheiro**. Aqui moram as **regras**:
  "essa aluna já existe?", "esse plano pode ser ativado?". É o cérebro.
- **Repository** (`app/repositories/`) — o **despenseiro**. A única peça que
  abre a despensa pra pegar ou guardar coisa. Ninguém mais encosta no banco.
- **Supabase** — a **despensa**. Onde os dados realmente ficam.

> Por que separar tudo isso? Porque se um dia a gente trocar a despensa de lugar
> (mudar de banco de dados), só o despenseiro precisa aprender o caminho novo —
> o resto do restaurante nem percebe. Isso se chama **arquitetura em camadas**, e
> é exatamente assim que empresas de verdade organizam o código.

---

## ✅ O que já está pronto

Hoje o sistema sabe **cadastrar, listar, editar e remover** (o famoso **CRUD**:
**C**reate, **R**ead, **U**pdate, **D**elete) quatro tipos de informação:

- 👩 **Aluna (Client)** — dados da aluna: nome, CPF, WhatsApp, status.
- 🧑‍🏫 **Instrutor (Instructor)** — quem dá as aulas, com registro profissional.
- 📋 **Plano (Plan)** — os pacotes (ex.: "8 aulas/mês"), com valor mensal.
- 🩺 **Anamnese (Anamnesis)** — a ficha de saúde da aluna (lesões, restrições...).

Além disso:
- 🖥️ Um **painel visual** (frontend) que cobre as quatro coisas acima, com **modo
  claro/escuro** e troca de tela pela barra lateral.
- ♻️ **Reativação de aluna**: se alguém cadastra um CPF que já existiu mas foi
  removido, o sistema **avisa** e pergunta se quer reativar, em vez de só dar erro.

---

## 💡 Três conceitos que aparecem o tempo todo

Vale decifrar esses três, porque eles voltam em vários lugares:

**1. Soft-delete (a "lixeira do computador")**
Quando a gente "apaga" uma aluna, o sistema **não joga fora de verdade**. Ele só
marca como "inativa" (igual mandar pra Lixeira do Windows). O dado continua lá,
guardado. Isso é importante por **lei** (LGPD) e pra **auditoria** — dá pra saber
o que aconteceu e até desfazer.

**2. Reativação (tirar da lixeira)**
Como nada é apagado de verdade, se a aluna volta, dá pra **reativar** o cadastro
antigo em vez de criar tudo de novo. O sistema reconhece o CPF e oferece isso.

**3. Validação (o porteiro)**
Antes de salvar, o sistema **confere** os dados: CPF tem que ser válido de verdade
(tem uma continha oficial pra isso), WhatsApp tem que ter DDD certo, valor de
plano não pode ser negativo. É um **porteiro** que barra dado errado na entrada —
melhor avisar na hora do que descobrir o erro depois, com o dado já salvo torto.

---

## 🚀 Como rodar o projeto na sua máquina (passo a passo)

> Aqui é o pulo do gato pra quem ainda não roda projeto sozinha. Vai com calma,
> um comando de cada vez, e **se der erro, para e pergunta** — não tenta adivinhar. 🙂

### Pré-requisito: ter o Python instalado
Confere no terminal se já tem:
```bash
python --version
```
Se aparecer algo como `Python 3.12.x`, beleza. Se não, instala o Python 3.12+.

### Passo 1 — Baixar o projeto
```bash
git clone https://github.com/AmandaPardinho/projeto-aplicado-2.git
cd projeto-aplicado-2
```

### Passo 2 — Criar o "ambiente isolado" e instalar as dependências
Pensa na **venv** como uma **caixinha separada** só pro nosso projeto, pra ele não
se misturar com outras coisas do computador:
```bash
python -m venv .venv          # cria a caixinha
source .venv/bin/activate     # entra na caixinha (no Windows: .venv\Scripts\activate)
pip install -r requirements.txt  # instala tudo que o projeto precisa
```

### Passo 3 — Configurar o `.env` (as "chaves de acesso" ao Supabase)
O sistema precisa saber **onde** fica o banco e ter **permissão** pra entrar. Essas
informações ficam num arquivo chamado `.env` (que **nunca** vai pro GitHub, porque
é segredo). Tem um modelo pronto:
```bash
cp .env.example .env
```
Agora abra o `.env` e preencha. **Atenção a esta parte** 👇

### ⭐ O `.env`: o que você REALMENTE precisa pra rodar

Aqui mora a confusão que já travou gente da equipe. O `.env` tem 5 linhas, mas
**pra rodar o sistema, só 3 importam**:

| Variável | Precisa pra rodar? | Pra que serve |
|---|---|---|
| `SUPABASE_URL` | ✅ **Sim** | O endereço do nosso banco (igual o endereço de uma casa) |
| `SUPABASE_ANON_KEY` | ✅ **Sim** | Uma das chaves de acesso |
| `SUPABASE_KEY` | ✅ **Sim** | A chave de "administradora" que o backend usa |
| `SUPABASE_DB_HOST` | ⛔ Não (opcional) | Só serve pra uma tarefa avançada (gerar o dump do banco) |
| `SUPABASE_DB_PASSWORD` | ⛔ Não (opcional) | **A senha do banco. NÃO é necessária pra rodar o sistema!** |

> 🔑 **Resumão:** se você só quer **rodar o sistema**, precisa apenas de
> `SUPABASE_URL`, `SUPABASE_ANON_KEY` e `SUPABASE_KEY`. **A senha do banco
> (`SUPABASE_DB_PASSWORD`) NÃO faz falta** — ela só é usada por uma ferramenta
> extra (`pg_dump`) que tira uma "foto" da estrutura do banco. Pode deixar essas
> duas últimas linhas em branco que o sistema sobe normalmente.

> ⚠️ **Segredo é segredo:** nunca cole o conteúdo do `.env` em print, mensagem ou
> grupo. Essas chaves dão acesso ao nosso banco — se vazarem, a gente troca todas.

### Passo 4 — Ligar o backend (a cozinha)
```bash
uvicorn app.main:app --reload
```
Se tudo deu certo, o backend está no ar. Você pode testar abrindo no navegador:
- **http://localhost:8000/docs** — uma página automática onde dá pra testar os
  pedidos sem precisar do frontend. Se aqui aparecer dados, o banco está conectado. ✅

### Passo 5 — Ligar o frontend (o balcão) — e o erro mais comum
Em **outro terminal** (deixa o backend rodando no primeiro), ligue o painel:
```bash
cd frontend
python -m http.server 5500
```
Agora abra **http://localhost:5500** no **navegador de verdade** (Chrome, Firefox,
Edge...). Digite esse endereço na barra do navegador, não dentro do VS Code.

> 🖥️ **Abra no navegador, NÃO dentro do VS Code.** O VS Code tem um navegador
> embutido (o "Simple Browser") e algumas extensões abrem a página lá dentro — mas
> isso costuma dar confusão e pode não carregar os dados direito. O certo é abrir o
> seu **navegador normal** (aquele que você usa pra tudo) e digitar
> `http://localhost:5500` na barra de endereço.

> 🚨 **NÃO abra o `index.html` dando dois cliques no arquivo!** Se a barra do
> navegador mostrar algo começando com `file://`, o sistema vai dar
> **"Failed to fetch"** (não consegue buscar os dados). Isso acontece porque o
> backend, por segurança, só aceita pedidos vindos de um endereço `http://...`,
> e o duplo-clique abre a página como `file://...`. **Sempre suba o frontend pelo
> comando acima** e acesse por `http://localhost:5500`. Esse foi, literalmente, o
> erro que travou a equipe — agora você já sabe desviar dele. 😉

---

## 📚 Para quem quiser ir mais fundo (opcional)

Estas partes são mais técnicas — pula sem dó se ainda não for a sua praia.

<details>
<summary><strong>Estrutura das pastas do projeto</strong></summary>

```
projeto-aplicado-2/
├── app/                    # A "cozinha" (backend em Python)
│   ├── api/                # Os garçons (recebem os pedidos HTTP)
│   ├── services/           # Os cozinheiros (regras de negócio)
│   ├── repositories/       # Os despenseiros (únicos que falam com o banco)
│   ├── schemas/            # Os "moldes" dos dados (o que cada ficha tem)
│   ├── core/               # Configurações e o porteiro (validações)
│   └── main.py             # O interruptor geral que liga tudo
├── frontend/               # O "balcão" (tela em HTML/CSS/JavaScript)
├── database/               # Scripts e histórico da estrutura do banco
├── requirements.txt        # A lista de compras (dependências)
├── .env                    # As chaves de acesso (NÃO vai pro GitHub)
└── .env.example            # O modelo do .env (esse sim vai pro GitHub)
```
</details>

<details>
<summary><strong>Gerar o "dump" do banco (tarefa avançada — usa a senha)</strong></summary>

O **dump** é uma "foto" da estrutura do banco (as tabelas, as regras), salva num
arquivo `.sql`. Só precisamos disso quando **mudamos a estrutura** do banco. É a
**única** tarefa que usa o `SUPABASE_DB_HOST` e o `SUPABASE_DB_PASSWORD`.

Precisa da ferramenta `pg_dump` instalada:
```bash
sudo apt install postgresql-client   # Ubuntu/Debian/Mint
pg_dump --version
```
E então:
```bash
chmod +x database/scripts/dump_schema.sh   # só na primeira vez
./database/scripts/dump_schema.sh
```
Depois é só commitar o arquivo gerado em `database/migrations/`.
</details>

---

## 🗺️ Roadmap (o que vem por aí)

**Já feito ✅**
- [x] CRUD das 4 entidades: Aluna, Instrutor, Plano e Anamnese
- [x] Painel visual cobrindo as 4, com modo claro/escuro
- [x] Reativação de aluna + busca por CPF

**Próximos passos 🔜**
- [ ] Matrícula da aluna num plano (Client_Plan), agendamentos e lista de espera
- [ ] Aula experimental (registro + Google Calendar)
- [ ] Atendimento automático pelo **WhatsApp** com IA
- [ ] Login com senha (autenticação)
- [ ] Testes automatizados

---

## 👩‍💻 Equipe

- Amanda Marques Pardinho
- Daiane Olete da Silva Maniçoba
- Fabíola Reginaldo Corrêa da Silva
- Marta Sayuri Mukai

**Disciplina:** Projeto Aplicado II — Curso Superior de Tecnologia em Análise e Desenvolvimento de Sistemas
**Instituição:** Centro Universitário SENAI Santa Catarina
**Professora:** Janice Ines Deters
