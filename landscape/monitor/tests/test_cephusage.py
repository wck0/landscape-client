import tempfile
from landscape.lib.fs import touch_file
from landscape.tests.helpers import LandscapeTest, MonitorHelper
from landscape.monitor.cephusage import CephUsage


class CephUsagePluginTest(LandscapeTest):
    helpers = [MonitorHelper]

    def setUp(self):
        super(CephUsagePluginTest, self).setUp()
        self.mstore = self.broker_service.message_store
        self.plugin = CephUsage(create_time=self.reactor.time)

    def test_never_exchange_empty_messages(self):
        """
        The plugin will create a message with an empty C{usages} list when no
        previous data is available.  If an empty message is created during
        exchange, it should not be queued.
        """
        self.mstore.set_accepted_types(["ceph"])
        self.monitor.add(self.plugin)

        self.monitor.exchange()
        self.assertEqual(0, len(self.mstore.get_pending_messages()))

    def test_exchange_messages(self):
        """
        The Ceph usage plugin queues message when manager.exchange()
        is called.
        """
        ring_id = "whatever"
        self.mstore.set_accepted_types(["ceph"])

        point = (60, 100.0, 80.0, 20.0)
        self.plugin._ceph_usage_points = [point]
        self.plugin._ceph_ring_id = ring_id
        self.monitor.add(self.plugin)

        self.monitor.exchange()
        self.assertMessages(
            self.mstore.get_pending_messages(),
            [{"type": "ceph",
              "ring-id": ring_id,
              "usages": [point]}])

    def test_create_message(self):
        """
        Calling create_message returns an expected message.
        """
        ring_id = "blah"
        self.plugin._ceph_usage_points = []
        self.plugin._ceph_ring_id = ring_id
        message = self.plugin.create_message()

        self.assertIn("type", message)
        self.assertEqual(message["type"], "ceph")
        self.assertIn("usages", message)
        self.assertEqual(ring_id, message["ring-id"])
        ceph_usages = message["usages"]
        self.assertEqual(len(ceph_usages), 0)

        point = (60, 100.0, 80.0, 20.0)
        self.plugin._ceph_usage_points = [point]
        message = self.plugin.create_message()
        self.assertIn("type", message)
        self.assertEqual(message["type"], "ceph")
        self.assertIn("usages", message)
        self.assertEqual(ring_id, message["ring-id"])
        ceph_usages = message["usages"]
        self.assertEqual(len(ceph_usages), 1)
        self.assertEqual([point], ceph_usages)

    def test_no_message_if_not_accepted(self):
        """
        Don't add any messages at all if the broker isn't currently accepting
        their type.
        """
        interval = 30
        monitor_interval = 300

        plugin = CephUsage(
            interval=interval, monitor_interval=monitor_interval,
            create_time=self.reactor.time)

        self.monitor.add(plugin)

        self.reactor.advance(monitor_interval * 2)
        self.monitor.exchange()

        # self.mstore.set_accepted_types(["ceph"])
        self.assertMessages(list(self.mstore.get_pending_messages()), [])

    def test_wb_should_run_inactive(self):
        """
        A plugin with self.active set to False should not run.
        """
        plugin = CephUsage()
        plugin.active = False
        self.assertFalse(plugin._should_run())

    def test_wb_should_run_no_config_file(self):
        """
        A plugin without a set _ceph_config attribute should not run.
        """
        plugin = CephUsage()
        plugin._has_rados = True
        plugin._ceph_config = None
        self.assertFalse(plugin._should_run())

    def test_wb_should_run_no_rados(self):
        """
        If the Rados library cannot be imported (CephUsage._has_rados is False)
        the plugin logs a message then deactivates itself.
        """
        logging_mock = self.mocker.replace("logging.info")
        logging_mock("This machine does not appear to be a Ceph machine. "
                     "Deactivating plugin.")
        self.mocker.replay()

        plugin = CephUsage()
        plugin._has_rados = False
        self.assertFalse(plugin._should_run())

    def test_wb_should_run(self):
        """
        If the Rados library is present with the correct version and a ceph
        config exists, the C{_should_run} method returns True.
        """
        plugin = CephUsage()
        plugin._has_rados = True
        plugin._ceph_config = tempfile.mktemp()
        touch_file(plugin._ceph_config)
        self.assertTrue(plugin._should_run())

    def test_wb_handle_usage(self):
        """
        The C{_handle_usage} method stores the result of the rados call (here,
        an example value) in an Accumulator, and appends the step_data
        to the C{_ceph_usage_points} member when an accumulator interval is
        reached.
        """
        interval = 300
        stats = {"kb": 10240L, "kb_avail": 8192L, "kb_used": 2048L}

        plugin = CephUsage(
            create_time=self.reactor.time, interval=interval,
            monitor_interval=interval)

        self.monitor.add(plugin)

        plugin._handle_usage(stats)  # time is 0

        self.reactor.advance(interval)  # time is 300
        plugin._handle_usage(stats)

        self.assertEqual(
            [(300, 10.0, 8.0, 2.0)], plugin._ceph_usage_points)

    def test_resynchronize_message_calls_reset_method(self):
        """
        If the reactor fires a "resynchronize" even the C{_reset}
        method on the ceph plugin object is called.
        """
        self.called = False

        def stub_reset():
            self.called = True

        self.plugin._reset = stub_reset
        self.monitor.add(self.plugin)
        self.reactor.fire("resynchronize")
        self.assertTrue(self.called)
