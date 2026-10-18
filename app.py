"""Execute com python app.py; testes podem criar instancias isoladas via create_app."""
from pathlib import Path

from flask import Flask, jsonify, request
from graphql import GraphQLError, build_schema, graphql_sync
from werkzeug.exceptions import HTTPException

from domain import DomainError, SocialNetwork


def create_app():
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 64 * 1024
    network = SocialNetwork()
    schema = build_schema(Path(__file__).with_name("schema.graphql").read_text(encoding="utf-8"))

    def resolver(method):
        def resolve(source, info, **kwargs):
            try:
                return method(**kwargs)
            except DomainError as error:
                raise GraphQLError(str(error), extensions={"status": error.status}) from error
        return resolve

    for name, method in {
        "buscar_usuario": network.user,
        "posts_do_usuario": network.posts_do_usuario,
        "buscar_post": network.post,
        "seguidores_de": network.seguidores_de,
        "seguindo_de": network.seguindo_de,
        "feed_do_usuario": network.feed_do_usuario,
    }.items():
        schema.type_map["Query"].fields[name].resolve = resolver(method)
    for name in ("criar_usuario", "criar_post", "comentar", "curtir", "seguir"):
        schema.type_map["Mutation"].fields[name].resolve = resolver(getattr(network, name))
    for field, method in {
        "posts": network.posts_do_usuario,
        "seguidores": network.seguidores_de,
        "seguindo": network.seguindo_de,
    }.items():
        schema.type_map["Usuario"].fields[field].resolve = lambda user, info, method=method: method(user["id"])
    schema.type_map["Post"].fields["autor"].resolve = lambda post, info: network.user(post["usuario_id"])

    # Uma requisicao completa observa um estado consistente, inclusive no GraphQL.
    @app.before_request
    def acquire_lock():
        network.lock.acquire()

    @app.teardown_request
    def release_lock(error):
        network.lock.release()

    @app.errorhandler(DomainError)
    def domain_error(error):
        return jsonify({"erro": str(error)}), error.status

    @app.errorhandler(HTTPException)
    def http_error(error):
        return jsonify({"erro": error.description}), error.code

    def body(required, optional=()):
        data = request.get_json()
        if not isinstance(data, dict):
            raise DomainError("O corpo deve ser um objeto JSON.")
        missing = set(required) - data.keys()
        extra = data.keys() - set(required) - set(optional)
        if missing or extra:
            raise DomainError(f"Campos ausentes: {', '.join(sorted(missing)) or '-'}; desconhecidos: {', '.join(sorted(extra)) or '-'}.")
        return data

    @app.get("/")
    def index():
        return jsonify({"servico": "Rede social: REST e GraphQL", "rest": "/api", "graphql": "/graphql", "schema": "/schema.graphql"})

    @app.get("/schema.graphql")
    def show_schema():
        return app.response_class(Path(__file__).with_name("schema.graphql").read_text(encoding="utf-8"), mimetype="text/plain")

    @app.post("/api/usuarios")
    def criar_usuario():
        result = network.criar_usuario(**body(("nome",), ("bio",)))
        return jsonify(result), 201, {"Location": f'/api/usuarios/{result["id"]}'}

    @app.post("/api/posts")
    def criar_post():
        result = network.criar_post(**body(("usuario_id", "texto")))
        return jsonify(result), 201, {"Location": f'/api/posts/{result["id"]}'}

    @app.post("/api/posts/<post_id>/comentarios")
    def comentar(post_id):
        return jsonify(network.comentar(post_id=post_id, **body(("usuario_id", "texto")))), 201

    @app.post("/api/posts/<post_id>/curtidas")
    def curtir(post_id):
        return jsonify(network.curtir(post_id=post_id, **body(("usuario_id",)))), 201

    @app.post("/api/usuarios/<seguidor_id>/seguindo")
    def seguir(seguidor_id):
        return jsonify(network.seguir(seguidor_id=seguidor_id, **body(("seguido_id",)))), 201

    @app.get("/api/usuarios/<id>")
    def buscar_usuario(id):
        return jsonify(network.user(id))

    @app.get("/api/posts/<id>")
    def buscar_post(id):
        return jsonify(network.post(id))

    @app.get("/api/usuarios/<usuario_id>/posts")
    def posts_do_usuario(usuario_id):
        return jsonify(network.posts_do_usuario(usuario_id))

    @app.get("/api/usuarios/<usuario_id>/seguidores")
    def seguidores_de(usuario_id):
        return jsonify(network.seguidores_de(usuario_id))

    @app.get("/api/usuarios/<usuario_id>/seguindo")
    def seguindo_de(usuario_id):
        return jsonify(network.seguindo_de(usuario_id))

    @app.get("/api/usuarios/<usuario_id>/feed")
    def feed_do_usuario(usuario_id):
        return jsonify(network.feed_do_usuario(usuario_id))

    @app.post("/graphql")
    def graphql_endpoint():
        data = body(("query",), ("variables", "operationName"))
        if not isinstance(data["query"], str):
            raise DomainError("query deve ser um texto.")
        if data.get("variables") is not None and not isinstance(data["variables"], dict):
            raise DomainError("variables deve ser um objeto JSON.")
        if data.get("operationName") is not None and not isinstance(data["operationName"], str):
            raise DomainError("operationName deve ser um texto.")
        result = graphql_sync(schema, data["query"], variable_values=data.get("variables"), operation_name=data.get("operationName"))
        # Erros anteriores a execucao (sintaxe, validacao, variaveis): HTTP 400.
        status = 400 if result.errors and all(error.path is None for error in result.errors) else 200
        return jsonify(result.formatted), status

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=False)
