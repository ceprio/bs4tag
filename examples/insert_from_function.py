from bs4tag import SimpleDoc


def body_text():
    doc, tag, text = SimpleDoc().tagtext()
    with tag('h1'):
        text('Hello world!')
    return doc.soup


doc, tag, text = SimpleDoc().tagtext()

with tag('html'):
    with tag('body', id='hello'):
        pass

doc.soup.find(id='hello').append(body_text())

print(doc.getvalue())

# <html><body id="hello"><h1>Hello world!</h1></body></html>