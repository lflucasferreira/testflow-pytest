# PyTest — Perguntas Técnicas para Entrevistas

> Banco de perguntas para entrevistas com recrutadores técnicos, QA leads, SDETs e engenheiros de software.  
> Cobertura baseada no conteúdo dos slides (`slides/index.html`) + tópicos frequentes em empresas brasileiras e internacionais.  
> **Legenda:** `[SLIDE]` = abordado na apresentação · `[EXTRA]` = comum em entrevistas, fora dos slides.

---

## Índice

1. [Conceitos Fundamentais](#1-conceitos-fundamentais)
2. [PyTest + Playwright — Arquitetura](#2-pytest--playwright--arquitetura)
3. [Instalação e Configuração](#3-instalação-e-configuração)
4. [Estrutura de Projeto e Organização](#4-estrutura-de-projeto-e-organização)
5. [Fixtures e conftest.py](#5-fixtures-e-conftestpy)
6. [Markers, Parametrize e Seleção de Testes](#6-markers-parametrize-e-seleção-de-testes)
7. [CLI, Flags e Execução](#7-cli-flags-e-execução)
8. [Playwright — Locators e Interações](#8-playwright--locators-e-interações)
9. [Assertions — assert vs expect()](#9-assertions--assert-vs-expect)
10. [API Testing com pytest-playwright](#10-api-testing-com-pytest-playwright)
11. [Page Object Model (POM)](#11-page-object-model-pom)
12. [Fixtures, Factories e Dados de Teste](#12-fixtures-factories-e-dados-de-teste)
13. [Autenticação e Sessão](#13-autenticação-e-sessão)
14. [Mock, Route e Spy na UI](#14-mock-route-e-spy-na-ui)
15. [Visual Regression](#15-visual-regression)
16. [Acessibilidade](#16-acessibilidade)
17. [CI/CD e Multi-ambiente](#17-cicd-e-multi-ambiente)
18. [Plugins e Ecossistema Python](#18-plugins-e-ecossistema-python)
19. [Flakiness, Debugging e Estabilidade](#19-flakiness-debugging-e-estabilidade)
20. [Comparações com Outras Ferramentas](#20-comparações-com-outras-ferramentas)
21. [Padrões Avançados e Enterprise](#21-padrões-avançados-e-enterprise)
22. [Segurança e Boas Práticas](#22-segurança-e-boas-práticas)
23. [Python para QAs e SDETs](#23-python-para-qas-e-sdets)
24. [Cenários Comportamentais e Situação-Problema](#24-cenários-comportamentais-e-situação-problema)
25. [Perguntas de Recrutador / Screening](#25-perguntas-de-recrutador--screening)

---

## 1. Conceitos Fundamentais

| # | Pergunta | Tag |
|---|----------|-----|
| 1.1 | O que é o PyTest e por que ele é popular em projetos Python? | `[SLIDE]` |
| 1.2 | Quais são as convenções de descoberta de testes (`test_*.py`, `Test*`, `test_*`)? | `[SLIDE]` |
| 1.3 | Qual a diferença entre PyTest e o módulo `unittest` da stdlib? | `[EXTRA]` |
| 1.4 | O PyTest substitui testes unitários? Quando usar PyTest puro vs PyTest + Playwright? | `[SLIDE]` `[EXTRA]` |
| 1.5 | Por que este projeto combina PyTest com Playwright em vez de usar só `requests` + Selenium? | `[SLIDE]` |
| 1.6 | O que é assert introspection do PyTest e por que ajuda QAs? | `[SLIDE]` |
| 1.7 | Qual a diferença entre teste E2E, teste de API e teste de contrato neste repositório? | `[SLIDE]` |
| 1.8 | O PyTest é só para backend ou também serve para automação de UI? | `[SLIDE]` |
| 1.9 | O que significa "PyTest orquestra, Playwright executa" no testflow-pytest? | `[SLIDE]` |
| 1.10 | Qual a relação deste projeto com `testflow-cypress` e `testflow-playwright`? | `[SLIDE]` |
| 1.11 | PyTest suporta testes assíncronos nativamente? Como isso se relaciona com Playwright async? | `[EXTRA]` |
| 1.12 | O que é a pirâmide de testes e onde encaixam E2E, API e unitários? | `[EXTRA]` |
| 1.13 | Quando faz sentido escolher Python/PyTest em vez de TypeScript/Cypress ou Playwright TS? | `[SLIDE]` `[EXTRA]` |
| 1.14 | O PyTest é framework de teste ou runner + ecossistema de plugins? | `[EXTRA]` |
| 1.15 | Como o PyTest reporta falhas de forma diferente do JUnit/Nose? | `[EXTRA]` |

---

## 2. PyTest + Playwright — Arquitetura

| # | Pergunta | Tag |
|---|----------|-----|
| 2.1 | Como o plugin `pytest-playwright` injeta fixtures `page`, `context` e `browser`? | `[SLIDE]` `[EXTRA]` |
| 2.2 | Qual a diferença entre `page` (UI) e `api_request` (HTTP) no mesmo projeto? | `[SLIDE]` |
| 2.3 | Por que `api_request` usa `playwright.request.new_context()` e não `requests`/`httpx`? | `[SLIDE]` `[EXTRA]` |
| 2.4 | O Playwright Python usa CDP — qual a implicação para estabilidade vs Selenium WebDriver? | `[EXTRA]` |
| 2.5 | Sync vs async Playwright — este projeto usa qual e por quê? | `[EXTRA]` |
| 2.6 | Como funciona o auto-wait do Playwright em comparação com waits explícitos? | `[SLIDE]` |
| 2.7 | O que acontece se você usar `assert` puro logo após `page.click()` sem `expect()`? | `[SLIDE]` `[EXTRA]` |
| 2.8 | Qual o papel do `base_url` do `pytest.ini` nas fixtures do pytest-playwright? | `[SLIDE]` |
| 2.9 | Como traces e screenshots são gerados em falha (`--tracing`, `--screenshot`)? | `[SLIDE]` |
| 2.10 | Por que cada teste recebe um `page` novo por padrão (isolamento)? | `[EXTRA]` |
| 2.11 | O que é `browser_name` nos testes parametrizados do pytest-playwright? | `[EXTRA]` |
| 2.12 | Como o PyTest coleta e executa testes em paralelo com `pytest-xdist` vs workers do Playwright? | `[SLIDE]` `[EXTRA]` |
| 2.13 | Quais browsers o Playwright Python suporta oficialmente? | `[EXTRA]` |
| 2.14 | O Playwright roda headless por padrão — qual impacto no CI? | `[SLIDE]` |

---

## 3. Instalação e Configuração

| # | Pergunta | Tag |
|---|----------|-----|
| 3.1 | Quais são os pré-requisitos do testflow-pytest (Python, venv, TestFlow :5050)? | `[SLIDE]` |
| 3.2 | Por que é necessário `playwright install chromium` além do `pip install`? | `[SLIDE]` |
| 3.3 | Como resolver erro de certificado SSL (Zscaler) ao instalar browsers? | `[SLIDE]` |
| 3.4 | O que faz `pytest.ini` vs `conftest.py` vs `support/config.py`? | `[SLIDE]` |
| 3.5 | Para que serve `base_url = http://localhost:5050` no `pytest.ini`? | `[SLIDE]` |
| 3.6 | O que faz `--strict-markers` e `--strict-config`? | `[SLIDE]` `[EXTRA]` |
| 3.7 | Como configurar markers customizados (`smoke`, `regression`, `api`, `visual`, `a11y`)? | `[SLIDE]` |
| 3.8 | Quais `addopts` padrão este projeto usa e por quê (`-ra`, `--browser chromium`)? | `[SLIDE]` |
| 3.9 | Como passar variáveis de ambiente (`BASE_URL`, `DEMO_PASSWORD`) sem hardcode? | `[SLIDE]` |
| 3.10 | Qual a diferença entre defaults em `support/config.py` e secrets no CI? | `[SLIDE]` |
| 3.11 | Como configurar múltiplos ambientes (local, staging, CI) com a mesma suíte? | `[SLIDE]` `[EXTRA]` |
| 3.12 | O que é `pythonpath` no pytest e quando adicioná-lo? | `[EXTRA]` |
| 3.13 | Como usar `pyproject.toml` em vez de `pytest.ini`? | `[EXTRA]` |
| 3.14 | Como configurar timeout global de teste com `pytest-timeout`? | `[EXTRA]` |
| 3.15 | Como definir `--headed` vs headless por ambiente (local vs CI)? | `[SLIDE]` |
| 3.16 | O que faz `PLAYWRIGHT_BROWSERS_PATH` e quando exportá-lo? | `[EXTRA]` |

---

## 4. Estrutura de Projeto e Organização

| # | Pergunta | Tag |
|---|----------|-----|
| 4.1 | Descreva a estrutura de pastas do testflow-pytest (`tests/`, `pages/`, `support/`, `fixtures/`). | `[SLIDE]` |
| 4.2 | Por que Page Objects ficam em `pages/` e não dentro de `tests/`? | `[SLIDE]` |
| 4.3 | Qual a diferença entre `support/helpers/` e `support/factories/`? | `[SLIDE]` |
| 4.4 | Onde ficam schemas JSON de contrato REST? | `[SLIDE]` |
| 4.5 | Como organizar specs por feature (`auth/`, `dashboard/`, `api/`) vs por tipo (smoke)? | `[SLIDE]` |
| 4.6 | Um arquivo `test_*.py` deve cobrir uma feature ou múltiplas? Justifique. | `[SLIDE]` `[EXTRA]` |
| 4.7 | Por que usar classes `Test*` em vez de funções soltas? | `[SLIDE]` `[EXTRA]` |
| 4.8 | Como separar constantes (`TC-xxxx`, HTTP status) em `support/constants/`? | `[SLIDE]` |
| 4.9 | Como versionar credenciais demo sem commitar secrets reais? | `[SLIDE]` `[EXTRA]` |
| 4.10 | Como estruturar testes API e E2E na mesma base sem acoplamento? | `[SLIDE]` |
| 4.11 | Onde colocar helpers de visual regression (`support/helpers/visual.py`)? | `[SLIDE]` |
| 4.12 | Como organizar monorepo com múltiplos serviços Python testados por PyTest? | `[EXTRA]` |
| 4.13 | Qual convenção de nomes para arquivos de snapshot visual? | `[SLIDE]` |
| 4.14 | Como documentar testes com walkthroughs em `docs/pt/` e `docs/en/`? | `[SLIDE]` |

---

## 5. Fixtures e conftest.py

| # | Pergunta | Tag |
|---|----------|-----|
| 5.1 | O que são fixtures no PyTest e como funcionam como injeção de dependência? | `[SLIDE]` |
| 5.2 | Explique os scopes: `function`, `class`, `module`, `session`. | `[SLIDE]` |
| 5.3 | Quando usar `scope="session"` para `cache_auth_token`? | `[SLIDE]` |
| 5.4 | O que faz `autouse=True` e quando usar com cuidado? | `[SLIDE]` |
| 5.5 | Como funciona `yield` em fixtures para teardown? | `[SLIDE]` |
| 5.6 | Por que `api_request` faz `ctx.dispose()` no teardown? | `[SLIDE]` |
| 5.7 | Como a hierarquia de `conftest.py` (raiz vs subpastas) afeta visibilidade? | `[SLIDE]` |
| 5.8 | Qual a diferença entre fixture global e fixture local no arquivo de teste? | `[SLIDE]` |
| 5.9 | Como compartilhar setup de dashboard com `setup_dashboard` autouse por módulo? | `[SLIDE]` |
| 5.10 | O que é `scope="class"` em `valid_login_response` e qual ganho de performance? | `[SLIDE]` |
| 5.11 | Como resolver dependência circular entre fixtures? | `[EXTRA]` |
| 5.12 | O que é `pytest.fixture` vs `@pytest.fixture(scope="module")` para dados pesados? | `[SLIDE]` `[EXTRA]` |
| 5.13 | Como usar `request` fixture para parametrizar fixtures dinamicamente? | `[EXTRA]` |
| 5.14 | O que é `pytest.fixture(autouse=True)` vs `@pytest.mark.usefixtures`? | `[EXTRA]` |
| 5.15 | Como limpar estado entre testes sem vazar dados de sessão? | `[SLIDE]` `[EXTRA]` |
| 5.16 | Fixtures podem retornar generators, context managers ou callables? | `[EXTRA]` |
| 5.17 | O que acontece se uma fixture session falhar no início da suíte? | `[EXTRA]` |
| 5.18 | Como testar a própria fixture (meta-testing)? | `[EXTRA]` |

---

## 6. Markers, Parametrize e Seleção de Testes

| # | Pergunta | Tag |
|---|----------|-----|
| 6.1 | O que são markers e como filtrar com `pytest -m smoke`? | `[SLIDE]` |
| 6.2 | Como combinar markers: `pytest -m "regression and api"`? | `[SLIDE]` |
| 6.3 | Qual a diferença entre `pytestmark = pytest.mark.regression` e marker no método? | `[SLIDE]` |
| 6.4 | Markers em classe propagam para métodos filhos? | `[SLIDE]` |
| 6.5 | O que faz `@pytest.mark.parametrize` e quando preferir a múltiplos testes? | `[SLIDE]` |
| 6.6 | Para que serve `ids=` em parametrize (evitar `[case0]`, `[case1]`)? | `[SLIDE]` |
| 6.7 | Como parametrizar classes inteiras (`TestQuickAccessNavigation`)? | `[SLIDE]` |
| 6.8 | O que é node id e como executar um teste específico (`::TestKpiCards::test_...`)? | `[SLIDE]` |
| 6.9 | Como selecionar testes por expressão `-k "login and not api"`? | `[SLIDE]` |
| 6.10 | Qual a diferença entre `@pytest.mark.skip`, `skipif` e `xfail`? | `[SLIDE]` |
| 6.11 | Quando documentar bug conhecido com `xfail` vs abrir issue e corrigir? | `[SLIDE]` `[EXTRA]` |
| 6.12 | Como registrar markers em `pytest_configure` vs `pytest.ini`? | `[SLIDE]` |
| 6.13 | O que é `@pytest.mark.parametrize` indireto com `pytest_generate_tests`? | `[EXTRA]` |
| 6.14 | Como evitar combinação explosiva de parametrização (cartesian product)? | `[EXTRA]` |
| 6.15 | Como rodar só testes que falharam (`--lf`) ou failed-first (`--ff`)? | `[SLIDE]` |
| 6.16 | O que faz `--collect-only` e quando usar antes do CI? | `[SLIDE]` |
| 6.17 | Como criar marker customizado `critical` para gate de release? | `[SLIDE]` |

---

## 7. CLI, Flags e Execução

| # | Pergunta | Tag |
|---|----------|-----|
| 7.1 | Qual a diferença entre `-v`, `-vv` e `-q`? | `[SLIDE]` |
| 7.2 | Para que serve `-s` (desligar capture de stdout)? | `[SLIDE]` |
| 7.3 | O que faz `-x` (fail-fast) e `--maxfail=N`? | `[SLIDE]` |
| 7.4 | Como controlar traceback com `--tb=short`, `long`, `no`? | `[SLIDE]` |
| 7.5 | O que significa `-ra` no `addopts`? | `[SLIDE]` |
| 7.6 | Como executar suíte completa vs pasta vs arquivo vs método? | `[SLIDE]` |
| 7.7 | Como rodar testes em paralelo com `pytest -n auto` (xdist)? | `[SLIDE]` |
| 7.8 | Quais cuidados ao paralelizar testes E2E com estado compartilhado? | `[EXTRA]` |
| 7.9 | Como debugar com `--pdb` no ponto de falha? | `[SLIDE]` |
| 7.10 | Como suprimir warnings com `-W ignore::DeprecationWarning`? | `[SLIDE]` |
| 7.11 | Como gerar report JUnit XML com `--junitxml` para CI? | `[EXTRA]` |
| 7.12 | Como usar `--headed` para ver browser durante debug local? | `[SLIDE]` |
| 7.13 | Como passar opções customizadas (`--update-snapshots`) via `pytest_addoption`? | `[SLIDE]` |
| 7.14 | O que é exit code do PyTest e como pipelines usam isso como gate? | `[EXTRA]` |
| 7.15 | Como reexecutar subset da suíte por marker + diretório? | `[SLIDE]` |

---

## 8. Playwright — Locators e Interações

| # | Pergunta | Tag |
|---|----------|-----|
| 8.1 | Por que usar `page.get_by_test_id()` com `data-testid`? | `[SLIDE]` |
| 8.2 | Quando preferir `get_by_role` vs `get_by_test_id` vs `get_by_text`? | `[SLIDE]` `[EXTRA]` |
| 8.3 | Como encadear locators com `.locator()` para tabelas e listas? | `[SLIDE]` |
| 8.4 | Para que serve `.nth(i)` em listas dinâmicas? | `[SLIDE]` |
| 8.5 | Como navegar com `page.goto(path)` usando `base_url` relativo? | `[SLIDE]` |
| 8.6 | Como preencher, limpar e submeter formulários (`.fill`, `.clear`, `.click`)? | `[SLIDE]` |
| 8.7 | Como interagir com `<select>` via `.select_option()`? | `[SLIDE]` |
| 8.8 | Quando usar `.check()` / `.uncheck()` vs `.click()` em checkbox? | `[SLIDE]` |
| 8.9 | Como fechar modal com `page.keyboard.press("Escape")`? | `[SLIDE]` |
| 8.10 | Quando usar `.click(force=True)` e quais os riscos? | `[SLIDE]` `[EXTRA]` |
| 8.11 | Como ler valores de KPI com `.inner_text()`? | `[SLIDE]` |
| 8.12 | Como inspecionar `sessionStorage` com `page.evaluate()`? | `[SLIDE]` |
| 8.13 | Como injetar token antes do load com `page.add_init_script()`? | `[SLIDE]` |
| 8.14 | Como testar Shadow DOM e iframe (suite `advanced/`)? | `[SLIDE]` `[EXTRA]` |
| 8.15 | Como testar viewport mobile/responsivo no Playwright Python? | `[SLIDE]` `[EXTRA]` |
| 8.16 | Como fazer upload de arquivo com Playwright Python? | `[EXTRA]` |
| 8.17 | Como testar drag-and-drop? | `[EXTRA]` |
| 8.18 | Como lidar com elementos em iframe cross-origin? | `[EXTRA]` |
| 8.19 | Como esperar navegação após click sem `time.sleep()`? | `[SLIDE]` `[EXTRA]` |
| 8.20 | O que é strict mode de locators que resolve para múltiplos elementos? | `[EXTRA]` |

---

## 9. Assertions — assert vs expect()

| # | Pergunta | Tag |
|---|----------|-----|
| 9.1 | Qual a diferença entre `assert` puro do PyTest e `expect()` do Playwright? | `[SLIDE]` |
| 9.2 | Por que `expect(...).to_be_visible()` faz retry automático? | `[SLIDE]` |
| 9.3 | Quando usar `expect(page).to_have_url(...)` vs assert em `page.url`? | `[SLIDE]` |
| 9.4 | Como validar texto parcial com `to_contain_text`? | `[SLIDE]` |
| 9.5 | Como validar contagem de elementos com `to_have_count(n)`? | `[SLIDE]` |
| 9.6 | Como usar regex em `to_have_text(re.compile(...))`? | `[SLIDE]` |
| 9.7 | Como validar atributos HTML com `to_have_attribute`? | `[SLIDE]` |
| 9.8 | Como combinar assert numérico (`assert int(text) > 0`) com expect visual? | `[SLIDE]` |
| 9.9 | Como testar exceções com `pytest.raises`? | `[SLIDE]` |
| 9.10 | Por que `assert` dentro de teste API REST é suficiente para status code? | `[SLIDE]` |
| 9.11 | O que é soft assertion e existe nativamente no PyTest? | `[EXTRA]` |
| 9.12 | Como implementar soft asserts com plugin (`pytest-check`)? | `[EXTRA]` |
| 9.13 | Qual timeout padrão do `expect()` e como configurá-lo? | `[EXTRA]` |
| 9.14 | Como debugar assertion que passa localmente e falha no CI? | `[EXTRA]` |

---

## 10. API Testing com pytest-playwright

| # | Pergunta | Tag |
|---|----------|-----|
| 10.1 | Como usar a fixture `api_request` para GET/POST autenticados? | `[SLIDE]` |
| 10.2 | Como passar Bearer token no header `Authorization`? | `[SLIDE]` |
| 10.3 | O que faz `validate_schema()` com jsonschema? | `[SLIDE]` |
| 10.4 | Onde ficam schemas em `fixtures/schemas/`? | `[SLIDE]` |
| 10.5 | O que é `EXPECT` em `support/constants/http_status.py`? | `[SLIDE]` |
| 10.6 | Como evitar magic numbers em status codes? | `[SLIDE]` |
| 10.7 | O que é JSON Patch (RFC 6902) no rules engine? | `[SLIDE]` |
| 10.8 | Como funciona `patch_user_via_rules()` com `application/json-patch+json`? | `[SLIDE]` |
| 10.9 | O que faz `poll_get_users_field()` para eventual consistency? | `[SLIDE]` |
| 10.10 | Como parametrizar casos de PATCH com `VALID_PATCH_CASES` e `ids=`? | `[SLIDE]` |
| 10.11 | O que é `expect_same_members()` para golden fixtures? | `[SLIDE]` |
| 10.12 | Como medir duração de request API (`time.monotonic()`)? | `[SLIDE]` |
| 10.13 | Qual a diferença entre testar API com Playwright vs `httpx`/`requests`? | `[EXTRA]` |
| 10.14 | Como testar OAuth client credentials no `before` de API tests? | `[SLIDE]` `[EXTRA]` |
| 10.15 | Como testar respostas 400/401/404 (negative tests)? | `[SLIDE]` `[EXTRA]` |
| 10.16 | Como validar contrato com JSON Schema vs golden file? | `[SLIDE]` |
| 10.17 | Como testar idempotência de PATCH duplicado? | `[SLIDE]` `[EXTRA]` |
| 10.18 | Como usar `Correlation-Id` para rastreabilidade? | `[EXTRA]` |
| 10.19 | Como testar upload multipart com APIRequestContext? | `[EXTRA]` |
| 10.20 | Quando API tests bastam sem cobertura E2E UI? | `[SLIDE]` `[EXTRA]` |

---

## 11. Page Object Model (POM)

| # | Pergunta | Tag |
|---|----------|-----|
| 11.1 | O que é Page Object Model e quais problemas resolve? | `[SLIDE]` |
| 11.2 | O que deve ir no Page Object: locators, ações ou assertions? | `[SLIDE]` `[EXTRA]` |
| 11.3 | Por que retornar `Self` para method chaining (`login_with().should_...`)? | `[SLIDE]` |
| 11.4 | Como estruturar `LoginPage` com métodos granulares vs fluxo composto? | `[SLIDE]` |
| 11.5 | Como o spec fica legível com POM + Given/When/Then? | `[SLIDE]` |
| 11.6 | Como modelar KPIs e modais em `DashboardPage`? | `[SLIDE]` |
| 11.7 | Quais Page Objects existem no TestFlow (Team, Wizard, Activity…)? | `[SLIDE]` |
| 11.8 | POM vs Screenplay Pattern — quando migrar? | `[EXTRA]` |
| 11.9 | Como compartilhar componentes (sidebar, header) entre pages? | `[EXTRA]` |
| 11.10 | Page Object deve herdar de base class comum? | `[EXTRA]` |
| 11.11 | Como testar wizard multi-step com `WizardPage`? | `[SLIDE]` |
| 11.12 | O POM esconde demais a intenção do teste? Argumente a favor e contra. | `[EXTRA]` |
| 11.13 | Como versionar Page Objects quando a UI muda drasticamente? | `[EXTRA]` |

---

## 12. Fixtures, Factories e Dados de Teste

| # | Pergunta | Tag |
|---|----------|-----|
| 12.1 | O que são fixtures JSON em `fixtures/` vs factories dinâmicas? | `[SLIDE]` |
| 12.2 | Como carregar JSON com `read_fixture(name)`? | `[SLIDE]` |
| 12.3 | Quando usar Faker vs dados fixos (`credentials.json`)? | `[SLIDE]` |
| 12.4 | Como organizar fixtures por domínio (`users/`, `lookups/`, `schemas/`)? | `[SLIDE]` |
| 12.5 | O que é `fixtures/api/patch-payloads.json`? | `[SLIDE]` |
| 12.6 | Como evitar PII real em dados de teste? | `[SLIDE]` `[EXTRA]` |
| 12.7 | Como gerar dados dinâmicos em `support/factories/`? | `[SLIDE]` |
| 12.8 | Como resetar estado de dados entre testes? | `[SLIDE]` `[EXTRA]` |
| 12.9 | Como evitar dependência entre testes por dados compartilhados? | `[EXTRA]` |
| 12.10 | Como usar golden files (`golden-roles.json`) para regressão de contrato? | `[SLIDE]` |
| 12.11 | Factory vs Builder pattern para objetos de teste complexos? | `[EXTRA]` |
| 12.12 | Como seedar banco antes de E2E via API helper? | `[EXTRA]` |

---

## 13. Autenticação e Sessão

| # | Pergunta | Tag |
|---|----------|-----|
| 13.1 | O que faz `cache_auth_token` com scope session autouse? | `[SLIDE]` |
| 13.2 | Qual a diferença entre `login_via_api`, `login_via_ui` e `visit_with_token`? | `[SLIDE]` |
| 13.3 | Como `visit_authenticated()` acelera specs que não testam login? | `[SLIDE]` |
| 13.4 | O que é `session_store` e como persiste token em cache? | `[SLIDE]` `[EXTRA]` |
| 13.5 | Como injetar auth via `add_init_script` vs cookies vs localStorage? | `[SLIDE]` `[EXTRA]` |
| 13.6 | Por que login UI fica restrito à suite `auth/` e o resto usa API? | `[SLIDE]` |
| 13.7 | Como testar logout e sessão expirada? | `[SLIDE]` `[EXTRA]` |
| 13.8 | Como testar fluxos MFA/2FA (SettingsPage)? | `[SLIDE]` `[EXTRA]` |
| 13.9 | Como testar SSO/OAuth redirect flows? | `[EXTRA]` |
| 13.10 | O que acontece se token session expira no meio da suíte? | `[EXTRA]` |
| 13.11 | Como isolar auth por worker em execução paralela xdist? | `[EXTRA]` |

---

## 14. Mock, Route e Spy na UI

| # | Pergunta | Tag |
|---|----------|-----|
| 14.1 | O que faz `page.route()` para mock de API na UI? | `[SLIDE]` |
| 14.2 | Como simular empty state em Activity com `route.fulfill()`? | `[SLIDE]` |
| 14.3 | Qual a diferença entre mock (simular resposta) e spy (observar request)? | `[SLIDE]` |
| 14.4 | Como usar `page.expect_request()` para validar POST de login? | `[SLIDE]` |
| 14.5 | Como mockar erro 500 sem alterar backend? | `[SLIDE]` `[EXTRA]` |
| 14.6 | Como interceptar URL com glob `**/api/activity**`? | `[SLIDE]` |
| 14.7 | O route deve ser registrado antes ou depois do `goto`? | `[EXTRA]` |
| 14.8 | Como garantir ordem de múltiplos routes no mesmo fluxo? | `[EXTRA]` |
| 14.9 | Como simular latência de rede no route? | `[EXTRA]` |
| 14.10 | Mock de API na UI pode mascarar bug real — como equilibrar? | `[EXTRA]` |
| 14.11 | Como mockar GraphQL com Playwright route? | `[EXTRA]` |

---

## 15. Visual Regression

| # | Pergunta | Tag |
|---|----------|-----|
| 15.1 | O que são testes visuais no `tests/visual/`? | `[SLIDE]` |
| 15.2 | Por que este projeto usa `assert_locator_screenshot()` com Pillow em vez de `to_have_screenshot`? | `[SLIDE]` `[EXTRA]` |
| 15.3 | Como atualizar baselines com `pytest tests/visual --update-snapshots`? | `[SLIDE]` |
| 15.4 | Onde ficam snapshots (`tests/visual/snapshots/`)? | `[SLIDE]` |
| 15.5 | O que é `max_diff_pixel_ratio` na comparação Pillow? | `[SLIDE]` |
| 15.6 | Por que desabilitar animações (`animations="disabled"`) em screenshot? | `[SLIDE]` `[EXTRA]` |
| 15.7 | Como nomear snapshots por browser (`login-form-chromium.png`)? | `[SLIDE]` |
| 15.8 | Baselines devem ser versionados no Git para CI passar? | `[SLIDE]` `[EXTRA]` |
| 15.9 | Como lidar com diferenças de fonte/rendering entre OS local e CI Linux? | `[EXTRA]` |
| 15.10 | Visual regression vs ferramentas Percy/Applitools — prós e contras? | `[EXTRA]` |
| 15.11 | Como mascarar regiões dinâmicas (timestamp, avatar) em screenshots? | `[EXTRA]` |
| 15.12 | Como integrar marker `@pytest.mark.visual` no pipeline separado? | `[SLIDE]` |

---

## 16. Acessibilidade

| # | Pergunta | Tag |
|---|----------|-----|
| 16.1 | O que faz `check_a11y(page)` com axe-playwright-python? | `[SLIDE]` |
| 16.2 | Quais tags WCAG são validadas (`wcag2a`, `wcag2aa`)? | `[SLIDE]` |
| 16.3 | Por que `color-contrast` está desabilitada no sandbox? | `[SLIDE]` |
| 16.4 | Quando rodar testes `@pytest.mark.a11y` — em todo teste ou smoke dedicado? | `[SLIDE]` `[EXTRA]` |
| 16.5 | Como testar navegação por teclado (Tab, Enter, Escape)? | `[SLIDE]` `[EXTRA]` |
| 16.6 | Qual a diferença entre teste funcional e a11y automatizado? | `[EXTRA]` |
| 16.7 | O que o axe não detecta e precisa de teste manual? | `[EXTRA]` |
| 16.8 | Como configurar regras axe ignoradas por componente? | `[EXTRA]` |
| 16.9 | Como incluir a11y no Definition of Done? | `[EXTRA]` |

---

## 17. CI/CD e Multi-ambiente

| # | Pergunta | Tag |
|---|----------|-----|
| 17.1 | Como o GitHub Actions executa matrix de 12 suites + job smoke? | `[SLIDE]` |
| 17.2 | Como o service container `qaschool/testflow:latest` sobe na porta 5050? | `[SLIDE]` |
| 17.3 | Quais artefatos publicar em falha (traces, screenshots)? | `[SLIDE]` |
| 17.4 | Como cache de venv acelera pipeline? | `[SLIDE]` |
| 17.5 | Como passar `DEMO_PASSWORD` como secret no CI? | `[SLIDE]` |
| 17.6 | Como executar `pytest -m smoke` como gate rápido? | `[SLIDE]` |
| 17.7 | Como rodar job `visual` separado da regression? | `[SLIDE]` |
| 17.8 | Como configurar retries só no CI? | `[EXTRA]` |
| 17.9 | Como paralelizar jobs por suite vs xdist dentro do job? | `[SLIDE]` `[EXTRA]` |
| 17.10 | Como integrar PyTest com GitLab CI / Azure DevOps / Jenkins? | `[EXTRA]` |
| 17.11 | Como bloquear merge se smoke falhar? | `[EXTRA]` |
| 17.12 | Como executar contra staging URL via `BASE_URL`? | `[SLIDE]` |
| 17.13 | Como instalar Chromium no runner CI (`playwright install --with-deps`)? | `[EXTRA]` |
| 17.14 | Como publicar JUnit XML como check status no GitHub? | `[EXTRA]` |

---

## 18. Plugins e Ecossistema Python

| # | Pergunta | Tag |
|---|----------|-----|
| 18.1 | O que faz `pytest-playwright`? | `[SLIDE]` |
| 18.2 | O que faz `pytest-xdist` e quando usar `-n auto`? | `[SLIDE]` |
| 18.3 | Para que serve `jsonschema` neste projeto? | `[SLIDE]` |
| 18.4 | O que é `axe-playwright-python`? | `[SLIDE]` |
| 18.5 | Como Faker é usado em factories? | `[SLIDE]` |
| 18.6 | Para que serve `python-dotenv`? | `[SLIDE]` |
| 18.7 | O que é `pytest-base-url` (plugin relacionado)? | `[EXTRA]` |
| 18.8 | Como usar `pytest-html` para report HTML? | `[EXTRA]` |
| 18.9 | O que é `pytest-cov` e faz sentido em suíte E2E? | `[EXTRA]` |
| 18.10 | Como criar plugin PyTest customizado com hooks? | `[EXTRA]` |
| 18.11 | Quais hooks existem (`pytest_configure`, `pytest_collection_modifyitems`)? | `[SLIDE]` `[EXTRA]` |
| 18.12 | Como integrar Allure com `allure-pytest`? | `[EXTRA]` |
| 18.13 | O que é `pytest-rerunfailures` vs retries do Playwright? | `[EXTRA]` |

---

## 19. Flakiness, Debugging e Estabilidade

| # | Pergunta | Tag |
|---|----------|-----|
| 19.1 | O que é test flakiness e por que E2E é mais suscetível? | `[EXTRA]` |
| 19.2 | Quais causas comuns de flaky tests em PyTest + Playwright? | `[EXTRA]` |
| 19.3 | Por que evitar `time.sleep()` e o que usar no lugar? | `[EXTRA]` |
| 19.4 | Como debugar teste que passa com `--headed` e falha headless? | `[EXTRA]` |
| 19.5 | Como usar trace Playwright (`test-results/`) após falha? | `[SLIDE]` |
| 19.6 | Como usar screenshot `only-on-failure` como evidência? | `[SLIDE]` |
| 19.7 | Como isolar teste flaky com `@pytest.mark.focus` ou `-k` (sem commitar `.only`)? | `[EXTRA]` |
| 19.8 | Retries no CI ajudam ou mascaram bugs reais? | `[EXTRA]` |
| 19.9 | Como estabilizar testes dependentes de data/hora? | `[EXTRA]` |
| 19.10 | Como lidar com race condition entre UI e API assíncrona? | `[SLIDE]` `[EXTRA]` |
| 19.11 | Como investigar "element not visible" ou timeout do expect? | `[EXTRA]` |
| 19.12 | Qual estratégia quando 10% da suíte é flaky antes de release? | `[EXTRA]` |
| 19.13 | Como usar `--pdb` e `-x` juntos para debug local? | `[SLIDE]` |

---

## 20. Comparações com Outras Ferramentas

| # | Pergunta | Tag |
|---|----------|-----|
| 20.1 | PyTest + Playwright vs Cypress — prós e contras para QAs? | `[SLIDE]` `[EXTRA]` |
| 20.2 | PyTest + Playwright vs Playwright Test (TypeScript) — quando Python? | `[SLIDE]` `[EXTRA]` |
| 20.3 | PyTest vs Robot Framework para automação E2E? | `[EXTRA]` |
| 20.4 | Playwright Python vs Selenium + PyTest? | `[EXTRA]` |
| 20.5 | API tests com Playwright vs Postman/Newman vs RestAssured? | `[EXTRA]` |
| 20.6 | PyTest vs Behave (BDD/Gherkin) — integração possível? | `[EXTRA]` |
| 20.7 | É viável manter Cypress, Playwright TS e PyTest espelhados no mesmo produto? | `[SLIDE]` |
| 20.8 | Por que empresas escolhem Python para SDET em times de data/ML? | `[EXTRA]` |

---

## 21. Padrões Avançados e Enterprise

| # | Pergunta | Tag |
|---|----------|-----|
| 21.1 | Como aplicar test isolation com fixtures autouse por módulo? | `[SLIDE]` |
| 21.2 | Como estruturar suíte enterprise com 500+ testes PyTest? | `[EXTRA]` |
| 21.3 | Como decidir o que automatizar primeiro (risk-based testing)? | `[EXTRA]` |
| 21.4 | Como implementar contract testing além de jsonschema manual? | `[EXTRA]` |
| 21.5 | Como versionar breaking changes de API sem quebrar toda suíte? | `[EXTRA]` |
| 21.6 | Como testar feature flags em E2E? | `[EXTRA]` |
| 21.7 | Como estruturar testes para microfrontends? | `[EXTRA]` |
| 21.8 | Como lidar com multi-tenant no mesmo ambiente de teste? | `[EXTRA]` |
| 21.9 | Como mapear `[TC-xxxx]` para Zephyr/Jira/Xray? | `[SLIDE]` |
| 21.10 | Como manter paridade de cobertura entre repos espelhados (Cypress/Playwright/PyTest)? | `[SLIDE]` |
| 21.11 | Um cenário por `test_*` — por que isso importa em escala? | `[SLIDE]` |

---

## 22. Segurança e Boas Práticas

| # | Pergunta | Tag |
|---|----------|-----|
| 22.1 | Como evitar commitar secrets em `fixtures/credentials.json`? | `[SLIDE]` |
| 22.2 | Como gerenciar `DEMO_PASSWORD` e `SERVICE_CLIENT_SECRET` no CI? | `[SLIDE]` |
| 22.3 | É seguro rodar E2E contra produção? | `[EXTRA]` |
| 22.4 | Como sanitizar logs para não expor tokens Bearer? | `[SLIDE]` `[EXTRA]` |
| 22.5 | Quais dados nunca devem ir para fixtures versionadas? | `[EXTRA]` |
| 22.6 | Como auditar dependências Python por vulnerabilidades (`pip-audit`)? | `[EXTRA]` |
| 22.7 | Como usar `.env` local sem commitar (`.gitignore`)? | `[SLIDE]` `[EXTRA]` |

---

## 23. Python para QAs e SDETs

| # | Pergunta | Tag |
|---|----------|-----|
| 23.1 | Quais conceitos Python mínimos para escrever testes PyTest? | `[EXTRA]` |
| 23.2 | O que são type hints (`page: Page`, `-> Self`) e por que usar? | `[SLIDE]` `[EXTRA]` |
| 23.3 | O que é `dataclass` frozen em `HttpStatus`? | `[SLIDE]` `[EXTRA]` |
| 23.4 | Como funciona `import` de módulos do projeto (`from pages.login_page import LoginPage`)? | `[SLIDE]` |
| 23.5 | O que é venv e por que isolar deps do projeto? | `[SLIDE]` |
| 23.6 | Qual diferença entre list/dict comprehension e loops em asserts? | `[EXTRA]` |
| 23.7 | O que é `__init__.py` em pacotes Python? | `[EXTRA]` |
| 23.8 | Como debugar com breakpoint (`breakpoint()`) vs `--pdb`? | `[EXTRA]` |
| 23.9 | O que são f-strings e por que usar em mensagens de assert? | `[EXTRA]` |
| 23.10 | Como ler traceback PyTest e identificar fixture vs teste como origem? | `[EXTRA]` |
| 23.11 | O que é PEP 8 e o quanto importa em código de teste? | `[EXTRA]` |
| 23.12 | Como usar `pathlib.Path` vs strings para paths de fixtures? | `[EXTRA]` |

---

## 24. Cenários Comportamentais e Situação-Problema

> Perguntas abertas frequentes em entrevistas sênior/lead — sem resposta única.

| # | Cenário |
|---|---------|
| 24.1 | Um teste de login passa localmente mas falha no CI com timeout em `expect(page.get_by_test_id("login-submit"))`. Como investiga? |
| 24.2 | O time quer rodar 220 testes E2E em 15 minutos. Qual estratégia com matrix CI + xdist? |
| 24.3 | Baselines visuais passam no Mac e falham no Linux runner. Como estabilizar? |
| 24.4 | Um dev removeu todos os `data-testid`. Como reage e propõe alternativa? |
| 24.5 | Testes de um módulo dependem de estado criado por outro. Como refatorar para isolamento? |
| 24.6 | O PO pede cobertura E2E de 100%. Como negocia escopo risk-based? |
| 24.7 | Você herda suíte PyTest com 40% flakiness. Primeiros 30 dias de ação? |
| 24.8 | Como validar PATCH assíncrono se read API demora até 30s (`poll_get_users_field`)? |
| 24.9 | Dois QAs escreveram Page Objects duplicados para o mesmo modal. Como padronizar? |
| 24.10 | Pipeline quebrou: Chromium não encontrado no runner. Como corrigir? |
| 24.11 | Como introduzir testes API em projeto que só tinha E2E UI? |
| 24.12 | Wizard com 12 steps é difícil de manter. Como simplificar com POM? |
| 24.13 | Mock de activity API está mascarando bug real. Como equilibrar mock vs integração? |
| 24.14 | Como estruturar testes white-label com múltiplos clientes/branding? |
| 24.15 | Mesmo spec precisa rodar em pt/en/es. Qual abordagem com parametrize? |
| 24.16 | Fixture session `cache_auth_token` falha quando API está down. Como degradar gracefully? |
| 24.17 | Como documentar convenções PyTest para onboarding de novos QAs? |
| 24.18 | Time quer migrar de Selenium para Playwright mantendo PyTest. Plano de migração? |
| 24.19 | Como executar só testes afetados por PR (test impact analysis) com PyTest? |
| 24.20 | Playwright Python não tem `to_have_screenshot`. Como implementar visual regression? |

---

## 25. Perguntas de Recrutador / Screening

> Perguntas iniciais de triagem — recrutadores e tech recruiters.

| # | Pergunta |
|---|----------|
| 25.1 | Você já trabalhou com PyTest? Em qual contexto (unit, API, E2E)? |
| 25.2 | Quantos anos de experiência com automação de testes você tem? |
| 25.3 | Qual foi o maior projeto de automação que participou (quantidade de testes, tamanho do time)? |
| 25.4 | Você já integrou PyTest em pipeline CI/CD? Qual ferramenta? |
| 25.5 | Conhece Page Object Model? Já implementou em Python? |
| 25.6 | Qual a diferença entre QA manual, QA automatizador e SDET na sua visão? |
| 25.7 | Você programa em Python? Qual seu nível (1–5)? |
| 25.8 | Já usou Playwright (Python ou TypeScript)? |
| 25.9 | Já escreveu testes de API com validação de schema/contrato? |
| 25.10 | Conhece fixtures do PyTest? Sabe explicar scope session vs function? |
| 25.11 | Como lida com testes instáveis (flaky) no dia a dia? |
| 25.12 | Já trabalhou com BDD (Behave, pytest-bdd, Cucumber)? |
| 25.13 | Tem experiência com Docker em contexto de testes (service containers)? |
| 25.14 | Já usou relatórios JUnit, Allure ou HTML em CI? |
| 25.15 | Qual ferramenta domina além de PyTest (Cypress, Selenium, Postman)? |
| 25.16 | Já mentorou QAs em automação Python? |
| 25.17 | Conhece markers (`pytest -m smoke`)? |
| 25.18 | Já trabalhou com visual regression ou screenshots baseline? |
| 25.19 | Tem certificação ou curso relevante (CTFL, Python, Test Automation)? |
| 25.20 | Por que Python/PyTest para esta vaga em vez de JavaScript/Cypress? |

---

## Estatísticas

| Métrica | Valor |
|---------|-------|
| Total de perguntas | **320+** |
| Cobertas nos slides `[SLIDE]` | ~165 |
| Complementares `[EXTRA]` | ~155 |
| Cenários situacionais | 20 |
| Perguntas de screening | 20 |

---

## Como usar este material

1. **Preparação para entrevista:** escolha 3–5 categorias alinhadas à vaga (ex.: fixtures + API + CI/CD).
2. **Mock interview:** sorteie 10 perguntas de categorias diferentes.
3. **Gap analysis:** marque `[ ]` nas perguntas que não sabe responder e estude os tópicos.
4. **Evolução dos slides:** perguntas `[EXTRA]` são candidatas a novos slides ou guia HTML.

---

## Referências sugeridas para estudo

- [Documentação oficial PyTest](https://docs.pytest.org/en/stable/)
- [Playwright Python](https://playwright.dev/python/docs/intro)
- [pytest-playwright plugin](https://pytest-playwright.readthedocs.io/)
- [JSON Schema validation](https://python-jsonschema.readthedocs.io/)
- Slides do projeto: `docs/slides/index.html`
- Guia completo: `docs/slides/guia-completo.html`
- Walkthroughs: `docs/pt/README.md` · `docs/en/README.md`

---

*Gerado para o projeto TestFlow PyTest — Junho 2026*
