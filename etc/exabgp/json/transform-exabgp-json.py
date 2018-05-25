#!/usr/bin/env python
import sys
import socket
import json
from pprint import pprint

sock = socket.socket()
sock.connect( ('ELKSERVERIP', 5150) )

def get_attrs(json_in):
    attrs = {}
    attrs['neighbor'] =     json_in['neighbor']['address']['peer']
    attrs['peeras'] =       json_in['neighbor']['asn']['peer']

    msgtype =               json_in['neighbor']['message'].keys()[0]
    attrs['msgtype'] = msgtype

    if 'announce' in        json_in['neighbor']['message'][msgtype].keys():
      action = 'announce'
    elif 'withdraw' in      json_in['neighbor']['message'][msgtype].keys():
      action = 'withdraw'
    else:
      print "funky action in this message, %s" % json_in
    attrs['action'] = action

    afisafi  =              json_in['neighbor']['message'][msgtype][action].keys()[0]
    attrs['afi'] = afisafi.split()[0]
    attrs['safi'] = afisafi.split()[1]

    if action == 'announce':
      nexthop =             json_in['neighbor']['message'][msgtype][action][afisafi].keys()[0]
      attrs['nexthop'] =      nexthop

      # simple mapping, but substitute hyphens since elastic doesn't like em
      simple_attributes = ['local-preference','origin','med','originator-id','cluster-list']
      for simple_attribute in simple_attributes:
        if json_in['neighbor']['message'][msgtype]['attribute'].has_key(simple_attribute):
          attrs[simple_attribute.replace('-','')] = json_in['neighbor']['message'][msgtype]['attribute'][simple_attribute]

      # as-path needs to be casted from list to string
      if json_in['neighbor']['message'][msgtype]['attribute'].has_key('as-path'):
        if type(json_in['neighbor']['message'][msgtype]['attribute']['as-path']) == type([]):
          attrs['aspath'] = ' '.join(str(x) for x in json_in['neighbor']['message'][msgtype]['attribute']['as-path'])
        else:
          attrs['aspath'] =   json_in['neighbor']['message'][msgtype]['attribute']['as-path']

      # ext comms are string/value pairs by exa, only keep strings
      if json_in['neighbor']['message'][msgtype]['attribute'].has_key('extended-community'):
        extcomms = []
        for extcomm in json_in['neighbor']['message'][msgtype]['attribute']['extended-community']:
          extcomms.append(extcomm['string'])
        attrs['extcomms'] = extcomms

      # regular comms are lists, rewrite to colon=separated
      if json_in['neighbor']['message'][msgtype]['attribute'].has_key('community'):
        comms = []
        for comm in json_in['neighbor']['message'][msgtype]['attribute']['community']:
          comms.append("%s:%s" % (comm[0],comm[1]))
        attrs['community'] = comms
    return attrs

def get_evpn_routes(announce_in):
    announce = {}
    announce['rd'] =           announce_in['rd']
    routetype =                announce_in['code']
    routetypename =            announce_in['name']
    announce['routetype'] =    routetype
    announce['routetypename'] =    routetypename
    if routetype == 1:
      announce['esi'] = announce_in['esi']
      announce['ethernettag'] = announce_in['ethernet-tag']
      announce['label'] = announce_in['label']
    elif routetype == 2:
      announce['esi'] = announce_in['esi']
      announce['mac'] = announce_in['mac']
      announce['ethernettag'] = announce_in['ethernet-tag']
      try:
        announce['ip'] = announce_in['ip']
      except KeyError:
        pass
      announce['label'] = announce_in['label']
    elif routetype == 3:
      announce['ethernettag'] = announce_in['ethernet-tag']
      announce['ip'] = announce_in['ip']
    elif routetype == 4:
      announce['ip'] = announce_in['ip']
      announce['esi'] = announce_in['esi']
    elif routetype == 5:
      pass
    else: # not supported
      pass
    return announce

def get_mpls_vpn_routes(announce_in):
    announce = {}
    announce['rd'] = announce_in['rd']
    announce['label'] = announce_in['label']
    announce['prefix'] = announce_in['nlri']

    return announce

def get_unicast_routes(announce_in):
    announce = {}
    announce['prefix'] = announce_in['nlri']

    return announce

def get_flow_routes(announce_in):
    announce = {}
    announce['rule'] = announce_in['string']
    return announce

logfile = open('/tmp/transform.log','a')
lala = open('/tmp/lala.log','w')
counter = 0
while True:
    try:
        line = sys.stdin.readline().strip()
        pprint(line, stream=lala)
        if line == "":
            counter += 1
            if counter > 100:
                break
            continue
        counter = 0
        json_in = json.loads(line)
        json_out_list = []

        #logfile.write(line)
        attrs = get_attrs(json_in)
        attrs['orig'] = line # only when developing/troubleshooting
        #print "ATTRS:",attrs
        routes_to_parse = []
        if attrs['action'] == 'announce':
          routes_to_parse = json_in['neighbor']['message'][attrs['msgtype']][attrs['action']][attrs['afi'] + ' ' + attrs['safi']][attrs['nexthop']]
        elif attrs['action'] == 'withdraw':
          routes_to_parse = json_in['neighbor']['message'][attrs['msgtype']][attrs['action']][attrs['afi'] + ' ' + attrs['safi']]
        else:
          print "ERROR: we're not supposed to get here, funky action in ", line
        #print "RTP:", routes_to_parse
        for route in routes_to_parse:
          newroute = {}
          newroute.update(attrs)
          if attrs['safi'] == 'evpn':
            newroute.update(get_evpn_routes(route))
            json_newroute = json.dumps(newroute)
            json_out_list.append(json_newroute)
          elif attrs['safi'] == 'mpls-vpn':
            newroute.update(get_mpls_vpn_routes(route))
            json_newroute = json.dumps(newroute)
            json_out_list.append(json_newroute)
          elif attrs['safi'] == 'unicast':
            newroute.update(get_unicast_routes(route))
            json_newroute = json.dumps(newroute)
            json_out_list.append(json_newroute)
          elif attrs['safi'] == 'flow':
            newroute.update(get_flow_routes(route))
            json_newroute = json.dumps(newroute)
            json_out_list.append(json_newroute)
          else:
            logfile.write(line)
        #print "OUT LIST:",len(json_out_list), pprint(json_out_list)
        msg = '\n'.join(json_out_list)
        #print "MSG", type(msg),len(msg),msg
        sock.sendall(msg + '\n')
    except KeyboardInterrupt:
        sock.close()
#        logfile.close()
    except IOError:
        # most likely a signal during readline
        sock.close()
#        logfile.close()

sock.close()
#logfile.close()
