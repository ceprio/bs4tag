import unittest
from bs4tag import Doc
import xml.etree.ElementTree as ET


class TestDoc(unittest.TestCase):

    def test_select_option(self):
        doc, tag, text = Doc(
            defaults={'ingredient': ['chocolate', 'coffee']}
        ).tagtext()
        with doc.select(name='ingredient', multiple="multiple"):
            for value, description in (
                ("chocolate", "Dark Chocolate"),
                ("almonds", "Roasted almonds"),
                ("honey", "Acacia honey"),
                ("coffee", "Ethiopian coffee")
            ):
                with doc.option(value=value):
                    text(description)
        root = ET.fromstring(doc.getvalue())
        self.assertEqual(root[3].attrib['selected'], 'selected')

    def test_input_text(self):
        doc, tag, text = Doc(
            defaults={'color': 'yellow'},
            errors={'color': 'yellow not available'}
        ).tagtext()
        with tag('body'):
            doc.input('color', ('data-stuff', 'stuff'), type='text')
        root = ET.fromstring(doc.getvalue())
        self.assertEqual(
            root[1].attrib['value'],
            'yellow'
        )
        self.assertEqual(
            root[1].attrib['data-stuff'],
            'stuff'
        )
        self.assertTrue(
            'error' in root[1].attrib['class']
        )

    def test_input_no_slash(self):
        doc = Doc(stag_end='>')
        doc.input('passw', type="password")
        self.assertTrue(
            doc.getvalue() in (
                '<input name="passw" type="password">',
                '<input type="password" name="passw">'
            )
        )

    def test_textarea(self):
        doc, tag, text = Doc(
            defaults={
                'contact_message': 'You just won the lottery!'
            },
            errors={
                'contact_message': 'Your message looks like spam.'
            }
        ).tagtext()
        with tag('p'):
            with doc.textarea(('data-my-data', '12345'), name='contact_message'):
                pass
        root = ET.fromstring(doc.getvalue())
        self.assertEqual(
            root[1].attrib['class'], 'error'
        )
        self.assertEqual(
            root[1].attrib['data-my-data'], '12345'
        )
        self.assertEqual(
            root[1].text,
            'You just won the lottery!'
        )

    def test_input_radio(self):
        doc, tag, text = Doc(defaults={'color': 'red'}).tagtext()
        with tag('body'):
            for color in ('blue', 'red', 'pink', 'yellow', 'ugly-yellow'):
                doc.input(('type', 'radio'), id='color-input', name="color", value=color)
                text(color)
        root = ET.fromstring(doc.getvalue())
        self.assertEqual(
            root[2].attrib['name'], 'color'
        )
        self.assertEqual(
            root[3].attrib['type'], 'radio'
        )
        self.assertEqual(
            root[1].attrib['checked'], 'checked'
        )
        self.assertRaises(
            KeyError, lambda: root[0].attrib['checked']
        )

    def test_file_and_tel_input_types(self):
        doc, tag, text = Doc().tagtext()
        with tag('body'):
            doc.input(name='test', type='file')
            doc.input(name='test2', type='tel')
        root = ET.fromstring(doc.getvalue())
        self.assertEqual(
            root[0].attrib['type'], 'file'
        )
        self.assertEqual(
            root[1].attrib['type'], 'tel'
        )

    def test_file_input_with_default_error(self):
        doc, tag, text = Doc(defaults={"test":'notastreamhandler'}).tagtext()
        with self.assertRaises(Exception) as context:
             doc.input(name='test', type='file')

        self.assertTrue(
            'Default value for HTML form input of type "file" is not supported' in str(context.exception)
        )

    def test_input_checkbox(self):
        doc, tag, text = Doc(defaults={'gift-wrap': 'yes'}).tagtext()
        with tag('body'):
            doc.input('gift-wrap', type='checkbox', value="yes")
        root = ET.fromstring(doc.getvalue())
        self.assertEqual(
            root[0].attrib['checked'], 'checked'
        )

        doc, tag, text = Doc(defaults={'extras': ['fast-shipping', 'gift-wrap']}).tagtext()
        with tag('body'):
            for extra in ('fast-shipping', 'extension-of-warranty', 'gift-wrap'):
                doc.input('extras', type="checkbox", value=extra)
        root = ET.fromstring(doc.getvalue())
        self.assertEqual(
            root[0].attrib['checked'], 'checked'
        )
        self.assertRaises(
            KeyError, lambda: root[1].attrib['checked']
        )
        self.assertEqual(
            root[2].attrib['checked'], 'checked'
        )


if __name__ == '__main__':
    unittest.main()

