"""Regras compartilhadas pelos adaptadores REST e GraphQL."""
from threading import RLock


class DomainError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


class SocialNetwork:
    def __init__(self):
        self.users = {}
        self.posts = {}
        self.comments = []
        self.likes = set()
        self.follows = set()
        self.lock = RLock()

    @staticmethod
    def text(value, field, maximum):
        if not isinstance(value, str) or not value.strip():
            raise DomainError(f"{field} deve ser um texto nao vazio.")
        value = value.strip()
        if len(value) > maximum:
            raise DomainError(f"{field} deve ter no maximo {maximum} caracteres.")
        return value

    @staticmethod
    def identifier(value):
        if isinstance(value, bool) or not isinstance(value, (str, int)) or not str(value).isascii() or not str(value).isdigit() or int(value) < 1:
            raise DomainError("ID deve ser um inteiro positivo.")
        return str(int(value))

    def user(self, id):
        id = self.identifier(id)
        if id not in self.users:
            raise DomainError("Usuario nao encontrado.", 404)
        return self.users[id]

    def post(self, id):
        id = self.identifier(id)
        if id not in self.posts:
            raise DomainError("Post nao encontrado.", 404)
        return {
            **self.posts[id],
            "comentarios": [dict(c) for c in self.comments if c["post_id"] == id],
            "curtidas": [{"usuario_id": u, "post_id": p} for u, p in sorted(self.likes) if p == id],
        }

    def criar_usuario(self, nome, bio=""):
        nome = self.text(nome, "nome", 100)
        if not isinstance(bio, str) or len(bio) > 500:
            raise DomainError("bio deve ser um texto de ate 500 caracteres.")
        id = str(len(self.users) + 1)
        self.users[id] = {"id": id, "nome": nome, "perfil": {"usuario_id": id, "bio": bio.strip()}}
        return self.users[id]

    def criar_post(self, usuario_id, texto):
        usuario = self.user(usuario_id)
        texto = self.text(texto, "texto", 2000)
        id = str(len(self.posts) + 1)
        self.posts[id] = {"id": id, "usuario_id": usuario["id"], "texto": texto}
        return self.post(id)

    def comentar(self, usuario_id, post_id, texto):
        usuario = self.user(usuario_id)
        post = self.post(post_id)
        texto = self.text(texto, "texto", 1000)
        comment = {"id": str(len(self.comments) + 1), "usuario_id": usuario["id"], "post_id": post["id"], "texto": texto}
        self.comments.append(comment)
        return dict(comment)

    def curtir(self, usuario_id, post_id):
        usuario = self.user(usuario_id)
        post = self.post(post_id)
        pair = (usuario["id"], post["id"])
        if pair in self.likes:
            raise DomainError("Usuario ja curtiu este post.", 409)
        self.likes.add(pair)
        return {"usuario_id": pair[0], "post_id": pair[1]}

    def seguir(self, seguidor_id, seguido_id):
        follower = self.user(seguidor_id)
        followed = self.user(seguido_id)
        pair = (follower["id"], followed["id"])
        if pair[0] == pair[1]:
            raise DomainError("Usuario nao pode seguir a si mesmo.")
        if pair in self.follows:
            raise DomainError("Usuario ja segue este perfil.", 409)
        self.follows.add(pair)
        return {"seguidor_id": pair[0], "seguido_id": pair[1]}

    def posts_do_usuario(self, usuario_id):
        id = self.user(usuario_id)["id"]
        return [self.post(p["id"]) for p in reversed(list(self.posts.values())) if p["usuario_id"] == id]

    def seguidores_de(self, usuario_id):
        id = self.user(usuario_id)["id"]
        return [self.user(a) for a, b in sorted(self.follows, key=lambda pair: int(pair[0])) if b == id]

    def seguindo_de(self, usuario_id):
        id = self.user(usuario_id)["id"]
        return [self.user(b) for a, b in sorted(self.follows, key=lambda pair: int(pair[1])) if a == id]

    def feed_do_usuario(self, usuario_id):
        id = self.user(usuario_id)["id"]
        authors = {id} | {b for a, b in self.follows if a == id}
        return [self.post(p["id"]) for p in reversed(list(self.posts.values())) if p["usuario_id"] in authors]
