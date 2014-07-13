#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
This file is part of YAMLDoc.

YAMLDoc is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

YAMLDoc is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with YAMLDoc.  If not, see <http://www.gnu.org/licenses/>.
"""

import re
import types
import inspect
import yaml
from yamldoc._exceptions import YAMLDocError

docTemplate = u"""
<span class="%(className)s YAMLDoc" markdown="1">

%(headerLevel)s %(headerText)s

%(desc)s

%(sections)s
%(misc)s

</span>
"""

class BaseDoc(object):

	"""
	desc:
		The base class from which the other doc classes are derived. You
		don't create a `BaseDoc` object directly, but use the `DocFactory()`
		function to create an object-specific doc object for you.
	visible:
		True
	"""

	undefined = u'No description specified.'

	def __init__(self, obj, enc=u'utf-8', namePrefix=u'', level=1):

		"""
		desc:
			Constructor.

		arguments:
			obj:		The object to document.

		keywords:
			enc:
				desc:	The string encoding.
				type:	[str, unicode]
			namePrefix:
				desc:	A prefix to be pre-pended to the object's name.
				type:	[str, unicode]
			level:
				desc:	Describes the header level to be used, so that you can
						generate formatted documentation.
				type:	int
		"""

		self.obj = obj
		self.enc = enc
		self.level = level
		self.namePrefix = namePrefix

	def __str__(self):

		"""
		desc:
			Returns a string representation of the object's documentation.

		returns:
			desc:	A string representation of the object's documentation.
			type:	str
		"""

		return unicode(self).encode(self.enc)

	def __unicode__(self):

		"""
		desc:
			Returns a unicode string representation of the object's
			documentation.

		returns:
			desc:	A unicode string representation of the object's
					documentation.
			type:	unicode
		"""

		_dict = self._dict()
		if not _dict[u'visible']:
			return u''
		md = docTemplate % {
			u'className' 		: self.__class__.__name__,
			u'headerLevel'		: u'#' * self.level,
			u'headerText'		: self.header(_dict),
			u'desc'				: _dict[u'desc'],
			u'sections'			: self.sections(_dict),
			u'misc'				: self.misc(_dict),
			}
		return md

	def _name(self):

		"""
		desc:
			Returns the object's name without prefix.

		visible:	False

		returns:
			desc:	The object's name without prefix.
			type:	unicode
		"""

		return self.obj.__name__.decode(self.enc)

	def _dict(self):

		"""
		desc:
			Generates a dict representation of the object's documentation.

		returns:
			desc:	A dict representation of the object's documentation.
			type:	dict
		"""

		docStr = inspect.getdoc(self.obj)
		if isinstance(docStr, types.NoneType):
			_dict = {
				u'desc':	self.undefined,
				u'visible':	False
				}
		elif isinstance(docStr, str):
			docStr = docStr.decode(self.enc)
			# If the docstring contains a YAML block between '---' then we
			# use only this bit.
			for r in re.finditer(u'^---(.*?)^---', docStr, re.M|re.S):
				docStr = r.groups()[0]
				break
			try:
				_dict = yaml.load(docStr)
				if isinstance(_dict, str):
					_dict = _dict.decode(self.enc)
				if isinstance(_dict, unicode):
					_dict = {
						u'desc':	_dict,
						u'visible':	False
						}
			except:
				_dict = {
					u'desc':	docStr,
					u'visible':	False
					}
		if u'desc' not in _dict:
			_dict[u'desc'] = self.undefined
		if u'visible' not in _dict:
			_dict[u'visible'] = True
		return _dict

	def objAttribs(self):

		"""
		desc:
			Retrieves all object attributes.

		visible:	False

		returns:
			desc:	A list of (name, object) tuples for all the object's
					attributes.
			type:	list
		"""

		l = []
		for attrib in dir(self.obj):
			# Avoid recursion
			if attrib == u'__class__':
				continue
			if hasattr(self.obj, attrib):
				l.append((attrib, getattr(self.obj, attrib)))
		return l

	def name(self):

		"""
		desc:
			Returns the object's name with prefix.

		returns:
			desc:	The object's name with prefix.
			type:	unicode
		"""

		return self.namePrefix + self._name()

	def header(self, _dict):

		"""
		desc:
			Generates a Markdown header line for the documentation.

		visible:	False

		arguments:
			_dict:
				desc:	A docstring dictionary.
				type:	dict

		returns:
			desc:	A properly formatted header.
			type:	unicode

		"""

		return u''

	def misc(self, _dict):

		"""
		desc:
			Generates miscellaneous documentation, to be added to the end of
			the standard doc sections.

		visible:	False

		arguments:
			_dict:
				desc:	A docstring dictionary.
				type:	dict

		returns:
			desc:	A Markdown-formatted section with miscellaneous
					documentation.
			type:	unicode

		"""

		return u''

	def sections(self, _dict):

		"""
		desc:
			Generates a Markdown description of all the documentation sections,
			such as 'arguments', 'example', etc.

		visible:	False

		arguments:
			_dict:
				desc:	A docstring dictionary.
				type:	dict

		returns:
			desc:	A properly formatted header.
			type:	unicode

		"""

		md = u''
		if u'example' in _dict:
			md += u'__Example:__\n\n' + self.exampleSection(_dict[u'example'])
		return md

	def exampleSection(self, example):

		return u'~~~\n%s\n~~~\n\n' % example.strip()