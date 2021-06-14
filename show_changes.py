import pprint
import pickle

pp = pprint.PrettyPrinter(indent = 2)



# suite_changes_html.py -vasquez-
# 
# Look for relevant changes for provided pkl files from a suite
# uses both design values and mean values
#
# when used as function, returns the analysis results dict and the html filename 
# 
# usage example
#
# html_title = 'relevant_changes'
# all_pkl_name = 'diff.srm_icc2_spg_opt_area_all.pkl'
# means_pkl_name = 'diff.srm_icc2_spg_opt_area_means.pkl'
# n_designs = 4
# metrics_selection = {
#                     'DCMvArea' : 0.3,
#                     'DCWNS': 0.3,
#                     'DCTNSPMT': 1,
#                     'CLKDCAllOpt' : 0.4,
#                     'DCStdCelTotPow' : 0.3,
#                     'DCMem' : 0.1
#                     }
#
# suite_changes_html(html_title, all_pkl_name, means_pkl_name, metrics_selection, n_designs)
#

def suite_changes_html(html_title, all_pkl_name, means_pkl_name, metrics_selection, n_designs):
  
  print('\nsuite_changes_html.py')
  print('\nLooking for noticeable changes in suite.')
  
  print('\treading ' + all_pkl_name)
  suite_all_file = open(all_pkl_name, 'rb')
  suite_all = pickle.load(suite_all_file)
  suite_all_file.close()

  print('\treading ' + means_pkl_name)
  suite_means_file = open(means_pkl_name, 'rb')
  suite_means = pickle.load(suite_means_file)
  suite_means_file.close();

  result = {}

  print('\tanalyzing...')
  for nightly in suite_means :

      result[nightly] = {}

      for report in suite_means[nightly]:
          result[nightly][report] = {}

          for metric in metrics_selection:
              
              # clean NaN values before sorting
              cleanList = []

              if metric in suite_means[nightly][report]:
                  
                  if suite_means[nightly][report][metric] != '--':

                      current_mean = float(suite_means[nightly][report][metric])
                  
                      # look if the metric is out of threshold
                      if  abs(current_mean) > metrics_selection[metric]:

                          # then we sort this
                          for design in suite_all[nightly][report][metric]:
                              
                              current_design_value = suite_all[nightly][report][metric][design]

                              if current_design_value != '--':
                                  
                                  cleanList.append((design,float(current_design_value)))
                          
                              # sort designs from min to max
                              sor = sorted(cleanList, key=lambda x: x[1])
                              #print(nightly+' '+report+' '+metric)
                              #print(sor)
                              #if  k > (len(sor) - 1):
                              #    k = len(sor) - 1

                              best = sor[0:n_designs] # the first k designs tuples (design,value)

                              lenSor=len(sor)
                              worst = sor[lenSor-n_designs:lenSor] # last k designs tuples (design,value)

                              #turn best list to dict
                              bestDict = {}
                              for design in best:
                                  bestDict[design[0]] = design[1]

                              # turn worst list to dict
                              worstDict = {}
                              for design in worst:
                                  worstDict[design[0]] = design[1]
                              

                              result[nightly][report][metric] = {}
                              result[nightly][report][metric]['mean'] = suite_means[nightly][report][metric] 
                              
                              if current_mean > 0:
                                  result[nightly][report][metric]['worst'] = worstDict   
                              if current_mean < 0:
                                  result[nightly][report][metric]['best'] = bestDict
                              
  #pp.pprint(result)

  ## make the html
  print('\tmaking a beautiful html...')
  html_report = ''
  html_report += '''
  <!DOCTYPE html>
  <html>
  <title>''' + html_title + '''Template</title>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
  <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
  <style>
  html,body,h1,h2,h3,h4,h5 {font-family: "Raleway", sans-serif}
  </style>


  <body class="w3-light-grey">

  <!-- BARRA CON LINKS -->

  <div class="w3-bar w3-black w3-small">
    <a href="#" class="w3-bar-item w3-button w3-small"><b>PV Dashboard</b></a>
    <div class="w3-dropdown-hover">
      <button class="w3-button w3-small">Tool</button>
      <div class="w3-dropdown-content w3-bar-block w3-card-4">
        <a href="#" class="w3-bar-item w3-button">Design Compiler</a>
        <a href="#" class="w3-bar-item w3-button">Descartes</a>
      </div>
    </div>
    
    <div class="w3-dropdown-hover">
      <button class="w3-button w3-small">Branch</button>
      <div class="w3-dropdown-content w3-bar-block w3-card-4">
        <a href="#" class="w3-bar-item w3-button">P2019-03</a>
        <a href="#" class="w3-bar-item w3-button">O2018-06</a>
      </div>
    </div>

    <div class="w3-dropdown-hover">
      <button class="w3-button w3-small">Suite</button>
      <div class="w3-dropdown-content w3-bar-block w3-card-4">
        <a href="#" class="w3-bar-item w3-button">DC_ICC2</a>
        <a href="#" class="w3-bar-item w3-button">HPDRT</a>
        <a href="#" class="w3-bar-item w3-button">DC_ICC2_Platform</a>
      </div>
    </div>

    <div class="w3-dropdown-hover">
      <button class="w3-button w3-small">Flow</button>
      <div class="w3-dropdown-content w3-bar-block w3-card-4">
        <a href="#" class="w3-bar-item w3-button">SRM_ICC2_spg_opt_area</a>
        <a href="#" class="w3-bar-item w3-button">SRM_ICC2_spg_timing_opt_area</a>
        <a href="#" class="w3-bar-item w3-button">SRMFm_ICC2_spg_opt_area</a>
      </div>
    </div>

    <div class="w3-dropdown-hover">
        <button class="w3-button w3-small">Views</button>
        <div class="w3-dropdown-content w3-bar-block w3-card-4">
          <a href="#" class="w3-bar-item w3-button">Run Status</a>
          <a href="#" class="w3-bar-item w3-button">Metric Selections</a>
          <a href="#" class="w3-bar-item w3-button">Best Metrics</a>
          <a href="#" class="w3-bar-item w3-button">Worst Metrics</a>
        </div>
    </div>
  </div>
  '''

  html_report += '''
    <!-- TITULO -->
    <header class="w3-container">
      <h5><b><i class="fa fa-dashboard"></i>''' + html_title + '''</b></h5>
    </header>'''

  for nightly in result:
    
    for report in result[nightly]:
      
      #start of html nightly
      html_report += '''

        <!-- !THIS IS A NIGHTLY! -->
        <div class="w3-panel w3-white w3-padding w3-margin w3-round-xlarge">
        <h5 class="w3-large"><b>''' + nightly + '''</b></h5>
        '''
      for metric in result[nightly][report]:
        
        m_mean = float(result[nightly][report][metric]['mean'])

        if m_mean > 0:
          #start html for metrics
          html_report += '''
          <div class="w3-container w3-pale-red w3-round-xlarge w3-cell w3-cell-top blok">
            <span class="w3-medium"><b>''' + metric + '''</b></span><br>
            <span class="w3-large">'''  + str(m_mean) + '''</span><br>'''

          #start html for worst designs
          html_report += '''<h6 class="w3-small">Worst Designs</h6>
          <h6 class="w3-small">'''
          
          for design in result[nightly][report][metric]['worst']:

            d_value = result[nightly][report][metric]['worst'][design]
            
            #start html for list of worst designs
            html_report += '<b>' + str(d_value) + '</b> ' +	design + '<br>'

          #end html for worst designs
          html_report += '</h6>'

        if m_mean < 0:
          #start html for metrics
          html_report += '''
          <div class="w3-container w3-pale-green w3-round-xlarge w3-cell w3-cell-top blok">
            <span class="w3-medium"><b>''' + metric + '''</b></span><br>
            <span class="w3-large">'''  + str(m_mean) + '''</span><br>'''

          
          #start html for best designs
          html_report += '''<h6 class="w3-small">Best Designs</h6>
          <h6 class="w3-small">'''
          
          for design in result[nightly][report][metric]['best']:

            d_value = result[nightly][report][metric]['best'][design]
            
            #start html for list of best designs
            html_report += '<b>' + str(d_value) + '</b> ' +	design + '<br>'

          #end html for best designs
          html_report += '</h6>'


        #end of html for metrics
        html_report += '</div>'  

      # end of html for nightly
      html_report += '\t</div>'

  # conclude the html 
  html_report += '''
    <!-- Footer -->
    <footer class="w3-container w3-padding-16 w3-light-grey">
      <h4>FOOTER</h4>
      <p>Powered by <a href="https://www.w3schools.com/w3css/default.asp" target="_blank">w3.css</a></p>
    </footer>

    <!-- End page content -->
  </div>

  <script>
  // Get the Sidebar
  var mySidebar = document.getElementById("mySidebar");

  // Get the DIV with overlay effect
  var overlayBg = document.getElementById("myOverlay");

  // Toggle between showing and hiding the sidebar, and add overlay effect
  function w3_open() {
    if (mySidebar.style.display === 'block') {
      mySidebar.style.display = 'none';
      overlayBg.style.display = "none";
    } else {
      mySidebar.style.display = 'block';
      overlayBg.style.display = "block";
    }
  }

  // Close the sidebar with the close button
  function w3_close() {
    mySidebar.style.display = "none";
    overlayBg.style.display = "none";
  }
  </script>

  </body>
  <style>
  .blok {
    width : 220px;
    height : 180px;
    display: inline-block;
    margin-bottom: 5px;
  }

  body {
      font-family: 'Roboto';
      padding-right: 160px;
      padding-left: 160px;
  }

  </style>

  </html>
  '''

  # put the html in a file

  html_name = html_title + '.html'
  html_file = open( html_name, 'w')
  html_file.write(html_report)
  html_file.close()

  print('\t' + html_name + ' written')
  return [result, html_title]
