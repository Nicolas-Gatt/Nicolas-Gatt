import os
import sys
import requests
from typing import Dict, Any, List

print("Iniciando script python...")
GITHUB_TOKEN = os.getenv("GH_TOKEN")

if not GITHUB_TOKEN:
    print("ERRO: GITHUB_TOKEN nao encontrado no ambiente.")
    sys.exit(1)
else:
    print(f"Token detectado com sucesso (tamanho: {len(GITHUB_TOKEN)} caracteres).")


class GitHubMetricsFetcher:
    GRAPHQL_URL = "https://api.github.com/graphql"
    
    def __init__(self, username: str, token: str):
        self.username = username
        self.headers = {"Authorization": f"Bearer {token}"}

    def fetch_stats(self) -> Dict[str, Any]: 
        query = """
        query($login: String!) {
          user(login: $login) {
            followers { totalCount }
            repositories(first: 100, ownerAffiliations: OWNER, orderBy: {field: PUSHED_AT, direction: DESC}) {
              totalCount
              nodes {
                stargazerCount
                languages(first: 10) {
                  edges { size }
                }
              }
            }
          }
        }
        """
        variables = {"login": self.username}
        
        try:
            print(f"Enviando requisicao GraphQL para o usuario: {self.username}")
            response = requests.post(
                self.GRAPHQL_URL, 
                json={'query': query, 'variables': variables}, 
                headers=self.headers,
                timeout=10
            )
            print(f"Status HTTP recebido: {response.status_code}")
            response.raise_for_status()
            return self._parse_metrics(response.json())
        except Exception as e:
            print(f"EXCECAO CAPTURADA NO FETCH: {e}")
            if 'response' in locals() and hasattr(response, 'text'):
                print(f"Corpo da resposta: {response.text}")
            sys.exit(1)

    def _parse_metrics(self, data: Dict[str, Any]) -> Dict[str, str]:
        try:
            if 'errors' in data:
                print(f"Erros retornados pela API do GraphQL: {data['errors']}")
                sys.exit(1)
                
            user_data = data['data']['user']
            repos = user_data['repositories']['nodes']
            
            total_stars = sum(repo['stargazerCount'] for repo in repos)
            total_loc = 0
            
            for repo in repos:
                for edge in repo['languages'].get('edges', []):
                    total_loc += edge['size'] // 30 

            return {
                "repos": str(user_data['repositories']['totalCount']),
                "stars": str(total_stars),
                "commits": "2,116",
                "followers": str(user_data['followers']['totalCount']),
                "loc": f"{total_loc:,}"
            }
        except Exception as e:
            print(f"EXCECAO CAPTURADA NO PARSE: {e}")
            sys.exit(1)


class SvgRenderer:
    def __init__(self, metrics: Dict[str, str], ascii_art: List[str]):
        self.metrics = metrics
        self.ascii_art = ascii_art
        self.line_height = 20

    def _build_right_column(self) -> List[str]:
        return [
            f"<tspan fill='#E5C07B'>      Bem-vindo ao meu perfil!     </tspan>",
            f"<tspan fill='#5C6370'>-----------------------------------</tspan>",
            f". <tspan fill='#61AFEF'>Email</tspan>: <tspan fill='#5C6370'>.........</tspan> nicolasgatti2101@gmail.com",
            f". <tspan fill='#61AFEF'>LinkedIn</tspan>: <tspan fill='#5C6370'>......</tspan> linkedin.com/in/nicolas-gatti",
            f". <tspan fill='#61AFEF'>Idade</tspan>: <tspan fill='#5C6370'>......................</tspan> 19 anos",
            f". <tspan fill='#61AFEF'>Setup</tspan>: <tspan fill='#5C6370'>..</tspan> Ryzen 5 5600X, RX570, 16GB, 1TB",
            "",
            f"<tspan fill='#E5C07B'>Linguagens &amp; Tecnologias</tspan> <tspan fill='#5C6370'>------------------------</tspan>",
            f". <tspan fill='#61AFEF'>Back-End</tspan>: <tspan fill='#5C6370'>.....</tspan> Python, Java, TypeScript, C#",
            f". <tspan fill='#61AFEF'>IA &amp; Dados</tspan>: <tspan fill='#5C6370'>...</tspan> LangGraph, Pandas, Perceptron",
            f". <tspan fill='#61AFEF'>Databases</tspan>: <tspan fill='#5C6370'>....</tspan> PostgreSQL, MySQL, SQLite",
            f". <tspan fill='#61AFEF'>Infra</tspan>: <tspan fill='#5C6370'>........</tspan> Linux, Docker, Azure, Asterisk",
            f". <tspan fill='#61AFEF'>Front-End</tspan>: <tspan fill='#5C6370'>....</tspan> React, JS, HTML5, CSS",
            "",
            f"<tspan fill='#E5C07B'>GitHub Stats</tspan> <tspan fill='#5C6370'>------------------------------------</tspan>",
            f". <tspan fill='#61AFEF'>Repositorios</tspan>: <tspan fill='#5C6370'>...</tspan> {self.metrics['repos']} | <tspan fill='#61AFEF'>Stars</tspan>: <tspan fill='#5C6370'>.........</tspan> {self.metrics['stars']}",
            f". <tspan fill='#61AFEF'>Commits</tspan>: <tspan fill='#5C6370'>........</tspan> {self.metrics['commits']} | <tspan fill='#61AFEF'>Followers</tspan>: <tspan fill='#5C6370'>.....</tspan> {self.metrics['followers']}",
            f". <tspan fill='#61AFEF'>Lines of Code</tspan>: <tspan fill='#5C6370'>.......................</tspan> {self.metrics['loc']}"
        ]

    def generate_svg(self, filename: str) -> None:
        right_lines = self._build_right_column()
        max_lines = max(len(self.ascii_art), len(right_lines))
        
        svg_content = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="850" height="{max_lines * self.line_height + 40}" viewBox="0 0 850 {max_lines * self.line_height + 40}">',
            '<rect width="100%" height="100%" fill="#1E2227" rx="10"/>',
            '<style>',
            '  .text { font-family: "Courier New", Courier, monospace; font-size: 14px; fill: #ABB2BF; }',
            '</style>',
            '<g class="text">'
        ]

        for i in range(max_lines):
            y_pos = (i + 1) * self.line_height + 10
            left = self.ascii_art[i] if i < len(self.ascii_art) else ""
            right = right_lines[i] if i < len(right_lines) else ""
            
            left = left.replace(" ", "&#160;")
            
            svg_content.append(f'  <text x="20" y="{y_pos}">{left}</text>')
            svg_content.append(f'  <text x="400" y="{y_pos}" xml:space="preserve">{right}</text>')

        svg_content.extend(['</g>', '</svg>'])

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("\n".join(svg_content))
        print(f"Arquivo {filename} gerado com sucesso!")


if __name__ == "__main__":
    ASCII_ART = [
        "                                ",
        "                                ",
        "      - -  W E L C O M E  - -   ",
        "                                ",
        "          (  )   (   )  )       ",
        "           ) (   )  (  (        ",
        "           ( )  (    ) )        ",
        "           _____________        ",
        "          &lt;_____________&gt; ___   ",
        "          |             |/ _ \\  ",
        "          |               | | | ",
        "          |               |_| | ",
        "       ___|             |\\___/  ",
        "      /    \\___________/    \\   ",
        "      \\_____________________/   ",
        "                                ",
        "                                "
    ]

    fetcher = GitHubMetricsFetcher(username="Nicolas-Gatt", token=GITHUB_TOKEN)
    current_metrics = fetcher.fetch_stats()
    
    renderer = SvgRenderer(metrics=current_metrics, ascii_art=ASCII_ART)
    renderer.generate_svg("github_stats.svg")
