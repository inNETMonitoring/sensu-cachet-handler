# sensu-cachet-handler

A python based handler to send status updates to cachet using sensu checks.

## Installation

__This script is still under development and not considered stable!__


This script requires cachet-client and sensu-plugin as well as a python installation on your
sensu master. An example dockerfile is visible below:

```text
FROM sensu/sensu:5.15.0

RUN apk update && apk add python3 git
RUN pip3 install cachet-client==2.0.1 sensu-plugin==0.8.0 git+https://github.com/inNETMonitoring/sensu-cachet-handler.git
```

## Usage

```text
usage: cachet_publisher.py [-h] [--map-v2-event-into-v1] --id ID --url URL
                           --token TOKEN [--warning-code WARNING_CODE]
                           [--error-code ERROR_CODE] [--create-incident]
                           [--incident-title INCIDENT_TITLE]
                           [--incident-message INCIDENT_MESSAGE]
                           [--resolve-message RESOLVE_MESSAGE]

optional arguments:
  -h, --help            show this help message and exit
  --map-v2-event-into-v1
  --id ID, -i ID        Id of the cachet component to update
  --url URL, -u URL     Cachet API endpoint
  --token TOKEN, -t TOKEN
                        The access token for the cachet API
  --warning-code WARNING_CODE, -w WARNING_CODE
                        The cachet status to set if sensu emits a
                        warning(default: 2 - Performance Issue)
  --error-code ERROR_CODE, -e ERROR_CODE
                        The cachet status to set if sensu emits an
                        error(default: 4 - Major Outage)
  --create-incident, -c
                        If the flag is set, an issue will be created for
                        incoming errors
  --incident-title INCIDENT_TITLE
                        Custom issue title
  --incident-message INCIDENT_MESSAGE
                        Custom issue message
  --resolve-message RESOLVE_MESSAGE
                        Message which will be sent if the issue gets resolved
```
