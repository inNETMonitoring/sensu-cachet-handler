#!/usr/bin/env python
import unittest
import sys

from unittest.mock import patch

# Alter path and import modules
from cachet_publisher.cachet_publisher import CachetHandler

ERROR_RESULT = '''
{
  "id": "ef6b87d2-1f89-439f-8bea-33881436ab90",
  "action": "create",
  "timestamp": 1460172826,
  "occurrences": 2,
  "check": {
    "type": "standard",
    "total_state_change": 11,
    "history": ["0", "0", "1", "1", "2", "2"],
    "status": 2,
    "output": "No keepalive sent from client for 230 seconds (>=180)",
    "executed": 1460172826,
    "issued": 1460172826,
    "name": "keepalive",
    "thresholds": {
      "critical": 180,
      "warning": 120
    }
  },
  "client": {
    "timestamp": 1460172596,
    "version": "1.1.0",
    "socket": {
      "port": 3030,
      "bind": "127.0.0.1"
    },
    "subscriptions": [
      "production"
    ],
    "environment": "development",
    "address": "127.0.0.1",
    "name": "client-01"
  }
}
'''

WARNING_RESULT = '''
{
  "id": "ef6b87d2-1f89-439f-8bea-33881436ab90",
  "action": "create",
  "timestamp": 1460172826,
  "occurrences": 1,
  "check": {
    "type": "standard",
    "total_state_change": 11,
    "history": ["0", "0", "0", "0", "0", "0"],
    "status": 1,
    "output": "No keepalive sent from client for 130 seconds (>=120)",
    "executed": 1460172826,
    "issued": 1460172826,
    "name": "keepalive",
    "thresholds": {
      "critical": 180,
      "warning": 120
    }
  },
  "client": {
    "timestamp": 1460172596,
    "version": "1.1.0",
    "socket": {
      "port": 3030,
      "bind": "127.0.0.1"
    },
    "subscriptions": [
      "production"
    ],
    "environment": "development",
    "address": "127.0.0.1",
    "name": "client-01"
  }
}
'''

OK_RESULT = '''
{
  "id": "ef6b87d2-1f89-439f-8bea-33881436ab90",
  "action": "create",
  "timestamp": 1460172826,
  "occurrences": 1,
  "check": {
    "type": "standard",
    "total_state_change": 11,
    "history": ["0", "0", "1", "1", "2", "2"],
    "status": 0,
    "output": "No keepalive sent from client for 130 seconds (>=120)",
    "executed": 1460172826,
    "issued": 1460172826,
    "name": "keepalive",
    "thresholds": {
      "critical": 180,
      "warning": 120
    }
  },
  "client": {
    "timestamp": 1460172596,
    "version": "1.1.0",
    "socket": {
      "port": 3030,
      "bind": "127.0.0.1"
    },
    "subscriptions": [
      "production"
    ],
    "environment": "development",
    "address": "127.0.0.1",
    "name": "client-01"
  }
}
'''


class IncidentMock:
    def __init__(self, incident_id, name, message):
        self._id = incident_id
        self._name = name
        self._message = message

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def message(self):
        return self._message


class TestCachetPublisher(unittest.TestCase):
    def setUp(self) -> None:
        '''
        Instantiate a fresh SensuHandler before each test.
        '''
        self.cachet_handler = CachetHandler(autorun=False)

    def test_error(self):
        '''
        Tests the run method.
        '''

        # event should be valid json
        with patch('sensu_plugin.handler.sys.stdin') as mocked_stdin, \
                patch.object(sys, "argv", ["cachet_publisher.py", "-u", "https://my.status.io/v1",
                                            "-t", "api-key", "-i", "10"]), \
                patch.object(self.cachet_handler, "_CachetHandler__update_status", return_value=None) as updater, \
                patch.object(self.cachet_handler, "_CachetHandler__has_active_issue", return_value=None):

            mocked_stdin.read = lambda: ERROR_RESULT
            self.cachet_handler.run()
            assert updater.call_args == ((10, 4), )

    def test_warning(self):
        '''
        Tests the run method.
        '''

        # event should be valid json
        with patch('sensu_plugin.handler.sys.stdin') as mocked_stdin, \
                patch.object(sys, "argv", ["cachet_publisher.py", "-u", "https://my.status.io/v1",
                                            "-t", "api-key", "-i", "11"]), \
                patch.object(self.cachet_handler, "_CachetHandler__update_status", return_value=None) as updater, \
                patch.object(self.cachet_handler, "_CachetHandler__has_active_issue", return_value=None):

            mocked_stdin.read = lambda: WARNING_RESULT
            self.cachet_handler.run()
            assert updater.call_args == ((11, 2), )

    def test_custom_levels(self):
        '''
        Tests the run method.
        '''

        # event should be valid json
        with patch('sensu_plugin.handler.sys.stdin') as mocked_stdin, \
                patch.object(sys, "argv", ["cachet_publisher.py", "-u", "https://my.status.io/v1",
                                           "-t", "api-key", "-i", "10", "--warning-code", "3", "--error-code", "3"]), \
                patch.object(self.cachet_handler, "_CachetHandler__update_status", return_value=None) as updater, \
                patch.object(self.cachet_handler, "_CachetHandler__has_active_issue", return_value=None):

            mocked_stdin.read = lambda: WARNING_RESULT
            self.cachet_handler.run()
            assert updater.call_args == ((10, 3), )

            mocked_stdin.read = lambda: ERROR_RESULT
            self.cachet_handler.run()
            assert updater.call_args == ((10, 3), )

    def test_create_issue(self):
        with patch('sensu_plugin.handler.sys.stdin') as mocked_stdin, \
                patch.object(sys, "argv", ["cachet_publisher.py", "-u", "https://status.innet.io/api/v1",
                                           "-t", "1BlxhjbyeD9sOdIBBO57", "-i", "10", "--create-incident",
                                           "--incident-message", "test", "--incident-title", "test"]), \
                patch.object(self.cachet_handler, "_CachetHandler__update_status", return_value=None):

            with patch.object(self.cachet_handler, "_CachetHandler__has_active_issue", return_value=None), \
                    patch.object(self.cachet_handler, "_CachetHandler__create_incident", return_value=None) \
                    as incident_hdl:

                mocked_stdin.read = lambda: ERROR_RESULT
                self.cachet_handler.run()
                assert incident_hdl.call_args == ((10, "test", "test", 4), )

            incident = IncidentMock(42, "test", "test")
            with patch.object(self.cachet_handler, "_CachetHandler__has_active_issue",
                              return_value=incident), \
                    patch.object(self.cachet_handler, "_CachetHandler__resolve_incident", return_value=None) \
                    as incident_hdl:

                mocked_stdin.read = lambda: OK_RESULT
                self.cachet_handler.run()
                assert incident_hdl.call_args == ((incident, 4, "Incident was resolved"), )
