"""Construit site/index.html (version autonome, hébergeable n'importe où) à partir de index.html."""
import pathlib
here=pathlib.Path(__file__).parent
body=(here/'index.html').read_text()
head='''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0057B7">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Сонячко">
<link rel="icon" href="favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="favicon-16.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="manifest" href="manifest.json">
<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
</head>
<body>
'''
(here/'site'/'index.html').write_text(head+body+'\n</body>\n</html>\n')
print('site/index.html écrit')

# Version « un seul fichier » : les icônes sont intégrées dans le HTML (pratique pour coller dans l'éditeur Neocities).
import base64, json
def uri(name, mime="image/png"):
    return f"data:{mime};base64,"+base64.b64encode((here/'site'/name).read_bytes()).decode()
manifest=json.loads((here/'site'/'manifest.json').read_text())
manifest['icons']=[{**manifest['icons'][0],'src':uri('icon-192.png')}]
manifest['start_url']='./'
single=head.replace('href="favicon.ico"',f'href="{uri("favicon-48.png")}"') \
  .replace('href="favicon-32.png"',f'href="{uri("favicon-32.png")}"') \
  .replace('href="favicon-16.png"',f'href="{uri("favicon-16.png")}"') \
  .replace('href="apple-touch-icon.png"',f'href="{uri("apple-touch-icon.png")}"') \
  .replace('href="manifest.json"','href="data:application/manifest+json;base64,'+base64.b64encode(json.dumps(manifest).encode()).decode()+'"')
(here/'site-single').mkdir(exist_ok=True)
(here/'site-single'/'index.html').write_text(single+body+'\n</body>\n</html>\n')
print('site-single/index.html écrit')
