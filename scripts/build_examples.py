"""Gera exemplos e respostas reais, exercitando instancias limpas da API."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app import create_app


def rest_cases():
    return [
        ('criar_usuario', 'POST', '/api/usuarios', {"nome": 'Ana', "bio": 'Estudante'}),
        ('criar_usuario (segundo usuario)', 'POST', '/api/usuarios', {"nome": 'Bruno'}),
        ('criar_post', 'POST', '/api/posts', {"usuario_id": '2', "texto": 'Ola, rede!'}),
        ('comentar', 'POST', '/api/posts/1/comentarios', {"usuario_id": '1', "texto": 'Bem-vindo!'}),
        ('curtir', 'POST', '/api/posts/1/curtidas', {"usuario_id": '1'}),
        ('seguir', 'POST', '/api/usuarios/1/seguindo', {"seguido_id": '2'}),
        ('buscar_usuario', 'GET', '/api/usuarios/1', None),
        ('posts_do_usuario', 'GET', '/api/usuarios/2/posts', None),
        ('buscar_post', 'GET', '/api/posts/1', None),
        ('seguidores_de', 'GET', '/api/usuarios/2/seguidores', None),
        ('seguindo_de', 'GET', '/api/usuarios/1/seguindo', None),
        ('feed_do_usuario', 'GET', '/api/usuarios/1/feed', None),
    ]


def graphql_cases():
    operations = [
        ('criar_usuario', 'mutation { criar_usuario(nome: "Ana", bio: "Estudante") { id nome perfil { usuario_id bio } } }'),
        ('criar_usuario (segundo usuario)', 'mutation { criar_usuario(nome: "Bruno") { id nome perfil { usuario_id bio } } }'),
        ('criar_post', 'mutation { criar_post(usuario_id: "2", texto: "Ola, rede!") { id usuario_id texto comentarios { id } curtidas { usuario_id } } }'),
        ('comentar', 'mutation { comentar(usuario_id: "1", post_id: "1", texto: "Bem-vindo!") { id usuario_id post_id texto } }'),
        ('curtir', 'mutation { curtir(usuario_id: "1", post_id: "1") { usuario_id post_id } }'),
        ('seguir', 'mutation { seguir(seguidor_id: "1", seguido_id: "2") { seguidor_id seguido_id } }'),
        ('buscar_usuario', '{ buscar_usuario(id: "1") { id nome perfil { usuario_id bio } } }'),
        ('posts_do_usuario', '{ posts_do_usuario(usuario_id: "2") { id texto autor { nome } } }'),
        ('buscar_post', '{ buscar_post(id: "1") { id texto comentarios { id texto } curtidas { usuario_id } } }'),
        ('seguidores_de', '{ seguidores_de(usuario_id: "2") { id nome } }'),
        ('seguindo_de', '{ seguindo_de(usuario_id: "1") { id nome } }'),
        ('feed_do_usuario', '{ feed_do_usuario(usuario_id: "1") { id texto autor { nome perfil { bio } } } }'),
    ]
    return [(name, 'POST', '/graphql', {"query": query}) for name, query in operations]


def main():
    directory = ROOT / 'examples'
    directory.mkdir(exist_ok=True)
    for protocol, cases in [('rest', rest_cases()), ('graphql', graphql_cases())]:
        client = create_app().test_client()
        entries = []
        http = []
        markdown = [f'# Exemplos {protocol.upper()}', '',
                    'Execute na ordem abaixo, com o servidor recém-iniciado e vazio. Reinicie antes de trocar de protocolo.', '',
                    'As respostas foram geradas pela aplicação. A ordem das chaves JSON não altera o resultado.', '',
                    'Cada bloco HTTP pode ser colado no arquivo `.http` de um cliente HTTP. Para executar tudo pelo terminal, veja o README.', '']
        for index, (name, method, path, payload) in enumerate(cases, 1):
            response = client.open(path, method=method, json=payload) if payload is not None else client.get(path)
            assert response.status_code in (200, 201), response.get_json()
            assert 'errors' not in response.get_json(), response.get_json()
            data = response.get_json()
            entries.append({"operacao": name, "method": method, "path": path, "body": payload, "status": response.status_code, "response": data})
            request = f'{method} http://127.0.0.1:5000{path}\n'
            if payload is not None:
                request += 'Content-Type: application/json\n\n' + json.dumps(payload, ensure_ascii=False, indent=2) + '\n'
            http.append(f'### {index}. {name}\n{request}')
            markdown.extend([f'## {index}. {name}', '', '```http', request.rstrip(), '```', '', f'Resposta: HTTP {response.status_code}', '', '```json', json.dumps(data, ensure_ascii=False, indent=2), '```', ''])
        (directory / f'{protocol}.json').write_text(json.dumps(entries, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        (directory / f'{protocol}.http').write_text('\n'.join(http), encoding='utf-8')
        (directory / f'{protocol}.md').write_text('\n'.join(markdown), encoding='utf-8')
        print(f'{protocol}: {len(entries)} exemplos verificados e gerados.')


if __name__ == '__main__':
    main()
