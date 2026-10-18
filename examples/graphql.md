# Exemplos GRAPHQL

Execute na ordem abaixo, com o servidor recém-iniciado e vazio. Reinicie antes de trocar de protocolo.

As respostas foram geradas pela aplicação. A ordem das chaves JSON não altera o resultado.

Cada bloco HTTP pode ser colado no arquivo `.http` de um cliente HTTP. Para executar tudo pelo terminal, veja o README.

## 1. criar_usuario

```http
POST http://127.0.0.1:5000/graphql
Content-Type: application/json

{
  "query": "mutation { criar_usuario(nome: \"Ana\", bio: \"Estudante\") { id nome perfil { usuario_id bio } } }"
}
```

Resposta: HTTP 200

```json
{
  "data": {
    "criar_usuario": {
      "id": "1",
      "nome": "Ana",
      "perfil": {
        "bio": "Estudante",
        "usuario_id": "1"
      }
    }
  }
}
```

## 2. criar_usuario (segundo usuario)

```http
POST http://127.0.0.1:5000/graphql
Content-Type: application/json

{
  "query": "mutation { criar_usuario(nome: \"Bruno\") { id nome perfil { usuario_id bio } } }"
}
```

Resposta: HTTP 200

```json
{
  "data": {
    "criar_usuario": {
      "id": "2",
      "nome": "Bruno",
      "perfil": {
        "bio": "",
        "usuario_id": "2"
      }
    }
  }
}
```

## 3. criar_post

```http
POST http://127.0.0.1:5000/graphql
Content-Type: application/json

{
  "query": "mutation { criar_post(usuario_id: \"2\", texto: \"Ola, rede!\") { id usuario_id texto comentarios { id } curtidas { usuario_id } } }"
}
```

Resposta: HTTP 200

```json
{
  "data": {
    "criar_post": {
      "comentarios": [],
      "curtidas": [],
      "id": "1",
      "texto": "Ola, rede!",
      "usuario_id": "2"
    }
  }
}
```

## 4. comentar

```http
POST http://127.0.0.1:5000/graphql
Content-Type: application/json

{
  "query": "mutation { comentar(usuario_id: \"1\", post_id: \"1\", texto: \"Bem-vindo!\") { id usuario_id post_id texto } }"
}
```

Resposta: HTTP 200

```json
{
  "data": {
    "comentar": {
      "id": "1",
      "post_id": "1",
      "texto": "Bem-vindo!",
      "usuario_id": "1"
    }
  }
}
```

## 5. curtir

```http
POST http://127.0.0.1:5000/graphql
Content-Type: application/json

{
  "query": "mutation { curtir(usuario_id: \"1\", post_id: \"1\") { usuario_id post_id } }"
}
```

Resposta: HTTP 200

```json
{
  "data": {
    "curtir": {
      "post_id": "1",
      "usuario_id": "1"
    }
  }
}
```

## 6. seguir

```http
POST http://127.0.0.1:5000/graphql
Content-Type: application/json

{
  "query": "mutation { seguir(seguidor_id: \"1\", seguido_id: \"2\") { seguidor_id seguido_id } }"
}
```

Resposta: HTTP 200

```json
{
  "data": {
    "seguir": {
      "seguido_id": "2",
      "seguidor_id": "1"
    }
  }
}
```

## 7. buscar_usuario

```http
POST http://127.0.0.1:5000/graphql
Content-Type: application/json

{
  "query": "{ buscar_usuario(id: \"1\") { id nome perfil { usuario_id bio } } }"
}
```

Resposta: HTTP 200

```json
{
  "data": {
    "buscar_usuario": {
      "id": "1",
      "nome": "Ana",
      "perfil": {
        "bio": "Estudante",
        "usuario_id": "1"
      }
    }
  }
}
```

## 8. posts_do_usuario

```http
POST http://127.0.0.1:5000/graphql
Content-Type: application/json

{
  "query": "{ posts_do_usuario(usuario_id: \"2\") { id texto autor { nome } } }"
}
```

Resposta: HTTP 200

```json
{
  "data": {
    "posts_do_usuario": [
      {
        "autor": {
          "nome": "Bruno"
        },
        "id": "1",
        "texto": "Ola, rede!"
      }
    ]
  }
}
```

## 9. buscar_post

```http
POST http://127.0.0.1:5000/graphql
Content-Type: application/json

{
  "query": "{ buscar_post(id: \"1\") { id texto comentarios { id texto } curtidas { usuario_id } } }"
}
```

Resposta: HTTP 200

```json
{
  "data": {
    "buscar_post": {
      "comentarios": [
        {
          "id": "1",
          "texto": "Bem-vindo!"
        }
      ],
      "curtidas": [
        {
          "usuario_id": "1"
        }
      ],
      "id": "1",
      "texto": "Ola, rede!"
    }
  }
}
```

## 10. seguidores_de

```http
POST http://127.0.0.1:5000/graphql
Content-Type: application/json

{
  "query": "{ seguidores_de(usuario_id: \"2\") { id nome } }"
}
```

Resposta: HTTP 200

```json
{
  "data": {
    "seguidores_de": [
      {
        "id": "1",
        "nome": "Ana"
      }
    ]
  }
}
```

## 11. seguindo_de

```http
POST http://127.0.0.1:5000/graphql
Content-Type: application/json

{
  "query": "{ seguindo_de(usuario_id: \"1\") { id nome } }"
}
```

Resposta: HTTP 200

```json
{
  "data": {
    "seguindo_de": [
      {
        "id": "2",
        "nome": "Bruno"
      }
    ]
  }
}
```

## 12. feed_do_usuario

```http
POST http://127.0.0.1:5000/graphql
Content-Type: application/json

{
  "query": "{ feed_do_usuario(usuario_id: \"1\") { id texto autor { nome perfil { bio } } } }"
}
```

Resposta: HTTP 200

```json
{
  "data": {
    "feed_do_usuario": [
      {
        "autor": {
          "nome": "Bruno",
          "perfil": {
            "bio": ""
          }
        },
        "id": "1",
        "texto": "Ola, rede!"
      }
    ]
  }
}
```
