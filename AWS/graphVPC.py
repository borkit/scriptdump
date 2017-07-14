#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generate dot file for vpc routing map
can use with GraphViz: http://www.graphviz.org/Download..php
"""

import sys
import boto.ec2
import boto.vpc

def dprint (body):
#    print >> sys.stderr, body
    return

e = boto.ec2.connect_to_region('us-east-1')
v = boto.vpc.connect_to_region('us-east-1')

vpcs=v.get_all_vpcs()
print vpcs

argvs = sys.argv
if len(argvs) != 2:
    print "usage : "+argvs[0]+" vpc-xxxxxxxx"
    print "\navailable vpcs:"
    if len(vpcs) == 0:
        print "no VPC available"
    else:
        for vpc in vpcs:
            print "\t"+vpc.id
        sys.exit()
else:
    target=argvs[1]

instances=e.get_all_instances()
route_tables=v.get_all_route_tables()
subnets=v.get_all_subnets()

instance={}
for i in instances:
    instance[i.instances[0].id]=i.instances[0]

route={}
route_table_id={}
for route_table in route_tables:
    route_table.id
    route[route_table.id]=route_table.routes
    for association in route_table.associations:
        if association.main == True:
            route_table_id[route_table.vpc_id]=route_table.id
        else:
            route_table_id[association.subnet_id]=route_table.id

used={}
for vpc in vpcs:
    print vpc
    if vpc.id != target:
        next
    print "digraph G{"
    dprint(vpc.id)
    for subnet in subnets:
        if subnet.vpc_id == target:
            dprint(subnet.id)
            print "\t\t"+subnet.id.replace("-","_")+'[ label="'+subnet.cidr_block+'"]'
            if route_table_id.get(subnet.id)==None:
                route_entries=route[route_table_id[vpc.id]]
            else:
                route_entries=route[route_table_id[subnet.id]]
            for route_entry in route_entries:
                if route_entry.gateway_id != None and route_entry.gateway_id != "local":
                    dprint(route_entry.destination_cidr_block + " -> " +route_entry.gateway_id)
                    print "\t\t"+subnet.id.replace("-","_") + " -> " + route_entry.gateway_id.replace("-","_") + '[ label = "'+route_entry.destination_cidr_block+'"]'
                    if used.get(route_entry.gateway_id)==None:
                        print route_entry.gateway_id.replace("-","_") + '[ label="'+route_entry.gateway_id+'"]'
                        used[route_entry.gateway_id]=True
                if route_entry.instance_id != None:
                    i=instance[route_entry.instance_id]
                    dprint(route_entry.destination_cidr_block + " -> " +route_entry.instance_id + " in "+ i.subnet_id)
                    print "\t\t"+subnet.id.replace("-","_") + " -> " + route_entry.instance_id.replace("-","_") + '[ label = "'+route_entry.destination_cidr_block+'"]'
                    if used.get(route_entry.instance_id)==None:
                        print route_entry.instance_id.replace("-","_") + '[ label="'+route_entry.instance_id+'"]'
                        print route_entry.instance_id.replace("-","_") + " -> " + i.subnet_id.replace("-","_")
                        used[route_entry.instance_id]=True
    print "}"
