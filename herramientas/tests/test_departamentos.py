from guardas.departamentos import dueno


def test_dueno_de_carpeta():
    assert dueno("lecciones/fases.yaml") == "lecciones"


def test_dueno_de_workflow_por_nombre():
    assert dueno(".github/workflows/sitio.yml") == "sitio"


def test_dueno_de_workflows_especiales():
    assert dueno(".github/workflows/guardas.yml") == "herramientas"
    assert dueno(".github/workflows/pages.yml") == "sitio"


def test_dueno_de_raiz():
    assert {dueno("README.md"), dueno("docs/x.md"), dueno(".github/dependabot.yml")} == {"raiz"}
