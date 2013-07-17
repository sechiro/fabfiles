#-*- coding:utf-8 -*-
from fabric.api import run, sudo, put, env, local, settings, hide
from fabric.decorators import task, runs_once, parallel
import re

@task(default=True)
@parallel
def dtop(dstat_file='/tmp/dstat',dstat_opts='-Tclmdrn',interval='1'):
    """ fab -H 192.168.1.1,localhost dtop """
    index = env.hosts.index(env.host)
    max_host_len = _get_max_host_len()
    start_line = 3

    while True:
        try:
            with settings( hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
                result = run(dstat_file + ' ' + dstat_opts + ' ' + interval +' 1')
                if result.failed:
                    result = run('dstat ' + dstat_opts + ' ' + interval + ' 1')

            with settings( hide('warnings', 'running', 'stderr'), warn_only=True):
                lines = result.stdout.splitlines()
                try:
                    host_stat = lines.pop()
                    _init_console()
                    _display_header(lines, max_host_len)
                except IndexError:
                    host_stat = 'Can not run dstat! Run "fab dtop.put_dstat" task.'

                # ホストリストの順に描画行を決定して、そこにカーソルを移動する
                line_control = '\x1b[' + str(index + start_line) + ';0H'
                print line_control,
                print '%s%s%s' % (env.host.ljust(max_host_len), '\t', host_stat)
        except KeyboardInterrupt:
            line_control = '\x1b[0;0B' # 最後の行に移動
            print line_control,
            break

@runs_once
def _init_console():
    """ 最初の1回だけコンソール画面をクリアする """
    local('clear')

def _display_header(lines, max_host_len):
    """ 最初の2行にヘッダ行を表示する """
    first_line = lines.pop(0)
    if re.match('(Terminal width too small)|(You did not select any stats)', first_line):
        first_line = lines.pop(0)
    elif first_line == 'Can not execute dstat':
        return

    line_control = '\x1b[0;0H' # 最初の行に移動
    print line_control,
    print '%s\t%s' % ( ' ' * max_host_len, first_line )
    print '%s\t%s' % ( ' ' * max_host_len, lines.pop(0) )

@runs_once
def _get_max_host_len():
    """ 表示成形用に最も長い文字数のホストの文字数を返す """
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
    run('chmod +x ' + dst + '/dstat')
