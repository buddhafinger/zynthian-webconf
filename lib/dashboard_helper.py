# -*- coding: utf-8 -*-
#********************************************************************
# ZYNTHIAN PROJECT: Zynthian Web Configurator
#
# Dashboard Handler
#
# Copyright (C) 2020 Fernando Moyano <jofemodo@zynthian.org>
# Copyright (C) 2020 Brian Walton <riban@zynthian.org>
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
import re
import sys
import logging
import tornado.web
from subprocess import check_output, DEVNULL
from distutils import util

sys.path.append(os.environ.get('ZYNTHIAN_UI_DIR'))
import zynconf

#------------------------------------------------------------------------------
# Dashboard Handler
#------------------------------------------------------------------------------

class DashboardHelper():

	def get_git_info(self, path):
		branch = check_output("cd %s; git branch | grep '*'" % path, shell=True).decode()[2:-1]
		gitid = check_output("cd %s; git rev-parse HEAD" % path, shell=True).decode()[:-1]
		return { "branch": branch, "gitid": gitid }


	def get_host_name(self):
		with open("/etc/hostname") as f:
			hostname=f.readline()
			return hostname
		return ""


	def get_os_info(self):
		return check_output("lsb_release -ds", shell=True).decode()


	def get_build_info(self):
		info = {}
		try:
			zynthian_dir = os.environ.get('ZYNTHIAN_DIR',"/zynthian")
			with open(zynthian_dir + "/build_info.txt", 'r') as f:
				rows = f.read().split("\n")
				f.close()
				for row in rows:
					try:
						k,v = row.split(": ")
						info[k] = v
						logging.debug("Build info => {}: {}".format(k,v))
					except:
						pass
		except Exception as e:
			logging.warning("Can't get build info! => {}".format(e))
			info['Timestamp'] = '???'

		return info


	def get_ip(self):
		#out=check_output("hostname -I | cut -f1 -d' '", shell=True).decode()
		out=check_output("hostname -I", shell=True).decode()
		return out


	def get_gpio_expander(self):
		try:
			out=check_output("gpio i2cd", shell=True).decode().split("\n")
			if len(out)>3 and out[3].startswith("20: 20"):
				out2 = check_output("i2cget -y 1 0x20 0x10", shell=True).decode().strip()
				if out2=='0x00':
					return "MCP23008"
				else:
					return "MCP23017"
		except:
			pass
		return "Not detected"


	def get_ram_info(self):
		out=check_output("free -m | grep 'Mem'", shell=True).decode()
		parts=re.split('\s+', out)
		return { 'total': parts[1]+"M", 'used': parts[2]+"M", 'free': parts[3]+"M", 'usage': "{}%".format(int(100*float(parts[2])/float(parts[1]))) }


	def get_temperature(self):
		try:
			return check_output("/opt/vc/bin/vcgencmd measure_temp", shell=True).decode()[5:-3] + "ยบC"
		except:
			return "???"


	def get_volume_info(self, volume='/dev/root'):
		try:
			out=check_output("df -h | grep '{}'".format(volume), shell=True).decode()
			parts=re.split('\s+', out)
			return { 'total': parts[1], 'used': parts[2], 'free': parts[3], 'usage': parts[4] }
		except:
			return { 'total': 'NA', 'used': 'NA', 'free': 'NA', 'usage': 'NA' }


	def get_sd_info(self):
		return self.get_volume_info('/dev/root')


	def get_new_issue_url(self):
		# Get git info
		git_info_zyncoder=self.get_git_info("/zynthian/zyncoder")
		git_info_ui=self.get_git_info("/zynthian/zynthian-ui")
		git_info_sys=self.get_git_info("/zynthian/zynthian-sys")
		git_info_webconf=self.get_git_info("/zynthian/zynthian-webconf")
		git_info_data=self.get_git_info("/zynthian/zynthian-data")

		# Get Memory & SD Card info
		ram_info=self.get_ram_info()
		sd_info=self.get_sd_info()

		return "https://github.com/zynthian/zynthian-issue-tracking/issues/new?body=" + tornado.escape.url_escape("**Describe the bug**\n\nA clear and concise description of what the bug is.\n\n**To Reproduce**\nSteps to reproduce the behaviour:\n1. Go to '...'\n2. Click on '....'\n3. Scroll down to '....'\n4. See error\n\n**Expected behaviour**\nA clear and concise description of what you expected to happen.\n\n**Actual behaviour**\nA clear and concise description of what actally happens.\n\n**Screenshots**\nIf applicable, add screenshots to help explain your problem.\n\n**Hardware**\n- %s\n- Soundcard: %s\n- Display: %s\n- Wiring: %s\n- GPIO Expander: %s\n\n**System**\n- %s\n- Build Date: %s\n- Memory: %s (%s/%s)\n- SD Card: %s (%s/%s)\n\n**Software**\n- zyncoder: %s (%s)\n- zynthian-ui: %s (%s)\n- zynthian-sys: %s (%s)\n- zynthian-data: %s (%s)\n- zynthian-webconf: %s (%s)\n\n**Additional context**\nAdd any other context about the problem here.\n" % (os.environ.get('RBPI_VERSION'), os.environ.get('SOUNDCARD_NAME'), os.environ.get('DISPLAY_NAME'), os.environ.get('ZYNTHIAN_WIRING_LAYOUT'), self.get_gpio_expander(), self.get_os_info(), self.get_build_info()['Timestamp'], ram_info['usage'], ram_info['used'], ram_info['total'], sd_info['usage'], sd_info['used'], sd_info['total'], git_info_zyncoder['branch'], git_info_zyncoder['gitid'][0:7], git_info_ui['branch'], git_info_ui['gitid'][0:7], git_info_sys['branch'], git_info_sys['gitid'][0:7], git_info_data['branch'], git_info_data['gitid'][0:7], git_info_webconf['branch'], git_info_webconf['gitid'][0:7]))


