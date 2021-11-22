import unittest
from bs4tag import SimpleDoc
import xml.etree.ElementTree as ET


class TestSimpledoc(unittest.TestCase):

    def test_tag(self):
        doc, tag, text = SimpleDoc().tagtext()
        with tag('h1', id='main-title'):
            with tag('a', href="/"):
                text("Hello world!")
        self.assertEqual(
            doc.getvalue(),
            '<h1 id="main-title"><a href="/">Hello world!</a></h1>'
        )

    def test_asis(self):
        doc = SimpleDoc("<b></b>")
        doc.asis('<!DOCTYPE html>')
        self.assertEqual('<html><body><b></b></body></html><!DOCTYPE html>\n', doc.getvalue())

    def test_attrs(self):
        doc, tag, text = SimpleDoc().tagtext()
        with tag('div', id='article'):
            if True:
                doc.attr(klass='new')
            else:
                doc.attr(klass='old')
            with tag('a', ('data-my-id', '89'), klass='alert'):
                text('hi')
            doc.stag('img', src='squirrel.jpg', klass='animal')

        root = ET.fromstring(doc.getvalue())
        self.assertEqual(root.attrib['class'], "new")
        self.assertEqual(root[0].attrib['class'], "alert")
        self.assertEqual(root[0].attrib['data-my-id'], '89')
        self.assertEqual(root[1].attrib['src'], 'squirrel.jpg')
        self.assertEqual(root[1].attrib['class'], 'animal')
        self.assertRaises(
            KeyError,
            lambda: root[1].attrib['klass']
        )

    def test_attrs_no_value(self):
        doc, tag, text = SimpleDoc().tagtext()
        with tag('paper-button', 'raised'):
            text('I am a fancy button')
        self.assertEqual(
            doc.getvalue(),
            "<paper-button raised>I am a fancy button</paper-button>"
        )

    def test_html_classes(self):

        def class_elems(node):
            return set(node.attrib['class'].split(' '))

        doc, tag, text = SimpleDoc().tagtext()

        with tag('p', klass='news'):
            doc.add_class('highlight', 'today')
            doc.discard_class('news')
            doc.toggle_class('active', True)
            with tag('a', href='/', klass='small useless'):
                doc.discard_class('useless')
            with tag('a', href='/', klass='important'):
                doc.discard_class('important')

        root = ET.fromstring(doc.getvalue())
        self.assertEqual(
            class_elems(root),
            set(['highlight', 'today', 'active'])
        )
        self.assertEqual(
            class_elems(root[0]),
            set(['small'])
        )
        self.assertRaises(KeyError, lambda: class_elems(root[1]))

    def test_cdata(self):
        doc, tag, text = SimpleDoc().tagtext()
        with tag('example'):
            doc.cdata('6 > 8 & 54')
        self.assertEqual(
            doc.getvalue(),
            '<example><![CDATA[6 > 8 & 54]]></example>'
        )

        doc = SimpleDoc()
        doc.cdata('Jean Michel', safe=True)
        self.assertEqual(doc.getvalue(), '<![CDATA[Jean Michel]]>')

        doc = SimpleDoc()
        doc.cdata('A CDATA section should end with ]]>')
        self.assertEqual(
            doc.getvalue(),
            '<![CDATA[A CDATA section should end with ]]]]><![CDATA[>]]>'
        )

        doc = SimpleDoc()
        doc.cdata('Some data ]]><script src="malicious.js">')
        self.assertEqual(
            doc.getvalue(),
            '<![CDATA[Some data ]]]]><![CDATA[><script src="malicious.js">]]>'
        )

    def test_line(self):
        doc, tag, text, line = SimpleDoc().ttl()
        line('h1', 'Some interesting links')
        line('a', "Python's strftime directives", href="http://strftime.org"),
        line('a', "Example of good UX for a homepage", href="http://zombo.com")
        self.assertEqual(
            doc.getvalue(),
            (
                '<h1>Some interesting links</h1>'
                '<a href="http://strftime.org">Python\'s strftime directives</a>'
                '<a href="http://zombo.com">Example of good UX for a homepage</a>'
            )
        )

    def test_stag(self):
        doc = SimpleDoc()
        doc.stag('img', src='/salmon-plays-piano.jpg')
        self.assertEqual(
            doc.getvalue(),
            '<img src="/salmon-plays-piano.jpg"/>'
        )

        # Incompatible with BS4
        # doc = SimpleDoc(stag_end='>')
        # doc.stag('img', src='/salmon-plays-piano.jpg')
        # self.assertEqual(
        #     doc.getvalue(),
        #     '<img src="/salmon-plays-piano.jpg">'
        # )

    def test_text(self):
        message = "Hello\nworld!"

        doc = SimpleDoc()
        doc.text(message)
        self.assertEqual(doc.getvalue(), message)

        doc = SimpleDoc(nl2br=True)
        doc.text(message)
        self.assertEqual(doc.getvalue(), "Hello<br/>world!")

        # doc = SimpleDoc(nl2br=True, stag_end='>')
        # doc.text(message)
        # self.assertEqual(doc.getvalue(), "Hello<br>world!")

        doc = SimpleDoc(nl2br=True)
        doc.text("\n\n\n")
        self.assertEqual(doc.getvalue(), "<br/><br/><br/>")

        doc = SimpleDoc(nl2br=True)
        doc.text("One\r\nTwo\r\nThree\r\n\r\n")
        self.assertEqual(doc.getvalue(), "One<br/>Two<br/>Three<br/><br/>")

        doc = SimpleDoc()
        doc.text("1 < 2 > 1")
        self.assertEqual(doc.getvalue(), "1 &lt; 2 &gt; 1")

        doc = SimpleDoc()
        doc.text("&")
        self.assertEqual(doc.getvalue(), "&amp;")

    def test_tag2(self):
        doc = SimpleDoc()
        tag, text, line, stag = doc.ttls()
        doc.asis('<!DOCTYPE html>')
        with tag('html', lang="en"):
            pass
        self.assertEqual('<!DOCTYPE html>\n<html lang="en"></html>', doc.getvalue())

    def test_ttls(self):
        doc = SimpleDoc("")
        tag, text, line, stag = doc.ttls()
        doc.asis('<!DOCTYPE html>')
        with tag('html', lang="en"):
            text("/* html content here */")
        self.assertEqual('<!DOCTYPE html>\n<html lang="en">/* html content here */</html>', doc.getvalue())

    def test_stag2(self):
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

    def test_line2(self):
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
