# PyTest — Slides

Apresentação Reveal.js sobre PyTest + Playwright (E2E, API, POM, markers e comandos do **testflow-pytest**).

## Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `index.html` | Apresentação interativa (Reveal.js) |
| `guia-completo.html` | **Guia passo a passo** — instalação, PyTest, Playwright e todos os comandos |
| `pytest-intro-slides.pdf` | Versão PDF (gerada via decktape) |
| `css/theme-pytest.css` | Tema visual PyTest (slides) |
| `css/guide.css` | Tema visual PyTest (guia HTML) |
| `assets/pytest-logo.svg` | Logo oficial (flauta + wordmark) — [pytest-dev/design](https://github.com/pytest-dev/design) |
| `assets/pytest-mark.svg` | Ícone sem texto (favicon) |

## Pré-requisito (slides)

```bash
npm install
```

## Visualizar no browser

```bash
npm install
npm run slides
# http://localhost:3336/docs/slides/
# Guia passo a passo: http://localhost:3336/docs/slides/guia-completo.html
```

Atalho (macOS):

```bash
npm run slides:open
```

## Regenerar PDF

```bash
npm run slides:pdf
```

Gera `docs/slides/pytest-intro-slides.pdf` via [decktape](https://github.com/astefanutti/decktape) (1280×720, todos os fragments visíveis).

## Export manual (Chrome)

1. Abra `http://localhost:3336/docs/slides/?print-pdf`
2. `Cmd+P` → Destino: **Salvar como PDF**
3. Layout: **Paisagem**, Margens: **Nenhuma**, **Gráficos de fundo** ativado
