# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import webapp2


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        with open('footballpool.html') as f:
            self.response.write(f.read())

class ScheduleJSPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        with open('schedule.json') as f:
            self.response.write(
                'var DATA = ' + f.read() + ';\n')

class PicksJSPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        with open('picks.json') as f:
            self.response.write(
                'var STATE = {"picks": ' + f.read() + '};\n')

class JSONdownloadPage(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'application/octet-stream'
        self.response.write(self.request.POST['hiddenpicks'])



app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/footballpool.html', MainPage),
    ('/schedule.js', ScheduleJSPage),
    ('/picks.js', PicksJSPage),
    ('/picks.json', JSONdownloadPage),
], debug=True)
