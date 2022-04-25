from time import sleep
import requests
import urllib.parse as par
import plotly
import pandas as pd
import io
import urllib
from pprint import pprint
import mpld3
import matplotlib.pyplot as plt
import random
from opcua import ua, Client
import threading
from http.server import HTTPServer,BaseHTTPRequestHandler
import cgi

def init_questdb_table():
    q = """\
    CREATE TABLE 
        sensor_data (ID STRING,
                         value DOUBLE, 
                         ts TIMESTAMP)
        timestamp(ts)
    """

    r = requests.get("http://localhost:9000/exec?query=" + q)
    if r.status_code in [200,400]:
        print("success")
    else:
        print(r.status_code)
        print("failure")

def add_data_point(ID, value):
    q = "INSERT INTO sensor_data values('{}', {}, systimestamp())".format(ID, value)

    r = requests.get("http://localhost:9000/exec?query=" + q)
    if r.status_code in [200,400]:
        print("success")
    else:
        print(r.status_code)
        print("failure")


def get_data_points():
    q = "SELECT * from sensor_data"
    q = urllib.parse.quote(q)
    r = requests.get("http://localhost:9000/exp?query=" + q)
    if r.status_code in [200,400]:
        print("success")
        return(r.text)
    else:
        print(r.status_code)
        print("failure")

def generate_plot_html():
    queryData = get_data_points()
    data = pd.read_csv(io.StringIO(queryData), parse_dates=['ts'])
    level1 = data.loc[data["ID"] == "level1"]
    level2 = data.loc[data["ID"] == "level2"]
    level3 = data.loc[data["ID"] == "level3"]
    plt.plot(level1['ts'], level1['value'], label='level1', color='g')
    plt.plot(level2['ts'], level2['value'], label='level2', color='r')
    plt.plot(level3['ts'], level3['value'], label='level3', color='b')
    html = mpld3.fig_to_html(plt.figure(1), no_extras=True, template_type='simple')
    return(html)

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        html = ''
        html += generate_plot_html()
#         button = \
# """<div>Relay 1:
#   <form action= '{% url my_view_name%}' method="GET">
#       <input type="submit" value="Toggle" id="toggle1" />
#   </form>
# </div>"""
#         html += "\n" + button

        field = \
"""
<body><h1>Parameters:</h1>
<form method='POST'>
<input name='setpoint_1' placeholder='255' value='' />set point 1<br />
<input name='setpoint_2' placeholder='255' value='' />set point 2<br />
<input type='submit' value='submit!'/></form>
</form></body>
"""
        html += "\n" + field

        refresh = \
"""<script>
    window.setInterval('refresh()', 30000); 	
    // Call a function every 10000 milliseconds 
    // (OR 10 seconds).

    // Refresh or reload page.
    function refresh() {
        window .location.reload();
    }
</script>"""

        html += refresh
        self.send_response(200)
        self.send_header('Content-type' , 'text/html')
        self.end_headers()
        self.wfile.write(bytes(html, 'utf-8'))

    def do_POST(self):
        args = urllib.parse.parse_qs(self.path[2:])
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })

        if form.getvalue('setpoint_1') != None:
            value = form.getvalue('setpoint_1')
            try:
                value = int(value)
            except:
                pass
            if isinstance(value, int) and value <100 and value >= 0:
                var = get_cloudtestvar()
                var.set_attribute(ua.AttributeIds.Value, ua.DataValue(value+10))
        elif form.getvalue('setpoint_2') != None:
            value = form.getvalue('setpoint_2')
            try:
                value = int(value)
            except:
                pass
            if isinstance(value, int) and value <100 and value >= 0:
                var = get_cloudtestvar()
                var.set_attribute(ua.AttributeIds.Value, ua.DataValue(-value-10))

        self.do_GET()

def main(server_port: "Port to serve on." = 9950, server_address: "Local server name." = ''):
    httpd = HTTPServer((server_address, server_port), RequestHandler)
    httpd.server_name = 'localhost'
    print(f'Serving on http://{httpd.server_name}:{httpd.server_port} ...')
    httpd.serve_forever()


def get_cloudtestvar():

    client1 = Client('opc.tcp://172.16.4.12:48858')
    client1.connect()
    root1 = client1.get_root_node()
    cloud_var = client1.get_node('ns=4:s={9D1EEBE0-4E56-4181-84A5-6F643B6B3580}:Cloudtestvar.Value')

def get_level_1():
    client1 = Client('opc.tcp://172.16.4.12:48858')
    client1.connect()
    root1 = client1.get_root_node()
    var = client1.get_node('ns=4:s={9D1EEBE0-4E56-4181-84A5-6F643B6B3580}:Cloudtestvar.Value')
    var.get_value()
    return var.get_value()


def get_level_2():
    client1 = Client('opc.tcp://172.16.4.12:48858')
    client1.connect()
    root1 = client1.get_root_node()
    var = client1.get_node('ns=4:s={9D1EEBE0-4E56-4181-84A5-6F643B6B3580}:Cloudtestvar.Value')
    var.get_value()
    return var.get_value()


def get_level_3():
    client1 = Client('opc.tcp://172.16.4.12:48858')
    client1.connect()
    root1 = client1.get_root_node()
    var = client1.get_node('ns=4:s={9D1EEBE0-4E56-4181-84A5-6F643B6B3580}:Cloudtestvar.Value')
    var.get_value()
    return var.get_value()


if __name__ == "__main__":
    init_questdb_table()
    serverthread = threading.Thread(target=main)
    serverthread.start()
    while True:

        #add_data_point('level1', get_level_1())
        #add_data_point('level2', get_level_2())
        #add_data_point('level3', get_level_3())
        add_data_point('level1', random.randint(0, 63))
        add_data_point('level2', random.randint(0, 63))
        add_data_point('level3', random.randint(0, 63))

        queryData = get_data_points()
        data = pd.read_csv(io.StringIO(queryData), parse_dates=['ts'])
        pprint(data)
        sleep(30)
