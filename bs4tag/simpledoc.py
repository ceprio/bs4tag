__all__ = ['SimpleDoc']

import re
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Set
from typing import Tuple
from typing import Union
from typing import cast
from bs4 import BeautifulSoup, NavigableString, CData


class DocError(Exception):
    pass


class SimpleDoc(object):

    """
    class generating xml/html documents using context managers

    doc, tag, text = SimpleDoc().tagtext()

    with tag('html'):
        with tag('body', id = 'hello'):
            with tag('h1'):
                text('Hello world!')

    print(doc.getvalue())
    """

    class Tag(object):

        def __init__(self, doc, name, attrs):  # name is the tag name (ex: 'div')
            # type: (SimpleDoc, str, Dict[str, Union[str, int, float]]) -> None

            self.doc = doc
            self.name = name
            self.attrs = attrs
            self.bs4_tag = doc.soup.new_tag(name)

        def  _append(self, *args, **kwargs):
            self.bs4_tag.append(*args, **kwargs)

        def __enter__(self):
            # type: () -> None
            self.parent_tag = self.doc.current_tag
            self.doc.current_tag = self
            self.parent_tag._append(self.bs4_tag)
            # ! self.position = len(self.doc.soup)
            # ! self.doc._append('')  # put paceholder at this position

        def __exit__(self, tpe, value, traceback):
            # type: (Any, Any, Any) -> None
            if value is None:
                if self.attrs:
                    self.bs4_tag.attrs.update(self.attrs)
                #     self.doc.soup[self.position] = "<%s %s>" % (
                #         self.name,
                #         dict_to_attrs(self.attrs),
                #     )
                # else:
                #     self.doc.soup[self.position] = "<%s>" % self.name
                # ! self.doc._append("</%s>" % self.name)
                self.doc.current_tag = self.parent_tag

    class DocumentRoot(object):

        def __init__(self, doc):
            self.doc = doc

        class DocumentRootError(DocError, AttributeError):
            # Raising an AttributeError on __getattr__ instead of just a DocError makes it compatible
            # with the pickle module (some users asked for pickling of SimpleDoc instances).
            # I also keep the DocError from earlier versions to avoid possible compatibility issues
            # with existing code.
            pass

        def  _append(self, *args, **kwargs):
            self.doc.soup.append(*args, **kwargs)

        def __getattr__(self, item):
            # type: (str) -> Any
            raise SimpleDoc.DocumentRoot.DocumentRootError("DocumentRoot here. You can't access anything here.")

    _newline_rgx = re.compile(r'\r?\n')

    def __init__(self, *args, nl2br=False, **kwargs):
        # type: (str, bool) -> None
        r"""
        Initialisation uses the same arguments as Beautifulsoup
        """
        assert "stag_end" not in kwargs, "stag_end not supported by bs4tag (or BS4)"
        self.features = args[1] if 1 < len(args) else kwargs.get('features', None)
        if self.features is None or len(self.features) == 0:
            self.features = "lxml"
        if 1 < len(args):
            args[1] = self.features
        else:
            kwargs['features'] = self.features

        self.soup = BeautifulSoup(*args, **kwargs)
        self.current_tag = self.__class__.DocumentRoot(self)
        self._nl2br = nl2br

    def tag(self, tag_name, *args, **kwargs):
        # type: (str, Tuple[str, Union[str, int, float]], Union[str, int, float]) -> Tag
        """
        opens a HTML/XML tag for use inside a `with` statement
        the tag is closed when leaving the `with` block
        HTML/XML attributes can be supplied as keyword arguments,
        or alternatively as (key, value) pairs.
        The values of the keyword arguments should be strings.
        They are escaped for use as HTML attributes
        (the " character is replaced with &quot;)

        In order to supply a "class" html attributes, you must supply a `klass` keyword
        argument. This is because `class` is a reserved python keyword so you can't use it
        outside of a class definition.

        Example::

            with tag('h1', id = 'main-title'):
                text("Hello world!")

            # <h1 id="main-title">Hello world!</h1> was appended to the document

            with tag('td',
                ('data-search', 'lemon'),
                ('data-order', '1384'),
                id = '16'
            ):
                text('Citrus Limon')

            # you get: <td data-search="lemon" data-order="1384" id="16">Citrus Limon</td>

        """
        return self.__class__.Tag(self, tag_name, _attributes(args, kwargs))

    def text(self, *strgs):
        # type: (str) -> None
        r"""
        appends 0 or more strings to the document
        the strings are escaped for use as text in html documents, that is,
        & becomes &amp;
        < becomes &lt;
        > becomes &gt;

        Example::

            username = 'Max'
            text('Hello ', username, '!') # appends "Hello Max!" to the current node
            text('16 > 4') # appends "16 &gt; 4" to the current node

        New lines ('\n' or '\r\n' sequences) are left intact, unless you have set the
        nl2br option to True when creating the SimpleDoc instance. Then they would be
        replaced with `<br/>` tags option
        of the SimpleDoc constructor as shown in the example below).

        Example::

            >>> doc = SimpleDoc()
            >>> doc.text('pistachio\nice cream')
            >>> doc.getvalue()
            'pistachio\nice cream'

            >>> doc = SimpleDoc(nl2br=True)
            >>> doc.text('pistachio\nice cream')
            >>> doc.getvalue()
            'pistachio<br />ice cream'

            >>> doc = SimpleDoc(nl2br=True)
            >>> doc.text('pistachio\nice cream')
            >>> doc.getvalue()
            'pistachio<br>ice cream'

        """
        for strg in strgs:
            # ! transformed_string = html_escape(strg)
            if self._nl2br:
                strgs = \
                    self.__class__._newline_rgx.split(
                        strg
                    )
                for s in strgs[:-1]:
                    self.current_tag._append(NavigableString(s))
                    self.stag('br')
                self.current_tag._append(NavigableString(strgs[-1]))
            else:
                self.current_tag._append(NavigableString(strg))

    def line(self, tag_name, text_content, *args, **kwargs):
        # type: (str, str, Tuple[str, Union[str, int, float]], Union[str, int, float]) -> None
        """
        Shortcut to write tag nodes that contain only text.
        For example, in order to obtain::

            <h1>The 7 secrets of catchy titles</h1>

        you would write::

            line('h1', 'The 7 secrets of catchy titles')

        which is just a shortcut for::

            with tag('h1'):
                text('The 7 secrets of catchy titles')

        The first argument is the tag name, the second argument
        is the text content of the node.
        The optional arguments after that are interpreted as xml/html
        attributes. in the same way as with the `tag` method.

        Example::

            line('a', 'Who are we?', href = '/about-us.html')

        produces::

            <a href="/about-us.html">Who are we?</a>
        """
        with self.tag(tag_name, *args, **kwargs):
            self.text(text_content)

    def asis(self, *strgs):
        # type: (str) -> None
        """
        appends 0 or more strings to the documents
        contrary to the `text` method, the strings are appended "as is"
        &, < and > are NOT escaped

        Example::

            doc.asis('<!DOCTYPE html>') # appends <!DOCTYPE html> to the document
        """
        for strg in strgs:
            if strg is None:
                raise TypeError("Expected a string, got None instead.")
                # passing None by mistake was frequent enough to justify a check
                # see https://github.com/leforestier/yattag/issues/20
            self.current_tag._append(BeautifulSoup(strg, features=self.features))

    def attr(self, *args, **kwargs):
        # type: (Tuple[str, Union[str, int, float]], Union[str, int, float]) -> None
        """
        sets HTML/XML attribute(s) on the current tag
        HTML/XML attributes are supplied as (key, value) pairs of strings,
        or as keyword arguments.
        The values of the keyword arguments should be strings.
        They are escaped for use as HTML attributes
        (the " character is replaced with &quot;)
        Note that, instead, you can set html/xml attributes by passing them as
        keyword arguments to the `tag` method.

        In order to supply a "class" html attributes, you can either pass
        a ('class', 'my_value') pair, or supply a `klass` keyword argument
        (this is because `class` is a reserved python keyword so you can't use it
        outside of a class definition).

        Examples::

            with tag('h1'):
                text('Welcome!')
                doc.attr(id = 'welcome-message', klass = 'main-title')

            # you get: <h1 id="welcome-message" class="main-title">Welcome!</h1>

            with tag('td'):
                text('Citrus Limon')
                doc.attr(
                    ('data-search', 'lemon'),
                    ('data-order', '1384')
                )


            # you get: <td data-search="lemon" data-order="1384">Citrus Limon</td>

        """
        self.current_tag.attrs.update(_attributes(args, kwargs))

    def data(self, *args, **kwargs):
        # type: (Tuple[str, Union[str, int, float]], Union[str, int, float]) -> None
        """
        sets HTML/XML data attribute(s) on the current tag
        HTML/XML data attributes are supplied as (key, value) pairs of strings,
        or as keyword arguments.
        The values of the keyword arguments should be strings.
        They are escaped for use as HTML attributes
        (the " character is replaced with &quot;)
        Note that, instead, you can set html/xml data attributes by passing them as
        keyword arguments to the `tag` method.

        Examples::

            with tag('h1'):
                text('Welcome!')
                doc.data(msg='welcome-message')

            # you get: <h1 data-msg="welcome-message">Welcome!</h1>

            with tag('td'):
                text('Citrus Limon')
                doc.data(
                    ('search', 'lemon'),
                    ('order', '1384')
                )


            # you get: <td data-search="lemon" data-order="1384">Citrus Limon</td>

        """
        self.attr(
            *(('data-%s' % key, value) for (key, value) in args),
            **dict(('data-%s' % key, value) for (key, value) in kwargs.items())
        )

    def stag(self, tag_name, *args, **kwargs):
        # type: (str, Tuple[str, Union[str, int, float]], Union[str, int, float]) -> None
        """
        appends a self closing tag to the document
        html/xml attributes can be supplied as keyword arguments,
        or alternatively as (key, value) pairs.
        The values of the keyword arguments should be strings.
        They are escaped for use as HTML attributes
        (the " character is replaced with &quot;)

        Example::

            doc.stag('img', src = '/salmon-plays-piano.jpg')
            # appends <img src="/salmon-plays-piano.jpg" /> to the document

        If you want to produce self closing tags without the ending slash (HTML5 style),
        it may not be possible to do under BS4.
        """
        new_tag = self.soup.new_tag(tag_name)
        if args or kwargs:
            new_tag.attrs.update(dict_to_attrs(_attributes(args, kwargs)))
        new_tag.can_be_empty_element = True
        self.current_tag._append(new_tag)

#        return self.__class__.Tag(self, tag_name, _attributes(args, kwargs))

    def cdata(self, strg, safe=False):
        # type: (str, bool) -> None
        """
        appends a CDATA section containing the supplied string

        You don't have to worry about potential ']]>' sequences that would terminate
        the CDATA section. They are replaced with ']]]]><![CDATA[>'.

        If you're sure your string does not contain ']]>', you can pass `safe = True`.
        If you do that, your string won't be searched for ']]>' sequences.
        """
        if safe:
            cdata = CData(strg)
            self.current_tag._append(cdata)
        else:
            strgs = strg.split("]]>")
            l = len(strgs)
            for i, s in enumerate(strgs):
                if i == 0 and l == 1:
                    cdata = CData(s)
                elif i == 0:
                    cdata = CData(f"{s}]]")
                elif i == l - 1:
                    cdata = CData(f">{s}")
                else:
                    cdata = CData(f">{s}]]")
                self.current_tag._append(cdata)

    def getvalue(self):
        # type: () -> str
        """
        returns the whole document as a single string
        """
        return str(self.soup)

    def tagtext(self):
        # type: () -> Tuple[SimpleDoc, Any, Any]
        """
        return a triplet composed of::
            . the document itself
            . its tag method
            . its text method

        Example::

            doc, tag, text = SimpleDoc().tagtext()

            with tag('h1'):
                text('Hello world!')

            print(doc.getvalue()) # prints <h1>Hello world!</h1>
        """

        return self, self.tag, self.text

    def ttl(self):
        # type: () -> Tuple[SimpleDoc, Any, Any, Any]
        """
        returns a quadruplet composed of::
            . the document itself
            . its tag method
            . its text method
            . its line method

        Example::

            doc, tag, text, line = SimpleDoc().ttl()

            with tag('ul', id='grocery-list'):
                line('li', 'Tomato sauce', klass="priority")
                line('li', 'Salt')
                line('li', 'Pepper')

            print(doc.getvalue())
        """
        return self, self.tag, self.text, self.line

    def ttls(self):
        # type: () -> Tuple[Any, Any, Any, Any]
        """
        returns a quadruplet composed of::
            . its tag method
            . its text method
            . its line method
            . its stag method

        Example::

            doc = SimpleDoc()
            tag, text, line, stag = doc.ttls()

            with tag('ul', id='grocery-list'):
                line('li', 'Tomato sauce', klass="priority")
                line('li', 'Salt')
                line('li', 'Pepper')

            print(doc.getvalue())
        """
        return self.tag, self.text, self.line, self.stag

    def add_class(self, *classes):
        # type: (str) -> None
        """
        adds one or many elements to the html "class" attribute of the current tag
        Example::
            user_logged_in = False
            with tag('a', href="/nuclear-device", klass = 'small'):
                if not user_logged_in:
                    doc.add_class('restricted-area')
                text("Our new product")

            print(doc.getvalue())

            # prints <a class="restricted-area small" href="/nuclear-device"></a>
        """
        self._set_classes(
            self._get_classes().union(classes)
        )

    def discard_class(self, *classes):
        # type: (str) -> None
        """
        remove one or many elements from the html "class" attribute of the current
        tag if they are present (do nothing if they are absent)
        """
        self._set_classes(
            self._get_classes().difference(classes)
        )

    def toggle_class(self, elem, active):
        # type: (str, bool) -> None
        """
        if active is a truthy value, ensure elem is present inside the html
        "class" attribute of the current tag, otherwise (if active is falsy)
        ensure elem is absent
        """
        classes = self._get_classes()
        if active:
            classes.add(elem)
        else:
            classes.discard(elem)
        self._set_classes(classes)

    def _get_classes(self):
        # type: () -> Set[str]
        try:
            current_classes = self.current_tag.attrs['class']
        except KeyError:
            return set()
        else:
            return set(current_classes.split())

    def _set_classes(self, classes_set):
        # type: (Set[str]) -> None
        if classes_set:
            self.current_tag.attrs['class'] = ' '.join(classes_set)
        else:
            try:
                del self.current_tag.attrs['class']
            except KeyError:
                pass


def html_escape(s):
    # type: (Union[str, int, float]) -> str
    if isinstance(s, (int, float)):
        return str(s)
    try:
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    except AttributeError:
        raise TypeError(
            "You can only insert a string, an int or a float inside a xml/html text node. "
            "Got %s (type %s) instead." % (repr(s), repr(type(s)))
        )


def attr_escape(s):
    # type: (Union[str, int, float]) -> str
    if isinstance(s, (int, float)):
        return str(s)
    try:
        return s.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")
    except AttributeError:
        raise TypeError(
            "xml/html attributes should be passed as strings, ints or floats. "
            "Got %s (type %s) instead." % (repr(s), repr(type(s)))
        )


ATTR_NO_VALUE = None


def dict_to_attrs(dct):
    # type: (Dict[str, Any]) -> str
    return {key: None if value is ATTR_NO_VALUE
            else attr_escape(value)
            for key, value in dct.items()}
    # return ' '.join(
    #     (key if value is ATTR_NO_VALUE
    #     else '%s="%s"' % (key, attr_escape(value)))
    #     for key, value in dct.items()
    # )


def _attributes(args, kwargs):
    # type: (Any, Any) -> Dict[str, Any]
    lst = []  # type: List[Any]
    for arg in args:
        if isinstance(arg, tuple):
            lst.append(arg)
        elif isinstance(arg, str):
            lst.append((arg, ATTR_NO_VALUE))
        else:
            raise ValueError(
                "Couldn't make a XML or HTML attribute/value pair out of %s."
                % repr(arg)
            )
    result = dict(lst)
    result.update(
        (('class', value) if key == 'klass' else (key, value))
        for key, value in kwargs.items()
    )
    return result
