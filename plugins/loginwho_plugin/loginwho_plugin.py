# -*- coding: UTF-8 -*-
from base_plugin import BasePlugin


class LoginWhoPlugin(BasePlugin):
    """
    Displays a /who upon login
    """
    name = 'loginwho_plugin'
    depends = ['command_plugin', 'admin_commands_plugin']

    def activate(self):
        super(LoginWhoPlugin, self).activate()
        self.user_commands = self.plugins['admin_commands_plugin']

    def after_connect_success(self, data):
        self.user_commands.who(data)
