from guardas.alcance_pr import errores_alcance


def test_un_departamento_con_su_workflow_pasa():
    rutas = ["lecciones/fases.yaml", ".github/workflows/lecciones.yml"]
    assert errores_alcance(rutas, autor="jair") == []


def test_dos_departamentos_falla():
    errores = errores_alcance(["lecciones/a.mdx", "sitio/b.ts"], autor="jair")
    assert errores and "lecciones" in errores[0] and "sitio" in errores[0]


def test_contratos_con_otro_falla():
    assert errores_alcance(["contratos/a.json", "lecciones/b.mdx"], autor="jair")


def test_sin_cambios_pasa():
    assert errores_alcance([], autor="jair") == []


def test_dependabot_solo_workflows_pasa():
    rutas = [".github/workflows/sitio.yml", ".github/workflows/lecciones.yml"]
    assert errores_alcance(rutas, autor="dependabot[bot]") == []


def test_dependabot_con_otros_archivos_falla():
    rutas = ["sitio/package.json", ".github/workflows/lecciones.yml"]
    assert errores_alcance(rutas, autor="dependabot[bot]")
