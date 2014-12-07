#
#      Copyright (c) 2014 Two Sigma Investments, LLC.
#      All Rights Reserved
#

import json
from supervisor import childutils
import sys
import pycurl
import socket
import StringIO

def make_curl_request(method, url, data):
    """Makes a request to the given url with the specified method (HEAD, PUT, POST, etc).
    If the request is a POST or PUT, includes the given data. Assumes that all POSTed data
    is JSON, for simplicity of working with Pagerduty."""
    curl_obj = pycurl.Curl()

    stringdata = StringIO.StringIO(data)

    # BEGIN PROXY RELATED CUSTOMIZATIONS

    # Here's where you can make changes to interact with a proxy

    # This line sets the proxy upstream; you'll want to change this when you uncomment it
    #curl_obj.setopt(pycurl.PROXY, "http://anyone:@proxy.example.com:3128")

    # This line configures curl to automatically use whatever authorization mechanism is available
    #curl_obj.setopt(pycurl.PROXYAUTH, pycurl.HTTPAUTH_ANY)
    # In case your proxy doesn't support anyauth, this line configures curl to use NTLM (for example)
    #curl_obj.setopt(pycurl.PROXYAUTH, pycurl.HTTPAUTH_NTLM)
    # You can also use pycurl.HTTPAUTH_BASIC, pycurl.HTTPAUTH_DIGEST, or pycurl.HTTPAUTH_GSSNEGOTIATE

    # If your proxy requires a username:password pair, uncomment the following line and fill in the details
    #curl_obj.setopt(pycurl.PROXYUSERPWD, "username:password")

    # END PROXY RELATED CUSTOMIZATIONS

    # 30 seconds to connect to the proxy seems reasonable, if you're using a proxy
    curl_obj.setopt(pycurl.CONNECTTIMEOUT, 30)

    curl_obj.setopt(pycurl.VERBOSE, 1L)

    clen = len(data)
    if method == "HEAD":
         curl_obj.setopt(pycurl.NOBODY, 1L)
    elif method == "GET":
        pass
    elif method == "DELETE":
         curl_obj.setopt(pycurl.CUSTOMREQUEST, "DELETE")
    elif method == "POST":
        curl_obj.setopt(pycurl.POST, 1L)
        curl_obj.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json'])
        if clen:
            curl_obj.setopt(pycurl.POSTFIELDSIZE, clen)
        curl_obj.setopt(pycurl.READFUNCTION, stringdata.read)
    elif method == "PUT":
        curl_obj.setopt(pycurl.READFUNCTION, stringdata.read)
        if clen:
            curl_obj.setopt(pycurl.INFILESIZE, clen)
        curl_obj.setopt(pycurl.PUT, 1L)

    # target URL
    curl_obj.setopt(pycurl.URL, url)

    curl_obj.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_1_1)

    result = curl_obj.perform()

    return result

class PagerDutyNotifier(object):
    """This class uses the supervisor API to listen for supervisor
    events and notify pagerduty when processes crash unexpectedly."""
    def __init__(self, pd_service_key):
        self.pd_service_key = pd_service_key

    def run(self):
        """The main entry point of the notification system. This function will not return,
        as it loops forever."""
        while True:
            headers, payload = childutils.listener.wait()
            sys.stderr.write(str(headers) + '\n')
            payload = dict(v.split(':') for v in payload.split(' '))
            sys.stderr.write(str(payload) + '\n')
            if headers['eventname'] == 'PROCESS_STATE_EXITED' and not int(payload['expected']):
                data = {'service_key': self.pd_service_key,
                        'incident_key': '{0} {1} supervisor'.format(payload['processname'], socket.gethostname()),
                        'event_type': 'trigger',
                        'description': '{0} service has crashed unexpectedly on {1}'.format(payload['processname'], socket.gethostname())
                }
                try:
                    res = make_curl_request('POST', 'https://events.pagerduty.com/generic/2010-04-15/create_event.json', json.dumps(data))
                except pycurl.error, ex:
                    sys.stderr.write('curl exception: {0}\n'.format(str(ex)))
                else:
                    sys.stderr.write('{0}\n'.format(str(res)))
                childutils.listener.ok()
                sys.stderr.flush()
    
if __name__ == '__main__':
    pager_duty_service_key = sys.argv[1]
    pager_duty_notifer = PagerDutyNotifier(pager_duty_service_key)
    pager_duty_notifer.run()
