import os, re, pprint

pp = pprint.PrettyPrinter(indent=2)


start_date = '2020/12/23'
end_date   = '2020/12/31'


targets = '''
iloti
rjk
'''.strip().split('\n')


new_targets = []
for t in targets:
    fcn = t.strip().split('+')[0]
    if fcn != None : new_targets.append(fcn)

targets = new_targets 

print(targets)

cls_cmd     = 'p4 changes -L //synthesis/spf/r2020.09_sp/dev/...@%s,%s'%(start_date,end_date)
# cls_cmd     = 'p4 changes -L //synthesis/spf/q2019.12_sp/dev/...@%s,%s'%(start_date,end_date)

print(cls_cmd)

p4_output   = os.popen(cls_cmd).readlines()

cl_list = []

got_cl = False

cl    = ''
title = ''
cl_info = ''

for line in p4_output:
    line = line.split()

    #print(line)

    if len(line) > 2:
        
        if line[0] == 'Change':
            cl = line[1].strip()
            cl_info = ' '.join(line)
            got_cl = True
        
        if got_cl and line[0] == 'Title:':
            # print(line)
            title = ' '.join(line)
            got_cl = False

        if cl: 
            cl_list.append({'cl': cl, 'cl_info' : cl_info, 'title': title})
            print(cl_info)
            cl    = ''
            title = ''
            cl_info = ''
            

# print(cl_list)
for target in targets:
    for change in cl_list:

        cl_verb_cmd = 'p4 describe %s'%change['cl']

        try: 
            cl_verbose  =  os.popen(cl_verb_cmd).readlines()

            results = ''
            for line in cl_verbose:
                if target in line:
                    results += '\t\t' + line
            if results:
                som_str  = 'Change: %s\n'%change['cl_info']
                som_str += 'Title: %s\n'%change['title']
                som_str += results
                print(som_str)
                print('\nFOUND %s'%target)
                input("Press Enter to continue...")
            else:
                print(change, 'nothing')

        except: 
            print('cl %s dont work'%cl)

print('\n\n\n\n\n\n')


# for change in cl_list:
#     if int(change['cl']) >= 6050945 and int(change['cl']) <= 6054656:
#         if change['title']:
#             print(change['cl'], change['title'], ';', change['cl_info'])

# #pp.pprint(cl_list)