import sys,os, re
import pprint
from jinja2 import Template, Environment, FileSystemLoader
import getpass 
import datetime
  
# manu snippets to deal with Jira
sys.path.append('/remote/pv/repo/user/mramire/fcfe_scripts')
from jira_api import *

pp = pprint.PrettyPrinter(indent=1, depth=3)

team_JQL = 'labels in (DCPVPRS, DCPVPRS-HPDRT, DCPVPRS-ARM, DCPVPRS-RMS, DCPVPRS-NXP, "KW:DCNXTCSS/ARM", "KW:DCNXT/DCNXT2ICCII", "KW:DCNXT/HPDRT", "KW:DCNXT/RMS", "KW:DCNXTCSS/AMD", "KW:DCNXTCSS/APPLE", "KW:DCNXTCSS/ARM", "KW:DCNXTCSS/NXP") AND not (labels in (nocl01,ftcl01)) AND type != Epic'


def star_board_from_jql(JQL, days = 10):    
    
    star_board = {}

    star_board['showstopper'] = {'JQL': JQL +' AND status != Done AND labels in ("bu_top")', 'days': ''}
    star_board['current']      = {'JQL': JQL +' AND status != Done', 'days': ''}
    star_board['last_resolved']= {'JQL': JQL +' AND resolved >= "-%sd"'%days , 'days': days}
    star_board['last_created'] = {'JQL': JQL +' AND created >= "-%sd" AND status != Done'%days, 'days': days}

    print('STARs Board v0.0')
    print('-Connecting to Jira Server with user')
    conn = jira_connection(server = "jira")
    
    for board in star_board:  
        
        print('-Getting JQL filter:\n \"%s\"'%star_board[board]['JQL'])
        team_stars = get_stars(star_board[board]['JQL'], conn)
        # pp.pprint(team_stars['issues'])
        star_board[board]['board'] = []
        
        for star in team_stars:
            # pp.pprint(star.raw)

            brnch = '--'

            if 'customfield_10600' in star.raw['fields']:
                if star.raw['fields']['customfield_10600']:
                    brnch = star.raw['fields']['customfield_10600']['name']
            
            comments = []
            for comm in get_comments(star):
                comments.append({'author': comm.author.key, 'text': comm.body})
            
            # transitions = conn.transitions(star)
            # print(star.raw['key'])
            # pp.pprint(transitions)
            # exit()
            affects_versions = []
            
            for v in star.raw['fields']['versions']:
                if v['name'] not in affects_versions and v['name'] != brnch:
                    affects_versions.append(v['name'])

            star_board[board]['board'].append({
                    'STAR ID'  : star.raw['id'], 
                    'Key'      : star.raw['key'], 
                    'Summary'  : star.raw['fields']['summary'],
                    'Reporter' : star.raw['fields']['reporter']['key'],  
                    'Assignee' : star.raw['fields']['assignee']['key'] if star.raw['fields']['assignee'] else '' ,
                    'Priority' : star.raw['fields']['priority']['name'], 
                    'Status'   : star.raw['fields']['status']['name'],
                    'Created'  : star.raw['fields']['created'].split('T')[0], 
                    'Updated'  : star.raw['fields']['updated'].split('T')[0], 
                    'Product L1 Name' : star.raw['fields']['project']['name'],
                    'link'     : 'https://jira.internal.synopsys.com/browse/%s'%star.raw['key'],
                    'Branch'   : brnch,
                    'Last Comment' : comments,
                    'Affects Version' : affects_versions
                })

            

            # print(affects_versions)
        
        #pp.pprint(star.raw)

        
    # pp.pprint(star_board)
    
    print('Done.')
    return star_board

def create_board_html(star_dict, all_links_dict = None):

    # pp.pprint(star_dict['showstopper']['board'])
    
    stars_text_dir = os.path.join(os.getcwd(), 'STARs_comments')
    
    if not os.path.exists(stars_text_dir):
        print('-Creating dir to save comments for STARs at: \n%s'%stars_text_dir)
        os.mkdir(stars_text_dir)
        os.chmod(stars_text_dir, 0o777)
        print('-Created.')
    else:
        print('-STARs comment files found at:\n %s'%stars_text_dir)

    template_file = '/slowfs/dcopt105/vasquez/utils/suite_collectors_dev/v_repo/suite_collectors/star_board.jinja'
    #template = Template(template_text)
    env = Environment(loader=FileSystemLoader('/'))
    template = env.get_template(template_file)

    title = 'STAR Board'

    b_dict = {}
    
    branch_ls_ptrn = '([A-Z]-[0-9]{4}.[0-9]{2})'
    branch_sp_ptrn = '([A-Z]-[0-9]{4}.[0-9]{2}-SP).*'


    # get branch main names to group in summary
    for k,v in star_dict.items():
        if k not in b_dict:
            print(k)
            b_dict[k] = {}

        for st in v['board']:
            branch_macro = ''
            m_sp = re.match(branch_sp_ptrn, st['Branch'])    
            m_ls = re.match(branch_ls_ptrn, st['Branch'])
            
            if m_sp:
                branch_macro = m_sp.group(1)
                # print('match this', branch_macro)
            elif m_ls:
                branch_macro = m_ls.group(1)
                # print('match this', branch_macro)
            else:
                pass
                # print('match notin')


            if branch_macro not in b_dict[k]:
                b_dict[k][branch_macro] = []
            
            b_dict[k][branch_macro].append(st)

    # dump a match of STAR-ID and Jira keys, usefull for QoR comments.
    id_key_match = {}
    for board in star_dict:
        for star in star_dict[board]['board']:
            jira_key = star['Key']
            star_num = star['STAR ID']
            id_key_match[jira_key] = star_num

    # write json
    json_file = open(os.path.join(stars_text_dir,"jira_keys.json"), "w")
    json_file.write(json.dumps(id_key_match))
    json_file.close()

    #pp.pprint(b_dict)

    html = template.render(
        html_title = title,
        update_time = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
        star_dict = star_dict,
        stars_text_dir = stars_text_dir,
        all_links_dict = all_links_dict,
        tool = 'DC',
        b_dict = b_dict
        )

    html_name = 'star_board.php'
    report_file = open(html_name, 'w')
    report_file.write(html)
    report_file.close()

    print('-Beautiful html created at: \n https://clearcase%s'%os.path.join(os.getcwd(),html_name))
    return html_name

# open_star_dict = star_board_from_jql(team_JQL)

# star_board_html = create_board_html(star_dict)
