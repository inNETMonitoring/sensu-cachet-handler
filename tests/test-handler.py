#!/usr/bin/env python
import unittest
import sys

from unittest.mock import patch

# Alter path and import modules
from cachet_publisher.cachet_publisher import CachetHandler

OK_RESULT = '''
{
   "timestamp":1575996938,
   "entity":{
      "entity_class":"proxy",
      "system":{
         "network":{
            "interfaces":null
         }
      },
      "metadata":{
         "name":"test",
         "namespace":"default"
      },
      "sensu_agent_version":""
   },
   "check":{
      "command":"/usr/lib/nagios/plugins/check_http -w 3 -c 10 --ssl -H google.ch",
      "timeout":0,
      "round_robin":false,
      "duration":0.057158899,
      "executed":1575996938,
      "history":[
         {
            "status":0,
            "executed":1575996818
         },
         {
            "status":0,
            "executed":1575996878
         },
         {
            "status":0,
            "executed":1575996938
         }
      ],
      "issued":1575996938,
      "output":"HTTP OK: HTTP/1.1 200 OK - 305 bytes in 0.055 second response time |time=0.054662s;3.000000;10.000000;0.000000 size=305B;;;0n",
      "state":"passing",
      "status":0,
      "total_state_change":0,
      "last_ok":1575996938,
      "occurrences":26,
      "occurrences_watermark":51,
      "output_metric_format":"",
      "output_metric_handlers":null,
      "metadata":{
         "name":"test-check",
         "namespace":"default"
      }
   },
   "metadata":{
      "namespace":"default"
   }
}
'''

WARNING_RESULT = '''
{
   "timestamp":1575996938,
   "entity":{
      "entity_class":"proxy",
      "system":{
         "network":{
            "interfaces":null
         }
      },
      "metadata":{
         "name":"test",
         "namespace":"default"
      },
      "sensu_agent_version":""
   },
   "check":{
      "command":"/usr/lib/nagios/plugins/check_http -w 3 -c 10 --ssl -H google.ch",
      "timeout":0,
      "round_robin":false,
      "duration":0.057158899,
      "executed":1575996938,
      "history":[
         {
            "status":0,
            "executed":1575996818
         },
         {
            "status":0,
            "executed":1575996878
         },
         {
            "status":0,
            "executed":1575996938
         }
      ],
      "issued":1575996938,
      "output":"HTTP OK: HTTP/1.1 200 OK - 305 bytes in 3.2 second response time |time=0.054662s;3.000000;10.000000;0.000000 size=305B;;;0n",
      "state":"passing",
      "status":1,
      "total_state_change":0,
      "last_ok":1575996938,
      "occurrences":26,
      "occurrences_watermark":51,
      "output_metric_format":"",
      "output_metric_handlers":null,
      "metadata":{
         "name":"test-check",
         "namespace":"default"
      }
   },
   "metadata":{
      "namespace":"default"
   }
}
'''

ERROR_RESULT = '''
{
   "timestamp":1575996938,
   "entity":{
      "entity_class":"proxy",
      "system":{
         "network":{
            "interfaces":null
         }
      },
      "metadata":{
         "name":"test",
         "namespace":"default"
      },
      "sensu_agent_version":""
   },
   "check":{
      "command":"/usr/lib/nagios/plugins/check_http -w 3 -c 10 --ssl -H google.ch",
      "timeout":0,
      "round_robin":false,
      "duration":0.057158899,
      "executed":1575996938,
      "history":[
         {
            "status":0,
            "executed":1575996818
         },
         {
            "status":0,
            "executed":1575996878
         },
         {
            "status":0,
            "executed":1575996938
         }
      ],
      "issued":1575996938,
      "output":"HTTP OK: HTTP/1.1 200 OK - 305 bytes in 10.2 second response time |time=0.054662s;3.000000;10.000000;0.000000 size=305B;;;0n",
      "state":"passing",
      "status":2,
      "total_state_change":0,
      "last_ok":1575996938,
      "occurrences":26,
      "occurrences_watermark":51,
      "output_metric_format":"",
      "output_metric_handlers":null,
      "metadata":{
         "name":"test-check",
         "namespace":"default"
      }
   },
   "metadata":{
      "namespace":"default"
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
                patch.object(self.cachet_handler, "_CachetHandler__has_active_issue", return_value=None), \
                patch.object(self.cachet_handler, "_CachetHandler__get_current_state", return_value=1):

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
                patch.object(self.cachet_handler, "_CachetHandler__has_active_issue", return_value=None), \
                patch.object(self.cachet_handler, "_CachetHandler__get_current_state", return_value=1):

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

            # Return 0 for current state in both cases. This makes it easier to test custom error and warning codes
            with patch.object(self.cachet_handler, "_CachetHandler__get_current_state", return_value=1):
                mocked_stdin.read = lambda: WARNING_RESULT
                self.cachet_handler.run()
                assert updater.call_args == ((10, 3), )

                mocked_stdin.read = lambda: ERROR_RESULT
                self.cachet_handler.run()
                assert updater.call_args == ((10, 3), )

    def test_create_issue(self):
        with patch('sensu_plugin.handler.sys.stdin') as mocked_stdin, \
                patch.object(sys, "argv", ["cachet_publisher.py", "-u", "https://my.status.io/v1",
                                           "-t", "api-key", "-i", "10", "--create-incident",
                                           "--incident-message", "test", "--incident-title", "test"]), \
                patch.object(self.cachet_handler, "_CachetHandler__update_status", return_value=None):

            with patch.object(self.cachet_handler, "_CachetHandler__has_active_issue", return_value=None), \
                    patch.object(self.cachet_handler, "_CachetHandler__create_incident", return_value=None) \
                    as incident_hdl, \
                    patch.object(self.cachet_handler, "_CachetHandler__get_current_state", return_value=1):

                mocked_stdin.read = lambda: ERROR_RESULT
                self.cachet_handler.run()
                assert incident_hdl.call_args == ((10, "test", "test", 4), )

            incident = IncidentMock(42, "test", "test")
            with patch.object(self.cachet_handler, "_CachetHandler__has_active_issue",
                              return_value=incident), \
                    patch.object(self.cachet_handler, "_CachetHandler__resolve_incident", return_value=None) \
                    as incident_hdl, \
                    patch.object(self.cachet_handler, "_CachetHandler__get_current_state", return_value=4):

                mocked_stdin.read = lambda: OK_RESULT
                self.cachet_handler.run()
                assert incident_hdl.call_args == ((incident, 4, "Incident was resolved"), )

    def test_no_issue_rewrite(self):
        with patch('sensu_plugin.handler.sys.stdin') as mocked_stdin, \
                patch.object(sys, "argv", ["cachet_publisher.py", "-u", "https://my.status.io/v1",
                                           "-t", "api-key", "-i", "10"]), \
                patch.object(self.cachet_handler, "_CachetHandler__update_status", return_value=None) as updater, \
                patch.object(self.cachet_handler, "_CachetHandler__has_active_issue", return_value=None), \
                patch.object(self.cachet_handler, "_CachetHandler__get_current_state", return_value=1):

            mocked_stdin.read = lambda: OK_RESULT
            self.cachet_handler.run()

            assert updater.call_count == 0
