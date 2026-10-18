# Atividade 02 — APIs e protocolos

Rede social simplificada exposta por **REST e GraphQL**, em um único projeto Python. Os dois adaptadores usam o mesmo domínio e o mesmo armazenamento: um usuário criado por REST pode ser consultado por GraphQL e vice-versa.

O objetivo é comparar duas formas de expor as mesmas operações. Tecnicamente, REST é um estilo arquitetural e GraphQL é uma linguagem de consulta com um modelo de execução; nesta atividade, ambos são transportados por HTTP com JSON.

## Executar do zero

Pré-requisitos: Python 3.10 ou superior, com `pip` e `venv`, e acesso à internet para instalar as dependências. Git é opcional se o projeto for baixado como ZIP. A implementação foi testada com Python 3.12.10.

Clone o repositório pelo botão **Code** da página da entrega ou baixe e extraia o ZIP. Abra o terminal na pasta que contém este README.

### Windows / PowerShell

```powershell
python -m venv .venv

.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Não é necessário ativar o ambiente virtual nem alterar a política de execução do PowerShell. Se `python` não estiver disponível, use `py -3` no primeiro comando.

### Linux / macOS

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
```

O servidor fica em <http://127.0.0.1:5000>. A rota `/` informa os endereços da API; `/schema.graphql` mostra o contrato GraphQL. Mantenha o terminal aberto. Para parar, pressione `Ctrl+C`. A porta 5000 deve estar livre.

Não há banco de dados, credenciais ou serviço externo para configurar. **Os dados ficam em memória e são apagados ao parar o processo.** Cada execução começa vazia.

## Experimentar e conferir as respostas

Em um segundo terminal, na mesma pasta, execute uma demonstração completa:

```powershell
.\.venv\Scripts\python.exe scripts/demo.py rest
```

Pare e inicie novamente o servidor para limpar os dados. Depois execute:

```powershell
.\.venv\Scripts\python.exe scripts/demo.py graphql
```

No Linux/macOS, substitua `.\.venv\Scripts\python.exe` por `.venv/bin/python`. Cada demonstração faz 12 requisições HTTP reais, imprime as respostas e compara os resultados com os exemplos documentados. Ela cria Ana e Bruno, publica um post de Bruno, registra comentário e curtida de Ana, faz Ana seguir Bruno e executa todas as consultas. Execute cada demonstração apenas uma vez por servidor vazio.

### Requisição e resposta copiáveis para cada operação

| Protocolo | Requisições e respostas completas | Arquivo para cliente HTTP | Dados para demonstração |
|---|---|---|---|
| REST | [Exemplos REST](examples/rest.md) | [rest.http](examples/rest.http) | [rest.json](examples/rest.json) |
| GraphQL | [Exemplos GraphQL](examples/graphql.md) | [graphql.http](examples/graphql.http) | [graphql.json](examples/graphql.json) |

Os arquivos `.http` podem ser executados com um cliente que suporte esse formato, como a extensão REST Client do VS Code. Execute os blocos na ordem. No Postman ou Insomnia, copie o método, a URL, o cabeçalho `Content-Type: application/json` e o corpo JSON dos exemplos. As respostas esperadas estão nos arquivos Markdown e JSON.

Para uma consulta isolada após a demonstração, no PowerShell:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/usuarios/1 | ConvertTo-Json -Depth 10
```

Resposta REST:

```json
{"id":"1","nome":"Ana","perfil":{"usuario_id":"1","bio":"Estudante"}}
```

A consulta GraphQL equivalente pode escolher somente o nome:

```powershell
$body = @{ query = '{ buscar_usuario(id: "1") { nome } }' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/graphql -ContentType 'application/json' -Body $body | ConvertTo-Json -Depth 10
```

Resposta GraphQL:

```json
{"data":{"buscar_usuario":{"nome":"Ana"}}}
```

## Domínio e regras

| Entidade | Campos e relacionamentos |
|---|---|
| Usuario | `id`, `nome`; possui um Perfil e pode publicar vários Posts |
| Perfil | `usuario_id`, `bio`; criado junto com o Usuario |
| Post | `id`, `usuario_id`, `texto`; possui Comentarios e Curtidas |
| Comentario | `id`, `usuario_id`, `post_id`, `texto` |
| Curtida | Par único `usuario_id`, `post_id` |
| Seguidor | Par único `seguidor_id`, `seguido_id`; a direção indica quem segue quem |

- IDs são strings de inteiros positivos, gerados sequencialmente; as referências precisam existir.
- Nome, texto do post e comentário são obrigatórios e não podem conter apenas espaços. Limites: nome 100, bio 500, post 2000 e comentário 1000 caracteres.
- Bio é opcional e começa vazia. Nomes não precisam ser únicos.
- Não é permitido seguir a si mesmo, seguir novamente a mesma pessoa ou curtir novamente o mesmo post. Essas duplicações não alteram os dados.
- O feed reúne os posts do próprio usuário e dos usuários que ele segue, do mais recente ao mais antigo, pela ordem de criação. Não inclui posts de pessoas não seguidas.
- `posts_do_usuario` usa a mesma ordenação do feed; seguidores e seguindo são ordenados por ID crescente. Coleções vazias retornam `[]`.
- REST e GraphQL compartilham os dados durante uma mesma execução. Reiniciar é necessário somente para repetir os exemplos com os IDs previstos.

## Operações implementadas

Todos os comandos REST retornam HTTP **201** quando bem-sucedidos. As consultas retornam **200**. Criação de usuário e post também retorna `Location` com a URL do recurso.

| Operação exigida | REST | GraphQL em `POST /graphql` |
|---|---|---|
| criar_usuario | `POST /api/usuarios` | `mutation { criar_usuario(...) { ... } }` |
| criar_post | `POST /api/posts` | `mutation { criar_post(...) { ... } }` |
| comentar | `POST /api/posts/{post_id}/comentarios` | `mutation { comentar(...) { ... } }` |
| curtir | `POST /api/posts/{post_id}/curtidas` | `mutation { curtir(...) { ... } }` |
| seguir | `POST /api/usuarios/{seguidor_id}/seguindo` | `mutation { seguir(...) { ... } }` |
| buscar_usuario | `GET /api/usuarios/{id}` | `query { buscar_usuario(...) { ... } }` |
| posts_do_usuario | `GET /api/usuarios/{usuario_id}/posts` | `query { posts_do_usuario(...) { ... } }` |
| buscar_post | `GET /api/posts/{id}` | `query { buscar_post(...) { ... } }` |
| seguidores_de | `GET /api/usuarios/{usuario_id}/seguidores` | `query { seguidores_de(...) { ... } }` |
| seguindo_de | `GET /api/usuarios/{usuario_id}/seguindo` | `query { seguindo_de(...) { ... } }` |
| feed_do_usuario | `GET /api/usuarios/{usuario_id}/feed` | `query { feed_do_usuario(...) { ... } }` |

O requisito `seguidores_de/seguindo_de` foi implementado nas duas direções, resultando em cinco comandos e seis campos de consulta por protocolo.

O [schema GraphQL](schema.graphql) define os tipos, argumentos, obrigatoriedade e relacionamentos. A biblioteca `graphql-core` faz parsing, validação e execução reais; suporta seleção de campos, aliases, variáveis, fragments e introspecção. O corpo HTTP tem `query` e, opcionalmente, `variables` e `operationName`. Este servidor aceita GraphQL apenas por POST.

### Erros

REST retorna `{"erro":"mensagem"}`. Os códigos principais são 400 para entrada inválida, 404 para recurso inexistente, 409 para relacionamento duplicado e 415 quando o corpo não tem tipo JSON. Campos extras ou obrigatórios ausentes são rejeitados.

GraphQL retorna `errors` com mensagem e localização quando disponível. Erros de sintaxe, validação ou coerção de variáveis retornam HTTP 400; erros de domínio durante a execução retornam HTTP 200 com `errors[].extensions.status` indicando 400, 404 ou 409. Como os campos principais são não nulos, uma falha neles pode tornar `data` nulo. O cliente deve verificar `errors`, além do status HTTP. Corpos HTTP inválidos são rejeitados antes da execução com o mesmo formato `erro` do adaptador HTTP.

## Testes e organização

Sem iniciar o servidor:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Os testes cobrem integração entre os protocolos, relações aninhadas, seleção de campos, variáveis, filtro e ordenação do feed, referências inexistentes, duplicações, dados inválidos e coleções vazias. As duas demonstrações acima verificam também o transporte HTTP e as respostas de todas as operações documentadas.

```text
app.py                    Adaptadores HTTP REST e GraphQL
domain.py                 Entidades em memória e regras compartilhadas
schema.graphql            Contrato tipado GraphQL
requirements.txt          Dependências diretas com versões fixadas
examples/                 Requisições e respostas dos dois protocolos
scripts/demo.py           Cliente HTTP com conferência das respostas
scripts/build_examples.py Geração dos exemplos usando instâncias isoladas
tests/test_api.py         Testes de integração e validação
```

Para atualizar a documentação após uma alteração intencional, execute `python scripts/build_examples.py` usando o Python do ambiente virtual. Esse comando não altera o servidor em execução.

## Comparação final

| Critério | REST neste projeto | GraphQL neste projeto |
|---|---|---|
| Organização | URLs representam recursos e relacionamentos; GET consulta e POST cria | Um endpoint com campos de Query e Mutation descritos no schema |
| Formato da resposta | Definido por cada rota | O cliente escolhe os campos e o nível de aninhamento |
| Consulta simples | GET direto e fácil de experimentar no navegador | Requer documento GraphQL dentro do corpo JSON |
| Dados relacionados | O feed retorna IDs de autores; buscar nomes exige consultas de usuários | O feed pode trazer `autor { nome perfil { bio } }` na mesma requisição |
| Quantidade de dados | Uma consulta de usuário sempre inclui seu perfil | É possível pedir somente `nome`, evitando campos desnecessários |
| Validação | Validação explícita no adaptador e no domínio | Tipos e argumentos validados pelo schema, além das regras do domínio |
| Erros | Status HTTP expressa diretamente o resultado | Erros de execução aparecem em `errors`, mesmo com HTTP 200 |
| Cache | GET pode aproveitar mecanismos HTTP se forem configurados | Como aqui tudo usa POST, o cache costuma exigir tratamento específico no cliente/servidor |
| Complexidade | Rotas simples, mas cresce com novas necessidades de composição | Schema e resolvers acrescentam estrutura e exigem controle do custo das consultas |

**Diferença observável:** para exibir o feed de Ana com nome e bio dos autores, nesta API REST é preciso consultar `/api/usuarios/1/feed` e buscar cada autor distinto. Em GraphQL, `feed_do_usuario(usuario_id: "1") { texto autor { nome perfil { bio } } }` resolve isso em uma requisição. Já para obter um usuário completo, a rota REST é mais direta. Isso decorre do desenho desta implementação: uma API REST também poderia oferecer respostas expandidas ou um endpoint dedicado.

**Quando escolher cada um:** REST atende bem APIs simples orientadas a recursos e integrações que se beneficiam das convenções HTTP. GraphQL é útil quando diferentes telas ou clientes precisam de combinações variadas de dados relacionados. GraphQL não é automaticamente mais rápido: uma consulta muito aninhada pode exigir bastante processamento; menos requisições não significa necessariamente menor custo no servidor. Não foram realizados benchmarks de desempenho.

**Conclusão:** os dois formatos expressam as mesmas regras da rede social. REST torna explícitos os recursos e os códigos HTTP; GraphQL oferece flexibilidade para selecionar e combinar os dados. A escolha depende das necessidades dos clientes e da complexidade que a equipe consegue manter.

### Limites do exercício

Aplicação didática local, sem persistência, autenticação, paginação, uploads ou implantação de produção. O usuário é identificado pelos IDs enviados. O servidor Flask usado é de desenvolvimento. Há limite de 64 KiB por requisição, mas não há limite de profundidade/custo GraphQL nem rate limiting. Não execute múltiplos processos esperando compartilhar os dados em memória.

### Referências

- [HTTP Semantics — RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html): métodos e códigos HTTP.
- [GraphQL — Queries](https://graphql.org/learn/queries/): seleção de campos e consultas.
- [GraphQL — Mutations](https://graphql.org/learn/mutations/): operações de escrita.
- [GraphQL — Serving over HTTP](https://graphql.org/learn/serving-over-http/): transporte HTTP.

## Entrega no SIGAA

Publique os arquivos deste projeto em um repositório Git, confira se o README e os exemplos estão acessíveis ao professor e envie o link do repositório no SIGAA. O ambiente `.venv` é local e deve permanecer fora do repositório, conforme `.gitignore`.
