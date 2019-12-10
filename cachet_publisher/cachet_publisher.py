from sensu_plugin import SensuHandler
from cachetclient import Client
import json
import sys


class CachetHandler(SensuHandler):
    def __init__(self, autorun=True):
        super().__init__(autorun)
        self.client = None

    def setup(self):
        self.parser.add_argument("--id", "-i", required=True, type=int, help="Id of the cachet component to update")
        self.parser.add_argument("--url", "-u", required=True, help="Cachet API endpoint")
        self.parser.add_argument("--token", "-t", required=True, help="The access token for the cachet API")
        self.parser.add_argument("--warning-code", "-w", type=int, default=2,
                                 help="The cachet status to set if sensu emits a warning"
                                      "(default: 2 - Performance Issue)")
        self.parser.add_argument("--error-code", "-e", type=int, default=4,
                                 help="The cachet status to set if sensu emits an error"
                                      "(default: 4 - Major Outage)")
        self.parser.add_argument("--create-incident", "-c", action="store_true",
                                 help="If the flag is set, an issue will be created for incoming errors")
        self.parser.add_argument("--incident-title", help="Custom issue title")
        self.parser.add_argument("--incident-message", help="Custom issue message")
        self.parser.add_argument("--resolve-message", default="Incident was resolved",
                                 help="Message which will be sent if the issue gets resolved")

    def __update_status(self, component_id, status):
        self.client.components.update(component_id, status=status)

    def __create_incident(self, component_id, incident_title, incident_message, status_code):
        self.client.incidents.create(name=incident_title, message=incident_message, status=1, visible=1,
                                     component_id=component_id, component_status=status_code)

    def __has_active_issue(self, component_id, issue_title):
        response = self.client._http.get(f"incidents?component_id={component_id}&name={issue_title}&sort=id&order=desc")
        if response.status_code == 200:
            content = json.loads(response.content.decode("utf-8"))
            if len(content["data"]) > 0:
                incident = self.client.incidents.instance_from_dict(content["data"][0])
                return None if incident.status == 4 else incident
            else:
                return None
        else:
            return None

    def __resolve_incident(self, incident, state, resolve_message):
        self.client.incidents.update(incident_id=incident.id, status=state, name=incident.name,
                                     message=resolve_message + "\n\n---\n\n" + incident.message, visible=1)

    def __get_incident_name(self):
        title = self.options.incident_title
        if title is None:
            title = f"Troubles with {self.event['check']['name']}"
        return title

    def __get_incident_message(self):
        message = self.options.incident_message
        if message is None:
            message = self.event["check"]["output"]
        return message

    def handle(self):
        self.client = Client(self.options.url, self.options.token)
        event_data = json.loads(sys.stdin.read())

        check_status = event_data["check"]["status"]

        if check_status == 1:  # WARNING
            self.__update_status(self.options.id, self.options.warning_code)
        elif check_status == 2:  # ERROR
            issue = self.__has_active_issue(self.options.id, self.__get_incident_name())
            if self.options.create_incident and issue is None:
                self.__create_incident(self.options.id, self.__get_incident_name(), self.__get_incident_message(),
                                       self.options.error_code)
            else:
                self.__update_status(self.options.id, self.options.error_code)
        else:
            issue = self.__has_active_issue(self.options.id, self.__get_incident_name())

            if issue is not None:
                self.__resolve_incident(issue, 4, self.options.resolve_message)

            self.__update_status(self.options.id, status=1)


if __name__ == "__main__":
    CachetHandler(True)
