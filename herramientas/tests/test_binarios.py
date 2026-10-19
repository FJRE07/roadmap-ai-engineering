from guardas.binarios import prohibidos


def test_detecta_pdf_y_epub_sin_importar_mayusculas():
    assert prohibidos(["a/B.PDF", "c.epub", "notas.md"]) == ["a/B.PDF", "c.epub"]
