

#hist = '04BJ420'
# example usage

# hist = '9402134'
# mark_value = 39.1
# g_width = 100
# g_height = 15
# color = 'rgb(67,58,183)'
	

# print(mini_hist(hist, mark_value, g_width, g_height, color))

def mini_hist(hist, mark_value, g_width, g_height, color):

	letters = '0123456789ABCDEFGHIJKLMNPQRSTUVWXYZ^'
	valdict = {}
	for i in range(len(letters)):
		valdict[letters[i]]= i

	hist_nums = []
	for ch in hist:
		hist_nums.append(valdict[ch])

	hist_max_num = max(hist_nums)

	hist_cols = len(hist)
	bar_width = g_width/hist_cols

	g_nums = []


	for val in hist_nums:
		g_num = val/hist_max_num * (g_height-1) if hist_max_num != 0 else 0
		g_nums.append(g_num)



	html_svg  = ''
	html_svg += '<svg width="%s" height="%s">\n'%(g_width,g_height)
	html_svg += '<line x1="0" y1="%s" x2="%s" y2="%s" style="stroke:%s;stroke-width:2" />'%(g_height,g_width,g_height,color)

	x = 0
	for num in g_nums:
		y = g_height - num
		
		html_svg += '\t<rect width="%s" height="%s"'%(bar_width,num)
		html_svg += ' x="%s" y="%s"'%(x,y)
		html_svg += ' style="fill:%s"/>\n'%(color)
		x += bar_width

	# putting th dot for mark_value
	###
	loc_list = [-100,-15,-5,-1,1,5,15,101]
	
	if mark_value:
		y_pos = g_height/2
		for i in range(1,len(loc_list)):
			if mark_value >= loc_list[i-1] and mark_value < loc_list[i]:
				x_pos = i*bar_width - bar_width/2
				html_svg += '\t<circle cx="%s" cy="%s" r="4" fill="red" />\n'%(x_pos,y_pos)
				break

	html_svg += '</svg>\n'
	return html_svg


