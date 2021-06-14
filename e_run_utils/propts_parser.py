#!/usr/bin/python
import sys
sys.path.append('/slowfs/dcopt105/dcpv_cl01/scripts/')
import os
import glob


def read_propts(propts):
    '''Read a propts file and return a string with all lines'''
    read_propts =''
    if os.path.isfile(propts):
        f = open(propts, 'r')
        read_propts = f.read().splitlines()
        f.close()
    else:
        print propts,"isn\'t a file"
    return read_propts

def get_designs(propts):
    '''Return design list from propts file'''
    r_propts = read_propts(propts)
    
    flag_design = 0
    designs = []
    
    for line in r_propts:
        #if 'designs:' in line and not(line.startswith(':')):
        if line.startswith('designs:') and not(line.startswith(':')):
            # print line
            flag_design = 1
            one_line_designs = line.split(' ')
            #print one_line_designs
            if len(one_line_designs) > 1:
                if len(one_line_designs) ==2 and one_line_designs[-1] == '':
                    pass
                else:
                    designs.extend(one_line_designs[1:])
                    designs[:] = (value for value in designs if value != '')
                    flag_design = 0
        elif flag_design:
            if not(line.startswith('#')) and not(line.startswith(':')) and not(line.startswith('\n')) and not(line.startswith(' ')):
                flag_design = 0
                continue
            # print line
            designs.append(line)
        else:
            pass
    #print designs
    designs = [ x for x in designs if not(x.strip(' ').startswith('#')) and not(x.strip(' ').startswith('\n')) ] #remove comments and newlines
    designs = [ x.strip('\n').strip(' ').strip('::').strip(' ') for x in designs]
    #if designs are all in one line split it and add to designs list
    for design in designs:
        if ' ' in design:
            designs.extend(design.split(' '))
            designs.remove(design)
    #print designs
    return designs

def get_flows(propts):
    '''Return flows list from propts file'''
    r_propts = read_propts(propts)
    
    flag_flow = 0
    flows = []
    
    for line in r_propts:
        #if 'flows:' in line:
        if line.startswith('flows:') and not(line.startswith(':')):
            # print line
            flag_flow = 1
            one_line_flows = line.split(' ')
            #print one_line_flows
            if len(one_line_flows) > 1:
                if len(one_line_flows) ==2 and one_line_flows[-1] == '':
                    pass
                else:
                    flows.extend(one_line_flows[1:])
                    flows[:] = (value for value in flows if value != '')
                    flag_design = 0
        elif flag_flow:
            if not(line.startswith('#')) and not(line.startswith(':')) and not(line.startswith('\n')) and not(line.startswith(' ')):
                flag_flow = 0
                continue
            # print line
            flows.append(line)
        else:
            pass
    #print flows
    flows = [ x for x in flows if not(x.strip(' ').startswith('#')) and not(x.strip(' ').startswith('\n')) ] #remove comments and newlines
    flows = [ x.strip('\n').strip(' ').strip('::').strip(' ') for x in flows]
    #if flows are all in one line split it and add to flows list
    for flow in flows:
        if ' ' in flow:
            flows.extend(flow.split(' '))
            flows.remove(flow)
    #print flows
    return flows

def get_flows_title(propts):
    flows = get_flows(propts)
    r_propts = read_propts(propts)
    flows_titles = {}
    for line in r_propts:
        for flow in flows:
            if flow + '.title' in line:
                title = line.split(':')[-1]
                while ' ' in title[0]:
                    title = title[1:]
                flows_titles.update({flow:title})
    return flows_titles


# def print_all(propts):
#     print get_flows(propts)

propts = 'propts.cfg'

print(get_flows(propts))