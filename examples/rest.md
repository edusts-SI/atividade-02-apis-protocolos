# Exemplos REST

Execute na ordem abaixo, com o servidor recém-iniciado e vazio. Reinicie antes de trocar de protocolo.

As respostas foram geradas pela aplicação. A ordem das chaves JSON não altera o resultado.

Cada bloco HTTP pode ser colado no arquivo `.http` de um cliente HTTP. Para executar tudo pelo terminal, veja o README.

## 1. criar_usuario

```http
POST http://127.0.0.1:5000/api/usuarios
Content-Type: application/json

{
  "nome": "Ana",
  "bio": "Estudante"
}
```

Resposta: HTTP 201

```json
{
  "id": "1",
  "nome": "Ana",
  "perfil": {
    "bio": "Estudante",
    "usuario_id": "1"
  }
}
```

## 2. criar_usuario (segundo usuario)

```http
POST http://127.0.0.1:5000/api/usuarios
Content-Type: application/json

{
  "nome": "Bruno"
}
```

Resposta: HTTP 201

```json
{
  "id": "2",
  "nome": "Bruno",
  "perfil": {
    "bio": "",
    "usuario_id": "2"
  }
}
```

## 3. criar_post

```http
POST http://127.0.0.1:5000/api/posts
Content-Type: application/json

{
  "usuario_id": "2",
  "texto": "Ola, rede!"
}
```

Resposta: HTTP 201

```json
{
  "comentarios": [],
  "curtidas": [],
  "id": "1",
  "texto": "Ola, rede!",
  "usuario_id": "2"
}
```

## 4. comentar

```http
POST http://127.0.0.1:5000/api/posts/1/comentarios
Content-Type: application/json

{
  "usuario_id": "1",
  "texto": "Bem-vindo!"
}
```

Resposta: HTTP 201

```json
{
  "id": "1",
  "post_id": "1",
  "texto": "Bem-vindo!",
  "usuario_id": "1"
}
```

## 5. curtir

```http
POST http://127.0.0.1:5000/api/posts/1/curtidas
Content-Type: application/json

{
  "usuario_id": "1"
}
```

Resposta: HTTP 201

```json
{
  "post_id": "1",
  "usuario_id": "1"
}
```

## 6. seguir

```http
POST http://127.0.0.1:5000/api/usuarios/1/seguindo
Content-Type: application/json

{
  "seguido_id": "2"
}
```

Resposta: HTTP 201

```json
{
  "seguido_id": "2",
  "seguidor_id": "1"
}
```

## 7. buscar_usuario

```http
GET http://127.0.0.1:5000/api/usuarios/1
```

Resposta: HTTP 200

```json
{
  "id": "1",
  "nome": "Ana",
  "perfil": {
    "bio": "Estudante",
    "usuario_id": "1"
  }
}
```

## 8. posts_do_usuario

```http
GET http://127.0.0.1:5000/api/usuarios/2/posts
```

Resposta: HTTP 200

```json
[
  {
    "comentarios": [
      {
        "id": "1",
        "post_id": "1",
        "texto": "Bem-vindo!",
        "usuario_id": "1"
      }
    ],
    "curtidas": [
      {
        "post_id": "1",
        "usuario_id": "1"
      }
    ],
    "id": "1",
    "texto": "Ola, rede!",
    "usuario_id": "2"
  }
]
```

## 9. buscar_post

```http
GET http://127.0.0.1:5000/api/posts/1
```

Resposta: HTTP 200

```json
{
  "comentarios": [
    {
      "id": "1",
      "post_id": "1",
      "texto": "Bem-vindo!",
      "usuario_id": "1"
    }
  ],
  "curtidas": [
    {
      "post_id": "1",
      "usuario_id": "1"
    }
  ],
  "id": "1",
  "texto": "Ola, rede!",
  "usuario_id": "2"
}
```

## 10. seguidores_de

```http
GET http://127.0.0.1:5000/api/usuarios/2/seguidores
```

Resposta: HTTP 200

```json
[
  {
    "id": "1",
    "nome": "Ana",
    "perfil": {
      "bio": "Estudante",
      "usuario_id": "1"
    }
  }
]
```

## 11. seguindo_de

```http
GET http://127.0.0.1:5000/api/usuarios/1/seguindo
```

Resposta: HTTP 200

```json
[
  {
    "id": "2",
    "nome": "Bruno",
    "perfil": {
      "bio": "",
      "usuario_id": "2"
    }
  }
]
```

## 12. feed_do_usuario

```http
GET http://127.0.0.1:5000/api/usuarios/1/feed
```

Resposta: HTTP 200

```json
[
  {
    "comentarios": [
      {
        "id": "1",
        "post_id": "1",
        "texto": "Bem-vindo!",
        "usuario_id": "1"
      }
    ],
    "curtidas": [
      {
        "post_id": "1",
        "usuario_id": "1"
      }
    ],
    "id": "1",
    "texto": "Ola, rede!",
    "usuario_id": "2"
  }
]
```
