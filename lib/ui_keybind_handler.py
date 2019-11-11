# -*- coding: utf-8 -*-
#********************************************************************
# ZYNTHIAN PROJECT: Zynthian Web Configurator
#
# UI Keyboard Binding Handler
#
# Copyright (C) 2019 Brian Walton <brian@riban.co.uk>
#
#********************************************************************
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of
# the License, or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# For a full copy of the GNU General Public License see the LICENSE.txt file.
#
#********************************************************************

import os
import logging
import tornado.web
from collections import OrderedDict

from lib.zynthian_config_handler import ZynthianConfigHandler
from zyngui.zynthian_gui_keybinding import zynthian_gui_keybinding

#------------------------------------------------------------------------------
# UI Configuration
#------------------------------------------------------------------------------

class UiKeybindHandler(ZynthianConfigHandler):

	@tornado.web.authenticated
	def get(self, errors=None):
		zynthian_gui_keybinding.getInstance().load()
		config=OrderedDict([])
		config['UI_KEYBINDINGS'] = zynthian_gui_keybinding.getInstance().map

		self.render("config.html", body="ui_keybind.html", config=config, title="Keyboard Binding", errors=errors)


	@tornado.web.authenticated
	def post(self):
		action = self.get_argument('ZYNTHIAN_KEYBIND_ACTION')
		if action:
			errors = {
				'SAVE_KEYBIND': lambda: self.do_save_keybind(),
			}[action]()
		self.get(errors)

		
	def do_save_keybind(self):
		try:
			postedBindings = tornado.escape.recursive_unicode(self.request.arguments)
			zynthian_gui_keybinding.getInstance().resetModifiers()
			try:
				for cuia, value in postedBindings.items():
					self.update_binding(cuia, value)
			except Exception as e:
				pass
			zynthian_gui_keybinding.getInstance().save()
			super().restart_ui() # TODO Would be better to trigger UI to reload keymap rather than do full restart

		except Exception as e:
			logging.error("Saving keyboard binding failed: %s" % format(e))
			return format(e)


	def update_binding(self, cuia, value):
		cuia_name,cuia_param = cuia.split(':')
		logging.info("Update binding for %s with param %s value %s", cuia_name, cuia_param, value)
		try:
			if cuia_param == "shift":
				zynthian_gui_keybinding.getInstance().map[cuia_name]['modifier'] |= 1
			if cuia_param == "ctrl":
				zynthian_gui_keybinding.getInstance().map[cuia_name]['modifier'] |= 4
			if cuia_param == "alt":
				zynthian_gui_keybinding.getInstance().map[cuia_name]['modifier'] |= 8
			if cuia_param == "caps":
				zynthian_gui_keybinding.getInstance().map[cuia_name]['modifier'] |= 2
			if cuia_param == "keysym":
				zynthian_gui_keybinding.getInstance().map[cuia_name]['keysym'] = value
		except Exception as e:
			logging.error("Failed to set binding %s for %s: %s", cuia_param, cuia_name, format(e))