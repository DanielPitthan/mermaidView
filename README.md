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
- **Interface Web personalizável**:
  - **Temas visuais**: Tema Misto (padrão), Tema Escuro e Tema Azul-Roxo (paleta azul ao roxo, preto, cinza e branco)
  - **Logo opcional** no header (à esquerda), com opção de enviar logotipo personalizado
  - Preferências (tema e logo) salvas no navegador (localStorage) para persistência entre sessões

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

### Interface Web

Na interface web você pode:

- **Escolher o tema da aplicação** no menu do header: **Tema Misto** (header escuro, corpo claro), **Tema Escuro** (interface toda escura) ou **Tema Azul-Roxo** (paleta azul, roxo, preto, cinza e branco). A escolha é mantida no navegador.
- **Usar logo personalizado**: o header exibe um logo à esquerda (opcional). É possível enviar seu próprio logotipo pelo botão "Logo"; a imagem fica salva localmente no navegador até você remover.
- **Editor e visualização**: painel à esquerda para editar o código Mermaid, à direita a pré-visualização. Use *Ctrl+Enter* para renderizar, ou o botão "Renderizar". O tema do *diagrama* (Padrão, Forest, Escuro, Neutro) e o formato (PNG/SVG) podem ser alterados antes do download.

## Docker

### Executar a partir do Docker Hub

Para baixar e subir o container usando a imagem publicada:

```bash
# Baixar a imagem
docker pull pitthan/mermaidview:latest

# Subir o container (porta 8000)
docker run -d -p 8000:8000 --name mermaidview pitthan/mermaidview:latest
```

Acesse http://localhost:8000 no navegador. Para parar o container: `docker stop mermaidview`. Para remover: `docker rm mermaidview`.

### Início Rápido com Docker (build local)

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

### Publicar no Docker Hub

1. **Crie uma conta** em [hub.docker.com](https://hub.docker.com) (se ainda não tiver).

2. **Faça login** no terminal:
   ```bash
   docker login
   ```
   Informe seu usuário e senha (ou token de acesso) quando solicitado.

3. **Construa a imagem** com a tag no formato `SEU_USUARIO/nome-do-repositorio:tag`:
   ```bash
   docker build -t SEU_USUARIO/mermaidview:latest -f docker/Dockerfile .
   ```
   Exemplo: se seu usuário for `joao`, use `joao/mermaidview:latest`.

4. **Envie a imagem** para o Docker Hub:
   ```bash
   docker push SEU_USUARIO/mermaidview:latest
   ```

5. **(Opcional)** Para publicar também uma versão específica (ex.: `1.0.0`):
   ```bash
   docker tag SEU_USUARIO/mermaidview:latest SEU_USUARIO/mermaidview:1.0.0
   docker push SEU_USUARIO/mermaidview:1.0.0
   ```

Depois de publicar, qualquer pessoa pode executar com:
```bash
docker run -p 8000:8000 SEU_USUARIO/mermaidview:latest
```

No Docker Hub você pode preencher a descrição do repositório, adicionar um README e configurar visibilidade (público ou privado).

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
- [Typer](https://typer.tiangolo.com/) - Framework CLI
