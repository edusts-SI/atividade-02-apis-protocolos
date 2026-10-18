"""Cliente HTTP real: executa os exemplos e compara cada resposta esperada."""
import argparse
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def main():
    parser = argparse.ArgumentParser(description='Execute contra um servidor vazio; reinicie antes de cada demonstracao.')
    parser.add_argument('protocol', choices=['rest', 'graphql'])
    parser.add_argument('--url', default='http://127.0.0.1:5000')
    args = parser.parse_args()
    path = Path(__file__).resolve().parents[1] / 'examples' / f'{args.protocol}.json'
    for case in json.loads(path.read_text(encoding='utf-8')):
        body = json.dumps(case['body']).encode() if case['body'] is not None else None
        request = Request(args.url.rstrip('/') + case['path'], data=body, method=case['method'], headers={'Content-Type': 'application/json'})
        try:
            with urlopen(request, timeout=10) as response:
                status = response.status
                result = json.load(response)
        except HTTPError as error:
            raise SystemExit(f"Falha em {case['operacao']}: HTTP {error.code}, {error.read().decode()}") from error
        except URLError as error:
            raise SystemExit(f'Nao foi possivel conectar. Inicie python app.py. Detalhe: {error}') from error
        if status != case['status'] or result != case['response']:
            raise SystemExit(f"Resposta inesperada em {case['operacao']}. Reinicie o servidor para limpar os dados.\nRecebido: {result}")
        print(f"OK {case['operacao']} — HTTP {status}")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    print('Todos os exemplos conferem com as respostas documentadas.')


if __name__ == '__main__':
    main()
