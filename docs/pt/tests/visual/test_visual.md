# Testes Visuais — Regressão por screenshot

**Arquivo-fonte:** [`../../../../tests/visual/test_visual.py`](../../../../tests/visual/test_visual.py)

---

## Propósito

Este módulo implementa **testes de regressão visual** com Playwright: captura screenshots de páginas-chave e compara com **baselines** armazenadas. Qualquer diferença de layout, cor, fonte ou posicionamento falha o teste.

Páginas cobertas:

| Caso | Página | Autenticação |
|------|--------|--------------|
| `TC.VISUAL_LOGIN` | `/web/login.html` | Não (pública) |
| `TC.VISUAL_DASHBOARD` | `/web/dashboard.html` | Sim |
| `TC.VISUAL_COMPONENTS` | `/web/components.html` | Sim |

Ideal para treinar **parametrização PyTest**, estabilização visual e naming de snapshots.

---

## Pré-requisitos

| Item | Descrição |
|------|-----------|
| Servidor | Sandbox acessível em `BASE_URL` |
| Baselines | Diretório de snapshots do Playwright (gerado na primeira execução ou versionado no repo) |
| Credenciais | Para dashboard e components via `visit_authenticated` |
| Markers | `visual`, `regression` |

**Execução:**

```bash
pytest tests/visual/test_visual.py -v
pytest tests/visual/test_visual.py -m visual
```

**Atualizar baselines (quando mudança visual é intencional):**

```bash
pytest tests/visual/test_visual.py --update-snapshots
```

(Flag exata pode variar conforme configuração do `pytest-playwright` no projeto.)

---

## Markers utilizados

| Marker | Função |
|--------|--------|
| `visual` | Identifica suite de screenshot — excluída de runs rápidos de API/smoke |
| `regression` | Parte da regressão completa |

---

## Visão geral da estrutura

```
test_visual.py
├── imports
├── helper: _wait_for_fonts
└── TestVisualSnapshots
    └── test_visual_baseline (parametrizado × 3 cenários)
```

---

## Imports — bloco a bloco

### `import pytest`

Usado para `@pytest.mark` e `@pytest.mark.parametrize`.

---

### `from playwright.sync_api import Page, expect`

- **`Page`**: navegação e captura de screenshot via locator.
- **`expect`**: `to_have_screenshot` integra comparação visual com retry.

---

### `from support.auth import visit_authenticated`

Login via API + navegação — usado nos cenários dashboard e components.

---

### `from support.config import BASE_URL`

URL base do ambiente (ex.: `http://localhost:3000`). Login visual usa `page.goto(f"{BASE_URL}/web/login.html")` com URL absoluta.

---

### `from support.constants.test_cases import TC`

Classe com IDs de casos de teste padronizados:

| Constante | ID |
|-----------|-----|
| `TC.VISUAL_LOGIN` | `TC-9001` |
| `TC.VISUAL_DASHBOARD` | `TC-9002` |
| `TC.VISUAL_COMPONENTS` | `TC-9003` |

Usados como `case_id` na parametrização e no nome do arquivo PNG.

---

## Helper: `_wait_for_fonts`

```python
def _wait_for_fonts(page: Page) -> None:
    page.emulate_media(reduced_motion="reduce")
    page.evaluate("() => document.fonts.ready")
```

### Por que existe?

Screenshots flaky frequentemente vêm de:

1. **Fontes web** ainda carregando (FOUT/FOIT)
2. **Animações** em movimento no momento da captura

### Bloco a bloco

| Linha | Efeito |
|-------|--------|
| `emulate_media(reduced_motion="reduce")` | Respeita preferência CSS `prefers-reduced-motion` — desativa ou reduz animações |
| `document.fonts.ready` | Promise do browser que resolve quando fontes declaradas em `@font-face` estão prontas |

**Conceito Playwright:** `page.evaluate` executa JavaScript no contexto da página — aqui aguardamos estabilidade antes do screenshot.

**Convenção:** prefixo `_` indica função privada ao módulo (não exportada).

---

## Classe `TestVisualSnapshots`

```python
@pytest.mark.visual
@pytest.mark.regression
class TestVisualSnapshots:
```

Agrupa um único método parametrizado que cobre três baselines.

---

## Parametrização: `@pytest.mark.parametrize`

```python
@pytest.mark.parametrize(
    "case_id,title,setup",
    [
        (
            TC.VISUAL_LOGIN,
            "login page baseline",
            lambda page, api_request: page.goto(f"{BASE_URL}/web/login.html"),
        ),
        (
            TC.VISUAL_DASHBOARD,
            "dashboard baseline",
            lambda page, api_request: visit_authenticated(page, api_request, "/web/dashboard.html"),
        ),
        (
            TC.VISUAL_COMPONENTS,
            "components baseline",
            lambda page, api_request: visit_authenticated(page, api_request, "/web/components.html"),
        ),
    ],
    ids=[TC.VISUAL_LOGIN, TC.VISUAL_DASHBOARD, TC.VISUAL_COMPONENTS],
)
```

### Parâmetros

| Nome | Tipo | Papel |
|------|------|-------|
| `case_id` | `str` | ID do caso (`TC-9001`, etc.) |
| `title` | `str` | Descrição legível para nome do PNG |
| `setup` | `callable` | Lambda que navega até o estado desejado |

### `ids=`

Define nomes curtos nos relatórios PyTest:

```
test_visual_baseline[TC-9001]
test_visual_baseline[TC-9002]
test_visual_baseline[TC-9003]
```

**Conceito PyTest:** parametrização evita copiar/colar três métodos quase idênticos — DRY com dados tabulares.

**Lambdas de setup:** recebem `(page, api_request)` para flexibilidade; login usa só `page`, autenticados usam ambos.

---

## Método `test_visual_baseline`

```python
def test_visual_baseline(
    self,
    page: Page,
    request,
    case_id: str,
    title: str,
    setup,
) -> None:
```

### Fixtures e parâmetros injetados

| Parâmetro | Origem |
|-----------|--------|
| `page` | pytest-playwright |
| `request` | PyTest — acesso a config, markers, node (útil para plugins de snapshot) |
| `case_id`, `title`, `setup` | Parametrize |

---

### Passo 1 — Setup da página

```python
setup(page, api_request)
```

**When:** executa a lambda correspondente ao cenário (goto login ou visit autenticado).

**Nota:** `api_request` é resolvido implicitamente pelo PyTest ao chamar `setup(page, api_request)` — deve existir fixture `api_request` no `conftest.py`.

---

### Passo 2 — Gate de prontidão e escolha do root

```python
if case_id == TC.VISUAL_LOGIN:
    expect(page.get_by_test_id("login-email")).to_be_visible()
    root = page.locator("body")
elif case_id == TC.VISUAL_DASHBOARD:
    expect(page.get_by_test_id("page-dashboard")).to_be_attached()
    root = page.get_by_test_id("page-dashboard")
else:
    expect(page.get_by_test_id("page-components")).to_be_attached()
    root = page.get_by_test_id("page-components")
```

| Cenário | Gate | Região capturada |
|---------|------|------------------|
| Login | Campo email visível | `body` inteiro (página pública sem shell autenticado) |
| Dashboard | `page-dashboard` anexado | Só o container principal (exclui ruído periférico) |
| Components | `page-components` anexado | Container da página de componentes |

**Conceito visual testing:** recortar (`root` = locator específico) reduz falsos positivos de header/footer dinâmicos.

---

### Passo 3 — Estabilização

```python
_wait_for_fonts(page)
```

**Given (estabilizado):** fontes carregadas, motion reduzido.

---

### Passo 4 — Screenshot assertion

```python
expect(root).to_have_screenshot(name=f"{case_id.lower()}-{title.replace(' ', '-')}.png")
```

Exemplo de nome gerado: `tc-9001-login-page-baseline.png`

**Conceito Playwright:**

- Primeira execução: grava baseline em pasta de snapshots do teste.
- Execuções seguintes: compara pixel a pixel (com threshold configurável no projeto).
- Falha: diff visual anexado ao relatório (dependendo do reporter).

**Formatação do nome:** `case_id.lower()` + título com espaços → hífens — nomes de arquivo portáveis.

---

## Given / When / Then por cenário

### Login

| Fase | Ação |
|------|------|
| Given | Browser limpo |
| When | `goto` login |
| Then | Email visível → screenshot do body |

### Dashboard / Components

| Fase | Ação |
|------|------|
| Given | Sessão autenticada |
| When | `visit_authenticated` na rota |
| Then | Marcador de página presente → screenshot do container |

---

## Conceitos para estudantes

### Por que testes visuais?

- Capturam regressões que testes funcionais não veem (CSS quebrado, overflow, alinhamento).
- Custo: baselines precisam manutenção; ambientes devem ser consistentes (OS, DPI, fonts).

### Estabilização

- Fontes, animações, dados dinâmicos (datas, avatares) são inimigos de snapshot.
- Este projeto mitiga com `_wait_for_fonts` e regiões recortadas.

### PyTest parametrize vs classes separadas

Parametrize escala quando **lógica de assert é idêntica** e só mudam dados/setup.

---

## Checklist de aprendizado

- [ ] Explicar diferença entre snapshot de `body` vs `page-dashboard`
- [ ] Descrever papel de `document.fonts.ready`
- [ ] Executar teste visual e localizar pasta de snapshots gerada
- [ ] Saber quando usar `--update-snapshots`
- [ ] Relacionar `TC.VISUAL_*` com IDs em `support/constants/test_cases.py`
