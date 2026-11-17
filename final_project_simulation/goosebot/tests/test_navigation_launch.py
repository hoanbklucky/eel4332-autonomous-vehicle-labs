"""Offline regression checks for saved-map startup; no ROS installation required."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

import yaml


LAUNCH = Path(__file__).resolve().parents[1] / 'navigation.launch.py'
spec = importlib.util.spec_from_file_location('course_navigation', LAUNCH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class MapStartupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'map directory with spaces'
        self.root.mkdir()
        self.map = self.root / 'campus.yaml'
        self.image = self.root / 'campus.pgm'
        self.image.write_bytes(b'P5\n1 1\n255\n\xff')
        self.map.write_text('image: campus.pgm\nresolution: 0.05\norigin: [0, 0, 0]\n')
        self.params = self.root / 'params.yaml'
        self.original = {
            'map_server': {'ros__parameters': {'yaml_filename': '', 'topic_name': 'map'}},
            'amcl': {'ros__parameters': {'scan_topic': '/custom_scan'}},
            'controller_server': {'ros__parameters': {'controller_frequency': 7.5}},
        }
        self.params.write_text(yaml.safe_dump(self.original))
        self.output = self.root / 'prepared.yaml'

    def test_blank_or_stale_path_is_replaced_without_changing_other_parameters(self):
        for old in ('', '/previous/ist.yaml'):
            self.original['map_server']['ros__parameters']['yaml_filename'] = old
            self.params.write_text(yaml.safe_dump(self.original))
            selected, image = module.prepare_parameters(self.map, self.params, self.output)
            expected = yaml.safe_load(self.params.read_text())
            expected['map_server']['ros__parameters']['yaml_filename'] = str(self.map.resolve())
            self.assertEqual(yaml.safe_load(self.output.read_text()), expected)
            self.assertEqual(selected, self.map.resolve())
            self.assertEqual(image, self.image.resolve())
            self.assertEqual(yaml.safe_load(self.params.read_text()), self.original)

    def test_missing_map_or_image_fails_before_producing_parameters(self):
        self.image.unlink()
        with self.assertRaisesRegex(ValueError, 'Map image not found'):
            module.prepare_parameters(self.map, self.params, self.output)
        self.assertFalse(self.output.exists())
        self.map.unlink()
        with self.assertRaisesRegex(ValueError, 'Saved map YAML not found'):
            module.prepare_parameters(self.map, self.params, self.output)

    def test_absolute_image_and_missing_map_server_section(self):
        self.map.write_text(yaml.safe_dump({'image': str(self.image.resolve())}))
        self.params.write_text(yaml.safe_dump({'amcl': self.original['amcl']}))
        module.prepare_parameters(self.map, self.params, self.output)
        self.assertEqual(yaml.safe_load(self.output.read_text())['map_server']['ros__parameters']
                         ['yaml_filename'], str(self.map.resolve()))


if __name__ == '__main__':
    unittest.main()
