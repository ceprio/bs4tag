import unittest

if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os.path import abspath, join, dirname
        add_path = abspath(join(dirname(__file__), '..'))
        sys.path.append(add_path)
        from bs4tag import SimpleDoc
    else:
        from ..bs4tag import SimpleDoc


class TestCase_row(unittest.TestCase):

    def test_create_doc(self):
        doc = SimpleDoc()

    def test_asis(self):
        doc = SimpleDoc("<b></b>")
        doc.asis('<!DOCTYPE html>')
        self.assertEqual('<html><body><b></b></body></html><!DOCTYPE html>\n', doc.getvalue())

    def test_tag(self):
        doc = SimpleDoc("")
        tag, text, line, stag = doc.ttls()
        doc.asis('<!DOCTYPE html>')
        with tag('html', lang="en"):
            pass
        self.assertEqual('<!DOCTYPE html>\n<html lang="en"></html>', doc.getvalue())

    def test_text(self):
        doc = SimpleDoc("")
        tag, text, line, stag = doc.ttls()
        doc.asis('<!DOCTYPE html>')
        with tag('html', lang="en"):
            text("/* html content here */")
        self.assertEqual('<!DOCTYPE html>\n<html lang="en">/* html content here */</html>', doc.getvalue())

    def test_stag(self):
        doc = SimpleDoc("<!DOCTYPE html>")
        tag, text, line, stag = doc.ttls()
        with tag('html', lang="en"):
            with tag('head'):
                stag('meta', charset="UTF-8")
                stag('meta', name="viewport", content="width=10, initial-scale=1")
                with tag('style'):
                    pass
        self.assertEqual(
            '<!DOCTYPE html>\n<html lang="en"><head><meta charset="UTF-8"/><meta content="width=10, initial-scale=1" name="viewport"/><style></style></head></html>',
            doc.getvalue()
        )

    def test_line(self):
        doc = SimpleDoc("<!DOCTYPE html>")
        tag, text, line, stag = doc.ttls()
        with tag('div', klass="slides"):
            line('section', 'Slide 1')
        self.assertEqual(
            '<!DOCTYPE html>\n<div class="slides"><section>Slide 1</section></div>',
            doc.getvalue()
        )


if __name__ == '__main__':
    unittest.main()