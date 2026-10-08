#!/usr/bin/ruby --disable-gems
require 'json'
require 'socket'
r = {}
r['workspace_read'] = File.read('visible.txt').strip
File.write('actor-written.txt', "ACTOR_TOOL_WRITE_OK\n")
r['workspace_write'] = File.read('actor-written.txt').strip
JSON.parse(File.read('probe-paths.json')).each do |label, path|
  begin
    File.read(path)
    r[label] = {'status' => 'UNEXPECTED_READ_ALLOWED'}
  rescue Errno::EPERM, Errno::EACCES => e
    r[label] = {'status' => 'DENIED', 'error' => e.message, 'errno' => e.errno}
  rescue StandardError => e
    r[label] = {'status' => 'UNVERIFIED', 'error' => e.message, 'class' => e.class.name}
  end
end
{'direct_external_ip' => '1.1.1.1', 'external_github' => 'github.com'}.each do |label, host|
  begin
    Socket.tcp(host, 443, connect_timeout: 3) { |socket| socket.close }
    r[label] = {'status' => 'UNEXPECTED_CONNECTION_ALLOWED'}
  rescue Errno::EPERM, Errno::EACCES => e
    r[label] = {'status' => 'DENIED', 'error' => e.message, 'errno' => e.errno}
  rescue StandardError => e
    r[label] = {'status' => 'UNVERIFIED', 'error' => e.message, 'class' => e.class.name}
  end
end
File.write('probe-results.json', JSON.pretty_generate(r) + "\n")
puts JSON.generate(r)
