#!/usr/bin/env python2
#
#  File: test-afl-sancov.py
#
#  Purpose: Run afl-sancov through a series of tests to ensure proper operations
#           on the local system.
#
#  License (GNU General Public License):
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02111-1301,
#  USA
#

from aflsancov import *
import unittest
import os
import json
try:
    import subprocess32 as subprocess
except ImportError:
    import subprocess

class TestAflSanCov(unittest.TestCase):

    ### set a few paths
    tmp_file     = './tmp_cmd.out'

    top_out_dir  = './afl-out'
    sancov_dir = top_out_dir + '/sancov'
    dd_dir = sancov_dir + '/delta-diff'
    expects_dir = './expects'
    expects_ddmode_ubsan_dir = expects_dir + '/ddmode/ubsan'
    expects_ddnum_ubsan_dir = expects_dir + '/ddnum/ubsan'
    expects_ddmode_asan_dir = expects_dir + '/ddmode/asan'
    expects_ddnum_asan_dir = expects_dir + '/ddnum/asan'
    dd_filename1 = '/HARDEN:0001,SESSION000:id:000000,sig:06,src:000003,op:havoc,rep:2.json'
    dd_filename2 = '/HARDEN:0001,SESSION001:id:000000,sig:06,src:000003,op:havoc,rep:4.json'
    dd_file1 = dd_dir + dd_filename1
    dd_file2 = dd_dir + dd_filename2
    ## UBSAN
    expects_ddmode_ubsan_file1 = expects_ddmode_ubsan_dir + dd_filename1
    expects_ddmode_ubsan_file2 = expects_ddmode_ubsan_dir + dd_filename2
    expects_ddnum_ubsan_file1 = expects_ddnum_ubsan_dir + dd_filename1
    expects_ddnum_ubsan_file2 = expects_ddnum_ubsan_dir + dd_filename2
    ## ASAN
    expects_ddmode_asan_file1 = expects_ddmode_asan_dir + dd_filename1
    expects_ddmode_asan_file2 = expects_ddmode_asan_dir + dd_filename2
    expects_ddnum_asan_file1 = expects_ddnum_asan_dir + dd_filename1
    expects_ddnum_asan_file2 = expects_ddnum_asan_dir + dd_filename2

    expected_line_substring = 'afl-sancov/tests/test-sancov.c:main:25:3'

    def compare_json(self, file1, file2):

        with open(file1) as data_file1:
            data1 = json.load(data_file1)
        with open(file2) as data_file2:
            data2 = json.load(data_file2)

        self.assertEqual(data1["shrink-percent"], data2["shrink-percent"], 'Shrink percent did not match')
        self.assertEqual(data1["dice-linecount"], data2["dice-linecount"], 'Dice line count did not match')
        self.assertEqual(data1["slice-linecount"], data2["slice-linecount"], 'Slice line count did not match')
        self.assertEqual(data1["diff-node-spec"][0]["count"], data2["diff-node-spec"][0]["count"],
                         'Dice frequency did not match')
        self.assertTrue(self.expected_line_substring in data1["diff-node-spec"][0]["line"],
                        'Dice line did not match')
        self.assertEqual(data1["crashing-input"], data2["crashing-input"], 'Crashing input did not match')
        if 'parent-input' in data1 and 'parent-input' in data2:
            self.assertEqual(data1["parent-input"], data2["parent-input"], 'Parent input did not match')
        return True

    def test_version(self):
        self.assertFalse(AFLSancovReporter(['--version']).run())

    def test_overwrite_dir(self):
        args = ['-d', './afl-out', '-e "cat AFL_FILE | ./test-sancov-ubsan"', '--bin-path={}/test-sancov-ubsan'.format(os.getcwd()),
                '--sancov-path=/usr/bin/sancov-3.8', '--llvm-sym-path=/usr/bin/llvm-symbolizer-3.8',
                '--pysancov-path=/usr/local/bin/pysancov', '--crash-dir={}/unique'.format(os.getcwd())]
        reporter = AFLSancovReporter(args)
        self.assertTrue(reporter.run())

    def test_ddmode_ubsan(self):
        args = ['-d', './afl-out', '-e', 'cat AFL_FILE | ./test-sancov-ubsan', '--bin-path={}/test-sancov-ubsan'.format(os.getcwd()),
                '--sancov-path=/usr/bin/sancov-3.8', '--llvm-sym-path=/usr/bin/llvm-symbolizer-3.8',
                '--pysancov-path=/usr/local/bin/pysancov', '--crash-dir={}/unique'.format(os.getcwd()),'--overwrite']
        reporter = AFLSancovReporter(args)
        self.assertFalse(reporter.run())
        self.assertTrue(os.path.exists(self.dd_dir),
                        "No delta-diff dir generated during dd-mode invocation")
        self.assertTrue((os.path.exists(self.dd_file1) and os.path.exists(self.dd_file2)),
                        "Missing delta-diff file(s) during dd-mode invocation")

        self.assertTrue(self.compare_json(self.dd_file1, self.expects_ddmode_ubsan_file1),
                        "Delta-diff file {} does not match".format(self.dd_filename1))
        self.assertTrue(self.compare_json(self.dd_file2, self.expects_ddmode_ubsan_file2),
                        "Delta-diff file {} does not match".format(self.dd_filename2))

    def test_ddmode_ubsan_sancov_bug(self):
        args = ['-d', './afl-out', '-e', 'cat AFL_FILE | ./test-sancov-ubsan', '--bin-path={}/test-sancov-ubsan'.format(os.getcwd()),
                '--sancov-path=/usr/bin/sancov-3.8', '--llvm-sym-path=/usr/bin/llvm-symbolizer-3.8',
                '--pysancov-path=/usr/local/bin/pysancov', '--crash-dir={}/unique'.format(os.getcwd()),'--overwrite',
                '--sancov-bug']
        reporter = AFLSancovReporter(args)
        self.assertFalse(reporter.run())
        self.assertTrue(os.path.exists(self.dd_dir),
                        "No delta-diff dir generated during dd-mode invocation")
        self.assertTrue((os.path.exists(self.dd_file1) and os.path.exists(self.dd_file2)),
                        "Missing delta-diff file(s) during dd-mode invocation")

        self.assertTrue(self.compare_json(self.dd_file1, self.expects_ddmode_ubsan_file1),
                        "Delta-diff file {} does not match".format(self.dd_filename1))
        self.assertTrue(self.compare_json(self.dd_file2, self.expects_ddmode_ubsan_file2),
                        "Delta-diff file {} does not match".format(self.dd_filename2))

    def test_ddnum_ubsan(self):
        args = ['-d', './afl-out', '-e', 'cat AFL_FILE | ./test-sancov-ubsan', '--bin-path={}/test-sancov-ubsan'.format(os.getcwd()),
                '--sancov-path=/usr/bin/sancov-3.8', '--llvm-sym-path=/usr/bin/llvm-symbolizer-3.8',
                '--pysancov-path=/usr/local/bin/pysancov', '--overwrite', '--dd-num=3',
                '--crash-dir={}/unique'.format(os.getcwd())]
        reporter = AFLSancovReporter(args)
        self.assertFalse(reporter.run())
        self.assertTrue(os.path.exists(self.dd_dir),
                        "No delta-diff dir generated during dd-num invocation")
        self.assertTrue((os.path.exists(self.dd_file1) and os.path.exists(self.dd_file2)),
                        "Missing delta-diff file(s) during dd-num invocation")

        self.assertTrue(self.compare_json(self.dd_file1, self.expects_ddnum_ubsan_file1),
                        "Delta-diff file {} does not match".format(self.dd_filename1))
        self.assertTrue(self.compare_json(self.dd_file2, self.expects_ddnum_ubsan_file2),
                        "Delta-diff file {} does not match".format(self.dd_filename2))

    def test_ddnum_ubsan_sancov_bug(self):
        args = ['-d', './afl-out', '-e', 'cat AFL_FILE | ./test-sancov-ubsan',
                '--bin-path={}/test-sancov-ubsan'.format(os.getcwd()),
                '--sancov-path=/usr/bin/sancov-3.8', '--llvm-sym-path=/usr/bin/llvm-symbolizer-3.8',
                '--pysancov-path=/usr/local/bin/pysancov', '--overwrite', '--dd-num=3',
                '--crash-dir={}/unique'.format(os.getcwd()), '--sancov-bug']
        reporter = AFLSancovReporter(args)
        self.assertFalse(reporter.run())
        self.assertTrue(os.path.exists(self.dd_dir),
                        "No delta-diff dir generated during dd-num invocation")
        self.assertTrue((os.path.exists(self.dd_file1) and os.path.exists(self.dd_file2)),
                        "Missing delta-diff file(s) during dd-num invocation")

        self.assertTrue(self.compare_json(self.dd_file1, self.expects_ddnum_ubsan_file1),
                        "Delta-diff file {} does not match".format(self.dd_filename1))
        self.assertTrue(self.compare_json(self.dd_file2, self.expects_ddnum_ubsan_file2),
                        "Delta-diff file {} does not match".format(self.dd_filename2))


    def test_ddmode_asan(self):
        args = ['-d', './afl-out', '-e', 'cat AFL_FILE | ./test-sancov-asan',
                '--bin-path={}/test-sancov-asan'.format(os.getcwd()),
                '--sancov-path=/usr/bin/sancov-3.8', '--llvm-sym-path=/usr/bin/llvm-symbolizer-3.8',
                '--pysancov-path=/usr/local/bin/pysancov', '--crash-dir={}/unique'.format(os.getcwd()), '--overwrite',
                '--sanitizer=asan']
        reporter = AFLSancovReporter(args)
        self.assertFalse(reporter.run())
        self.assertTrue(os.path.exists(self.dd_dir),
                        "No delta-diff dir generated during dd-mode invocation")
        self.assertTrue((os.path.exists(self.dd_file1) and os.path.exists(self.dd_file2)),
                        "Missing delta-diff file(s) during dd-mode invocation")

        self.assertTrue(self.compare_json(self.dd_file1, self.expects_ddmode_asan_file1),
                        "Delta-diff file {} does not match".format(self.dd_filename1))
        self.assertTrue(self.compare_json(self.dd_file2, self.expects_ddmode_asan_file2),
                        "Delta-diff file {} does not match".format(self.dd_filename2))


    def test_ddmode_asan_sancov_bug(self):
        args = ['-d', './afl-out', '-e', 'cat AFL_FILE | ./test-sancov-asan',
                '--bin-path={}/test-sancov-asan'.format(os.getcwd()),
                '--sancov-path=/usr/bin/sancov-3.8', '--llvm-sym-path=/usr/bin/llvm-symbolizer-3.8',
                '--pysancov-path=/usr/local/bin/pysancov', '--crash-dir={}/unique'.format(os.getcwd()), '--overwrite',
                '--sancov-bug', '--sanitizer=asan']
        reporter = AFLSancovReporter(args)
        self.assertFalse(reporter.run())
        self.assertTrue(os.path.exists(self.dd_dir),
                        "No delta-diff dir generated during dd-mode invocation")
        self.assertTrue((os.path.exists(self.dd_file1) and os.path.exists(self.dd_file2)),
                        "Missing delta-diff file(s) during dd-mode invocation")

        self.assertTrue(self.compare_json(self.dd_file1, self.expects_ddmode_asan_file1),
                        "Delta-diff file {} does not match".format(self.dd_filename1))
        self.assertTrue(self.compare_json(self.dd_file2, self.expects_ddmode_asan_file2),
                        "Delta-diff file {} does not match".format(self.dd_filename2))


    def test_ddnum_asan(self):
        args = ['-d', './afl-out', '-e', 'cat AFL_FILE | ./test-sancov-asan',
                '--bin-path={}/test-sancov-asan'.format(os.getcwd()),
                '--sancov-path=/usr/bin/sancov-3.8', '--llvm-sym-path=/usr/bin/llvm-symbolizer-3.8',
                '--pysancov-path=/usr/local/bin/pysancov', '--overwrite', '--dd-num=3',
                '--crash-dir={}/unique'.format(os.getcwd()), '--sanitizer=asan']
        reporter = AFLSancovReporter(args)
        self.assertFalse(reporter.run())
        self.assertTrue(os.path.exists(self.dd_dir),
                        "No delta-diff dir generated during dd-num invocation")
        self.assertTrue((os.path.exists(self.dd_file1) and os.path.exists(self.dd_file2)),
                        "Missing delta-diff file(s) during dd-num invocation")

        self.assertTrue(self.compare_json(self.dd_file1, self.expects_ddnum_asan_file1),
                        "Delta-diff file {} does not match".format(self.dd_filename1))
        self.assertTrue(self.compare_json(self.dd_file2, self.expects_ddnum_asan_file2),
                        "Delta-diff file {} does not match".format(self.dd_filename2))


    def test_ddnum_asan_sancov_bug(self):
        args = ['-d', './afl-out', '-e', 'cat AFL_FILE | ./test-sancov-asan',
                '--bin-path={}/test-sancov-asan'.format(os.getcwd()),
                '--sancov-path=/usr/bin/sancov-3.8', '--llvm-sym-path=/usr/bin/llvm-symbolizer-3.8',
                '--pysancov-path=/usr/local/bin/pysancov', '--overwrite', '--dd-num=3',
                '--crash-dir={}/unique'.format(os.getcwd()), '--sancov-bug', '--sanitizer=asan']
        reporter = AFLSancovReporter(args)
        self.assertFalse(reporter.run())
        self.assertTrue(os.path.exists(self.dd_dir),
                        "No delta-diff dir generated during dd-num invocation")
        self.assertTrue((os.path.exists(self.dd_file1) and os.path.exists(self.dd_file2)),
                        "Missing delta-diff file(s) during dd-num invocation")

        self.assertTrue(self.compare_json(self.dd_file1, self.expects_ddnum_asan_file1),
                        "Delta-diff file {} does not match".format(self.dd_filename1))
        self.assertTrue(self.compare_json(self.dd_file2, self.expects_ddnum_asan_file2),
                        "Delta-diff file {} does not match".format(self.dd_filename2))

    def test_validate_cov_cmd(self):
        args = []
        reporter = AFLSancovReporter(args)
        # Checks no cov cmd
        self.assertTrue(reporter.run())
        args = ['-e', 'cat FILE | ./test-sancov-asan']
        reporter = AFLSancovReporter(args)
        # Checks incorrect cov cmd
        self.assertTrue(reporter.run())
        args = ['-e', 'cat AFL_FILE | ./test-sancov-asan']
        reporter = AFLSancovReporter(args)
        # Checks no afl fuzz dir
        self.assertTrue(reporter.run())
        args.extend(['-d', './afl-out'])
        reporter = AFLSancovReporter(args)
        # Checks no crash dir
        self.assertTrue(reporter.run())
        args.extend(['--crash-dir={}/unique'.format(os.getcwd())])
        reporter = AFLSancovReporter(args)
        # Checks no bin path
        self.assertTrue(reporter.run())
        args.extend(['--bin-path={}/test-sancov-noexist'.format(os.getcwd())])
        reporter = AFLSancovReporter(args)
        # Checks incorrect bin path
        self.assertTrue(reporter.run())
        args[len(args)-1] = '--bin-path={}/test-sancov-ubsan'.format(os.getcwd())
        args.extend(['--sancov-path=sancov-noexist'])
        reporter = AFLSancovReporter(args)
        # Checks incorrect sancov path
        self.assertTrue(reporter.run())
        args[len(args)-1] = '--pysancov-path=pysancov-noexist'
        reporter = AFLSancovReporter(args)
        # Checks incorrect pysancov path
        self.assertTrue(reporter.run())
        args[len(args)-1] = '--llvm-sym-path=llvm-symbolizer-noexist'
        reporter = AFLSancovReporter(args)
        # Checks incorrect llvm-sym path
        self.assertTrue(reporter.run())

if __name__ == "__main__":
    unittest.main()
