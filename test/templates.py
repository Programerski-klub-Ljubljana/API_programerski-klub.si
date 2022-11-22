import re

from core import cutils

temp = cutils.root_path('templates')
for file in temp.glob('*.html'):

	if file.name.startswith('_'):
		continue

	file_name = file.name.replace('.html', '')
	p = [e for e in re.findall(r'{{(.*?)}}', file.read_text()) if not e.startswith('CONST.')]
	print(f'{file_name:30}{p}')
