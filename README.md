<<<<<<< HEAD
# mermaidView
MermaidView para ser executado local
=======
# MermaidView

Uma aplicação Python para visualizar e exportar diagramas [Mermaid](https://mermaid.js.org/) para PNG/SVG.

Construída com arquitetura Domain-Driven Design (DDD), apresentando interface CLI, API REST e interface web.

## Funcionalidades

- **Renderização de diagramas Mermaid** para formato PNG ou SVG
- **Múltiplas interfaces**: CLI, API REST e Interface Web
- **Saída de alta qualidade** usando Playwright (navegador Chromium headless)
- **Renderizador de fallback** usando a API mermaid.ink
- **Suporte a Docker** para fácil implantação
- **Arquitetura DDD** para código manutenível e testável
- **Suporte a todos os tipos de diagramas Mermaid**: Fluxogramas, Diagramas de Sequência, Diagramas de Classe, Diagramas de Estado, Diagramas ER, Gráficos de Gantt e mais

## Início Rápido

### Pré-requisitos

- Python 3.10 ou superior
- Node.js (para instalação do Playwright)

### Instalação

```bash
# Clonar o repositório
git clone https://github.com/yourusername/mermaidview.git
cd mermaidview

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instalar dependências
pip install -e .

# Instalar navegadores do Playwright
playwright install chromium
```

### Uso Básico

#### Renderizar a partir de arquivo

```bash
mermaid-view render diagrama.mmd -o saida.png
```

#### Renderizar a partir de código

```bash
mermaid-view render --code "graph TD; A-->B; B-->C" -o saida.png
```

#### Iniciar servidor web

```bash
mermaid-view serve --port 8000
```

Em seguida, abra http://localhost:8000 no seu navegador.

## Docker

### Início Rápido com Docker

```bash
# Construir e executar
docker-compose up --build

# Acessar em http://localhost:8000
```

### Construir imagem Docker manualmente

```bash
docker build -t mermaid-view -f docker/Dockerfile .
docker run -p 8000:8000 mermaid-view
```

## Referência da CLI

```bash
# Renderizar diagrama
mermaid-view render [ARQUIVO_ENTRADA] [OPÇÕES]

Opções:
  -c, --code TEXT         Código Mermaid (alternativa ao arquivo)
  -o, --output PATH       Caminho do arquivo de saída [padrão: output.png]
  -w, --width INTEGER     Largura em pixels [padrão: 800]
  -h, --height INTEGER    Altura em pixels [padrão: 600]
  -t, --theme [default|forest|dark|neutral]  Tema do Mermaid
  -f, --format [png|svg]  Formato de saída [padrão: png]
  -s, --scale FLOAT       Fator de escala [padrão: 2.0]
  --transparent           Fundo transparente

# Iniciar servidor web
mermaid-view serve [OPÇÕES]

Opções:
  --host TEXT      Host para vincular [padrão: 0.0.0.0]
  -p, --port INT   Porta para escutar [padrão: 8000]
  --reload         Habilitar auto-reload

# Mostrar exemplos
mermaid-view example

# Mostrar informações
mermaid-view info
```

## Referência da API

### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Interface web |
| GET | `/health` | Verificação de saúde |
| POST | `/api/v1/render` | Renderizar diagrama (resposta JSON) |
| POST | `/api/v1/render/image` | Renderizar diagrama (resposta imagem) |
| GET | `/api/v1/diagrams` | Listar diagramas |
| GET | `/api/v1/diagrams/{id}` | Obter diagrama por ID |
| GET | `/api/v1/quick-render` | Renderização rápida via GET |

### Exemplo: Renderizar via API

```bash
curl -X POST http://localhost:8000/api/v1/render/image \
  -H "Content-Type: application/json" \
  -d '{"code": "graph TD; A-->B", "theme": "default", "output_format": "png"}' \
  --output diagrama.png
```

## Configuração

Variáveis de ambiente:

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `MERMAID_VIEW_HOST` | `0.0.0.0` | Host do servidor |
| `MERMAID_VIEW_PORT` | `8000` | Porta do servidor |
| `MERMAID_VIEW_DEBUG` | `false` | Modo debug |
| `MERMAID_VIEW_HEADLESS` | `true` | Navegador headless |
| `MERMAID_VIEW_TIMEOUT` | `30000` | Timeout de renderização (ms) |
| `MERMAID_VIEW_USE_FALLBACK` | `true` | Usar fallback mermaid.ink |
| `MERMAID_VIEW_THEME` | `default` | Tema padrão |
| `MERMAID_VIEW_WIDTH` | `800` | Largura padrão |
| `MERMAID_VIEW_HEIGHT` | `600` | Altura padrão |
| `MERMAID_VIEW_SCALE` | `2.0` | Escala padrão |

## Desenvolvimento

### Configuração

```bash
# Instalar dependências de desenvolvimento
pip install -e ".[dev]"

# Executar testes
pytest

# Executar testes com cobertura
pytest --cov=src/mermaid_view

# Formatar código
black src/ tests/
isort src/ tests/

# Verificar lint
ruff check src/ tests/
```

### Estrutura do Projeto

```
mermaidView/
├── src/mermaid_view/
│   ├── domain/           # Lógica de negócio (entidades, value objects, ports)
│   ├── application/      # Casos de uso (commands, queries, handlers)
│   ├── infrastructure/   # Adaptadores externos (Playwright, storage, web)
│   └── presentation/     # Interface CLI
├── tests/
│   ├── unit/            # Testes unitários
│   └── integration/     # Testes de integração
├── docs/                # Documentação
├── docker/              # Arquivos Docker
└── docker-compose.yml
```

## Tipos de Diagramas Suportados

- Fluxograma (Flowchart)
- Diagrama de Sequência
- Diagrama de Classe
- Diagrama de Estado
- Diagrama de Entidade-Relacionamento
- Jornada do Usuário
- Gráfico de Gantt
- Gráfico de Pizza
- Gráfico de Quadrante
- Diagrama de Requisitos
- GitGraph
- Diagrama C4
- Mapa Mental
- Linha do Tempo
- ZenUML
- Diagrama Sankey
- Gráfico XY
- Diagrama de Bloco
- E mais...

## Licença

Licença MIT - veja [LICENSE](LICENSE) para detalhes.

## Contribuindo

Contribuições são bem-vindas! Por favor, leia nossas diretrizes de contribuição antes de enviar PRs.

## Agradecimentos

- [Mermaid.js](https://mermaid.js.org/) - A biblioteca de diagramas
- [Playwright](https://playwright.dev/) - Automação de navegador
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web
- [Typer](https://typer.tiangolo.com/) - Framework CL
>>>>>>> 5d1e4d6 (feat: implementação inicial MermaidView - visualizador de diagramas Mermaid)
