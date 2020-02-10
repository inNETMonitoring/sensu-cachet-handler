from sensu_plugin import SensuHandler
from cachetclient import Client


class CachetMetrics(SensuHandler):
    def __init__(self, autorun=True):
        super().__init__(autorun)
        self.client = None

    def setup(self):
        self.parser.add_argument("--id", "-i", required=True, type=int, help="Id of the cachet component to update")
        self.parser.add_argument("--url", "-u", required=True, help="Cachet API endpoint")
        self.parser.add_argument("--token", "-t", required=True, help="The access token for the cachet API")
        self.parser.add_argument("--name", "-n", required=True,
                                 help="The name of the measurement to be published to cachet")

    def __publish_metric(self, timestamp, value):
        data = {
            "timestamp": str(timestamp),
            "value": value
        }
        response = self.client._http.post(f"metrics/{self.options.id}/points",
                                          data=data)
        return response.status_code == 200

    def handle(self):
        self.client = Client(self.options.url, self.options.token)

        metrics = self.event["metrics"]["points"]

        if len(metrics) < 1:
            print("No metrics passed")
            exit(-1)

        for m in metrics:
            if m["name"] == self.options.name:
                self.__publish_metric(m["timestamp"], m["value"])


if __name__ == "__main__":
    CachetMetrics(True)
