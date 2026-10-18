import unittest

from app import create_app


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def gql(self, query, **kwargs):
        return self.client.post('/graphql', json={"query": query, **kwargs})

    def user(self, nome='Ana'):
        return self.client.post('/api/usuarios', json={"nome": nome}).get_json()

    def test_cross_protocol_workflow(self):
        ana = self.user()
        response = self.gql('mutation { criar_usuario(nome: "Bruno", bio: "Oi") { id perfil { bio } } }')
        self.assertEqual(response.get_json()['data']['criar_usuario']['id'], '2')
        self.assertEqual(self.client.get('/api/usuarios/2').get_json()['perfil']['bio'], 'Oi')
        response = self.gql('mutation { criar_post(usuario_id: "2", texto: "Primeiro") { id texto } }')
        self.assertEqual(response.get_json()['data']['criar_post']['id'], '1')
        self.assertEqual(self.client.post('/api/usuarios/1/seguindo', json={"seguido_id": '2'}).status_code, 201)
        response = self.gql('mutation { comentar(usuario_id: "1", post_id: "1", texto: "Legal") { id } curtir(usuario_id: "1", post_id: "1") { post_id } }')
        self.assertNotIn('errors', response.get_json())
        post = self.client.get('/api/posts/1').get_json()
        self.assertEqual(post['comentarios'][0]['texto'], 'Legal')
        self.assertEqual(post['curtidas'], [{"usuario_id": '1', "post_id": '1'}])
        self.assertEqual(self.client.get('/api/usuarios/2/posts').get_json(), [post])
        self.assertEqual(self.client.get('/api/usuarios/1/feed').get_json(), [post])
        self.assertEqual(self.client.get('/api/usuarios/2/seguidores').get_json(), [ana])
        response = self.gql('{ buscar_usuario(id: "1") { nome seguindo { nome } } buscar_post(id: "1") { autor { nome } comentarios { texto } } posts_do_usuario(usuario_id: "2") { id } seguidores_de(usuario_id: "2") { id } seguindo_de(usuario_id: "1") { id } feed_do_usuario(usuario_id: "1") { id } }')
        data = response.get_json()['data']
        self.assertEqual(data['buscar_usuario'], {"nome": 'Ana', "seguindo": [{"nome": 'Bruno'}]})
        self.assertEqual(data['buscar_post']['autor']['nome'], 'Bruno')
        self.assertEqual(data['posts_do_usuario'], [{"id": '1'}])
        self.assertEqual(data['seguidores_de'], [{"id": '1'}])
        self.assertEqual(data['seguindo_de'], [{"id": '2'}])
        self.assertEqual(data['feed_do_usuario'], [{"id": '1'}])

    def test_feed_filters_and_orders(self):
        for name in ['Ana', 'Bruno', 'Carla']:
            self.user(name)
        for author in ['1', '2', '3', '2']:
            self.client.post('/api/posts', json={"usuario_id": author, "texto": 'Post'})
        self.client.post('/api/usuarios/1/seguindo', json={"seguido_id": '2'})
        self.assertEqual([p['id'] for p in self.client.get('/api/usuarios/1/feed').get_json()], ['4', '2', '1'])
        self.assertEqual([p['id'] for p in self.client.get('/api/usuarios/2/posts').get_json()], ['4', '2'])

    def test_domain_errors_and_duplicates(self):
        self.user()
        self.user('Bruno')
        self.client.post('/api/posts', json={"usuario_id": '1', "texto": 'Oi'})
        for url, data in [('/api/posts/1/curtidas', {"usuario_id": '2'}), ('/api/usuarios/1/seguindo', {"seguido_id": '2'})]:
            self.assertEqual(self.client.post(url, json=data).status_code, 201)
            self.assertEqual(self.client.post(url, json=data).status_code, 409)
        self.assertEqual(self.client.post('/api/usuarios/1/seguindo', json={"seguido_id": '1'}).status_code, 400)
        self.assertEqual(self.client.post('/api/posts/99/comentarios', json={"usuario_id": '1', "texto": 'Oi'}).status_code, 404)
        self.assertEqual(self.client.post('/api/posts', json={"usuario_id": '99', "texto": 'Oi'}).status_code, 404)
        self.assertEqual(self.client.get('/api/usuarios/99/feed').status_code, 404)
        response = self.gql('mutation { curtir(usuario_id: "2", post_id: "1") { post_id } }')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['errors'][0]['extensions']['status'], 409)

    def test_validation(self):
        for data in [{}, [], {"nome": '   '}, {"nome": 4}, {"nome": 'A', "bio": None}, {"nome": 'A', "extra": True}]:
            with self.subTest(data=data):
                self.assertEqual(self.client.post('/api/usuarios', json=data).status_code, 400)
        self.assertEqual(self.client.post('/api/usuarios', data='{', content_type='application/json').status_code, 400)
        self.assertEqual(self.client.post('/api/usuarios', data='nome=A').status_code, 415)
        self.assertEqual(self.client.get('/api/usuarios/abc').status_code, 400)
        self.assertEqual(self.client.post('/api/usuarios', json={"nome": 'x' * 101}).status_code, 400)

    def test_graphql_validation_variables_and_selection(self):
        self.user()
        response = self.gql('query Pessoa($id: ID!) { pessoa: buscar_usuario(id: $id) { nome } }', variables={"id": '1'}, operationName='Pessoa')
        self.assertEqual(response.get_json(), {"data": {"pessoa": {"nome": 'Ana'}}})
        for query in ['{ nao_existe }', '{', 'query Pessoa($id: ID!) { buscar_usuario(id: $id) { nome } }']:
            self.assertEqual(self.gql(query).status_code, 400)
        self.assertEqual(self.gql('{ buscar_usuario(id: "1") { nome } }', variables=[]).status_code, 400)
        response = self.gql('{ buscar_usuario(id: "99") { nome } }')
        self.assertEqual(response.get_json()['errors'][0]['extensions']['status'], 404)

    def test_empty_collections(self):
        self.user()
        for path in ['posts', 'feed', 'seguidores', 'seguindo']:
            self.assertEqual(self.client.get('/api/usuarios/1/' + path).get_json(), [])


if __name__ == '__main__':
    unittest.main()
