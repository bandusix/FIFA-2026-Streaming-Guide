/* ============================================================
   FIFA World Cup 2026 — BROADCAST / STREAMING SOURCES (per country)
   ------------------------------------------------------------
   Delivery is BY COUNTRY (broadcast rights are territorial). The page
   detects the visitor's country (IP geo) and shows that country's sources.

   ⚖️  Official / licensed rights-holders are listed here.
       In addition, a global fallback array `WC_SOURCES_FALLBACK` is provided 
       containing aggregator streams as requested.

   ✅  VERIFY BEFORE LAUNCH: exact 2026 rights assignments and deep-link
       player paths can change per cycle — confirm each against FIFA's
       official "Where to Watch":
       https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026

   Shape:  window.WC_SOURCES_FALLBACK = [
     {name:"Footybite", url:"..."},
     ...
   ];

   window.WC_SOURCES = {
     "<ISO alpha-2>": [ { name, url, lang?, matchNo? }, ... ]   // 2 per country
   }
   ============================================================ */

window.WC_SOURCES_FALLBACK = [
  {name:"Footybite", url:"https://footybite.ac/fifa-world-cup"},
  {name:"VIPBox", url:"https://www.vipboxtv.sk/live-now-stream"},
  {name:"OlympicWeb", url:"https://olympicweb.me/live/2026-worldcup-stream"},
  {name:"BuffStreams", url:"https://buffstreams.plus/soccer-live-streams"},
  {name:"BoxingInfo", url:"https://boxinginfo.info/#soccer"},
  {name:"MMA Fighter", url:"https://mmafighter.info/"},
  {name:"PPV.to", url:"https://ppv.to/#34"}
];

window.WC_SOURCES = {
  // ---------------- NORTH AMERICA ----------------
  US: [{name:"FOX Sports", url:"https://www.foxsports.com/live", lang:"en"},
       {name:"Telemundo",  url:"https://www.telemundo.com/now",  lang:"es"}],
  CA: [{name:"TSN",        url:"https://www.tsn.ca/tsn-live",    lang:"en"},
       {name:"RDS",        url:"https://www.rds.ca/direct",      lang:"fr"}],
  MX: [{name:"ViX",        url:"https://vix.com",                lang:"es"},
       {name:"Azteca Deportes", url:"https://www.aztecadeportes.com/envivo", lang:"es"}],

  // ---------------- LATIN AMERICA ----------------
  BR: [{name:"Globoplay (ge.globo)",  url:"https://ge.globo.com/futebol/copa-do-mundo/",   lang:"pt"},
       {name:"CazéTV",     url:"https://www.youtube.com/@CazeTV/streams", lang:"pt"}],
  AR: [{name:"TyC Sports", url:"https://www.tycsports.com/vivo.html", lang:"es"},
       {name:"TV Pública", url:"https://www.tvpublica.com.ar/vivo",   lang:"es"}],
  CO: [{name:"Caracol TV", url:"https://www.caracoltv.com/senal-en-vivo", lang:"es"},
       {name:"Canal RCN",  url:"https://www.canalrcn.com/senal-en-vivo",  lang:"es"}],
  CL: [{name:"Chilevisión",url:"https://www.chilevision.cl/senal-online", lang:"es"},
       {name:"Mega",       url:"https://www.mega.cl/senal-en-vivo",       lang:"es"}],
  PE: [{name:"Latina",     url:"https://www.latina.pe/tv/vivo",  lang:"es"},
       {name:"América TV", url:"https://www.americatv.com.pe/vivo", lang:"es"}],
  UY: [{name:"DSports (DGO)", url:"https://www.dgo.com", lang:"es"},
       {name:"Teledoce",   url:"https://www.teledoce.com/envivo/", lang:"es"}],
  PY: [{name:"Tigo Sports",url:"https://www.tigosports.com.py/", lang:"es"},
       {name:"DSports (DGO)", url:"https://www.dgo.com",         lang:"es"}],
  EC: [{name:"Teleamazonas", url:"https://www.teleamazonas.com/vivo/", lang:"es"},
       {name:"DSports (DGO)", url:"https://www.dgo.com",         lang:"es"}],
  BO: [{name:"Tigo Sports",url:"https://www.tigosports.com.bo/", lang:"es"},
       {name:"DSports (DGO)", url:"https://www.dgo.com",         lang:"es"}],
  VE: [{name:"DSports (DGO)", url:"https://www.dgo.com",         lang:"es"},
       {name:"IVC / Venevisión", url:"https://venevision.net/",  lang:"es"}],
  CR: [{name:"Teletica",   url:"https://www.teletica.com/en-vivo", lang:"es"},
       {name:"Repretel",   url:"https://www.repretel.com/envivo/", lang:"es"}],
  PA: [{name:"RPC TV",     url:"https://www.rpctv.com/", lang:"es"},
       {name:"Telemetro",  url:"https://www.telemetro.com/en-vivo", lang:"es"}],

  // ---------------- EUROPE ----------------
  GB: [{name:"BBC iPlayer",url:"https://www.bbc.co.uk/iplayer", lang:"en"},
       {name:"ITVX",       url:"https://www.itv.com/watch",     lang:"en"}],
  IE: [{name:"RTÉ Player", url:"https://www.rte.ie/player/",    lang:"en"},
       {name:"Virgin Media",url:"https://www.virginmediatelevision.ie/player", lang:"en"}],
  ES: [{name:"RTVE Play",  url:"https://www.rtve.es/play/directo/", lang:"es"},
       {name:"Movistar Plus+", url:"https://ver.movistarplus.es/", lang:"es"}],
  FR: [{name:"TF1+",       url:"https://www.tf1.fr/direct",      lang:"fr"},
       {name:"beIN SPORTS",url:"https://www.beinsports.com/france/direct", lang:"fr"}],
  DE: [{name:"ARD Sportschau", url:"https://www.sportschau.de/livestream/", lang:"de"},
       {name:"ZDF",        url:"https://www.zdf.de/live-tv",     lang:"de"}],
  IT: [{name:"RaiPlay",    url:"https://www.raiplay.it/dirette", lang:"it"},
       {name:"NOW (Sky)",  url:"https://www.nowtv.it/sport",     lang:"it"}],
  PT: [{name:"RTP Play",   url:"https://www.rtp.pt/play/direto", lang:"pt"},
       {name:"SPORT TV",   url:"https://www.sporttv.pt/",        lang:"pt"}],
  NL: [{name:"NOS",        url:"https://nos.nl/livestream",      lang:"en"},
       {name:"NPO Start",  url:"https://npo.nl/start/live",      lang:"en"}],
  BE: [{name:"RTBF Auvio", url:"https://auvio.rtbf.be/direct",   lang:"fr"},
       {name:"VRT MAX",    url:"https://www.vrt.be/vrtmax/livestream/", lang:"en"}],
  CH: [{name:"SRF",        url:"https://www.srf.ch/sport/livestream", lang:"de"},
       {name:"RTS",        url:"https://www.rts.ch/sport/direct/",    lang:"fr"}],
  AT: [{name:"ORF ON",     url:"https://on.orf.at/",             lang:"de"},
       {name:"ServusTV",   url:"https://www.servustv.com/sport/", lang:"de"}],
  SE: [{name:"SVT Play",   url:"https://www.svtplay.se/kanaler", lang:"en"},
       {name:"TV4 Play",   url:"https://www.tv4play.se/",        lang:"en"}],
  NO: [{name:"NRK TV",     url:"https://tv.nrk.no/direkte",      lang:"en"},
       {name:"TV 2 Play",  url:"https://play.tv2.no/",           lang:"en"}],
  DK: [{name:"DRTV",       url:"https://www.dr.dk/drtv/kanaler", lang:"en"},
       {name:"TV 2 Play",  url:"https://play.tv2.dk/",           lang:"en"}],
  PL: [{name:"TVP Sport",  url:"https://sport.tvp.pl/transmisje", lang:"en"},
       {name:"TVP VOD",    url:"https://vod.tvp.pl/live",        lang:"en"}],
  GR: [{name:"ERTFLIX",    url:"https://www.ertflix.gr/en/epg",  lang:"en"},
       {name:"ANT1",       url:"https://www.ant1.gr/live",       lang:"en"}],
  HR: [{name:"HRTi",       url:"https://hrti.hrt.hr/",           lang:"en"},
       {name:"RTL Hrvatska", url:"https://www.rtl.hr/",          lang:"en"}],
  RS: [{name:"RTS",        url:"https://www.rts.rs/page/tv/sr/live.html", lang:"en"},
       {name:"Arena Sport",url:"https://arenasport.telekom.rs/", lang:"en"}],
  UA: [{name:"Suspilne",   url:"https://suspilne.media/sport/",  lang:"ru"},
       {name:"MEGOGO",     url:"https://megogo.net/ua/sport",    lang:"ru"}],
  RU: [{name:"Match TV",   url:"https://matchtv.ru/on-air",      lang:"ru"},
       {name:"Okko Sport", url:"https://okko.tv/sport",          lang:"ru"}],
  TR: [{name:"TRT 1",      url:"https://www.trtizle.com/canli/trt-1", lang:"tr"},
       {name:"TRT Spor",   url:"https://www.trtizle.com/canli/trt-spor", lang:"tr"}],

  // ---------------- MIDDLE EAST & N. AFRICA (beIN holds MENA rights) ----------------
  SA: [{name:"TOD",          url:"https://www.tod.tv/", lang:"en"},
       {name:"beIN SPORTS",  url:"https://www.beinsports.com/en-mena/", lang:"en"}],
  AE: [{name:"TOD",          url:"https://www.tod.tv/", lang:"en"},
       {name:"beIN SPORTS",  url:"https://www.beinsports.com/en-mena/", lang:"en"}],
  QA: [{name:"beIN SPORTS",  url:"https://www.beinsports.com/en-mena/", lang:"en"},
       {name:"TOD",          url:"https://www.tod.tv/", lang:"en"}],
  EG: [{name:"TOD",          url:"https://www.tod.tv/", lang:"en"},
       {name:"beIN SPORTS",  url:"https://www.beinsports.com/en-mena/", lang:"en"}],
  IQ: [{name:"TOD",          url:"https://www.tod.tv/", lang:"en"},
       {name:"beIN SPORTS",  url:"https://www.beinsports.com/en-mena/", lang:"en"}],
  JO: [{name:"TOD",          url:"https://www.tod.tv/", lang:"en"},
       {name:"beIN SPORTS",  url:"https://www.beinsports.com/en-mena/", lang:"en"}],
  KW: [{name:"TOD",          url:"https://www.tod.tv/", lang:"en"},
       {name:"beIN SPORTS",  url:"https://www.beinsports.com/en-mena/", lang:"en"}],
  MA: [{name:"SNRT (Arryadia)", url:"https://snrtlive.ma/", lang:"fr"},
       {name:"beIN SPORTS",  url:"https://www.beinsports.com/en-mena/", lang:"fr"}],
  DZ: [{name:"EPTV",         url:"https://www.entv.dz/live/", lang:"fr"},
       {name:"beIN SPORTS",  url:"https://www.beinsports.com/en-mena/", lang:"fr"}],
  TN: [{name:"Watania (TNN)",url:"https://watania.tn/", lang:"fr"},
       {name:"beIN SPORTS",  url:"https://www.beinsports.com/en-mena/", lang:"fr"}],
  IR: [{name:"Telewebion (IRIB)", url:"https://telewebion.com/live", lang:"en"},
       {name:"IRIB Varzesh",  url:"https://live.irib.ir/", lang:"en"}],
  IL: [{name:"Sport 5",      url:"https://www.sport5.co.il/", lang:"en"},
       {name:"Kan 11",       url:"https://www.kan.org.il/live/tv.aspx", lang:"en"}],

  // ---------------- SUB-SAHARAN AFRICA ----------------
  ZA: [{name:"SuperSport (DStv)", url:"https://now.dstv.com/", lang:"en"},
       {name:"SABC", url:"https://www.sabcplus.com/", lang:"en"}],
  NG: [{name:"SuperSport (DStv)", url:"https://now.dstv.com/", lang:"en"},
       {name:"New World TV", url:"https://www.newworldtv.com/", lang:"fr"}],
  KE: [{name:"SuperSport (DStv)", url:"https://now.dstv.com/", lang:"en"},
       {name:"KBC", url:"https://www.kbc.co.ke/", lang:"en"}],
  GH: [{name:"SuperSport (DStv)", url:"https://now.dstv.com/", lang:"en"},
       {name:"GBC", url:"https://www.gbcghanaonline.com/", lang:"en"}],
  SN: [{name:"New World TV", url:"https://www.newworldtv.com/", lang:"fr"},
       {name:"RTS", url:"https://rts.sn/", lang:"fr"}],
  CD: [{name:"New World TV", url:"https://www.newworldtv.com/", lang:"fr"},
       {name:"RTNC", url:"https://rtnc.cd/", lang:"fr"}],

  // ---------------- SOUTHEAST ASIA ----------------
  ID: [{name:"Vidio",        url:"https://www.vidio.com/live", lang:"id"},
       {name:"EMTEK (SCTV)", url:"https://www.sctv.co.id/live", lang:"id"}],
  MY: [{name:"sooka",        url:"https://sooka.my/", lang:"en"},
       {name:"Astro Go",     url:"https://astrogo.astro.com.my/", lang:"en"}],
  TH: [{name:"Thai PBS",     url:"https://www.thaipbs.or.th/live", lang:"en"},
       {name:"TrueVisions",  url:"https://trueid.net/", lang:"en"}],
  VN: [{name:"VTVGo",        url:"https://vtvgo.vn/", lang:"en"},
       {name:"VTVcab ON",    url:"https://vtvcab.vn/", lang:"en"}],
  PH: [{name:"GMA Network",  url:"https://www.gmanetwork.com/sports/", lang:"en"},
       {name:"Tap Go",       url:"https://www.tapdmv.com/", lang:"en"}],
  SG: [{name:"meWATCH",      url:"https://www.mewatch.sg/", lang:"en"},
       {name:"StarHub TV+",  url:"https://www.starhub.com/tvplus.html", lang:"en"}],

  // ---------------- EAST ASIA / SOUTH ASIA / OCEANIA ----------------
  CN: [{name:"央视 CCTV (央视频)", url:"https://www.yangshipin.cn/", lang:"zh-Hans"},
       {name:"咪咕视频 Migu",      url:"https://www.miguvideo.com/", lang:"zh-Hans"}],
  TW: [{name:"愛爾達 ELTA",       url:"https://www.elta.tv/", lang:"zh-Hant"},
       {name:"公視 PTS",          url:"https://www.pts.org.tw/live/", lang:"zh-Hant"}],
  HK: [{name:"Now TV",            url:"https://nowplayer.now.com/", lang:"zh-Hant"},
       {name:"TVB myTV SUPER",    url:"https://www.mytvsuper.com/", lang:"zh-Hant"}],
  JP: [{name:"ABEMA",             url:"https://abema.tv/", lang:"en"},
       {name:"NHK Plus",          url:"https://plus.nhk.jp/", lang:"en"}],
  KR: [{name:"SBS",               url:"https://www.sbs.co.kr/live", lang:"en"},
       {name:"Coupang Play",      url:"https://www.coupangplay.com/", lang:"en"}],
  IN: [{name:"JioHotstar",        url:"https://www.hotstar.com/in/sports", lang:"hi"},
       {name:"Sports18",          url:"https://www.jiocinema.com/", lang:"hi"}],
  AU: [{name:"Optus Sport",       url:"https://sport.optus.com.au/", lang:"en"},
       {name:"SBS On Demand",     url:"https://www.sbs.com.au/ondemand/", lang:"en"}],
  NZ: [{name:"Sky Sport NZ",      url:"https://www.skysport.co.nz/", lang:"en"},
       {name:"Sky Sport Now",     url:"https://skysportnow.co.nz/", lang:"en"}]
};
