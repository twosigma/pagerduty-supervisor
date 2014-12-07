# PagerDuty + SupevisorD Integration

This simple makes it easy to use [PagerDuty](http://www.pagerduty.com/) with [SupervisorD](http://supervisord.org/). We required additional features beyond what the open-source integrations offered, so we developed this to provide an extensible integration.

## Features

- Whenever your supervised process crashes, an incident will be triggered on PagerDuty
- If your process crashes repeatedly, those failures will be consolidated to a single incident so that your on-call staff isn't overwhelmed with a flood of incidents
- If you require accessing the network through a proxy, there is a detailed section in the source code explaining how to configure proxy traversal

This code is based on this [gist](https://gist.github.com/reshefm/4996449).

## Usage

To use this program, simply insert the following into your SupervisorD configuration file. Make sure to specify the path to `python` and `pagerduty-supervisor.py`, and provide a pagerduty service key.

```
[eventlistener:pagerduty]
command= python pagerduty-supervisor.py $PAGERDUTY_SERVICE_KEY
events=PROCESS_STATE_EXITED
stderr_logfile = /path/to/somewhere.err
stdout_logfile = /path/to/somewhere.out
autorestart = true
exitcodes =
```

## Stability

Pagerduty-Supervisor has been used successfully in production for since late 2013.

## License

Copyright © 2014 Two Sigma Investments, LLC

Distributed under the Eclipse Public License
