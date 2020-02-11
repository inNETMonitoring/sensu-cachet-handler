#!/usr/bin/env python
import unittest
import sys

from unittest.mock import patch

# Alter path and import modules
from cachet_metric.cachet_metrics import CachetMetrics


METRIC_JSON = '''{
    "timestamp": 1581339925,
    "entity": {
    },
    "check": {
    },
    "metrics":  {
        "handlers": ["cachet_metrics"],
        "points": [
            {
                "name": "data.disk_usage.root.data.used",
                 "value": 178,
                 "timestamp": 1581339925,
                 "tags": null
            },
            {
                "name": "data.disk_usage.root.data.avail",
                "value": 782,
                "timestamp": 1581339925,
                "tags": null
            },
            {
                "name": "data.disk_usage.root.data.used_percentage",
                "value": 19,
                "timestamp": 1581339925,
                "tags": null
            }
        ]
    },
    "metadata": {"namespace": "default"}
}'''


class TestCachetPublisher(unittest.TestCase):
    def setUp(self) -> None:
        '''
        Instantiate a fresh SensuHandler before each test.
        '''
        self.cachet_metrics = CachetMetrics(autorun=False)

    def test_metrics(self):
        '''
        Tests the run method.
        '''

        # event should be valid json
        with patch('sensu_plugin.handler.sys.stdin') as mocked_stdin, \
                patch.object(sys, "argv", ["cachet_publisher.py", "-u", "https://my.status.io/v1",
                                           "-t", "api-key", "-i", "10", "-n", "data.disk_usage.root.data.used"]), \
                patch.object(self.cachet_metrics, "_CachetMetrics__publish_metric", return_value=None) as metric_pub:

            mocked_stdin.read = lambda: METRIC_JSON
            self.cachet_metrics.run()
            assert metric_pub.call_args == ((1581339925, 178), )
