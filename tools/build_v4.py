# build_v4.py: writes site/index.html from scratch (21.11.2026, plan by the Fable design review).
# One room, four uses: therapy, movement lab, AI laboratory, research for ERF. Run from the repo root.
import html, re, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEAD_FILE = sys.argv[1] if len(sys.argv) > 1 else None   # the old <head> (kept: meta, canonical, icons, ld+json)
PARTS = sys.argv[2] if len(sys.argv) > 2 else None        # folder with parts_euphony.html, parts_instr.html

def eur(x): return f'{x:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.') + ' €'
def esc(t): return html.escape(t, quote=True)

def fig(name, alt, cap=None, cls='pic', lazy=True, w=1920, h=1072):
    c = f'<figcaption>{cap}</figcaption>' if cap else ''
    ld = ' loading="lazy"' if lazy else ' fetchpriority="high"'
    return (f'<figure class="{cls}"><img src="img/{name}.jpg" srcset="img/{name}-960.jpg 960w, img/{name}.jpg 1920w" '
            f'sizes="(max-width:1100px) 100vw, 1100px" alt="{esc(alt)}" width="{w}" height="{h}"{ld}>{c}</figure>')

def yt(vid, title, extra=''):
    return (f'<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/{vid}{extra}" title="{esc(title)}" loading="lazy" '
            'referrerpolicy="strict-origin-when-cross-origin" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>'
            f'<p class="ytl"><a href="https://www.youtube.com/watch?v={vid}" rel="noopener">Ako se video ne prikaže, otvori ga na YouTubeu</a></p>')

def sec(num, sid, dot, kicker, title, body='', lede=None):
    l = f'<p class="lede">{lede}</p>' if lede else ''
    return (f'<section id="{sid}" class="sec"><div class="wrap"><span class="num" aria-hidden="true">{num}</span>'
            f'<p class="kicker"><i class="dot {dot}"></i>{num} · {kicker}</p><h2>{title}</h2>{l}</div>\n{body}\n</section>\n')

# ------------------------------------------------------------------ costs
ROOM = [
 ('Apple Mac mini M6, 24 GB memorije, 512 GB SSD', 1, 1489.00, 'https://www.apple.com/de/shop/buy-mac/mac-mini', 'apple.com/de', 'cijena iz tiska, provjeriti u konfiguratoru'),
 ('Optoma ZH430UST, ultrakratki laserski projektor, Full HD, 4.000 lumena', 4, 1398.00, 'https://www.beamer-discount.de/en/products/optoma-zh430ust-beamer-mit-4-000-ansi-lumen-und-full-hd-dura-core', 'beamer-discount.de', ''),
 ('Optoma OWM3000, stropni nosač za ultrakratki projektor', 4, 107.73, 'https://www.office-partner.de/optoma-owm3000-projektorhalterung-fuer-ultrakurzdistanzgeraete-max.tragkraft-15kg-7853514', 'office-partner.de', ''),
 ('pro snake AOC HDMI 15 m, optički HDMI kabel do projektora', 4, 69.00, 'https://www.thomann.de/de/pro_snake_aoc_hdmi_a_a_15m.htm', 'Thomann', ''),
 ('DisplayLink USB-C na HDMI adapter za četvrti projektor (OWC Dual HDMI)', 1, 97.90, 'https://www.owc.com/solutions/usb-c-dual-hdmi-4k-display-adapter', 'OWC', 'cijena iz usporedbe cijena'),
 ('Adam Audio D3V, par aktivnih zvučnika s USB-C ulazom', 4, 259.00, 'https://www.thomann.de/de/adam_audio_d3v_black.htm', 'Thomann', ''),
 ('Adam Audio D3V produžni kabel između zvučnika u paru', 4, 14.99, 'https://www.thomann.de/de/adam_audio_d3v_black.htm', 'Thomann', ''),
 ('iriz CM550, stropni nosač s navojem 3/8" za zvučnik', 8, 46.00, 'https://www.thomann.de/de/iriz_cm550_adjustable_ceiling_mount.htm', 'Thomann', ''),
 ('Lindy USB 2.0 preko mrežnog kabela Cat.6, do 50 m (USB kroz zid)', 4, 129.00, 'https://www.thomann.de/de/lindy_50m_usb_2_0_cat.6_extender.htm', 'Thomann', ''),
 ('USB hub s napajanjem, 7 priključaka', 1, 40.00, '', 'procjena', 'procjena'),
 ('Android mobitel s kamerom uz svaki zvučnik (rabljeni Pixel ili sličan)', 8, 120.00, '', 'procjena', 'procjena'),
 ('Godox MTH02, držač mobitela s navojem 1/4"', 8, 18.00, 'https://www.calumet.de/product/godox-mth02-smartphone-halterung', 'calumet.de', ''),
 ('USB punjač za mobitel na stropu', 8, 10.00, '', 'procjena', 'procjena'),
 ('Ubiquiti UniFi U7 Pro, Wi-Fi 7 pristupna točka na stropu', 1, 190.00, 'https://preisvergleich.heise.de/ubiquiti-unifi-7-pro-u7-pro-a3096524.html', 'heise.de', 'cijena iz usporedbe cijena'),
 ('Zylia ZM-2, 3D mikrofon s 19 kapsula u jednoj kugli, USB', 1, 1625.20, 'https://shop.zylia.co/', 'zylia.co', 'cjenik bez PDV-a, dostupnost na upit'),
 ('Audio-Technica PRO 45, viseći kondenzatorski mikrofon', 4, 109.00, 'https://www.thomann.de/de/audio_technica_pro45_haengemikrofon.htm', 'Thomann', ''),
 ('Behringer UMC404HD, USB zvučna kartica s 4 mikrofonska ulaza', 1, 95.00, 'https://www.thomann.de/de/behringer_umc404hd.htm', 'Thomann', ''),
 ('Mrežni kabeli Cat.6 kroz zid, zidne utičnice i spojnice', 1, 150.00, '', 'procjena', 'procjena'),
]
RING = [
 ('Global Truss F34, kružni segment 90°, promjer 3 m (četiri čine prsten)', 4, 549.00, 'https://www.musicstore.de/en_DE/EUR/Global-Truss-F34-Circular-300cm-90-4-Point/art-LIG0003704-000', 'musicstore.de', ''),
 ('Samsung Galaxy A36, kamera prstena (1080p, 60 sl/s)', 12, 326.69, 'https://www.bechtle.com/', 'Bechtle', 'cijena za 128 GB'),
 ('Stezaljka za truss i držač mobitela', 12, 20.00, '', 'procjena', 'procjena'),
 ('Vješanje prstena o strop (sajle, sidra, atest statičara)', 1, None, '', 'na upit', 'ponuda izvođača'),
]
SOFT = [
 ('Ableton Live 12 Suite (s Max for Live), vodi svih osam zvučnika', 1, 479.00, 'https://www.thomann.de/de/ableton_live_12_suite.htm', 'Thomann', ''),
 ('Envelop for Live, IEM Plugin Suite, ZYLIA Studio, Pose2Sim, MilkDrop', 1, 0.0, 'https://www.envelop.us/software', 'besplatno', 'besplatni alati za prostorni zvuk, 3D zvuk, 3D zglobove i vizualizacije'),
 ('Skeleton, moja aplikacija za praćenje pokreta s više kamera', 1, 0.0, '', 'Marko Boško', ''),
]
MONTH = [
 ('Claude Max (Claude Code), mozak AI laboratorija', '≈ 214 €', 'https://claude.com/pricing', 'claude.com', '200 $ mjesečno + PDV'),
 ('Higgsfield Plus, slike, video i zvuk u videu (API po potrošnji)', '≈ 49 $', 'https://higgsfield.ai/', 'higgsfield.ai', 'cijena s Higgsfieldovog bloga, plus PDV; API se plaća unaprijed po generiranju'),
 ('Suno, besplatni račun za svaku osobu', '0 €', 'https://suno.com/pricing', 'suno.com', 'oko 10 pjesama dnevno; Pro oko 10 $ za vlastiti glas'),
 ('myNoise, licenca za korištenje u terapijskoj sobi', 'na upit', 'https://mynoise.net/licensing.php', 'mynoise.net', 'godišnja licenca, cijenu predlaže korisnik'),
]
def table(items):
    rows=[]; tot=0
    for name,q,price,url,where,note in items:
        if price is None:
            rows.append(f'<tr><td>{name}<br><small>{note}</small></td><td class="n">{q}</td><td class="n">na upit</td><td class="n">na upit</td><td>{where}</td></tr>'); continue
        t=q*price; tot+=t
        w = f'<a href="{url}" rel="noopener">{where}</a>' if url else where
        nt = f'<br><small>{note}</small>' if note and note!='procjena' else ''
        rows.append(f'<tr><td>{name}{nt}</td><td class="n">{q}</td><td class="n">{eur(price)}</td><td class="n">{eur(t)}</td><td>{w}</td></tr>')
    head='<thead><tr><th>Stavka</th><th class="n">Kom.</th><th class="n">Cijena</th><th class="n">Ukupno</th><th>Gdje</th></tr></thead>'
    return head+'<tbody>'+'\n'.join(rows)+'</tbody>', tot
room_t, room_tot = table(ROOM); ring_t, ring_tot = table(RING); soft_t, soft_tot = table(SOFT)
month_rows = '\n'.join(f'<tr><td>{n}<br><small>{note}</small></td><td class="n">{p}</td><td><a href="{u}" rel="noopener">{w}</a></td></tr>' for n,p,u,w,note in MONTH)
ONE_TIME = room_tot + ring_tot + soft_tot

TRACKS = ['Trentemøller – Miss You','Chantress Seba i Malte Marten – Song from the Forest','Nils Frahm – Says','Chantress Seba – You Are Light','Nils Frahm – Ambre','Trentemøller – Nightwalker','Ólafur Arnalds – Near Light','Nils Frahm – Familiar','Chantress Seba i Malte Marten – The Oracle','Brian Eno – An Ending (Ascent)','Nils Frahm – Sunson','Hania Rani – Glass','Jon Hopkins – Abandon Window','Marconi Union – Weightless']
PLAYLIST = ['hE_8C33gm7A','bfcl1JMGXdI','dIwwjy4slI8','gRBg2d79Q8c','GFbkF_fsW24','SasKGA1hq9Y','0kYc55bXJFI','tgwBXJE-9sM','RpclSuABeRc','OlaTeXX3uH8','YFkKBfmSx5o','l0yRNQj2_tc','mqU0XsELBCA','UfcAVejslrU']

# ------------------------------------------------------------------ scheme (same as phase 3)
SCHEME = open(os.path.join(ROOT,'tools','scheme.svg.html')).read()

# ------------------------------------------------------------------ sections
hero = f'''<header class="hero">
<img class="hero-img" src="img/room.jpg" srcset="img/room-960.jpg 960w, img/room.jpg 1920w" sizes="100vw" alt="Mlada osoba u invalidskim kolicima usred sobe gleda kornjaču i ražu na zidovima; projektori i zvučnici s mobitelima vise sa stropa, pod je prazan" width="1920" height="1072" fetchpriority="high">
<div class="hero-in wrap">
<p class="kicker"><i class="dot t"></i><i class="dot a"></i><i class="dot v"></i><i class="dot w"></i>Prijedlog za ERF Zagreb</p>
<h1>Jedna soba, četiri namjene</h1>
<p class="lede">Soba u kojoj su četiri zida slika, a strop zvuk. Ujutro je terapijska soba pod morem, poslije laboratorij za analizu pokreta, a kad miruje, AI laboratorij u kojem glasom nastaje ono što opišeš. Sve visi sa stropa, na podu su samo ljudi.</p>
<nav class="chips" aria-label="Četiri namjene"><a href="#terapija"><i class="dot t"></i>Terapija</a><a href="#pokret"><i class="dot a"></i>Analiza pokreta</a><a href="#ai-lab"><i class="dot v"></i>AI laboratorij</a><a href="#erf"><i class="dot w"></i>Istraživanje</a></nav>
<p class="ded">Za prof. dr. sc. <a href="https://www.erf.unizg.hr/djelatnici/renata.martinec" rel="noopener">Renatu Martinec</a> i asistenticu <a href="https://www.erf.unizg.hr/djelatnici/brigita.vilc" rel="noopener">Brigitu Vilč</a>, Odsjek za motoričke poremećaje, kronične bolesti i art terapije, <a href="https://www.erf.unizg.hr" rel="noopener">Edukacijsko-rehabilitacijski fakultet</a>.</p>
</div></header>
<nav class="topnav" aria-label="Sadržaj"><div class="wrap"><a href="#terapija">Terapija</a><a href="#pokret">Pokret</a><a href="#ai-lab">AI laboratorij</a><a href="#erf">Za ERF</a><a href="#aplikacije">Aplikacije</a><a href="#oprema">Oprema</a><a href="#nadahnuce">Nadahnuće</a><a href="#o-meni">O meni</a></div></nav>
'''

s1 = sec('01','terapija','t','Terapija','Soba pod morem', f'''
<div class="wrap">
{fig('setup','Prazna soba odozdo: projektori i mali zvučnici vise sa stropa, uz zvučnike mobiteli, pod je potpuno prazan','Sve visi sa stropa: četiri projektora, osam zvučnika, osam mobitela.','pic wide')}
<p>Na podu nema ničega osim ljudi. Uz svaki zid sa stropa visi ultrakratki laserski projektor, a oko sobe osam malih zvučnika Adam Audio D3V, okrenutih naopako. Uz svaki zvučnik je Android mobitel: na ekranu pokazuje što taj zvučnik svira, a kamerom gleda u sobu i zna gdje je osoba. Kad se osoba približi zvučniku, njegov zvuk se mijenja.</p>
<h3>Igra pokreta: opuštanje i aktivacija</h3>
{fig('movement','Dijete na sredini sobe diže ruke, a na zidu svjetleći lik od točaka i linija ponavlja pokret dok oko njega plivaju ribe i kornjača','Pogođen pokret: ribe i kornjača doplivaju kao nagrada.','pic wide')}
<p>Moja aplikacija Skeleton na sliku osobe stavlja kostur od točaka i linija. Terapeut odabere pokret, aplikacija ga pokaže kao prozirnu siluetu, a kad ga osoba pogodi i zadrži, dolazi nagrada u slici i zvuku. Težinu određuje terapeut, od vrlo blage do točnije.</p>
<div class="duo">
<div class="card">{fig('relax','Dijete leži na mekanoj vreći usred tamnoplave sobe s meduzama, terapeutkinja sjedi uz njega')}<h3 class="h4">Opuštanje</h3><p>Spori, mali pokreti: ruke se dižu s udahom. Tamna voda i meduze. Nagrada je nježna: kit zapjeva iz kuta sobe.</p></div>
<div class="card">{fig('activation','Djeca dodiruju svjetleće krugove na zidu i iz njih izlaze jata riba')}<h3 class="h4">Aktivacija</h3><p>Veći pokreti: ruke u zvijezdu, dohvati krug svjetla. Svijetao greben. Nagrada je vesela: jato riba proleti cijelom sobom.</p></div>
</div>
<h3>Pjevaj i dobij svoju pjesmu</h3>
<div class="split">{fig('singing','Mladić u invalidskim kolicima sretno pjeva prema malom kuglastom mikrofonu sa stropa, terapeutkinja drži tablet')}<div><p>Osoba otpjeva nekoliko taktova u mikrofon, terapeut pritisne gumb, i za minutu iz svih zvučnika dođe cijela pjesma nastala iz te melodije. To radi <a href="https://suno.com" rel="noopener">Suno</a>: besplatni račun daje oko deset pjesama dnevno za osobnu upotrebu. Da pjesmu pjeva baš glas te osobe, treba plaćeni paket i osoba svoj glas mora sama potvrditi. Za djecu uz pristanak roditelja.</p></div></div>
<h3>Snimanje u 3D</h3>
<div class="split rev">{fig('microphones','Pogled prema stropu: u sredini visi mala kugla puna mikrofonskih kapsula, oko nje četiri tanka viseća mikrofona')}<div><p>U sredini stropa visi Zylia, jedna kugla s 19 mikrofona. Snima prostor u tri dimenzije, pa se pjesma, bubnjanje u krugu ili glas terapeuta mogu poslije reproducirati na osam zvučnika točno kako su zvučali. Četiri viseća mikrofona snimaju izbliza.</p></div></div>
<h3>Boja, zvuk i glazba</h3>
{fig('milkdrop','Zidovi puni mekih tekućih uzoraka u ljubičastoj, tirkiznoj i jantarnoj boji, mladić u kolicima i prijatelj gledaju','MilkDrop na sva četiri zida.','pic wide')}
<p>Na zidovima mogu biti i moje MilkDrop vizualizacije: tekuće slike koje nastaju iz glazbe. Za terapiju biram samo spore predloške, bez bljeskova.</p>
<div class="gal4"><img src="img/milkdrop/milkdrop-1-800.jpg" alt="MilkDrop: plavo-zlatno nebo kao oblaci" width="800" height="450" loading="lazy"><img src="img/milkdrop/milkdrop-3-800.jpg" alt="MilkDrop: zeleni i tirkizni slojevi poput tekuće stijene" width="800" height="450" loading="lazy"></div>
<p><button type="button" id="milk-start" class="btn big">Pokreni MilkDrop uz podvodni zvuk</button></p>
<h3>myNoise: zvučni pejzaži</h3>
<figure class="pic wide"><a href="https://mynoise.net/NoiseMachines/rainNoiseGenerator.php" rel="noopener"><img src="img/mynoise.jpg" srcset="img/mynoise-960.jpg 960w, img/mynoise.jpg 1920w" sizes="(max-width:1100px) 100vw, 1100px" alt="Snimka zaslona stranice myNoise, generator kiše: deset obojenih krugova za deset kanala zvuka, gumb za pokretanje i gotove postavke" width="1920" height="1080" loading="lazy"></a><figcaption>myNoise, generator kiše: svaki od deset obojenih krugova jedan je kanal zvuka. Snimka zaslona: mynoise.net.</figcaption></figure>
<p><a href="https://mynoise.net" rel="noopener">myNoise</a> je internetska stranica i aplikacija sa stotinama zvučnih pejzaža: kiša, more, šuma, vjetar, vatra, zdjele koje pjevaju. Izradio ju je belgijski inženjer zvuka Stéphane Pigeon od vlastitih snimki. Ljudi je koriste za opuštanje, san i usredotočenost.</p>
<p>Posebna je po tome što zvuk nije gotova snimka, nego deset kanala koje sam podešavam, od dubokog tutnjanja do sitnih kapi. Zato je dobra za ovu sobu: svaki kanal mogu poslati na drugi zvučnik, pa su kapi u kutovima, daleka grmljavina na jednoj strani, a dubina mora oko cijele sobe. Zvuk mogu prilagoditi i svakoj osobi, na primjer stišati visoke tonove za dijete osjetljivo na zvuk.</p>
<p><a class="btn off" href="https://mynoise.net/NoiseMachines/rainNoiseGenerator.php" rel="noopener">Kiša</a> <a class="btn off" href="https://mynoise.net/NoiseMachines/oceanNoiseGenerator.php" rel="noopener">More</a> <a class="btn off" href="https://mynoise.net/NoiseMachines/rainforestNoiseGenerator.php" rel="noopener">Prašuma</a> <a class="btn off" href="https://mynoise.net/NoiseMachines/windNoiseGenerator.php" rel="noopener">Vjetar</a> <a class="btn off" href="https://mynoise.net/NoiseMachines/singingBowlsDroneGenerator.php" rel="noopener">Zdjele koje pjevaju</a></p>
<p class="note">Za korištenje u terapijskoj sobi myNoise traži godišnju licencu.</p>
<h3>DJ Mantra: ambijentalna playlista</h3>
<p>Za mirne trenutke složio sam playlistu mekane, ambijentalne glazbe. Počinje s pjesmom Miss You od Trentemøllera, a dalje su Chantress Seba, Nils Frahm, Ólafur Arnalds, Brian Eno i Hania Rani.</p>
<div class="pl" id="pl"><div class="video" id="pl-box" hidden></div>
<ol class="pl-list">{''.join(f'<li><button type="button" class="pl-b" data-v="{v}"><img src="https://i.ytimg.com/vi/{v}/mqdefault.jpg" alt="" width="320" height="180" loading="lazy"><span>{esc(t)}</span></button><a href="https://www.youtube.com/watch?v={v}" rel="noopener" aria-label="{esc(t)} na YouTubeu">YouTube</a></li>' for v,t in zip(PLAYLIST,TRACKS))}</ol>
<p><a class="btn off" href="https://www.youtube.com/watch_videos?video_ids={','.join(PLAYLIST)}" rel="noopener">Otvori cijelu playlistu na YouTubeu</a></p></div>
</div>''', lede='Osoba u invalidskim kolicima sjedi usred sobe, a oko nje pliva karipski greben. Zvuk dolazi iz cijele sobe, kao da je stvarno pod morem. Ništa se ne mora raditi. A kad osoba to poželi, soba odgovara na njezin pokret i glas.')

s2 = sec('02','pokret','a','Analiza pokreta','Laboratorij pokreta: hod prije i poslije terapije', f'''
<div class="wrap">
{fig('ring','Prsten mobitela visi sa stropa u krugu, u sredini mala kuglasta mikrofonska kugla, mlada žena hoda kroz krug sa svjetlećim točkama na zglobovima','Prsten kamera i 3D mikrofon u sredini.','pic wide')}
<p>Sa stropa visi prsten promjera tri metra s dvanaest mobitela, svi okrenuti prema sredini. U sredini prstena je 3D mikrofon. Prsten mobitela snima osobu iz svih smjerova, a moja aplikacija Skeleton na svakoj snimci označi zglobove. Iz više kamera nastaje trodimenzionalni kostur koji se može izmjeriti.</p>
{fig('gait','Na zidu dva prozirna lika od točaka i linija u hodu, jedan nesimetričan, drugi uravnoteženiji; terapeutkinja pokazuje, studentica drži tablet','Isti hod prije i poslije terapije, jedan pored drugog.','pic wide')}
<p>Isti hod snimimo prije i poslije terapije i usporedimo ga na zidu: duljinu koraka, simetriju, ritam, držanje i opseg pokreta u zglobovima. Brojke ne zamjenjuju procjenu terapeuta; daju joj trag koji se može pratiti kroz mjesece.</p>
<div class="uses">
<div class="card"><h3 class="h4">Hod</h3><p>Duljina i ritam koraka, simetrija lijeve i desne strane, prije i poslije terapije.</p></div>
<div class="card"><h3 class="h4">Opseg pokreta</h3><p>Koliko se ruka diže, koljeno savija ili trup okreće, iz sesije u sesiju.</p></div>
<div class="card"><h3 class="h4">Ravnoteža</h3><p>Njihanje tijela u stajanju i pri prijelazima, uz igru na zidu kao motivaciju.</p></div>
<div class="card"><h3 class="h4">Usporena snimka</h3><p>Iz dvanaest kamera može se napraviti i "bullet time": pokret zamrznut i obiđen sa svih strana, za nastavu i za samu osobu.</p></div>
</div>
<p class="note">Za 3D zglobove iz više kamera postoji otvoreni alat <a href="https://pypi.org/project/pose2sim/" rel="noopener">Pose2Sim</a>. Istraživanja s takvim sustavima (npr. <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC10586693/" rel="noopener">OpenCap, 2023.</a>) pokazuju dobru točnost za ritam koraka i kutove u bočnoj ravnini, a slabiju za rotacije i stopalo, pa je laboratorij alat za praćenje i istraživanje, a ne dijagnostika. Snimke ostaju na računalu u sobi, uz pisani pristanak.</p>
</div>''', lede='Isti prostor postaje laboratorij za analizu ljudskog pokreta, bez markera i odijela: dovoljno je ući u krug.')

APPS_DONE = [
 ('Blender Control','AI na Mac miniju uređuje otvorenu scenu u Blenderu, radi snimke ekrana i renderira animacije.'),
 ('DaVinci Resolve Actions','gumbi i skripte za korekciju boje, izradu timelinea i izvoz u DaVinci Resolveu.'),
 ('Ableton Live Actions','spaja miksetu s Abletonom i sam priprema set kad se otvori.'),
 ('Vox to Txt','pritisneš F1, govoriš, i riječi se upišu gdje god je kursor.'),
 ('Mantra Manual Camera','mobitel postaje profesionalna kamera s ručnim postavkama i NDI izlazom.'),
 ('Cloud Mixer','miješa snimke, slike i prijenose uživo u jedan program s natpisima.'),
 ('Shruti Box','bordun, rage i akordi te trener glasa koji vodi kroz raspon.'),
]
s3 = sec('03','ai-lab','v','Kad soba miruje','AI laboratorij: govoriš, a soba stvara', f'''
<div class="wrap">
{fig('ai-storyboard','Muškarac se zavalio na nisku sofu usred sobe i mirno govori, a na zidovima se jedan po jedan pojavljuju crteži storyboarda','Kažeš što ti nije jasno, a storyboard se pojavi oko tebe.','pic wide')}
<p>Kad nema terapije, sjednem na sofu, pustim tihu glazbu i razgovaram s Claudeom; ono što opišem pojavi se na zidovima. Glazba i spora slika vode u opušteno, budno stanje, kakvo se obično povezuje s alfa i theta ritmom; meni u njemu ideje dolaze lakše. Ruke ostaju slobodne, nema tipkovnice ni miša: samo glas i četiri zida.</p>
<ol class="flow">
<li><b>Sjedneš</b> na sofu, svjetlo se priguši, svira tiha glazba.</li>
<li><b>Slušaš</b>: AI ti čita tekst ili scenarij naglas, prirodnim glasom.</li>
<li><b>Kažeš</b> što ti nije jasno: "Ne razumijem ovaj dio, napravi mi storyboard."</li>
<li><b>Gledaš</b> kako se za nekoliko minuta storyboard pojavljuje na zidovima oko tebe.</li>
<li><b>Doradiš glasom</b>: "Treći kadar bliže, više svjetla, dodaj glazbu." I opet.</li>
</ol>
<div class="split">{fig('ai-create','Žena na sofi govori i lagano gestikulira; na jednom zidu valovi glazbe, na drugom 3D žičani model, na trećem niz filmskih kadrova')}<div>
<p>Claude je mozak sobe: piše aplikacije, slaže glazbu u Abletonu, montira u DaVinci Resolveu, modelira i animira u Blenderu, a slike, video i zvuk izrađuje Higgsfield. Sve što se stvori odmah se vidi i čuje u cijeloj sobi.</p>
<ul class="tools"><li><b>Claude Code</b> mozak: razumije, planira, piše</li><li><b>Ableton Live</b> glazba i prostorni zvuk</li><li><b>DaVinci Resolve</b> montaža i boja</li><li><b>Blender</b> 3D i animacija</li><li><b>Higgsfield</b> slike, video, zvuk u videu</li><li><b>Speechify</b> čitanje naglas</li></ul>
</div></div>
<h3>To nije budućnost, to već radim</h3>
<p>Sve svoje aplikacije napravio sam razgovarajući s Claude Codeom. U ovoj sobi takve se stvari rade sjedeći na sofi.</p>
<details><summary>Sedam aplikacija koje sam već napravio glasom</summary><ul class="done">{''.join(f'<li><b>{n}</b>: {d}</li>' for n,d in APPS_DONE)}</ul></details>
{fig('alpha','Osoba sjedi prekriženih nogu na sofi zatvorenih očiju, a na zidovima teku meki oblici boja iz kojih izranjaju skice','Tišina prije ideje.','pic wide')}
</div>''', lede='Isti zidovi, isti zvučnici, ali bez terapije: radionica u kojoj se glasom stvara aplikacija, glazba, film, 3D svijet ili istraživanje.')

USES = [
 ('Istraživanje pokreta','Mjerljivi podaci o hodu i pokretu za radove odsjeka.','Primjer: ista skupina djece snimljena na početku i kraju semestra.'),
 ('Doktorske disertacije','Snimanje, obrada i prikaz podataka glasom, bez programiranja.','Primjer: "Usporedi duljinu koraka za svih dvadeset ispitanika i nacrtaj grafikon."'),
 ('Studije slučaja','Svaka sesija ostaje zapisana: pokret, zvuk, bilješke terapeuta.','Primjer: pregled napretka jednog korisnika kroz šest mjeseci na zidu.'),
 ('Usporedba korisnika','Grafikoni koji uspoređuju korisnike, terapije ili skupine.','Primjer: dvije metode terapije, jedna pored druge.'),
 ('Nastava i praksa','Studenti uče gledati pokret i vode terapiju uz povratnu informaciju.','Primjer: usporena 3D snimka hoda za predavanje.'),
 ('Skice i eksperimenti','Ideja izgovorena ujutro, aplikacija ili scena isprobana popodne.','Primjer: nova igra za ravnotežu za jednu djevojčicu.'),
 ('Logopedija','Snimanje glasa i govora te priče i slike složene oko riječi koje dijete vježba.','Primjer: priča s pet riječi s glasom R, s ilustracijama na zidovima.'),
 ('Autizam i senzorika','Mirna soba prilagođena osjetilnom profilu svakog djeteta.','Primjer: tiše boje i manje zvukova za dijete osjetljivo na podražaje.'),
 ('Oštećenja vida i sluha','Orijentacija po zvuku iz osam smjerova i velik, kontrastan prikaz.','Primjer: igra "odakle dolazi zvuk" za dijete slabijeg vida.'),
]
s4 = sec('04','erf','w','Za fakultet','Što soba daje ERF-u', f'''
<div class="wrap">
{fig('research','Tri istraživača razgovaraju usred sobe, na zidovima veliki grafikoni i niz malih svjetlećih likova','Zidovi kao radna ploča istraživanja.','pic wide')}
<div class="uses">{''.join(f'<div class="card"><span class="n2">{i+1:02d}</span><h3 class="h4">{t}</h3><p>{d}</p><p class="ex">{e}</p></div>' for i,(t,d,e) in enumerate(USES))}</div>
<p class="note">Istraživanja višeosjetilnih soba još su malobrojna i dokazi su ograničeni (npr. <a href="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12255839/" rel="noopener">pregled iz 2025.</a>), pa sobu vidim kao mjesto koje stvara nova istraživanja, a ne kao dokazanu terapiju. O svemu odlučuje terapeut, a svaka snimka nastaje uz pisani pristanak.</p>
</div>''', lede='Osim terapije, soba je mjesto za istraživanje, nastavu, disertacije i eksperimente. Evo što mogu zamisliti za vaše odsjeke.')

s5 = sec('05','aplikacije','t','Aplikacije','Što već postoji', lede='Tri aplikacije koje rade već danas, bez sobe.', body=f'''
<div class="wrap"><div class="apps">
<div class="card"><h3 class="h4">Skeleton</h3><p>Moja aplikacija za Mac: kostur preko slike s jedne ili više kamera, usporedba s ciljanom pozom, glasovne upute i ocjena od 0 do 100. Mobiteli preko USB-a ili Wi-Fija postaju njezine kamere.</p></div>
<div class="card mg"><h3 class="h4">MindGarden</h3><p>Moja besplatna aplikacija za vježbanje uma, napravljena za moju baku: zagonetke, kartice za pamćenje, čitanje sata, nizovi brojeva i igre jezika u kojima šest prijatelja iz šest zemalja zajedno uređuje vrt. Radi bez interneta, na šest jezika, za više korisnika.</p>
<div class="shots"><img src="img/mindgarden/mg-lang.jpg" alt="MindGarden: igra Upoznaj prijatelje sa šest zastava" width="600" height="663" loading="lazy"><img src="img/mindgarden/mg-clock.jpg" alt="MindGarden: koliko sati pokazuje sat" width="600" height="663" loading="lazy"><img src="img/mindgarden/mg-pairs.jpg" alt="MindGarden: pronađi parove, tri razine" width="600" height="663" loading="lazy"></div>
<p><a class="btn" href="https://drive.google.com/drive/folders/1ENHB7nE4Zr2pi9wOPSBpndioFYJy0ulF" rel="noopener">Preuzmi MindGarden (Android)</a></p></div>
<div class="card"><h3 class="h4">Chakra and Elements Toning</h3><p>Aplikacija za meditaciju sa zvukovima čakri i elemenata, MilkDrop slikom i krugom daha. Za Android.</p><p><a class="btn" href="https://github.com/markoboskoauroville/MANTRA_ROOM/releases/download/v25/25-chakra-elements-toning-v25.apk" data-dl-app="chakra-and-elements-toning" data-dl-label="preuzimanja" rel="noopener">Preuzmi</a></p></div>
</div></div>''')

s6 = sec('06','oprema','a','Izvedba','Oprema, shema i troškovi', f'''
<div class="wrap">
<div class="totals">
<div class="tile"><span>Soba, jednokratno</span><b>{eur(room_tot+soft_tot)}</b></div>
<div class="tile"><span>Prsten kamera, dodatno</span><b>{eur(ring_tot)}</b></div>
<div class="tile"><span>Mjesečno</span><b>≈ 260 €</b></div>
</div>
<h3>Shema spajanja</h3>
{SCHEME}
<p>Sve vodi jedan Mac mini M6 s 24 GB memorije. USB kabel je dobar samo do pet metara, pa USB do svakog para zvučnika ide kroz zid mrežnim kabelom, do 50 metara. macOS spaja sva četiri para u jednu zvučnu karticu s osam kanala. Mac sam vodi tri projektora, četvrti ide preko DisplayLink adaptera. Mobiteli šalju sliku preko Wi-Fija.</p>
<details><summary>Android ili iPhone?</summary><p>Preporučujem Android. Na Androidu sam razvijam aplikacije i instaliram ih bez trgovine, a Mac njima upravlja preko USB-a ili Wi-Fija. Skeleton već prima sliku s više Android mobitela odjednom. iPhone ima odličnu kameru, ali je skuplji, aplikacije idu samo kroz Appleovu trgovinu, a Mac ga kao kameru koristi jedan po jedan.</p></details>
<details><summary>Soba: oprema ({eur(room_tot)})</summary><div class="tw"><table>{room_t}<tfoot><tr><td colspan="3">Ukupno</td><td class="n">{eur(room_tot)}</td><td></td></tr></tfoot></table></div></details>
<details><summary>Laboratorij pokreta: prsten kamera ({eur(ring_tot)} + vješanje)</summary><div class="tw"><table>{ring_t}<tfoot><tr><td colspan="3">Ukupno</td><td class="n">{eur(ring_tot)}</td><td></td></tr></tfoot></table></div></details>
<details><summary>Softver, jednokratno ({eur(soft_tot)})</summary><div class="tw"><table>{soft_t}<tfoot><tr><td colspan="3">Ukupno</td><td class="n">{eur(soft_tot)}</td><td></td></tr></tfoot></table></div></details>
<details><summary>Pretplate, mjesečno</summary><div class="tw"><table><thead><tr><th>Pretplata</th><th class="n">Mjesečno</th><th>Gdje</th></tr></thead><tbody>{month_rows}</tbody></table></div></details>
<details><summary>Prije kupnje</summary><p>Kod Optome potvrditi da ZH430UST radi okrenut naopako na nosaču OWM3000. Adam D3V ima navoj 3/8" i izravno se navije na stropni nosač; rad naopako proizvođač ne navodi, pa svaki zvučnik dobiva sigurnosnu sajlu. Godox ne radi stropne nosače, pa je umjesto stalka za rasvjetu odabran stropni nosač s istim navojem. Zylia trenutno nema na zalihi u Njemačkoj. Prsten kamera vješa izvođač uz atest statičara. Stavke označene kao procjena nisu provjerene u trgovini. Nisu uključene utičnice na stropu ni ugradnja.</p></details>
<p class="note">Ukupno jednokratno: <b>{eur(ONE_TIME)}</b> (soba, prsten i softver), uz oko 260 € mjesečno (Claude Max i Higgsfield). Cijene su od 21.11.2026., s PDV-om osim gdje piše drugačije.</p>
</div>''')

EUPH = open(os.path.join(PARTS,'parts_euphony.html')).read() if PARTS else ''
INSTR = open(os.path.join(PARTS,'parts_instr.html')).read() if PARTS else ''
grid = re.search(r'<div id="instruments" class="grid">.*?</div>\s*</div>\s*(?=<p class="note">)', INSTR, re.S)
grid = grid.group(0) if grid else ''

s7 = sec('07','nadahnuce','w','Nadahnuće','Svaram, instrumenti i ljudi', f'''
<div class="wrap">
<p>Dok sam živio u Aurovilleu, snimao sam filmove za <a href="https://svaram.org" rel="noopener">Svaram</a>, radionicu za zvuk i instrumente. Njihovi prostori su uzor za ovu sobu: instrumenti koje dijete može dotaknuti i osjetiti cijelim tijelom.</p>
<div class="duo">
<div><figure class="pic nat"><img src="img/svaram/soundgarden-1.jpg" alt="Metalni ksilofon s velikim cijevima u zelenom vrtu Svarama" width="1600" height="534" loading="lazy"><figcaption><a href="https://svaram.org/sound-garden-art-installations/" rel="noopener">Soundgarden</a>: zvučni vrt na otvorenom.</figcaption></figure>{yt('GQyXzu90d0k','SVARAM Sound Garden, film Marka Boška')}</div>
<div><figure class="pic nat"><img src="img/svaram/sonorium-2.jpg" alt="Terapeut uz drveni krevet s monokordom na kojem leži žena" width="1600" height="667" loading="lazy"><figcaption><a href="https://svaram.org/sonorium/" rel="noopener">Sonorium</a>: prostor za opuštanje zvukom.</figcaption></figure>{yt('78xD4G86daA','SVARAM Sonorium, film Marka Boška')}</div>
</div>
<p class="note">Fotografije: Svaram, Auroville. Filmove sam snimio ja. Više: <a href="https://youtube.com/playlist?list=PLcbk1jSryyxkAe66vLKVKnSPGOVB5PmB3" rel="noopener">Auroville Videos by Marko Bosko</a>.</p>
<div class="trio">
<div class="card"><h3 class="h4">Euphony Trio: kristalna zvona</h3><p>Kristalna zvona Alana Towera vrte se do sedam minuta, a njihov se zvuk razlijeva cijelom sobom. Svira ih terapeut, ostali slušaju i osjećaju. Cijena na upit.</p>{yt('Mv5_qU3qfts','Marko svira kristalna zvona')}<p><a class="btn off" href="https://atower1717.github.io/Aperture-Gallery-2/listen/flumie-float/" rel="noopener">Poslušaj Euphony</a></p></div>
<div class="card">{fig('lifestyle-3','Djeca i odrasli muškarac sjede oko velikog bubnja i zajedno bubnjaju')}<h3 class="h4">Marko Borić: veliki bubnjevi</h3><p>Gradi bubnjeve na kojima svira više djece zajedno i vodi radionice izrade šejkera i bubnjeva, u kojima svatko napravi svoj instrument.</p></div>
<div class="card"><h3 class="h4">Stonewhistle: flaute bez pogrešnog tona</h3><p>Glinene flaute Hansa Houkesa u kojima svaka kombinacija rupica zvuči skladno. Moj video pokazuje kako se sviraju.</p>{yt('qVSTpt1eESs','Kako se sviraju flaute Stonewhistle, video Marka Boška')}</div>
</div>
<details><summary>Flaute Stonewhistle s cijenama</summary>{grid}<p class="note">Flaute se rade po narudžbi, čeka se 3 do 5 mjeseci; za sviranje je potreban dah.</p></details>
</div>''')

s8 = f'''<section id="o-meni" class="sec about"><div class="wrap"><p class="kicker">O meni</p><h2>Marko Boško</h2>
<p>Dvadeset sedam godina radio sam zvuk i sliku za hrvatske televizije, sedam godina živio sam u Aurovilleu u Indiji, sviram udaraljke, a kao DJ Mantra puštam glazbu za ples. Danas glasom, uz Claude Code, gradim aplikacije za zvuk, sliku i pokret.</p>
<p class="lede">Volio bih vam sobu pokazati uživo i čuti što bi vašem odsjeku bilo najkorisnije. Predlažem razgovor od pola sata, na fakultetu ili putem videopoziva.</p><p><a class="btn" href="mailto:marko.bosko@auroville.community">Dogovorimo razgovor</a></p>
<p class="links"><a href="https://markobosko.org" rel="noopener">markobosko.org</a> <a href="https://djmantra.markobosko.org" rel="noopener">djmantra.markobosko.org</a> <a href="mailto:marko.bosko@auroville.community">marko.bosko@auroville.community</a></p>
<p class="note">Slike sobe prikaz su zamišljenog prostora i izrađene su umjetnom inteligencijom. MilkDrop kadrovi su pravi.</p></div></section>
'''

head = open(HEAD_FILE).read()
head = re.sub(r'<title>[^<]*</title>', '<title>Jedna soba, četiri namjene · Marko Boško</title>', head)
head = re.sub(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="Jedna soba, četiri namjene · Marko Boško">', head)
head = re.sub(r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="Terapijska soba pod morem, laboratorij za analizu pokreta, AI laboratorij i istraživanje. Prijedlog za ERF Zagreb.">', head)
head = head.replace('<meta name="twitter:card"', '<meta property="og:image" content="https://therapies.markobosko.org/img/room.jpg">\n<meta name="twitter:card"') if 'og:image' not in head else head
head = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="Jedna soba, četiri namjene: terapijska soba pod morem, laboratorij za analizu pokreta, AI laboratorij i istraživanje. Prijedlog za ERF Zagreb.">', head)
head = head.replace('</head>', '<link rel="preload" as="image" href="img/room-960.jpg" imagesrcset="img/room-960.jpg 960w, img/room.jpg 1920w" imagesizes="100vw">\n</head>') if 'rel="preload"' not in head else head
page = (head + '<body>\n<a class="skip" href="#terapija">Preskoči na sadržaj</a>\n' + hero + '<main>\n' + s1 + s2 + s3 + s4 + s5 + s6 + s7 + s8 + '</main>\n'
        '<div id="mk" hidden role="dialog" aria-label="MilkDrop"><canvas id="mk-cv" aria-hidden="true"></canvas><button type="button" id="mk-x">✕ Izlaz</button></div>\n'
        '<audio id="mk-au" src="audio/karipsko-more-underwater.mp3" preload="none" loop></audio>\n'
        '<script src="playlist.js" defer></script>\n<script src="milk.js" defer></script>\n<script src="https://mantra-downloads.marko-bosko-925.workers.dev/counter.js" defer></script>\n</body>\n</html>\n')
open(os.path.join(ROOT,'site','index.html'),'w').write(page)
print('one-time', round(ONE_TIME,2), 'room', round(room_tot,2), 'ring', round(ring_tot,2), 'soft', soft_tot)
