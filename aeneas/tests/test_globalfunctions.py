#!/usr/bin/env python
# coding=utf-8

import io
import os
import sys
import unittest

import aeneas.globalconstants as gc
import aeneas.globalfunctions as gf

class TestGlobalFunctions(unittest.TestCase):

    def test_uuid_string(self):
        uuid = gf.uuid_string()
        self.assertEqual(len(uuid), 36)

    def test_custom_tmp_dir(self):
        tmp_dir = gf.custom_tmp_dir()
        if sys.platform in ["linux", "linux2", "darwin"]:
            self.assertEqual(tmp_dir, gc.TMP_PATH)
        else:
            self.assertEqual(tmp_dir, None)

    def test_tmp_directory(self):
        tmp_dir = gf.tmp_directory()
        self.assertTrue(gf.directory_exists(tmp_dir))
        gf.delete_directory(tmp_dir)

    def test_tmp_file(self):
        tmp_handler, tmp_file = gf.tmp_file()
        self.assertTrue(gf.file_exists(tmp_file))
        gf.delete_file(tmp_handler, tmp_file)

    def test_tmp_file_suffix(self):
        tmp_handler, tmp_file = gf.tmp_file(suffix=".txt")
        self.assertTrue(gf.file_exists(tmp_file))
        gf.delete_file(tmp_handler, tmp_file)

    def test_file_extension(self):
        tests = [
            (None, None),
            ("", ""),
            ("/", ""),
            ("/foo", ""),
            ("/foo.", ""),
            ("/.foo", ""),
            ("/foo.bar", "bar"),
            ("/foo/bar/foo.baz", "baz"),
            ("/foo/bar/baz", ""),
            ("/foo/bar/.baz", ""),
            ("foo", ""),
            ("foo.", ""),
            (".foo", ""),
            ("foo.bar", "bar"),
            ("foo/bar/foo.baz", "baz"),
            ("foo/bar/baz", ""),
            ("foo/bar/.baz", ""),
        ]
        for test in tests:
            self.assertEqual(gf.file_extension(test[0]), test[1])

    def test_file_name_without_extension(self):
        tests = [
            (None, None),
            ("", ""),
            ("/", ""),
            ("/foo", "foo"),
            ("/foo.", "foo"),
            ("/.foo", ".foo"),
            ("/foo.bar", "foo"),
            ("/foo/bar/foo.baz", "foo"),
            ("/foo/bar/baz", "baz"),
            ("/foo/bar/.baz", ".baz"),
            ("foo", "foo"),
            ("foo.", "foo"),
            (".foo", ".foo"),
            ("foo.bar", "foo"),
            ("foo/bar/foo.baz", "foo"),
            ("foo/bar/baz", "baz"),
            ("foo/bar/.baz", ".baz"),
        ]
        for test in tests:
            self.assertEqual(gf.file_name_without_extension(test[0]), test[1])

    def test_safe_float(self):
        tests = [
            ("3.14", 1.23, 3.14),
            (" 3.14", 1.23, 3.14),
            (" 3.14 ", 1.23, 3.14),
            ("3.14f", 1.23, 1.23),
            ("0x3.14", 1.23, 1.23),
            ("", 1.23, 1.23),
            ("foo", 1.23, 1.23),
            (None, 1.23, 1.23),
        ]
        for test in tests:
            self.assertEqual(gf.safe_float(test[0], test[1]), test[2])

    def test_safe_int(self):
        tests = [
            ("3.14", 1, 3),
            ("3.14 ", 1, 3),
            (" 3.14", 1, 3),
            (" 3.14 ", 1, 3),
            ("3.14f", 1, 1),
            ("0x3.14", 1, 1),
            ("3", 1, 3),
            ("3 ", 1, 3),
            (" 3", 1, 3),
            (" 3 ", 1, 3),
            ("3f", 1, 1),
            ("0x3", 1, 1),
            ("", 1, 1),
            ("foo", 1, 1),
            (None, 1, 1),
        ]
        for test in tests:
            self.assertEqual(gf.safe_int(test[0], test[1]), test[2])

    def test_safe_get(self):
        tests = [
            (None, None, u"default", u"default"),
            (None, u"key", u"default", u"default"),
            ({}, None, u"default", u"default"),
            ({}, u"key", u"default", u"default"),
            ([], u"key", u"default", u"default"),
            ({u"key": u"value"}, None, u"default", u"default"),
            ({u"key": u"value"}, u"key", u"default", u"value"),
        ]
        for test in tests:
            self.assertEqual(gf.safe_get(test[0], test[1], test[2]), test[3])

    def test_norm_join(self):
        tests = [
            (None, None, "."),
            (None, "", "."),
            (None, "/foo", "/foo"),
            (None, "/foo.bar", "/foo.bar"),
            (None, "/foo/../bar", "/bar"),
            (None, "/foo/./bar", "/foo/bar"),
            (None, "/foo/bar/baz", "/foo/bar/baz"),
            (None, "/foo/bar/../../baz", "/baz"),
            (None, "/foo/bar/./baz", "/foo/bar/baz"),
            ("", None, "."),
            ("/foo", None, "/foo"),
            ("/foo.bar", None, "/foo.bar"),
            ("/foo/../bar", None, "/bar"),
            ("/foo/./bar", None, "/foo/bar"),
            ("/foo/bar/baz", None, "/foo/bar/baz"),
            ("/foo/bar/../../baz", None, "/baz"),
            ("/foo/bar/./baz", None, "/foo/bar/baz"),
            ("", "", "."),
            ("/", "", "/"),
            ("", "/", "/"),
            ("/", "/", "/"),
            ("/foo", "bar", "/foo/bar"),
            ("/foo", "bar/foo.baz", "/foo/bar/foo.baz"),
            ("/foo", "bar/../foo.baz", "/foo/foo.baz"),
            ("/foo", "bar/../../foo.baz", "/foo.baz"),
            ("/foo", "bar.baz", "/foo/bar.baz"),
            ("/foo/../", "bar.baz", "/bar.baz"),
            ("/foo/", "../bar.baz", "/bar.baz"),
            ("/foo/./", "bar.baz", "/foo/bar.baz"),
            ("/foo/", "./bar.baz", "/foo/bar.baz"),
            ("foo", "bar", "foo/bar"),
            ("foo", "bar/foo.baz", "foo/bar/foo.baz"),
            ("foo", "bar/../foo.baz", "foo/foo.baz"),
            ("foo", "bar/../../foo.baz", "foo.baz"),
            ("foo", "bar.baz", "foo/bar.baz"),
            ("foo/../", "bar.baz", "bar.baz"),
            ("foo/", "../bar.baz", "bar.baz"),
            ("foo/./", "bar.baz", "foo/bar.baz"),
            ("foo/", "./bar.baz", "foo/bar.baz"),
        ]
        for test in tests:
            self.assertEqual(gf.norm_join(test[0], test[1]), test[2])

    def test_config_txt_to_string(self):
        tests = [
            (None, None),
            (u"", u""),
            (u"k1=v1", u"k1=v1"),
            (u"k1=v1\n\n", u"k1=v1"),
            (u"k1=v1\nk2=v2", u"k1=v1|k2=v2"),
            (u"k1=v1\nk2=v2\n\n\nk3=v3\n", u"k1=v1|k2=v2|k3=v3"),
            (u" k1=v1\n k2=v2 \n\n\nk3=v3 \n", u"k1=v1|k2=v2|k3=v3"),
            (u"k1=v1\nk2\nk3=v3", "k1=v1|k2|k3=v3"),
        ]
        for test in tests:
            self.assertEqual(gf.config_txt_to_string(test[0]), test[1])

    def test_config_string_to_dict(self):
        tests = [
            (None, {}),
            (u"", {}),
            (u"k1=v1", {u"k1": u"v1"}),
            (u"k1=v1|", {u"k1": u"v1"}),
            (u"|k1=v1|", {u"k1": u"v1"}),
            (u"|k1=v1", {u"k1": u"v1"}),
            (u"k1=v1|k1=v2", {u"k1": u"v2"}),
            (u"k1=v1|k2=v2", {u"k1": u"v1", u"k2": u"v2"}),
            (u"k1=v1|k2=v2|k1=v3", {u"k1": u"v3", u"k2": u"v2"}),
            (u"k1=v1||k2=v2", {u"k1": u"v1", u"k2": u"v2"}),
            (u"k1=v1|k2=v2|k3=v3", {u"k1": u"v1", u"k2": u"v2", u"k3": u"v3"}),
            (u"k1=v1|k2=|k3=v3", {u"k1": u"v1", u"k3": u"v3"}),
            (u"k1=v1|=v2|k3=v3", {u"k1": u"v1", u"k3": u"v3"}),
        ]
        for test in tests:
            self.assertEqual(gf.config_string_to_dict(test[0]), test[1])

    def test_config_xml_to_dict_job(self):
        tests = [
            (None, {}),
            (u"", {}),
            (u"<job></job>", {}),
            (u"<job><k1>v1</k1></job>", {u"k1": u"v1"}),
            (u"<job><k1>v1</k1><k2></k2></job>", {u"k1": u"v1"}),
            (u"<job><k1>v1</k1><k2>  </k2></job>", {u"k1": u"v1"}),
            (u"<job><k1>v1</k1><k2>v2</k2></job>", {u"k1": u"v1", u"k2": u"v2"}),
            (u"<job><k1>v1</k1><k2> v2</k2></job>", {u"k1": u"v1", u"k2": u"v2"}),
            (u"<job><k1>v1</k1><k2> v2 </k2></job>", {u"k1": u"v1", u"k2": u"v2"}),
            (u"<job><k1>v1</k1><k2>v2 </k2></job>", {u"k1": u"v1", u"k2": u"v2"}),
        ]
        for test in tests:
            self.assertEqual(gf.config_xml_to_dict(test[0], result=None, parse_job=True), test[1])

    def test_config_xml_to_dict_task(self):
        tests = [
            (None, []),
            (u"", []),
            (u"<job></job>", []),
            (u"<job><k1>v1</k1></job>", []),
            (u"<job><k1>v1</k1><k2></k2></job>", []),
            (u"<job><tasks></tasks></job>", []),
            (u"<job><tasks><foo></foo></tasks></job>", []),
            (u"<job><tasks><task></task></tasks></job>", [{}]),
            (u"<job><tasks><task></task><foo></foo></tasks></job>", [{}]),
            (u"<job><tasks><task></task><foo></foo><task></task></tasks></job>", [{}, {}]),
            (u"<job><tasks><task><k1></k1></task><foo></foo></tasks></job>", [{}]),
            (u"<job><tasks><task><k1>v1</k1></task></tasks></job>", [{u"k1": u"v1"}]),
            (u"<job><tasks><task><k1>v1</k1><k2>v2</k2></task></tasks></job>", [{u"k1": u"v1", u"k2": u"v2"}]),
            (u"<job><tasks><task><k1>v1</k1><k2> v2</k2></task></tasks></job>", [{u"k1": u"v1", u"k2": u"v2"}]),
            (u"<job><tasks><task><k1>v1</k1><k2> v2 </k2></task></tasks></job>", [{u"k1": u"v1", u"k2": u"v2"}]),
            (u"<job><tasks><task><k1>v1</k1><k2>v2 </k2></task></tasks></job>", [{u"k1": u"v1", u"k2": u"v2"}]),
            (u"<job><tasks><task><k1>v1</k1></task><task><k2>v2</k2></task></tasks></job>", [{u"k1": u"v1"}, {u"k2": u"v2"}]),
            (u"<job><tasks><task><k1>v1</k1></task><task><k2>v2</k2></task><task></task></tasks></job>", [{u"k1": u"v1"}, {u"k2": u"v2"}, {}]),
        ]
        for test in tests:
            self.assertEqual(gf.config_xml_to_dict(test[0], result=None, parse_job=False), test[1])

    def test_config_dict_to_string(self):
        self.assertTrue(gf.config_dict_to_string({}) == u"")
        self.assertTrue(gf.config_dict_to_string({u"k1": u"v1"}) == u"k1=v1")
        self.assertTrue(
            (gf.config_dict_to_string({u"k1": u"v1", u"k2": u"v2"}) == u"k1=v1|k2=v2") or
            (gf.config_dict_to_string({u"k1": u"v1", u"k2": u"v2"}) == u"k2=v2|k1=v1")
        )

    def test_pairs_to_dict(self):
        tests = [
            ([], {}),
            ([u""], {}),
            ([u"k1"], {}),
            ([u"k1="], {}),
            ([u"=v1"], {}),
            ([u"k1=v1"], {u"k1": u"v1"}),
            ([u"k1=v1", u""], {u"k1": u"v1"}),
            ([u"k1=v1", u"k2"], {u"k1": u"v1"}),
            ([u"k1=v1", u"k2="], {u"k1": u"v1"}),
            ([u"k1=v1", u"=v2"], {u"k1": u"v1"}),
            ([u"k1=v1", u"k2=v2"], {u"k1": u"v1", u"k2": u"v2"}),
        ]
        for test in tests:
            self.assertEqual(gf.pairs_to_dict(test[0]), test[1])

    def test_copytree(self):
        orig = gf.tmp_directory()
        tmp_path = os.path.join(orig, "foo.bar")
        with io.open(tmp_path, "w", encoding="utf-8") as tmp_file:
            tmp_file.write(u"Foo bar")
        dest = gf.tmp_directory()
        gf.copytree(orig, dest)
        self.assertTrue(gf.file_exists(os.path.join(dest, "foo.bar")))
        gf.delete_directory(dest)
        gf.delete_directory(orig)

    def test_ensure_parent_directory(self):
        orig = gf.tmp_directory()
        tmp_path = os.path.join(orig, "foo.bar")
        tmp_parent = orig
        gf.ensure_parent_directory(tmp_path)
        self.assertTrue(gf.directory_exists(tmp_parent))
        tmp_path = os.path.join(orig, "foo/bar.baz")
        tmp_parent = os.path.join(orig, "foo")
        gf.ensure_parent_directory(tmp_path)
        self.assertTrue(gf.directory_exists(tmp_parent))
        tmp_path = os.path.join(orig, "bar")
        gf.ensure_parent_directory(tmp_path, ensure_parent=False)
        self.assertTrue(gf.directory_exists(tmp_path))
        gf.delete_directory(orig)

    def test_ensure_parent_directory_parent_error(self):
        with self.assertRaises(OSError):
            gf.ensure_parent_directory("/foo/bar/baz")

    def test_ensure_parent_directory_no_parent_error(self):
        with self.assertRaises(OSError):
            gf.ensure_parent_directory("/foo/bar/baz", ensure_parent=False)

    def test_time_from_ttml(self):
        tests = [
            (None, 0),
            ("", 0),
            ("s", 0),
            ("0s", 0),
            ("000s", 0),
            ("1s", 1),
            ("001s", 1),
            ("1s", 1),
            ("001.234s", 1.234),
        ]
        for test in tests:
            self.assertEqual(gf.time_from_ttml(test[0]), test[1])

    def test_time_to_ttml(self):
        tests = [
            (None, "0.000s"),
            (0, "0.000s"),
            (1, "1.000s"),
            (1.234, "1.234s"),
        ]
        for test in tests:
            self.assertEqual(gf.time_to_ttml(test[0]), test[1])

    def test_time_from_ssmmm(self):
        tests = [
            (None, 0),
            ("", 0),
            ("0", 0),
            ("000", 0),
            ("1", 1),
            ("001", 1),
            ("1.234", 1.234),
            ("001.234", 1.234),
        ]
        for test in tests:
            self.assertEqual(gf.time_from_ssmmm(test[0]), test[1])

    def test_time_to_ssmm(self):
        tests = [
            (None, "0.000"),
            (0, "0.000"),
            (1, "1.000"),
            (1.234, "1.234"),
        ]
        for test in tests:
            self.assertEqual(gf.time_to_ssmmm(test[0]), test[1])

    def test_time_from_hhmmssmmm(self):
        tests = [
            (None, 0.000),
            ("", 0.000),
            ("23:45.678", 0.000), # no 2 ":"
            ("3:45.678", 0.000), # no 2 ":"
            ("45.678", 0.000), # no 2 ":"
            ("5.678", 0.000), # no 2 ":"
            ("5", 0.000), # no 2 ":"
            ("00:00:01", 0.000), # no "."
            ("1:23:45.678", 5025.678), # tolerate this (?)
            ("1:2:45.678", 3765.678), # tolerate this (?)
            ("1:23:4.678", 4984.678), # tolerate this (?)
            ("1:23:4.", 4984.000), # tolerate this (?)
            ("00:00:00.000", 0.000),
            ("00:00:12.000", 12.000),
            ("00:00:12.345", 12.345),
            ("00:01:00.000", 60),
            ("00:01:23.000", 83.000),
            ("00:01:23.456", 83.456),
            ("01:00:00.000", 3600.000),
            ("01:00:12.000", 3612.000),
            ("01:00:12.345", 3612.345),
            ("01:23:00.000", 4980.000),
            ("01:23:45.000", 5025.000),
            ("01:23:45.678", 5025.678),
        ]
        for test in tests:
            self.assertEqual(gf.time_from_hhmmssmmm(test[0]), test[1])

    def test_time_to_hhmmssmmm(self):
        tests = [
            (None, "00:00:00.000"),
            (0.000, "00:00:00.000"),
            (12.000, "00:00:12.000"),
            (12.345, "00:00:12.345"),
            (60, "00:01:00.000"),
            (83.000, "00:01:23.000"),
            (83.456, "00:01:23.456"),
            (3600.000, "01:00:00.000"),
            (3612.000, "01:00:12.000"),
            (3612.340, "01:00:12.340"), # numerical issues
            (4980.000, "01:23:00.000"),
            (5025.000, "01:23:45.000"),
            (5025.670, "01:23:45.670"), # numerical issues
        ]
        for test in tests:
            self.assertEqual(gf.time_to_hhmmssmmm(test[0]), test[1])

    def test_time_to_srt(self):
        tests = [
            (None, "00:00:00,000"),
            (0.000, "00:00:00,000"),
            (12.000, "00:00:12,000"),
            (12.345, "00:00:12,345"),
            (60, "00:01:00,000"),
            (83.000, "00:01:23,000"),
            (83.456, "00:01:23,456"),
            (3600.000, "01:00:00,000"),
            (3612.000, "01:00:12,000"),
            (3612.340, "01:00:12,340"), # numerical issues
            (4980.000, "01:23:00,000"),
            (5025.000, "01:23:45,000"),
            (5025.670, "01:23:45,670"), # numerical issues
        ]
        for test in tests:
            self.assertEqual(gf.time_to_srt(test[0]), test[1])

    def test_split_url(self):
        tests = [
            (None, (None, None)),
            ("", ("", None)),
            ("foo", ("foo", None)),
            ("foo.html", ("foo.html", None)),
            ("foo.html#", ("foo.html", "")),
            ("foo.html#id", ("foo.html", "id")),
            ("foo.html#id#bad", ("foo.html", "id")),
        ]
        for test in tests:
            self.assertEqual(gf.split_url(test[0]), test[1])

    def test_is_posix(self):
        # TODO
        pass

    def test_fix_slash(self):
        # TODO
        pass

    def test_can_run_c_extension(self):
        gf.can_run_c_extension()
        gf.can_run_c_extension("cdtw")
        gf.can_run_c_extension("cew")
        gf.can_run_c_extension("cmfcc")
        gf.can_run_c_extension("foo")
        gf.can_run_c_extension("bar")

    def test_run_c_extension_with_fallback(self):
        #TODO
        pass

    def test_file_can_be_read_true(self):
        handler, path = gf.tmp_file()
        self.assertTrue(gf.file_can_be_read(path))
        gf.delete_file(handler, path)

    def test_file_can_be_read_false(self):
        path = "/foo/bar/baz"
        self.assertFalse(gf.file_can_be_read(path))

    def test_file_can_be_written_true(self):
        handler, path = gf.tmp_file()
        self.assertTrue(gf.file_can_be_written(path))
        gf.delete_file(handler, path)

    def test_file_can_be_written_false(self):
        path = "/foo/bar/baz"
        self.assertFalse(gf.file_can_be_written(path))

    def test_directory_exists_true(self):
        orig = gf.tmp_directory()
        self.assertTrue(gf.directory_exists(orig))
        gf.delete_directory(orig)

    def test_directory_exists_false(self):
        orig = "/foo/bar/baz"
        self.assertFalse(gf.directory_exists(orig))

    def test_file_exists_true(self):
        handler, path = gf.tmp_file()
        self.assertTrue(gf.file_exists(path))
        gf.delete_file(handler, path)

    def test_file_exists_false(self):
        path = "/foo/bar/baz"
        self.assertFalse(gf.file_exists(path))

    def test_file_size_nonzero(self):
        handler, path = gf.tmp_file()
        with io.open(path, "w", encoding="utf-8") as tmp_file:
            tmp_file.write(u"Foo bar")
        self.assertEqual(gf.file_size(path), 7)
        gf.delete_file(handler, path)

    def test_file_size_zero(self):
        handler, path = gf.tmp_file()
        self.assertEqual(gf.file_size(path), 0)
        gf.delete_file(handler, path)

    def test_file_size_not_existing(self):
        path = "/foo/bar/baz"
        self.assertEqual(gf.file_size(path), -1)

    def test_delete_directory_existing(self):
        orig = gf.tmp_directory()
        self.assertTrue(gf.directory_exists(orig))
        gf.delete_directory(orig)
        self.assertFalse(gf.directory_exists(orig))

    def test_delete_directory_not_existing(self):
        orig = "/foo/bar/baz"
        self.assertFalse(gf.directory_exists(orig))
        gf.delete_directory(orig)
        self.assertFalse(gf.directory_exists(orig))

    def test_delete_file_existing(self):
        handler, path = gf.tmp_file()
        self.assertTrue(gf.file_exists(path))
        gf.delete_file(handler, path)
        self.assertFalse(gf.file_exists(path))

    def test_delete_file_not_existing(self):
        handler = None
        path = "/foo/bar/baz"
        self.assertFalse(gf.file_exists(path))
        gf.delete_file(handler, path)
        self.assertFalse(gf.file_exists(path))

    def test_get_rel_path(self):
        tests = [
            ("res", "aeneas/tools/", "aeneas/tools/res"),
            ("res/foo", "aeneas/tools/", "aeneas/tools/res/foo"),
            ("res/foo/bar.baz", "aeneas/tools/", "aeneas/tools/res/foo/bar.baz"),
            ("../tests", "aeneas/tools/", "aeneas/tests"),
            ("../tests/foo", "aeneas/tools/", "aeneas/tests/foo"),
            ("../tests/foo/bar.baz", "aeneas/tools/", "aeneas/tests/foo/bar.baz"),
            ("../..", "aeneas/tools/", "."),
            ("res", ".", "res"),
            ("res/foo", ".", "res/foo"),
            ("res/foo/bar.baz", ".", "res/foo/bar.baz"),
        ]
        for test in tests:
            self.assertEqual(gf.get_rel_path(test[0], test[1], False), test[2])

    def test_get_abs_path(self):
        base = os.path.dirname(os.path.realpath(sys.argv[0]))
        tests = [
            ("res", "aeneas/tools/somefile.py", os.path.join(base, "aeneas/tools/res")),
            ("res/foo", "aeneas/tools/somefile.py", os.path.join(base, "aeneas/tools/res/foo")),
            ("res/bar.baz", "aeneas/tools/somefile.py", os.path.join(base, "aeneas/tools/res/bar.baz")),
            ("res", "/aeneas/tools/somefile.py", "/aeneas/tools/res"),
            ("res/foo", "/aeneas/tools/somefile.py", "/aeneas/tools/res/foo"),
            ("res/bar.baz", "/aeneas/tools/somefile.py", "/aeneas/tools/res/bar.baz"),
        ]
        for test in tests:
            self.assertEqual(gf.get_abs_path(test[0], test[1]), test[2])

    def test_read_file_bytes(self):
        handler, path = gf.tmp_file()
        with io.open(path, "w", encoding="utf-8") as tmp_file:
            tmp_file.write(u"Foo bar")
        contents = gf.read_file_bytes(path)
        self.assertTrue(gf.is_bytes(contents))
        self.assertEqual(len(contents), 7)
        gf.delete_file(handler, path)

    def test_human_readable_number(self):
        tests = [
            (0, "0.0"),
            (0.0, "0.0"),
            (1, "1.0"),
            (1.0, "1.0"),
            (10, "10.0"),
            (100, "100.0"),
            (1000, "1000.0"),
            (2000, "2.0K"),
            (3000, "2.9K"),
            (1000000, "976.6K"),
            (2000000, "1.9M"),
            (3000000, "2.9M"),
        ]
        for test in tests:
            self.assertEqual(gf.human_readable_number(test[0]), test[1])

    def test_is_unicode(self):
        tests = [
            (None, False),
            (u"", True),
            (u"foo", True),
            (u"fox99", True),
            (b"foo", False),
            ([], False),
            ([u"foo"], False),
            ({u"foo": u"baz"}, False),
        ]
        if gf.PY2:
            tests.extend([
                ("", False),
                ("foo", False),
                ("fox99", False),
            ])
        else:
            tests.extend([
                ("", True),
                ("foo", True),
                ("fox99", True),
            ])
        for test in tests:
            self.assertEqual(gf.is_unicode(test[0]), test[1])

    def test_is_utf8_encoded(self):
        tests = [
            (u"foo".encode("ascii"), True),
            (u"foo".encode("latin-1"), True),
            (u"foo".encode("utf-8"), True),
            (u"foo".encode("utf-16"), False),
            (u"foo".encode("utf-32"), False),
            (u"foà".encode("latin-1"), False),
            (u"foà".encode("utf-8"), True),
            (u"foà".encode("utf-16"), False),
            (u"foà".encode("utf-32"), False),
        ]
        for test in tests:
            self.assertEqual(gf.is_utf8_encoded(test[0]), test[1])

    def test_is_bytes(self):
        tests = [
            (None, False),
            (b"", True),
            (b"foo", True),
            (b"fo\xff", True),
            (u"foo", False),
            ([], False),
            ([b"foo"], False),
            ({b"foo": b"baz"}, False),
        ]
        if gf.PY2:
            tests.extend([
                ("", True),
                ("foo", True),
                ("fox99", True),
            ])
        else:
            tests.extend([
                ("", False),
                ("foo", False),
                ("fox99", False),
            ])
        for test in tests:
            self.assertEqual(gf.is_bytes(test[0]), test[1])

    def test_safe_str(self):
        tests = [
            (None, None),
            (u"", ""),
            (u"foo", "foo"),
            (u"foà", "foà"),
        ]
        for test in tests:
            self.assertEqual(gf.safe_str(test[0]), test[1])

    def test_safe_unichr(self):
        tests = [
            (65, u"A"),
            (90, u"Z"),
            (0x20, u"\u0020"),
            (0x200, u"\u0200"),
            (0x2000, u"\u2000")
        ]
        for test in tests:
            self.assertEqual(gf.safe_unichr(test[0]), test[1])

    def test_safe_unicode(self):
        tests = [
            (None, None),
            ("", u""),
            ("foo", u"foo"),
            ("foà", u"foà"),
            (u"", u""),
            (u"foo", u"foo"),
            (u"foà", u"foà"),
        ]
        for test in tests:
            self.assertEqual(gf.safe_unicode(test[0]), test[1])

    def test_safe_bytes(self):
        tests = [
            (None, None),
            ("", b""),
            ("foo", b"foo"),
            (b"", b""),
            (b"foo", b"foo"),
            (b"fo\x99", b"fo\x99"),
        ]
        for test in tests:
            self.assertEqual(gf.safe_bytes(test[0]), test[1])

    def test_safe_unicode_stdin(self):
        #TODO
        pass

    def test_safe_print(self):
        #TODO
        pass

    def test_object_to_unicode(self):
        #TODO
        pass

    def test_object_to_bytes(self):
        #TODO
        pass



if __name__ == '__main__':
    unittest.main()



