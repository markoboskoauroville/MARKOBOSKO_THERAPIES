#!/usr/bin/env python3
"""Builds the picture grid under the instrument catalogue (22.11.2026): 16 small thumbnails of the makers' own pictures
(resize + centre crop only, 400 px, WebP) into site/img/inst-NN.webp and the same grid into both pages. Source files were
downloaded by hand into RAW (scratchpad); the table of sources is in TAKEOVER.md. Idempotent: replaces an existing grid."""
import os, re, sys
from PIL import Image
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = sys.argv[1]
# n, raw file, maker, name_hr, name_en, link, white background (multiply onto the panel)
T = [
 ('zaphir_N12N16a.jpg','Zaphir','Zaphir zvončići N°12 i N°16a','Zaphir chimes N°12 and N°16a','https://zaphir.fr/',0),
 ('remo_ocean.webp','Remo','Remo Ocean Drum','Remo Ocean Drum','https://remo.com/product/ocean-drum',0),
 ('ct_Dolphinessence-Set.jpg','Crystal Tones','Kristalne zdjele, set Dolphin Essence','Crystal singing bowls, Dolphin Essence set','https://crystalsingingbowls.com/shop/retail/dolphin-essence-set/',1),
 ('sw_IMG_0361-scaled-1024x1024.jpeg','Stonewhistle','Natey flauta, glina','Natey flute, clay','https://stonewhistle.com/instruments/natey/',0),
 ('paiste_gong.png','Paiste','Sound Creation gong No.3A Earth, 32"','Sound Creation gong No.3A Earth, 32"','https://paistegongs.com/gong.php?fid=4',0),
 ('zaphir_N192.jpg','Zaphir','Zaphir zvončići N°19+2','Zaphir chimes N°19+2','https://zaphir.fr/',0),
 ('hok_sansula-renaissance01jpg.jpg','Hokema','Sansula Renaissance','Sansula Renaissance','https://www.hokema.de/products/sansula-renaissance',1),
 ('acu_Chimeswobags.jpg','Acutonics','Acutonics ručni zvončići','Acutonics hand chimes','https://acutonics.com/sound-tools/hand-chimes/shop/hand-chime-sets',0),
 ('hess_65156-110161_Sound-Bath-Bowls-Set-Ohne_0.jpg','Peter Hess','Set zdjela za zvučnu kupku','Sound bath bowls set','https://www.hess-sound.de/en/products/sound-bath-bowls-set',0),
 ('remo_nightwaves-ocean-drum.webp','Remo','Remo Nightwaves Ocean Drum','Remo Nightwaves Ocean Drum','https://remo.com/product/nightwaves-ocean-drum',0),
 ('acu_IMG_2489.jpeg','Acutonics','Acutonics vilice za ugađanje','Acutonics tuning forks','https://acutonics.com/sound-tools/tuning-forks/shop/tuning-fork-sets',0),
 ('ct_Earth-Star-Chakra-Set-scaled.jpg','Crystal Tones','Kristalne zdjele, set Earth Star','Crystal singing bowls, Earth Star set','https://crystalsingingbowls.com/shop/retail/earth-star-set/',1),
 ('sw_IMG_0440-scaled-1024x1024.jpeg','Stonewhistle','Ova flauta, glina','Ova flute, clay','https://stonewhistle.com/instruments/ova-fluit/',0),
 ('zaphir_N9a916.jpg','Zaphir','Zaphir zvončići N°9a+9+16','Zaphir chimes N°9a+9+16','https://zaphir.fr/',0),
 ('hok_kalimba-b1701jpg.jpg','Hokema','Kalimba B17','Kalimba B17','https://www.hokema.de/products/kalimba-b17',1),
 ('hess_65100-122754_Feng-Gong-Einsteiger-Set_01.jpg','Peter Hess','Feng gong na stalku, početni set','Feng gong on a stand, starter set','https://www.hess-sound.de/en/products/feng-gong-einsteiger-set',0),
]
def square(im, drum=False):
    im = im.convert('RGBA') if im.mode in ('P','LA','RGBA') or 'A' in im.getbands() else im.convert('RGB')
    w, h = im.size
    if im.mode == 'RGBA' and drum:          # a drum in a wide transparent banner: centre the crop on the drum
        bb = im.getchannel('A').getbbox(); cx, cy = (bb[0]+bb[2])//2, (bb[1]+bb[3])//2; s = int(max(bb[2]-bb[0], bb[3]-bb[1]) * 1.12)
        s = min(s, h); box = (cx-s//2, max(0, min(h-s, cy-s//2)), cx-s//2+s, max(0, min(h-s, cy-s//2))+s)
    else:
        s = min(w, h); box = ((w-s)//2, (h-s)//2, (w-s)//2+s, (h-s)//2+s)
    return im.crop(box).resize((400, 400), Image.LANCZOS)
tiles = {'hr': [], 'en': []}
for i, (f, mk, nh, ne, link, mul) in enumerate(T, 1):
    im = square(Image.open(os.path.join(RAW, f)), drum=f.startswith('remo_'))
    out = 'img/inst-%02d.webp' % i
    im.save(os.path.join(R, 'site', out), 'WEBP', quality=78, method=6)
    for lang, name, foto, label in (('hr', nh, 'Foto', 'otvara se u novoj kartici'), ('en', ne, 'Photo', 'opens in a new tab')):
        alt = name.replace('"', '&quot;') + ' (' + mk + ')'
        tiles[lang].append('<a class="ig%s" href="%s" target="_blank" rel="noopener"><span class="igp"><img src="%s" alt="%s" width="400" height="400" loading="lazy" decoding="async"></span><span class="igt"><b>%s<span class="ext" aria-hidden="true">&nbsp;\u2197</span><span class="sr"> (%s)</span></b><small>%s: %s</small></span></a>'
                           % (' mul' if mul else '', link, ('/' if lang == 'en' else '') + out, alt, name.replace('"', '&quot;'), label, foto, mk))
TXT = {'hr': ('Instrumenti u slikama', 'Fotografije pripadaju izrađivačima navedenima na pločicama. Ovdje su prikazane samo da upute na njihove instrumente i bit će odmah uklonjene ako izrađivač to zatraži: <a href="mailto:marko.bosko@auroville.community">marko.bosko@auroville.community</a>.'),
       'en': ('The instruments in pictures', 'The pictures belong to the makers named on them. They are shown here only to point to their instruments and will be removed at once if a maker asks: <a href="mailto:marko.bosko@auroville.community">marko.bosko@auroville.community</a>.')}
for lang, p in (('hr', 'site/index.html'), ('en', 'site/en/index.html')):
    s = open(os.path.join(R, p), encoding='utf-8').read()
    s = re.sub(r'\n?<div class="igwrap">.*?</div><!--/igwrap-->', '', s, flags=re.S)
    block = '\n<div class="igwrap"><h3 class="h4">%s</h3><div class="igrid">%s</div><p class="note igcap">%s</p></div><!--/igwrap-->' % (TXT[lang][0], ''.join(tiles[lang]), TXT[lang][1])
    i = s.index('class="catalogue"'); j = s.index('</details>', i) + len('</details>')
    s = s[:j] + block + s[j:]
    open(os.path.join(R, p), 'w', encoding='utf-8').write(s)
print('ok')
