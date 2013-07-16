#-*- coding:utf-8 -*-
from fabric.api import run, sudo, put, env, local, settings, hide
from fabric.decorators import task, runs_once, parallel
import re

@task(default=True)
@parallel
def dtop(dstat_file='/tmp/dstat',dstat_opt='Tclmdrn',interval='1'):
    """ fab -H 192.168.1.1,localhost dtop """
    index = env.hosts.index(env.host)
    max_host_len = _get_max_host_len()
    start_line = 3

    while True:
        try:
            with settings( hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
                result = run(dstat_file + ' -' + dstat_opt + ' ' + interval +' 1')
                if result.failed:
                    result = run('dstat -Tclmdrn 1 1')

            with settings( hide('warnings', 'running', 'stderr'), warn_only=True):
                lines = result.stdout.splitlines()
                try:
                    host_stat = lines.pop()
                    _init_console(lines, max_host_len)
                except IndexError:
                    host_stat = 'Can not execute dstat'

                line_control = '\x1b[' + str(index + start_line) + ';0H'
                print line_control,
                print '%s%s%s' % (env.host.ljust(max_host_len), '\t', host_stat)
        except KeyboardInterrupt:
            break

@runs_once
def _init_console(lines, max_host_len):
    local('clear')
    first_line = lines.pop(0)
    if re.match('^Terminal width too small', first_line):
        first_line = lines.pop(0)

    print '%s\t%s' % ( ' ' * max_host_len, first_line )
    print '%s\t%s' % ( ' ' * max_host_len, lines.pop(0) )

@runs_once
def _get_max_host_len():
    max_host_len = 0
    for hostname in env.hosts:
        host_len = len(hostname)
        if max_host_len < host_len:
            max_host_len = host_len
    return max_host_len

@task
def put_dstat(dstat_file='~/src/dstat',dst='/tmp'):
    """ fab -H 192.168.11.1,localhost -P dtop.put_dstat:dstat_file=/path/to/dstat,dst=/tmp """
    put(dstat_file, dst)
    run('chmod 755 ' + dst + '/dstat')
