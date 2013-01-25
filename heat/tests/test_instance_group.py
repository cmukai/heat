# vim: tabstop=4 shiftwidth=4 softtabstop=4

#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


import os

import unittest
import mox

from nose.plugins.attrib import attr

from heat.common import context
from heat.common import template_format
from heat.engine.resources import autoscaling as asc
from heat.engine.resources import loadbalancer
from heat.engine import parser


@attr(tag=['unit', 'resource'])
@attr(speed='fast')
class InstanceGroupTest(unittest.TestCase):
    def setUp(self):
        self.m = mox.Mox()
        self.m.StubOutWithMock(loadbalancer.LoadBalancer, 'reload')

    def tearDown(self):
        self.m.UnsetStubs()
        print "InstanceGroupTest teardown complete"

    def load_template(self):
        self.path = os.path.dirname(os.path.realpath(__file__)).\
            replace('heat/tests', 'templates')
        f = open("%s/InstanceGroup.template" % self.path)
        t = template_format.parse(f.read())
        f.close()
        return t

    def parse_stack(self, t):
        ctx = context.RequestContext.from_dict({
            'tenant': 'test_tenant',
            'username': 'test_username',
            'password': 'password',
            'auth_url': 'http://localhost:5000/v2.0'})
        template = parser.Template(t)
        params = parser.Parameters('test_stack', template, {'KeyName': 'test'})
        stack = parser.Stack(ctx, 'test_stack', template, params)

        return stack

    def create_instance_group(self, t, stack, resource_name):
        resource = asc.InstanceGroup(resource_name,
                                     t['Resources'][resource_name],
                                     stack)
        self.assertEqual(None, resource.validate())
        self.assertEqual(None, resource.create())
        self.assertEqual(asc.InstanceGroup.CREATE_COMPLETE, resource.state)
        return resource

    def test_instance_group(self):

        t = self.load_template()
        stack = self.parse_stack(t)

        # start with min then delete
        resource = self.create_instance_group(t, stack, 'JobServerGroup')

        self.assertEqual('JobServerGroup', resource.FnGetRefId())
        self.assertEqual('JobServerGroup-0', resource.resource_id)
        self.assertEqual(asc.InstanceGroup.UPDATE_REPLACE,
                         resource.handle_update())

        resource.delete()