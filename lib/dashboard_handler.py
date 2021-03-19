# -*- coding: utf-8 -*-
#********************************************************************
# ZYNTHIAN PROJECT: Zynthian Web Configurator
#
# Dashboard Handler
#
# Copyright (C) 2018 Fernando Moyano <jofemodo@zynthian.org>
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
from collections import OrderedDict
from lib.zynthian_config_handler import ZynthianBasicHandler
from lib.dashboard_helper import DashboardHelper

sys.path.append(os.environ.get('ZYNTHIAN_UI_DIR'))
import zynconf

#------------------------------------------------------------------------------
# Dashboard Handler
#------------------------------------------------------------------------------

class DashboardHandler(ZynthianBasicHandler, DashboardHelper):

	@tornado.web.authenticated
	def get(self):
		# Get git info
		git_info_zyncoder=self.get_git_info("/zynthian/zyncoder")
		git_info_ui=self.get_git_info("/zynthian/zynthian-ui")
		git_info_sys=self.get_git_info("/zynthian/zynthian-sys")
		git_info_webconf=self.get_git_info("/zynthian/zynthian-webconf")
		git_info_data=self.get_git_info("/zynthian/zynthian-data")

		# Get Memory & SD Card info
		ram_info=self.get_ram_info()
		sd_info=self.get_sd_info()

		config=OrderedDict([
			['HARDWARE', {
				#'icon': 'glyphicon glyphicon-wrench',
				'icon': 'glyphicon glyphicon-cog',
				'info': OrderedDict([
					['RBPI_VERSION', {
						'title': os.environ.get('RBPI_VERSION')
					}],
					['SOUNDCARD_NAME', {
						'title': 'Soundcard',
						'value': os.environ.get('SOUNDCARD_NAME'),
						'url': "/hw-audio"
					}],
					['DISPLAY_NAME', {
						'title': 'Display',
						'value': os.environ.get('DISPLAY_NAME'),
						'url': "/hw-display"
					}],
					['WIRING_LAYOUT', {
						'title': 'Wiring',
						'value': os.environ.get('ZYNTHIAN_WIRING_LAYOUT'),
						'url': "/hw-wiring"
					}],
					['GPIO_EXPANDER', {
						'title': 'GPIO Expander',
						'value': self.get_gpio_expander(),
						'url': "/hw-wiring"
					}]
				])
			}],
			['SYSTEM', {
				#'icon': 'glyphicon glyphicon-dashboard',
				'icon': 'glyphicon glyphicon-tasks',
				'info': OrderedDict([
					['OS_INFO', {
						'title': "{}".format(self.get_os_info())
					}],
					['BUILD_DATE', {
						'title': 'Build Date',
						'value': self.get_build_info()['Timestamp'],
					}],
					['RAM', {
						'title': 'Memory',
						'value': "{} ({}/{})".format(ram_info['usage'],ram_info['used'],ram_info['total'])
					}],
					['SD CARD', {
						'title': 'SD Card',
						'value': "{} ({}/{})".format(sd_info['usage'],sd_info['used'],sd_info['total'])
					}],
					['TEMPERATURE', {
						'title': 'Temperature',
						'value': self.get_temperature()
					}]
				])
			}],
			['MIDI', {
				'icon': 'glyphicon glyphicon-music',
				'info': OrderedDict([
					['PROFILE', {
						'title': 'Profile',
						'value': os.path.basename(os.environ.get('ZYNTHIAN_SCRIPT_MIDI_PROFILE',"")),
						'url': "/ui-midi-options"
					}],
					['FINE_TUNING', {
						'title': 'Fine Tuning',
						'value': "{} Hz".format(os.environ.get('ZYNTHIAN_MIDI_FINE_TUNING',"440")),
						'url': "/ui-midi-options"
					}],
					['MASTER_CHANNEL', {
						'title': 'Master Channel',
						'value': self.get_midi_master_chan(),
						'url': "/ui-midi-options"
					}],
					['SINGLE_ACTIVE_CHANNEL', {
						'title': 'Single Active Channel',
						'value': self.bool2onoff(os.environ.get('ZYNTHIAN_MIDI_SINGLE_ACTIVE_CHANNEL','0')),
						'url': "/ui-midi-options"
					}],
					['ZS3_SUBSNAPSHOTS', {
						'title': 'ZS3 SubSnapShots',
						'value': self.bool2onoff(os.environ.get('ZYNTHIAN_MIDI_PROG_CHANGE_ZS3','1')),
						'url': "/ui-midi-options"
					}]
				])
			}],
			['SOFTWARE', {
				'icon': 'glyphicon glyphicon-random',
				'info': OrderedDict([
					['ZYNCODER', {
						'title': 'zyncoder',
						'value': "{} ({})".format(git_info_zyncoder['branch'], git_info_zyncoder['gitid'][0:7]),
						'url': "https://github.com/zynthian/zyncoder/commit/{}".format(git_info_zyncoder['gitid'])
					}],
					['UI', {
						'title': 'zynthian-ui',
						'value': "{} ({})".format(git_info_ui['branch'], git_info_ui['gitid'][0:7]),
						'url': "https://github.com/zynthian/zynthian-ui/commit/{}".format(git_info_ui['gitid'])
					}],
					['SYS', {
						'title': 'zynthian-sys',
						'value': "{} ({})".format(git_info_sys['branch'], git_info_sys['gitid'][0:7]),
						'url': "https://github.com/zynthian/zynthian-sys/commit/{}".format(git_info_sys['gitid'])
					}],
					['DATA', {
						'title': 'zynthian-data',
						'value': "{} ({})".format(git_info_data['branch'], git_info_data['gitid'][0:7]),
						'url': "https://github.com/zynthian/zynthian-data/commit/{}".format(git_info_data['gitid'])
					}],
					['WEBCONF', {
						'title': 'zynthian-webconf',
						'value': "{} ({})".format(git_info_webconf['branch'], git_info_webconf['gitid'][0:7]),
						'url': "https://github.com/zynthian/zynthian-webconf/commit/{}".format(git_info_webconf['gitid'])
					}]
				])
			}],
			['LIBRARY', {
				'icon': 'glyphicon glyphicon-book',
				'info': OrderedDict([
					['SNAPSHOTS', {
						'title': 'Snapshots',
						'value': str(self.get_num_of_files(os.environ.get('ZYNTHIAN_MY_DATA_DIR')+"/snapshots")),
						'url': "/lib-snapshot"
					}],
					['USER_PRESETS', {
						'title': 'User Presets',
						'value': str(self.get_num_of_presets(os.environ.get('ZYNTHIAN_MY_DATA_DIR')+"/presets")),
						'url': "/lib-presets"
					}],
					['USER_SOUNDFONTS', {
						'title': 'User Soundfonts',
						'value': str(self.get_num_of_files(os.environ.get('ZYNTHIAN_MY_DATA_DIR')+"/soundfonts")),
						'url': "/lib-soundfont"
					}],
					['AUDIO_CAPTURES', {
						'title': 'Audio Captures',
						'value': str(self.get_num_of_files(os.environ.get('ZYNTHIAN_MY_DATA_DIR')+"/capture","*.wav")),
						'url': "/lib-captures"
					}],
					['MIDI_CAPTURES', {
						'title': 'MIDI Captures',
						'value': str(self.get_num_of_files(os.environ.get('ZYNTHIAN_MY_DATA_DIR')+"/capture","*.mid")),
						'url': "/lib-captures"
					}]
				])
			}],
			['NETWORK', {
				'icon': 'glyphicon glyphicon-link',
				'info': OrderedDict([
					['HOSTNAME', {
						'title': 'Hostname',
						'value': self.get_host_name(),
						'url': "/sys-security"
					}],
					['WIFI', {
						'title': 'Wifi',
						'value': zynconf.get_current_wifi_mode(),
						'url': "/sys-wifi"
					}],
					['IP', {
						'title': 'IP',
						'value': self.get_ip(),
						'url': "/sys-wifi"
					}],
					['RTPMIDI', {
						'title': 'RTP-MIDI',
						'value': self.bool2onoff(self.is_service_active("jackrtpmidid")),
						'url': "/ui-midi-options"
					}],
					['QMIDINET', {
						'title': 'QMidiNet',
						'value': self.bool2onoff(self.is_service_active("qmidinet")),
						'url': "/ui-midi-options"
					}]
				])
			}]
		])

		media_usb0_info = self.get_media_info('/media/usb0')
		if media_usb0_info:
			config['SYSTEM']['info']['MEDIA_USB0'] = {
				'title': "USB Storage",
				'value': "{} ({}/{})".format(media_usb0_info['usage'],media_usb0_info['used'],media_usb0_info['total']),
				'url': "/lib-captures"
			}

		if self.is_service_active("touchosc2midi"):
			config['NETWORK']['info']['TOUCHOSC'] = {
				'title': 'TouchOSC',
				'value': 'on',
				'url': "/ui-midi-options"
			}

		super().get("dashboard_block.html", "Dashboard", config, None)


	def get_media_info(self, mpath="/media/usb0"):
		try:
			out=check_output("mountpoint '{}'".format(mpath), shell=True).decode()
			if out.startswith("{} is a mountpoint".format(mpath)):
				return self.get_volume_info(mpath)
			else:
				return None
		except Exception as e:
			#logging.error("Can't get info for '{}' => {}".format(mpath,e))
			pass


	def get_num_of_files(self, path, pattern=None):
		if pattern:
			pattern = "-name \"{}\"".format(pattern)
		else:
			pattern = ""
		n=check_output("find {} -type f -follow {} | wc -l".format(path, pattern), shell=True).decode()
		return n


	def get_num_of_presets(self, path):
		# LV2 presets
		n1 = int(check_output("find {}/lv2 -type f -prune -name manifest.ttl | wc -l".format(path), shell=True).decode())
		logging.debug("LV2 presets => {}".format(n1))
		# Pianoteq presets
		n2 = int(check_output("find {}/pianoteq -type f -prune | wc -l".format(path), shell=True).decode())
		logging.debug("Pianoteq presets => {}".format(n2))
		# Puredata presets
		n3 = int(check_output("find {}/puredata/*/* -type d -prune | wc -l".format(path), shell=True, stderr=DEVNULL).decode())
		logging.debug("Puredata presets => {}".format(n3))
		# ZynAddSubFX presets
		n4 = int(check_output("find {}/zynaddsubfx -type f -name *.xiz | wc -l".format(path), shell=True).decode())
		logging.debug("ZynAddSubFX presets => {}".format(n4))
		return n1 + n2 + n3 + n4


	def get_midi_master_chan(self):
		mmc = os.environ.get('ZYNTHIAN_MIDI_MASTER_CHANNEL',"16")
		if int(mmc)==0:
			return "off"
		else:
			return mmc


	def is_service_active(self, service):
		cmd="systemctl is-active %s" % service
		try:
			result=check_output(cmd, shell=True).decode('utf-8','ignore')
		except Exception as e:
			result="ERROR: %s" % e
		#print("Is service "+str(service)+" active? => "+str(result))
		if result.strip()=='active': return True
		else: return False


	@staticmethod
	def bool2onoff(b):
		if (isinstance(b, str) and util.strtobool(b)) or (isinstance(b, bool) and b):
			return "on"
		else:
			return "off"

