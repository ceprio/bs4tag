
This library is based on the sources and definitions of yattag with the fondamental difference that BeautifulSoup is used as the html renderer.

Differences between bs4tag and yattag
-------------------------------------

*** At this time, only SimpleDoc has been converted, Doc class is work in progress. ***

- The SimpleDoc/Doc object contains a BeautifulSoup intance in the soup attribute
- asis() and ttls() functions added to SimpleDoc

( tutorial for both libraries: yattag.org_ and BS4_)

Limitations
-----------

- No support for custom indentation (indent)
- stag_end option is not available


Basic example
-------------

Nested html tags, no need to close tags, same as yattag.

.. code:: python

    from bs4tag import Doc

    doc, tag, text = Doc().tagtext()

    with tag('html'):
        with tag('body', id = 'hello'):
            with tag('h1'):
                text('Hello world!')

    print(doc.getvalue())

With BeautifulSoup added functionalities
----------------------------------------

Insert bs4tag document into a BeautifulSoup instance.

.. code:: python

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

Installation
------------

pip3 install bs4tag



This library is compatible with the tutorial on yattag.org_

GitHub repo: https://github.com/ceprio/bs4tag
Derived from: https://github.com/leforestier/yattag

.. _yattag.org: https://www.yattag.org
.. _bs4: https://beautiful-soup-4.readthedocs.io/en/latest/
