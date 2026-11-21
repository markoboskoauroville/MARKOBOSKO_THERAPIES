# Builds the phase-3 body of site/index.html (21.11.2026). Run once from the repo root; idempotent markers.
import re, html
P='site/index.html'; s=open(P).read()

def fig(name, alt, cap=None):
    c = f'<figcaption>{cap}</figcaption>' if cap else ''
    return (f'<figure class="pic"><img src="img/{name}.jpg" srcset="img/{name}-960.jpg 960w, img/{name}.jpg 1920w" '
            f'sizes="(max-width:980px) 100vw, 940px" alt="{alt}" width="1920" height="1072" loading="lazy">{c}</figure>')
def yt(vid, title):
    return (f'<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/{vid}" title="{title}" loading="lazy" '
            'referrerpolicy="strict-origin-when-cross-origin" allow="accelerometer; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>')
def eur(x): return f'{x:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.') + ' €'

# ---------------- costs ----------------
HW = [
 ('Apple Mac mini M6, 24 GB memorije, 512 GB SSD', 1, 1489.00, 'https://www.apple.com/de/shop/buy-mac/mac-mini', 'apple.com/de', 'cijena iz tiska, provjeriti u konfiguratoru'),
 ('Optoma ZH430UST, ultrakratki laserski projektor, Full HD, 4.000 lumena', 4, 1398.00, 'https://www.beamer-discount.de/en/products/optoma-zh430ust-beamer-mit-4-000-ansi-lumen-und-full-hd-dura-core', 'beamer-discount.de', ''),
 ('Optoma OWM3000, stropni nosač za ultrakratki projektor', 4, 107.73, 'https://www.office-partner.de/optoma-owm3000-projektorhalterung-fuer-ultrakurzdistanzgeraete-max.tragkraft-15kg-7853514', 'office-partner.de', ''),
 ('pro snake AOC HDMI 15 m, optički HDMI kabel do projektora', 4, 69.00, 'https://www.thomann.de/de/pro_snake_aoc_hdmi_a_a_15m.htm', 'Thomann', ''),
 ('DisplayLink USB-C na HDMI adapter za četvrti projektor (OWC Dual HDMI)', 1, 97.90, 'https://www.owc.com/solutions/usb-c-dual-hdmi-4k-display-adapter', 'OWC', 'cijena iz usporedbe cijena'),
 ('Adam Audio D3V, par aktivnih zvučnika s USB-C ulazom', 4, 259.00, 'https://www.thomann.de/de/adam_audio_d3v_black.htm', 'Thomann', ''),
 ('Adam Audio D3V produžni kabel između zvučnika u paru', 4, 14.99, 'https://www.thomann.de/de/adam_audio_d3v_black.htm', 'Thomann', ''),
 ('iriz CM550, stropni nosač s navojem 3/8" za zvučnik', 8, 46.00, 'https://www.thomann.de/de/iriz_cm550_adjustable_ceiling_mount.htm', 'Thomann', ''),
 ('Lindy USB 2.0 preko mrežnog kabela Cat.6, do 50 m (USB kroz zid)', 4, 129.00, 'https://www.thomann.de/de/lindy_50m_usb_2_0_cat.6_extender.htm', 'Thomann', ''),
 ('USB hub s napajanjem, 7 priključaka, za Mac mini', 1, 40.00, '', 'procjena', 'procjena'),
 ('Android mobitel s kamerom uz svaki zvučnik (rabljeni Pixel ili sličan)', 8, 120.00, '', 'procjena', 'procjena'),
 ('Godox MTH02, držač mobitela s navojem 1/4"', 8, 18.00, 'https://www.calumet.de/product/godox-mth02-smartphone-halterung', 'calumet.de', ''),
 ('USB punjač za mobitel na stropu', 8, 10.00, '', 'procjena', 'procjena'),
 ('Ubiquiti UniFi U7 Pro, Wi-Fi 7 pristupna točka na stropu', 1, 190.00, 'https://preisvergleich.heise.de/ubiquiti-unifi-7-pro-u7-pro-a3096524.html', 'heise.de', 'cijena iz usporedbe cijena'),
 ('Zylia ZM-2, 3D mikrofon s 19 kapsula u jednoj kugli, USB', 1, 1625.20, 'https://shop.zylia.co/', 'zylia.co', 'cjenik bez PDV-a, dostupnost na upit'),
 ('Audio-Technica PRO 45, viseći kondenzatorski mikrofon', 4, 109.00, 'https://www.thomann.de/de/audio_technica_pro45_haengemikrofon.htm', 'Thomann', ''),
 ('Behringer UMC404HD, USB zvučna kartica s 4 mikrofonska ulaza', 1, 95.00, 'https://www.thomann.de/de/behringer_umc404hd.htm', 'Thomann', ''),
 ('Mrežni kabeli Cat.6 kroz zid, zidne utičnice i spojnice', 1, 150.00, '', 'procjena', 'procjena'),
]
SW = [
 ('Ableton Live 12 Suite (s Max for Live), vodi svih osam zvučnika', 1, 479.00, 'https://www.thomann.de/de/ableton_live_12_suite.htm', 'Thomann', ''),
 ('Envelop for Live i IEM Plugin Suite, prostorni zvuk i 3D dekoderi', 1, 0.0, 'https://www.envelop.us/software', 'envelop.us', 'besplatno'),
 ('ZYLIA Studio, snimanje i pretvorba 3D zvuka', 1, 0.0, 'https://www.zylia.co/', 'zylia.co', 'uz mikrofon'),
 ('Skeleton, moja aplikacija za praćenje pokreta s više kamera', 1, 0.0, '', 'Marko Boško', 'besplatno'),
 ('MilkDrop vizualizacije (butterchurn)', 1, 0.0, 'https://butterchurnviz.com/', 'butterchurn', 'besplatno'),
]
MONTHLY = [
 ('Claude Max (Claude Code), studio u kojem nastaju nove vježbe', 214.00, 'https://claude.com/pricing', 'claude.com', '200 $ mjesečno + PDV, oko 214 €'),
 ('Suno, besplatni račun za svaku osobu (10 pjesama dnevno)', 0.0, 'https://suno.com/pricing', 'suno.com', 'Pro oko 10 $ mjesečno za vlastiti glas'),
 ('myNoise, licenca za korištenje u terapijskoj sobi', None, 'https://mynoise.net/licensing.php', 'mynoise.net', 'godišnja licenca, cijenu predlaže korisnik'),
 ('YouTube, playlista DJ Mantra', 0.0, 'https://www.youtube.com/', 'youtube.com', 'besplatno'),
]
def rows(items):
    out=[]; tot=0
    for name,q,price,url,where,note in items:
        t=q*price; tot+=t
        w = f'<a href="{url}" rel="noopener">{where}</a>' if url else where
        nt = f'<br><small class="note">{note}</small>' if note and note not in ('procjena',) else ''
        out.append(f'<tr><td>{name}{nt}</td><td class="n">{q}</td><td class="n">{eur(price)}</td><td class="n">{eur(t)}</td><td>{w}</td></tr>')
    return '\n'.join(out), tot
hw_rows, hw_tot = rows(HW); sw_rows, sw_tot = rows(SW)
mo=[]; mo_tot=0
for name,price,url,where,note in MONTHLY:
    p = 'na upit' if price is None else eur(price)
    if price: mo_tot+=price
    mo.append(f'<tr><td>{name}<br><small class="note">{note}</small></td><td class="n">{p}</td><td><a href="{url}" rel="noopener">{where}</a></td></tr>')

PLAYLIST = ['bfcl1JMGXdI','dIwwjy4slI8','hE_8C33gm7A','gRBg2d79Q8c','GFbkF_fsW24','SasKGA1hq9Y','0kYc55bXJFI','tgwBXJE-9sM','RpclSuABeRc','OlaTeXX3uH8','YFkKBfmSx5o','l0yRNQj2_tc','mqU0XsELBCA','UfcAVejslrU']
TRACKS = ['Chantress Seba i Malte Marten – Song from the Forest','Nils Frahm – Says','Trentemøller – Miss You','Chantress Seba – You Are Light','Nils Frahm – Ambre','Trentemøller – Nightwalker','Ólafur Arnalds – Near Light','Nils Frahm – Familiar','Chantress Seba i Malte Marten – The Oracle','Brian Eno – An Ending (Ascent)','Nils Frahm – Sunson','Hania Rani – Glass','Jon Hopkins – Abandon Window','Marconi Union – Weightless']

SCHEME = '''<div class="scheme card" role="img" aria-label="Shema spajanja: Mac mini u središtu; HDMI prema četiri projektora; USB preko mrežnog kabela prema četiri para zvučnika; Wi-Fi prema osam mobitela; USB prema 3D mikrofonu i zvučnoj kartici s četiri viseća mikrofona">
<svg viewBox="0 0 900 560" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0L10,5L0,10z" class="sf"/></marker></defs>
<g class="ln hdmi"><path d="M450,250 L150,90"/><path d="M450,250 L330,60"/><path d="M450,250 L570,60"/><path d="M450,250 L750,90"/></g>
<g class="ln usb"><path d="M410,300 L120,330"/><path d="M420,320 L230,440"/><path d="M480,320 L670,440"/><path d="M490,300 L780,330"/></g>
<g class="ln wifi"><path d="M450,330 L450,410"/></g>
<g class="ln usb"><path d="M400,270 L170,220"/><path d="M500,270 L730,220"/></g>
<rect x="380" y="235" width="140" height="95" rx="14" class="box main"/><text x="450" y="275" class="t b">Mac mini M6</text><text x="450" y="296" class="t s">24 GB · 512 GB</text><text x="450" y="314" class="t s">Ableton · Skeleton</text>
<g><rect x="80" y="62" width="140" height="44" rx="10" class="box"/><text x="150" y="88" class="t">Projektor 1</text></g>
<g><rect x="260" y="32" width="140" height="44" rx="10" class="box"/><text x="330" y="58" class="t">Projektor 2</text></g>
<g><rect x="500" y="32" width="140" height="44" rx="10" class="box"/><text x="570" y="58" class="t">Projektor 3</text></g>
<g><rect x="680" y="62" width="140" height="44" rx="10" class="box"/><text x="750" y="88" class="t">Projektor 4</text></g>
<text x="450" y="125" class="t s">HDMI optički kabel, 15 m (četvrti preko DisplayLinka)</text>
<g><rect x="30" y="305" width="180" height="56" rx="10" class="box"/><text x="120" y="328" class="t">Par zvučnika 1</text><text x="120" y="347" class="t s">Adam D3V + mobitel</text></g>
<g><rect x="140" y="425" width="180" height="56" rx="10" class="box"/><text x="230" y="448" class="t">Par zvučnika 2</text><text x="230" y="467" class="t s">Adam D3V + mobitel</text></g>
<g><rect x="580" y="425" width="180" height="56" rx="10" class="box"/><text x="670" y="448" class="t">Par zvučnika 3</text><text x="670" y="467" class="t s">Adam D3V + mobitel</text></g>
<g><rect x="690" y="305" width="180" height="56" rx="10" class="box"/><text x="780" y="328" class="t">Par zvučnika 4</text><text x="780" y="347" class="t s">Adam D3V + mobitel</text></g>
<text x="450" y="500" class="t s">USB → mreža Cat.6 kroz zid → USB na stropu (Lindy)</text>
<g><rect x="370" y="410" width="160" height="56" rx="10" class="box"/><text x="450" y="433" class="t">Wi-Fi na stropu</text><text x="450" y="452" class="t s">8 kamera mobitela</text></g>
<g><rect x="60" y="195" width="150" height="50" rx="10" class="box"/><text x="135" y="216" class="t">3D mikrofon</text><text x="135" y="234" class="t s">Zylia, USB</text></g>
<g><rect x="690" y="195" width="170" height="50" rx="10" class="box"/><text x="775" y="216" class="t">Zvučna kartica</text><text x="775" y="234" class="t s">4 viseća mikrofona</text></g>
<g class="lg"><line x1="40" y1="525" x2="80" y2="525" class="ln hdmi"/><text x="88" y="530" class="t s l">slika (HDMI)</text>
<line x1="230" y1="525" x2="270" y2="525" class="ln usb"/><text x="278" y="530" class="t s l">zvuk i mikrofoni (USB)</text>
<line x1="470" y1="525" x2="510" y2="525" class="ln wifi"/><text x="518" y="530" class="t s l">kamere mobitela (Wi-Fi)</text></g>
</svg></div>'''

P1 = f'''<section id="projekt-1">
<h1>Soba pod morem</h1>
<figure class="fig"><img src="img/room.jpg" srcset="img/room-960.jpg 960w, img/room.jpg 1920w" sizes="(max-width:980px) 100vw, 940px" alt="Mlada osoba u invalidskim kolicima usred sobe gleda kornjaču i ražu na zidovima; projektori i zvučnici s mobitelima vise sa stropa, pod je prazan" width="1920" height="1072"></figure>
<p>Osoba u invalidskim kolicima sjedi usred sobe, a sa sva četiri zida oko nje pliva karipski greben. Tirkizna voda, koralji, ribe, kornjača i raža, i sunčeve zrake koje padaju s površine. Zvuk dolazi iz cijele sobe, kao da je osoba stvarno pod morem. Ništa se ne mora raditi, dovoljno je biti tu. A kad osoba to poželi, soba odgovara na njezin pokret i glas.</p>

<h2>Kako je složeno</h2>
<figure class="fig"><img src="img/setup.jpg" srcset="img/setup-960.jpg 960w, img/setup.jpg 1920w" sizes="(max-width:980px) 100vw, 940px" alt="Prazna soba odozdo: projektori i mali zvučnici vise sa stropa, uz zvučnike mobiteli, pod je potpuno prazan" width="1920" height="1072"></figure>
<p>Na podu nema ničega osim ljudi. Sve visi sa stropa: uz svaki zid jedan ultrakratki laserski projektor okrenut naopako, koji baca sliku odozgo na zid, i osam malih zvučnika Adam Audio D3V u četiri para, također naopako, na stropnim nosačima s navojem. Uz svaki zvučnik je Android mobitel.</p>
<p>Sve vodi jedan Mac mini M6 s 24 GB memorije i 512 GB prostora. Svaki par zvučnika spaja se na njega preko USB-a. Budući da je USB kabel dobar samo do pet metara, USB ide kroz zid mrežnim kabelom: uz Mac je mali odašiljač, na stropu prijemnik, a između njih do 50 metara kabela Cat.6. macOS spaja sva četiri para u jednu veliku zvučnu karticu s osam kanala, pa svaki zvučnik dobiva svoj zvuk. Zvuk vodi Ableton Live, koji kišu, valove ili ribu koja prolazi može smjestiti u bilo koji kut sobe i polako je pomicati.</p>
<h3>Shema spajanja</h3>
{SCHEME}
<p class="note">Mac mini M6 sam vodi tri zaslona (HDMI i dva Thunderbolt izlaza), pa četvrti projektor ide preko DisplayLink adaptera. HDMI optički kabeli rade samo u jednom smjeru i provlače se kroz zid zajedno s utikačima. Zvučnici, 3D mikrofon i zvučna kartica idu u USB hub s napajanjem jer Mac ima pet USB priključaka. Mobiteli šalju sliku kamere preko Wi-Fija, a pristupna točka je kabelom spojena na Mac. Uz svaki par zvučnika i uz svaki mobitel treba utičnica na stropu.</p>

<h2>Mobitel uz svaki zvučnik</h2>
{fig('phone-detail','Mali crni zvučnik naopako na stropnom nosaču, uz njega mobitel u držaču koji na ekranu pokazuje živi val zvuka', 'Mobitel pokazuje što zvučnik svira i kamerom gleda u sobu.')}
<p>Mobitel uz zvučnik ima dvije uloge. Na ekranu pokazuje što taj zvučnik upravo svira, kao živi val zvuka, pa terapeut odmah vidi gdje je koji zvuk. A kamerom gleda u sobu. Osam kamera iz osam smjerova zna gdje je osoba, je li blizu ili daleko i kako joj stoji tijelo. Kad se osoba približi zvučniku, njegov zvuk se mijenja: postaje bliži, topliji ili se pojavi nova životinja.</p>
<div class="card"><h3 style="margin-top:0">Android ili iPhone?</h3>
<p>Preporučujem Android. Na Androidu sam razvijam aplikacije i instaliram ih bez trgovine, Mac njima upravlja preko USB-a ili Wi-Fija (pokreće kameru, drži ekran upaljenim, mijenja postavke), a rabljeni Android s dobrom kamerom stoji oko 120 €. Moja aplikacija Skeleton već prima sliku s Android mobitela preko USB-a i Wi-Fija, četiri ili više odjednom. iPhone ima odličnu kameru, ali je skuplji, aplikacije idu samo kroz Appleovu trgovinu, a Mac ga kao kameru preko Continuityja koristi jedan po jedan.</p></div>

<h2>Igra pokreta: opuštanje i aktivacija</h2>
{fig('movement','Dijete na sredini sobe diže ruke, a na zidu svjetleći lik od linija ponavlja pokret dok oko njega plivaju ribe i kornjača','Pogođen pokret: ribe i kornjača doplivaju kao nagrada.')}
<p>Za to koristim svoju aplikaciju <b>Skeleton</b>. Ona na sliku osobe stavlja kostur od linija i točaka, istovremeno s četiri ili više kamera, a mobiteli su te kamere. Terapeut odabere pokret, a aplikacija ga prikaže kao prozirnu siluetu. Dijelovi tijela postaju zeleni kad se poklope, a kad osoba pokret pogodi i zadrži ga, dolazi nagrada u slici i u zvuku. Težina se podešava, od vrlo blage za početak (velika tolerancija, kratko zadržavanje) do točnije.</p>
<div class="gal">{fig('relax','Način opuštanja: dijete leži na mekanoj vreći usred tamnoplave sobe s meduzama, terapeutkinja sjedi uz njega','Opuštanje: spore meduze, tamna voda, dah.')}{fig('activation','Način aktivacije: djeca dodiruju svjetleće krugove na zidu i iz njih izlaze jata riba','Aktivacija: dohvati krug svjetla i pusti ribe.')}</div>
<div class="grid2">
<div class="card"><h3 style="margin-top:0">Opuštanje</h3><p>Pokreti su spori i mali: ruke se dižu s udahom i spuštaju s izdahom, glava se okreće prema zvuku. Slika je tamna i mirna, meduze i kitovi plivaju polako. Nagrada je nježna: zid zasvijetli toplije, kit zapjeva iz kuta sobe, kiša se utiša.</p></div>
<div class="card"><h3 style="margin-top:0">Aktivacija</h3><p>Pokreti su veći i brži: ruke u zvijezdu, dohvatiti krug svjetla na zidu, nagnuti se, okrenuti se prema drugom zidu. Slika je svijetla i živa. Nagrada je vesela: jato riba proleti cijelom sobom, bubanj udari, mjehurići se razlete iz svih zvučnika.</p></div>
</div>

<h2>Pjevaj i dobij svoju pjesmu</h2>
{fig('singing','Mladić u invalidskim kolicima sretno pjeva prema malom kuglastom mikrofonu koji visi sa stropa, terapeutkinja drži tablet','Otpjevaj nekoliko taktova i pjesma se vrati cijela.')}
<p>Soba je i igralište s umjetnom inteligencijom. Osoba otpjeva nekoliko taktova ili samo melodiju u mikrofon, terapeut pritisne gumb, i za minutu iz svih zvučnika dođe cijela pjesma nastala iz te melodije. Za osobe s teškoćama to je velika nagrada: čuju svoj glas i svoju ideju kao pravu pjesmu.</p>
<p>Za to služi <a href="https://suno.com" rel="noopener">Suno</a>. Snimka se učita u Suno (Upload audio), a Suno od nje napravi cijelu pjesmu (Cover ili Extend). Besplatni račun daje oko deset pjesama dnevno, bez prava na komercijalnu upotrebu, što je za osobnu nagradu dovoljno. Da pjesmu pjeva baš glas te osobe, Suno ima mogućnost Voices u plaćenom Pro paketu, a glas osoba mora sama potvrditi. Za djecu sve ide uz pristanak roditelja.</p>

<h2>Snimanje u 3D</h2>
{fig('microphones','Pogled prema stropu: u sredini visi mala kugla puna mikrofonskih kapsula, oko nje četiri tanka viseća mikrofona','3D mikrofon u sredini i četiri viseća mikrofona.')}
<p>Soba je i studio za 3D snimanje. Sa stropa u sredini visi <b>Zylia</b>, jedna kugla s 19 mikrofona, spojena USB-om. Ona snima prostor u tri dimenzije, pa se sve što se u sobi dogodi, pjesma, bubnjanje u krugu ili glas terapeuta, može poslije reproducirati na osam zvučnika točno kako je zvučalo, sa svih strana. Uz nju četiri viseća kondenzatorska mikrofona snimaju glasove i instrumente izbliza.</p>

<h2>Kad soba miruje: studio za nove vježbe</h2>
{fig('claude-studio','Terapeutkinja stoji usred sobe i govori prema mikrofonu sa stropa, a na zidovima su skice poza, valova zvuka i boja','Terapeut opisuje novu vježbu, a soba je izradi.')}
<p>Kad nema terapije, soba postaje radionica. Terapeut govori u mikrofon što bi trebalo: novu vježbu za ruke, novu zvučnu scenu sa šumom i pticama, novu igru za dvoje djece. Claude Code na Mac miniju to napiše i složi: nove poze za Skeleton, nove zvukove i slike za zidove. Za to treba pretplata Claude Max od oko 200 € mjesečno.</p>

<h2>Oprema i softver</h2>
<h3>Oprema</h3>
<div class="tw"><table>
<thead><tr><th>Stavka</th><th class="n">Kom.</th><th class="n">Cijena po kom.</th><th class="n">Ukupno</th><th>Gdje</th></tr></thead>
<tbody>
{hw_rows}
</tbody>
<tfoot><tr><td colspan="3">Oprema ukupno</td><td class="n">{eur(hw_tot)}</td><td></td></tr></tfoot>
</table></div>
<h3>Softver, jednokratno</h3>
<div class="tw"><table>
<thead><tr><th>Stavka</th><th class="n">Kom.</th><th class="n">Cijena</th><th class="n">Ukupno</th><th>Gdje</th></tr></thead>
<tbody>
{sw_rows}
</tbody>
<tfoot><tr><td colspan="3">Softver ukupno</td><td class="n">{eur(sw_tot)}</td><td></td></tr></tfoot>
</table></div>
<h3>Mjesečno i godišnje</h3>
<div class="tw"><table>
<thead><tr><th>Pretplata</th><th class="n">Mjesečno</th><th>Gdje</th></tr></thead>
<tbody>
{chr(10).join(mo)}
</tbody>
<tfoot><tr><td>Mjesečno ukupno (bez licence za myNoise)</td><td class="n">{eur(mo_tot)}</td><td></td></tr></tfoot>
</table></div>
<p><b>Jednokratno ukupno: {eur(hw_tot+sw_tot)}</b>, uz to oko {eur(mo_tot)} mjesečno. Cijene su od 21.11.2026. i uključuju PDV, osim gdje piše drugačije.</p>
<p class="note">Prije kupnje: kod Optome potvrditi da ZH430UST radi okrenut naopako i da mu odgovara nosač OWM3000. Adam D3V ima navoj 3/8" s donje strane i izravno se navije na stropni nosač; proizvođač ne navodi rad naopako, pa svaki zvučnik dobiva i sigurnosnu sajlu. Godox ne radi stropne nosače, pa je umjesto stalka za rasvjetu odabran stropni nosač s istim navojem. Zylia trenutno nema na zalihi u Njemačkoj, cijena je iz Zylijinog cjenika bez PDV-a. Stavke označene kao procjena nisu provjerene u trgovini. U iznos nisu uključene utičnice na stropu i ugradnja.</p>

<h2>Svaram: Soundgarden i Sonorium</h2>
<p>Dok sam živio u Aurovilleu, snimao sam filmove za <a href="https://svaram.org" rel="noopener">Svaram</a>, radionicu i istraživački centar za zvuk i instrumente. Njihova dva prostora su uzor za ovu sobu i bila bi prekrasno igralište za djecu s teškoćama: instrumenti koje dijete može dotaknuti, pokrenuti i osjetiti cijelim tijelom.</p>
<h3>Soundgarden</h3>
<figure class="pic"><img src="img/svaram/soundgarden-1.jpg" alt="Metalni ksilofon s velikim cijevima u zelenom vrtu Svarama" width="1600" height="534" loading="lazy"></figure>
<div class="gal"><figure class="pic"><img src="img/svaram/soundgarden-2.jpg" alt="Djevojčica svira bambusova zvona u vrtu" width="738" height="880" loading="lazy"></figure><figure class="pic"><img src="img/svaram/soundgarden-3.jpg" alt="Djevojčica dlanom trlja okrugli plavi zvučni stol" width="800" height="878" loading="lazy"></figure></div>
<p><a href="https://svaram.org/sound-garden-art-installations/" rel="noopener">Zvučni vrt</a> na otvorenom pun je instrumenata od kamena, bambusa, metala i drveta: kamenje koje zvoni, krug cijevnih zvona, zvučne ploče i bubanj oluje. Svatko može svirati, bez ikakvog znanja.</p>
{yt('GQyXzu90d0k','SVARAM Sound Garden, film Marka Boška')}
<h3>Sonorium</h3>
<figure class="pic"><img src="img/svaram/sonorium-2.jpg" alt="Terapeut uz drveni krevet s monokordom na kojem leži žena, oko njih viseća zvečka i cijevna zvona" width="1600" height="667" loading="lazy"></figure>
<figure class="pic"><img src="img/svaram/sonorium-1.jpg" alt="Sonorium: krevet sa žicama, gongovi, cijevna zvona i zdjele" width="1600" height="534" loading="lazy"></figure>
<div class="gal"><figure class="pic"><img src="img/svaram/sonorium-3.jpg" alt="Svirač udara veliku viseću zvučnu ploču dok žena leži na krevetu" width="738" height="880" loading="lazy"></figure><figure class="pic"><img src="img/svaram/sonorium-nidranantar.jpg" alt="Ruka prelazi preko žica Nidranantara, instrumenta za ležanje" width="738" height="880" loading="lazy"></figure></div>
<p><a href="https://svaram.org/sonorium/" rel="noopener">Sonorium</a> je prostor za zvučno iscjeljivanje: veliki monokordi, gongovi i zvona postavljeni u krug, a u sredini Nidranantar, instrument na kojem se leži. Zvuk i vibracija prolaze kroz cijelo tijelo.</p>
{yt('78xD4G86daA','SVARAM Sonorium, film Marka Boška')}
<p class="note">Fotografije: Svaram, Auroville (svaram.org). Filmove sam snimio ja za Svaram. Više mojih filmova iz Aurovillea: <a href="https://youtube.com/playlist?list=PLcbk1jSryyxkAe66vLKVKnSPGOVB5PmB3" rel="noopener">Auroville Videos by Marko Bosko</a>.</p>
</section>
'''

P2_HEAD = f'''<section id="projekt-2">
<h1>Soba za terapiju bojom i zvukom</h1>
<p>Ista soba s četiri zida, ali s drugom namjenom: boja, svjetlo i glazba. Osnova joj je moja Mantra Room. Na zidovima su spore boje i MilkDrop vizualizacije, a glazbu biraju terapeut i osoba zajedno.</p>
<h2>Kako to izgleda</h2>
<div class="gal"><figure class="pic"><img src="img/lifestyle-1.jpg" srcset="img/lifestyle-1-960.jpg 960w, img/lifestyle-1.jpg 1920w" sizes="(max-width:980px) 100vw, 940px" alt="Djeca i terapeutkinja sjede na mekanoj prostirki u sobi s nježnim ljubičastim i plavim svjetlom" width="1920" height="1080" loading="lazy"><figcaption>Boje i mir: djeca na prostirci uz polagano mijenjanje boja.</figcaption></figure><figure class="pic"><img src="img/lifestyle-4.jpg" srcset="img/lifestyle-4-960.jpg 960w, img/lifestyle-4.jpg 1920w" sizes="(max-width:980px) 100vw, 940px" alt="Odrasla osoba svira glinenu ocarinu, a pored nje sjedi terapeutkinja, dok zidovi prikazuju mirno more" width="1920" height="1080" loading="lazy"><figcaption>Sviranje glinene ocarine uz more na zidovima.</figcaption></figure></div>

<h2>MilkDrop: moje vizualizacije na zidovima</h2>
{fig('milkdrop','Zidovi puni mekih tekućih uzoraka u ljubičastoj, tirkiznoj i jantarnoj boji, mladić u kolicima i prijatelj gledaju','MilkDrop na sva četiri zida.')}
<p>MilkDrop je vizualizacija koja crta tekuće, žive slike iz glazbe. Koristim je u svojoj Mantra Room i ovdje: na četiri zida slika polako teče i mijenja se s glazbom. Za terapiju biram samo spore, nježne predloške, bez bljeskova. Ovo su četiri prava kadra iz MilkDropa:</p>
<div class="gal4">
<img src="img/milkdrop/milkdrop-1-800.jpg" alt="MilkDrop: plavo-zlatno nebo kao oblaci nad pustinjom" width="800" height="450" loading="lazy">
<img src="img/milkdrop/milkdrop-2-800.jpg" alt="MilkDrop: ružičasto-zlatna mreža koja se njiše" width="800" height="450" loading="lazy">
<img src="img/milkdrop/milkdrop-3-800.jpg" alt="MilkDrop: zeleni i tirkizni slojevi poput tekuće stijene" width="800" height="450" loading="lazy">
<img src="img/milkdrop/milkdrop-4-800.jpg" alt="MilkDrop: valovite pruge u sedefastim bojama" width="800" height="450" loading="lazy">
</div>
<p><button type="button" id="milk-start" class="btn big">Pokreni MilkDrop uz podvodni zvuk</button></p>
<p class="note">Cijeli zaslon: MilkDrop crta sliku iz zvuka "Karipsko more", koji sam napravio za ovu sobu. Esc ili gumb Izlaz vraća na stranicu.</p>

<h2>DJ Mantra: ambijentalna playlista</h2>
<p>Za mirne trenutke u sobi složio sam playlistu mekane, ambijentalne glazbe: Chantress Seba, Nils Frahm, Trentemøller i još nekoliko tihih skladbi. Glazba se pušta s YouTubea, a u sobi se šalje na svih osam zvučnika.</p>
{('<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/' + PLAYLIST[0] + '?playlist=' + ','.join(PLAYLIST[1:]) + '" title="DJ Mantra ambijentalna playlista" loading="lazy" referrerpolicy="strict-origin-when-cross-origin" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe></div>')}
<ol class="tracks">{''.join(f'<li><a href="https://www.youtube.com/watch?v={v}" rel="noopener">{html.escape(t)}</a></li>' for v,t in zip(PLAYLIST,TRACKS))}</ol>

<h2>Zvučni pejzaži: myNoise</h2>
<p>Za kišu, more, šumu i vjetar koristim <a href="https://mynoise.net" rel="noopener">myNoise</a>. Svaki pejzaž ima deset kanala koje mogu posebno podesiti i rasporediti po osam zvučnika: kapi kiše u kutovima, šum iz daljine sa stropa, dubina mora iz cijele sobe. Za korištenje u terapijskoj sobi myNoise traži godišnju licencu.</p>
<p><a class="btn off" href="https://mynoise.net/NoiseMachines/rainNoiseGenerator.php" rel="noopener">Kiša</a> <a class="btn off" href="https://mynoise.net/NoiseMachines/oceanNoiseGenerator.php" rel="noopener">More</a> <a class="btn off" href="https://mynoise.net/NoiseMachines/rainforestNoiseGenerator.php" rel="noopener">Prašuma</a> <a class="btn off" href="https://mynoise.net/NoiseMachines/windNoiseGenerator.php" rel="noopener">Vjetar</a> <a class="btn off" href="https://mynoise.net/NoiseMachines/singingBowlsDroneGenerator.php" rel="noopener">Zdjele koje pjevaju</a></p>
'''

# keep: the Euphony section (Alan Tower's crystal bells), Boric, instruments (+ Stonewhistle video), apps
start = s.index('<section id="projekt-1">')
eu = s.index('<section id="euphony">')
rest = s[eu:]
# Euphony: drop the link back to the removed Alan Tower card
rest = rest.replace(' (<a href="#euphony">više u nastavku</a>)', '')
# Stonewhistle video after the instruments grid note
sw_video = ('<h3>Kako se sviraju ove flaute</h3>\n<p>Moj video: kako se sviraju glinene flaute Stonewhistle.</p>\n' + yt('qVSTpt1eESs', 'Kako se sviraju flaute Stonewhistle, video Marka Boška') + '\n')
i_inst = rest.index('</section>', rest.index('<section id="instrumenti">'))
if 'qVSTpt1eESs' not in rest:
    rest = rest[:i_inst] + sw_video + rest[i_inst:]
s = s[:start] + P1 + '\n' + P2_HEAD + '\n' + rest

# MilkDrop overlay replaces the old Hemi-Sync therapy demo overlay and player.js
tm0 = s.index('<div id="tm"'); tm1 = s.index('<script src="player.js" defer></script>') + len('<script src="player.js" defer></script>')
s = s[:tm0] + '''<div id="mk" hidden role="dialog" aria-label="MilkDrop"><canvas id="mk-cv" aria-hidden="true"></canvas><button type="button" id="mk-x">✕ Izlaz</button></div>
<audio id="mk-au" src="audio/karipsko-more-underwater.mp3" preload="none" loop></audio>
<script src="milk.js" defer></script>''' + s[tm1:]
s = s.replace('Popis opreme s cijenama i uzorci Hemi-Sync glazbe.', 'Sve visi sa stropa, igra pokreta, pjesme iz glasa, 3D snimanje, popis opreme i troškova.')
open(P,'w').write(s)
print('hw', round(hw_tot,2), 'sw', sw_tot, 'monthly', mo_tot)
