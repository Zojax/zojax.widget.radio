##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id$
"""
from zope.i18n import translate
from zope import interface, component
from zope.schema.interfaces import ITitledTokenizedTerm
from zope.component import getMultiAdapter, queryMultiAdapter

from z3c.form.widget import FieldWidget
from z3c.form.browser import select, widget
from z3c.form.interfaces import IFormLayer, IFieldWidget
from zojax.layout.interfaces import IPagelet

from interfaces import ITermItem, IRadioChoice, IRadioWidget


class TermItem(object):
    interface.implements(ITermItem)

    def __init__(self, id, value, token, title, content, selected, description):
        self.id = id
        self.value = value
        self.token = token
        self.title = title
        self.content = content
        self.selected = selected
        self.description = description


class RadioWidget(select.SelectWidget):
    interface.implements(IRadioWidget)

    klass = u'z-listing'

    def update(self):
        super(RadioWidget, self).update()
        widget.addFieldClass(self)

        if getattr(self.field, 'horizontal', False):
            self.klass = 'z-hlisting'

        self.items = []
        #if not self.required :
        #    message = self.noValueMessage
        #    self.items.append({
        #        'id': self.id + '-novalue',
        #        'value': self.noValueToken,
        #        'content': message,
        #        'selected': self.value == []
        #        })

        for count, term in enumerate(self.terms):
            selected = self.isSelected(term)
            id = '%s-%i' % (self.id, count)
            content = term.token
            if ITitledTokenizedTerm.providedBy(term):
                content = translate(
                    term.title, context=self.request, default=term.title)

            item = TermItem(id, term.value, term.token,
                            term.title or unicode(term.value),
                            content, selected, getattr(term, 'description', u''))

            context = getattr(self.form, 'context', None)
            view = queryMultiAdapter(
                (context, self.form, self, item, self.request),
                IPagelet, term.token)
            if view is None:
                view = getMultiAdapter(
                    (context, self.form, self, item, self.request), IPagelet)

            view.update()
            self.items.append(view)


@interface.implementer(IFieldWidget)
@component.adapter(IRadioChoice, IFormLayer)
def RadioWidgetFactory(field, request):
    return FieldWidget(field, RadioWidget(request))
