#! /usr/bin/python
# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
#
# Copyright (c) 2015 Jun Omae
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import ctypes
import os.path
import sys
import types
from ctypes import POINTER


SERVER_DEAD = 0
SERVER_STARTING = 1
SERVER_READY = 2
SERVER_BUSY_READ = 3
SERVER_BUSY_WRITE = 4
SERVER_BUSY_KEEPALIVE = 5
SERVER_BUSY_LOG = 6
SERVER_BUSY_DNS = 7
SERVER_CLOSING = 8
SERVER_GRACEFUL = 9
SERVER_IDLE_KILL = 10


def incomplete_type_ptr(name):
    cls = types.ClassType(name, (ctypes.Structure,), {})
    return POINTER(cls)


apr = None
apr_initialize = None
apr_pool_create_ex = None
apr_pool_destroy = None
apr_shm_attach = None
apr_shm_baseaddr_get = None
apr_shm_detach = None
apr_shm_size_get = None
apr_terminate = None
apr_time_now = None

ap_generation_t = ctypes.c_int
ap_scoreboard_e = ctypes.c_int
apr_off_t = ctypes.c_longlong
apr_os_thread_t = ctypes.c_ulong
apr_status_t = ctypes.c_int
apr_time_t = ctypes.c_int64
clock_t = ctypes.c_long
pid_t = ctypes.c_int

apr_abortfunc_t = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int)
apr_allocator_t_ptr = incomplete_type_ptr('apr_allocator_t')
apr_pool_t_ptr = incomplete_type_ptr('apr_pool_t')
apr_shm_t_ptr = incomplete_type_ptr('apr_shm_t')


def initialize():
    g = globals()
    def declare(name, restype, *argtypes):
        prototype = ctypes.CFUNCTYPE(restype, *argtypes)
        g[name] = fn = prototype((name, apr))
        return fn
    g['apr'] = ctypes.cdll.LoadLibrary('libapr-1.so.0')
    declare('apr_initialize', apr_status_t)
    declare('apr_terminate', None)
    declare('apr_pool_create_ex',
            apr_status_t, POINTER(apr_pool_t_ptr), apr_pool_t_ptr,
            apr_abortfunc_t, apr_allocator_t_ptr)
    declare('apr_pool_destroy', None, apr_pool_t_ptr)
    declare('apr_shm_attach', apr_status_t,
            POINTER(apr_shm_t_ptr), ctypes.c_char_p, apr_pool_t_ptr)
    declare('apr_shm_detach', apr_status_t, apr_shm_t_ptr)
    declare('apr_shm_baseaddr_get', ctypes.c_void_p, apr_shm_t_ptr)
    declare('apr_shm_size_get', ctypes.c_size_t, apr_shm_t_ptr)
    declare('apr_time_now', apr_time_t)


class StructTms(ctypes.Structure):
    _fields_ = [
        ('tms_utime', clock_t),
        ('tms_stime', clock_t),
        ('tms_cutime', clock_t),
        ('tms_cstime', clock_t),
        ]

    def __repr__(self):
        return unicode(self)

    def __unicode__(self):
        return '<struct tms utime=%d, stime=%d, cutime=%d, cstime=%d>' % \
               (self.tms_utime, self.tms_stime, self.tms_cutime,
                self.tms_cstime)


class GlobalScore(ctypes.Structure):
    _fields_ = [
        ('server_limit', ctypes.c_int),
        ('thread_limit', ctypes.c_int),
        ('sb_type', ap_scoreboard_e),
        ('running_generation', ctypes.c_int),
        ('restart_time', apr_time_t),
        ('lb_limit', ctypes.c_int),
        ]

    def __repr__(self):
        return unicode(self)

    def __unicode__(self):
        return '<GlobalScore server_limit=%r, thread_limit=%r, sb_type=%r, ' \
               'running_generation=%r, restart_time=%r, lb_limit=%r>' % \
               (self.server_limit, self.thread_limit, self.sb_type,
                self.running_generation, self.restart_time, self.lb_limit)


class ProcessScore(ctypes.Structure):
    _fields_ = [
        ('pid', pid_t),
        ('generation', ap_generation_t),
        ('sb_type', ap_scoreboard_e),
        ('quiescing', ctypes.c_int),
        ]

    def __repr__(self):
        return unicode(self)

    def __unicode__(self):
        return '<ProcessScore pid=%r, generation=%r, sb_type=%r, ' \
               'quiescing=%r>' % \
               (self.pid, self.generation, self.sb_type,
                self.quiescing)


class WorkerScore(ctypes.Structure):
    _fields_ = [
        ('thread_num', ctypes.c_int),
        ('tid', apr_os_thread_t),
        ('pid', pid_t),
        ('generation', ap_generation_t),
        ('status', ctypes.c_ubyte),
        ('access_count', ctypes.c_ulong),
        ('bytes_served', apr_off_t),
        ('my_access_count', ctypes.c_ulong),
        ('my_bytes_served', apr_off_t),
        ('conn_bytes', apr_off_t),
        ('conn_count', ctypes.c_ushort),
        ('start_time', apr_time_t),
        ('stop_time', apr_time_t),
        ('times', StructTms),
        ('last_used', apr_time_t),
        ('client', ctypes.c_char * 32),
        ('request', ctypes.c_char * 64),
        ('vhost', ctypes.c_char * 32),
        ]

    def __repr__(self):
        return unicode(self)

    def __unicode__(self):
        return '<WorkerScore thread_num=%r, tid=%r, pid=%r, generation=%r, ' \
               'status=%r, access_count=%r, bytes_served=%r, ' \
               'my_access_count=%r, my_bytes_served=%r, conn_bytes=%r, ' \
               'conn_count=%r, start_time=%r, stop_time=%r, times=%r, ' \
               'last_used=%r, client=%r, request=%r, vhost=%r>' % \
               (self.thread_num, self.tid, self.pid, self.generation,
                self.status, self.access_count, self.bytes_served,
                self.my_access_count, self.my_bytes_served, self.conn_bytes,
                self.conn_count, self.start_time, self.stop_time, self.times,
                self.last_used, self.client, self.request, self.vhost)


def create_scoreboard(server_limit, thread_limit):
    class Scoreboard(ctypes.Structure):
        _fields_ = [
            ('global_', GlobalScore),
            ('processes', ProcessScore * server_limit),
            ('workers', WorkerScore * (server_limit * thread_limit)),
            ]
    return Scoreboard()


def retrieve_scoreboard(filename):
    pool = apr_pool_t_ptr()
    shm = apr_shm_t_ptr()
    apr_pool_create_ex(ctypes.byref(pool), None, apr_abortfunc_t(), None)
    rv = apr_shm_attach(ctypes.byref(shm), filename, pool)
    if rv != 0:
        sys.stderr.write('Failed to attach to a shared memory segment: "%s" '
                         '(error %d)\n' % (filename, rv))
        return None
    try:
        baseattr = apr_shm_baseaddr_get(shm)
        size = apr_shm_size_get(shm)
        if ctypes.sizeof(GlobalScore) > size:
            sys.stderr.write('Scoreboard too smal (%d > %d)\n' %
                             (ctypes.sizeof(GlobalScore), size))
            return None
        global_ptr = ctypes.cast(baseattr, POINTER(GlobalScore))
        global_ = global_ptr[0]

        board = create_scoreboard(global_.server_limit,
                                  global_.thread_limit)
        if ctypes.sizeof(board) > size:
            sys.stderr.write('Scoreboard invalid size (%d > %d)\n' %
                             (ctypes.sizeof(board), size))
            return None
        ctypes.memmove(ctypes.byref(board), baseattr, ctypes.sizeof(board))
        return board
    finally:
        baseattr = global_ = global_ptr = None
        apr_shm_detach(shm)
        apr_pool_destroy(pool)


def show_scoreboard(board):
    access_count = 0
    bytes_served = 0
    busy_workers = 0
    idle_workers = 0
    thread_limit = board.global_.thread_limit
    scoreboard = []

    for idx, worker in enumerate(board.workers):
        process = board.processes[idx // thread_limit]
        status = worker.status
        access_count += worker.access_count
        bytes_served += worker.bytes_served
        if not process.quiescing and process.pid:
            if status == SERVER_READY:
                idle_workers += 1
            elif status not in (SERVER_DEAD, SERVER_STARTING,
                                SERVER_IDLE_KILL):
                busy_workers += 1
        scoreboard.append('.S_RWKLDCGI'[status])
    uptime = (apr_time_now() - board.global_.restart_time) / 1000000.0
    scoreboard = ''.join(scoreboard)

    print 'Total Accesses: %d' % access_count
    print 'Total kBytes: %d' % (bytes_served // 1024)
    print 'Uptime: %d' % long(uptime)
    if uptime > 0:
        print 'ReqPerSec: %g' % (float(access_count) / uptime)
        print 'BytesPerSec: %g' % (float(bytes_served) / uptime)
    if access_count > 0:
        print 'BytesPerReq: %d' % (bytes_served / access_count)
    print 'BusyWorkers: %d' % busy_workers
    print 'IdleWorkers: %d' % idle_workers
    print 'Scoreboard: %s' % scoreboard


def main():
    if len(sys.argv) != 2:
        progname = os.path.basename(sys.argv[0])
        sys.stderr.write("""\
Usage: %s ScoreBoardFile

You should configure Apache before running this script.

    LoadModule status_module modules/mod_status.so
    ExtendedStatus On
    ScoreBoardFile run/httpd.scoreboard

""" % progname)
        return 0
    filename = sys.argv[1]

    initialize()
    apr_initialize()
    try:
        board = retrieve_scoreboard(filename)
        if board:
            show_scoreboard(board)
            return 0
        else:
            return 1
    finally:
        apr_terminate()


if __name__ == '__main__':
    sys.exit(main())
