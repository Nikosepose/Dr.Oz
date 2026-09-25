"""Norske symptomnavn, konkrete spørsmål og bokstavelige fritekstuttrykk.

Katalogen omfatter også forløp og utløsere. Mer spesifikke uttrykk skal
overstyre overlappende generelle uttrykk i friteksttolkeren. Se DATASET.md.
"""

# ID: (kort navn, oppfølgingsspørsmål, alternative brukeruttrykk).
_SYMPTOMS = {
    "fever": (
        "feber",
        "Har du målt feber, det vil si temperatur på 38 °C eller mer?",
        ["feber","febril","høy feber","høy temperatur"],
    ),
    "fatigue": (
        "uvanlig tretthet eller utmattelse",
        "Føler du deg uvanlig trett eller utmattet?",
        ["utmattet","utmattelse","slapp","slapphet","uvanlig trøtt","veldig sliten","tretthet"],
    ),
    "body_aches": (
        "verk i kroppen",
        "Har du verk i flere muskler eller i hele kroppen?",
        ["vondt i kroppen","verk i kroppen","muskelverk","muskelsmerter"],
    ),
    "abrupt_onset": (
        "symptomer som kom i løpet av få timer",
        "Kom plagene raskt, i løpet av noen få timer?",
        ["ble plutselig syk","plutselig syk","symptomene kom brått","plagene kom brått"],
    ),
    "cough": (
        "hoste",
        "Har du hoste?",
        ["hoste","hoster","hosting","tørrhoste"],
    ),
    "sore_throat": (
        "sår hals",
        "Er du sår eller har vondt i halsen?",
        ["sår hals","vondt i halsen","halsvondt","halsen er sår"],
    ),
    "runny_nose": (
        "rennende nese",
        "Renner det fra nesen?",
        ["rennende nese","renner fra nesen","nesen renner","snørrete","snufsete"],
    ),
    "blocked_nose": (
        "tett nese",
        "Er du tett i nesen?",
        ["tett nese","tett i nesen","nesen er tett","nesetetthet"],
    ),
    "sneezing": (
        "nysing",
        "Nyser du mye?",
        ["nysing","nyser","nys"],
    ),
    "hoarseness": (
        "hes stemme",
        "Har stemmen din blitt hes?",
        ["hes","heshet","hes stemme","stemmen er hes"],
    ),
    "sinus_pain": (
        "trykk eller smerter rundt kinn og panne",
        "Har du trykk eller smerter rundt kinnene, øynene eller pannen?",
        ["bihulesmerter","trykk i bihulene","vondt i bihulene","smerter i kinnene","trykk i ansiktet"],
    ),
    "reduced_smell": (
        "nedsatt luktesans",
        "Har luktesansen blitt dårligere enn vanlig?",
        ["nedsatt luktesans","dårlig luktesans","mistet luktesansen","kjenner ikke lukt"],
    ),
    "thick_nasal_mucus": (
        "tykt gult eller grønt neseslim",
        "Har du tykt gult eller grønt slim fra nesen?",
        ["gult snørr","grønt snørr","tykt neseslim","gult slim fra nesen","grønt slim fra nesen"],
    ),
    "painful_swallowing": (
        "smerter ved svelging",
        "Gjør det vondt når du svelger?",
        ["vondt å svelge","smerter når jeg svelger","smerter ved svelging","svelgesmerter"],
    ),
    "swollen_tonsils": (
        "røde og hovne mandler",
        "Ser mandlene i halsen røde og hovne ut?",
        ["hovne mandler","mandlene er hovne","store røde mandler"],
    ),
    "tonsil_exudate": (
        "hvitt belegg på mandlene",
        "Ser du hvitt belegg eller hvite prikker på mandlene?",
        ["hvitt belegg på mandlene","hvite prikker på mandlene","hvite flekker på mandlene","puss på mandlene"],
    ),
    "tender_neck_nodes": (
        "ømme lymfeknuter på halsen",
        "Kjenner du ømme, hovne lymfeknuter på sidene av halsen?",
        ["ømme lymfeknuter","hovne lymfeknuter på halsen","ømme kuler på halsen"],
    ),
    "productive_cough": (
        "hoste med oppspytt",
        "Hoster du opp slim?",
        ["slimhoste","hoster opp slim","hoste med slim","hoste med oppspytt"],
    ),
    "chest_pain_coughing": (
        "smerter i brystet ved hoste",
        "Gjør det vondt i brystet når du hoster?",
        ["vondt i brystet når jeg hoster","brystsmerter ved hoste","smerter i brystet ved hoste"],
    ),
    "shortness_of_breath": (
        "tungpust",
        "Er du mer tungpustet enn vanlig?",
        ["tungpust","tungpustet","tung pust","kortpustet","andpusten","pustevansker","pusteproblemer"],
    ),
    "wheezing": (
        "pipende pust",
        "Hører du piping i brystet når du puster?",
        ["pipende pust","piping i brystet","piper når jeg puster","hvesende pust"],
    ),
    "chest_tightness": (
        "tetthet i brystet",
        "Kjenner du tetthet eller stramming i brystet?",
        ["tetthet i brystet","strammer i brystet","brystet føles trangt"],
    ),
    "breathing_triggers": (
        "pusteplager utløst av aktivitet, kulde eller allergener",
        "Kommer pusteplagene særlig ved aktivitet, kald luft, støv eller pollen?",
        ["tungpust ved trening","pusteplager ved trening","tungpust i kulde","pusteplager ved pollen"],
    ),
    "itchy_nose": (
        "kløe i nesen",
        "Klør det i nesen?",
        ["kløe i nesen","klør i nesen","nesen klør","kløende nese"],
    ),
    "itchy_eyes": (
        "kløende øyne",
        "Klør det i øynene?",
        ["kløende øyne","kløe i øynene","klør i øynene","øynene klør"],
    ),
    "red_eyes": (
        "røde øyne",
        "Er ett eller begge øyne røde?",
        ["røde øyne","rødt øye","øyet er rødt","øynene er røde"],
    ),
    "eye_discharge": (
        "puss eller klissete sekret fra øynene",
        "Har du puss fra øyet eller øyelokk som kleber seg sammen?",
        ["puss i øyet","puss fra øyet","puss i øynene","klissete øyne","øyelokkene kleber","gjenklistrede øyne"],
    ),
    "gritty_eyes": (
        "sandfølelse i øynene",
        "Føles det som om du har sand eller rusk i øyet?",
        ["sandfølelse i øyet","sandfølelse i øynene","rusk i øyet","sand i øynene"],
    ),
    "ear_pain": (
        "øresmerter",
        "Har du vondt inne i ett eller begge ører?",
        ["øresmerter","øreverk","vondt i øret","vondt i ørene","smerter i øret"],
    ),
    "reduced_hearing": (
        "nedsatt hørsel",
        "Har hørselen blitt dårligere i ett eller begge ører?",
        ["nedsatt hørsel","hører dårlig","dårligere hørsel","hørselstap"],
    ),
    "ear_discharge": (
        "væske fra øret",
        "Renner det væske eller puss fra øret?",
        ["væske fra øret","renner fra øret","puss fra øret","øreflod"],
    ),
    "nausea": (
        "kvalme",
        "Er du kvalm?",
        ["kvalme","kvalm","uggen"],
    ),
    "vomiting": (
        "oppkast",
        "Har du kastet opp?",
        ["oppkast","kaster opp","kastet opp","spyr","spydde","brekninger"],
    ),
    "diarrhea": (
        "diaré",
        "Har du løs eller vannaktig avføring oftere enn vanlig?",
        ["diaré","diare","diarré","diarre","løs avføring","vanntynn avføring","vannaktig avføring"],
    ),
    "abdominal_cramps": (
        "magesmerter eller magekramper",
        "Har du smerter eller kramper i magen?",
        ["magekramper","mageknip","vondt i magen","magesmerter","knip i magen"],
    ),
    "bloating": (
        "oppblåst mage",
        "Føles magen oppblåst eller full av luft?",
        ["oppblåst","oppblåsthet","luft i magen","oppblåst mage"],
    ),
    "heartburn": (
        "halsbrann",
        "Har du halsbrann, en brennende følelse bak brystbeinet?",
        ["halsbrann","sure brenninger","brenner bak brystbeinet"],
    ),
    "acid_regurgitation": (
        "sure oppstøt",
        "Kommer det sur væske eller sur smak opp i munnen?",
        ["sure oppstøt","syre i munnen","sur smak i munnen","magesyre i halsen"],
    ),
    "worse_after_meals_or_lying": (
        "sure plager som øker etter mat eller ved ligging",
        "Blir halsbrann eller sure oppstøt verre etter mat eller når du ligger?",
        ["halsbrann etter mat","halsbrann når jeg ligger","sure oppstøt når jeg ligger","halsbrann etter måltider"],
    ),
    "constipation": (
        "sjeldnere avføring enn vanlig",
        "Har du avføring sjeldnere enn vanlig, for eksempel færre enn tre ganger i uken?",
        ["forstoppelse","forstoppet","sjelden avføring","sjeldnere avføring","treg mage","får ikke bæsjet"],
    ),
    "hard_stools": (
        "hard eller klumpete avføring",
        "Er avføringen hard, tørr eller klumpete?",
        ["hard avføring","hard bæsj","klumpete avføring","tørr avføring"],
    ),
    "straining": (
        "behov for å presse ved avføring",
        "Må du presse mye for å få ut avføringen?",
        ["må presse på do","presser ved avføring","presse for å bæsje","må presse mye"],
    ),
    "recurrent_bowel_changes": (
        "langvarig vekslende avføring",
        "Har avføringen vekslet mellom løs og hard gjennom flere uker?",
        ["vekslende avføring i flere uker","veksler mellom diaré og forstoppelse over tid","veksler mellom løs og hard avføring i flere uker"],
    ),
    "pain_relieved_defecation": (
        "magesmerter som lindres etter avføring",
        "Blir magesmertene vanligvis bedre etter at du har hatt avføring?",
        ["bedre etter avføring","magevondt bedres etter avføring","magesmertene blir bedre etter do","bedre etter å ha bæsjet"],
    ),
    "anal_itching": (
        "kløe rundt endetarmsåpningen",
        "Klør det rundt endetarmsåpningen?",
        ["kløe i endetarmen","klør i endetarmen","kløe rundt anus","kløe rundt endetarmsåpningen","klør i rumpa"],
    ),
    "anal_lump": (
        "kul ved endetarmsåpningen",
        "Kjenner du en kul ved endetarmsåpningen?",
        ["kul ved endetarmen","kul ved anus","kul ved endetarmsåpningen","kul i rumpa"],
    ),
    "bright_rectal_bleeding": (
        "friskt rødt blod etter avføring",
        "Har du sett friskt rødt blod på papiret eller utenpå avføringen?",
        ["friskt blod på papiret","rødt blod på papiret","friskt blod etter avføring","friskt rødt blod etter avføring"],
    ),
    "dysuria": (
        "svie ved vannlating",
        "Svir eller gjør det vondt når du tisser?",
        ["svie ved vannlating","svir når jeg tisser","vondt å tisse","smerter ved vannlating","tissesvie"],
    ),
    "urinary_frequency": (
        "hyppig vannlating",
        "Må du tisse oftere enn vanlig?",
        ["tisser ofte","hyppig vannlating","tisse ofte","tisser hele tiden"],
    ),
    "urinary_urgency": (
        "plutselig sterk vannlatingstrang",
        "Får du plutselig sterk trang til å tisse?",
        ["sterk tissetrang","plutselig tissetrang","vannlatingstrang","haster å tisse"],
    ),
    "lower_abdominal_pain": (
        "smerter nederst i magen",
        "Har du smerter nederst i magen, over skambeinet?",
        ["vondt nederst i magen","smerter nederst i magen","smerter over skambeinet","vondt over blæren"],
    ),
    "cloudy_urine": (
        "uklar urin",
        "Ser urinen uklar eller grumsete ut?",
        ["uklar urin","grumsete urin","urinen er uklar","urinen er grumsete"],
    ),
    "blood_urine": (
        "blod i urinen",
        "Har du sett blod i urinen eller tydelig rødlig urin?",
        ["blod i urinen","blodig urin","rød urin","tisser blod"],
    ),
    "flank_pain_waves": (
        "anfallsvis smerte i siden eller flanken",
        "Kommer det takvise smerter i siden av magen eller ryggen under ribbeina?",
        ["takvise flankesmerter","smerter i flanken i bølger","flankesmerter som kommer og går","takvise smerter i siden"],
    ),
    "pain_to_groin": (
        "smerter som stråler mot lysken",
        "Stråler smerter fra siden av magen ned mot lysken?",
        ["smerter mot lysken","stråler til lysken","stråler mot lysken","smerter ned i lysken"],
    ),
    "vaginal_itching": (
        "kløe i eller rundt skjeden",
        "Klør det i eller rundt skjeden?",
        ["kløe i skjeden","klør i skjeden","kløe rundt skjeden","kløe i underlivet","klør i underlivet"],
    ),
    "thick_white_discharge": (
        "tykk hvit utflod fra skjeden",
        "Har du tykk, hvit eller klumpete utflod fra skjeden?",
        ["tykk hvit utflod","hvit klumpete utflod","klumpete hvit utflod","cottage cheese utflod"],
    ),
    "vulval_soreness": (
        "sårhet rundt skjedeåpningen",
        "Er huden rundt skjedeåpningen sår eller sviende?",
        ["sårhet i underlivet","sår rundt skjedeåpningen","svir rundt skjeden","såre kjønnslepper"],
    ),
    "headache": (
        "hodepine",
        "Har du hodepine?",
        ["hodepine","vondt i hodet","verk i hodet","hodeverk"],
    ),
    "pulsating_headache": (
        "pulserende hodepine",
        "Pulserer eller banker hodepinen?",
        ["pulserende hodepine","bankende hodepine","dunkende hodepine","det banker i hodet"],
    ),
    "one_sided_headache": (
        "hodepine mest på én side",
        "Sitter hodepinen mest på én side av hodet?",
        ["ensidig hodepine","hodepine på én side","hodepine på en side","vondt i halve hodet"],
    ),
    "light_sensitivity": (
        "lysømfintlighet",
        "Er vanlig lys ubehagelig eller smertefullt?",
        ["lysømfintlig","lysømfintlighet","lyssky","lysskyhet","følsom for lys","lys gjør vondt"],
    ),
    "sound_sensitivity": (
        "lydømfintlighet",
        "Er vanlige lyder ubehagelige eller smertefulle?",
        ["lydømfintlig","lydømfintlighet","lydsky","følsom for lyd","lyder gjør vondt"],
    ),
    "headache_worse_activity": (
        "hodepine som forverres av aktivitet",
        "Blir hodepinen verre når du går i trapper eller beveger deg?",
        ["hodepine verre ved aktivitet","hodepinen blir verre når jeg beveger meg","hodepine verre ved bevegelse"],
    ),
    "visual_aura": (
        "forbigående sikksakkmønster eller flimring i synet",
        "Har du forbigående sikksakkmønstre eller flimring i synet før hodepinen?",
        ["sikksakk i synet","flimring før hodepinen","flimring i synet før hodepine","synsaura"],
    ),
    "pressing_headache": (
        "trykkende hodepine som et bånd",
        "Føles hodepinen trykkende, som et stramt bånd rundt hodet?",
        ["trykkende hodepine","stramt bånd rundt hodet","bånd rundt hodet","pressende hodepine"],
    ),
    "bilateral_headache": (
        "hodepine på begge sider",
        "Sitter hodepinen på begge sider av hodet?",
        ["hodepine på begge sider","vondt på begge sider av hodet","tosidig hodepine"],
    ),
    "neck_tightness": (
        "stramme eller ømme nakkemuskler",
        "Kjenner du stramme eller ømme muskler i nakken?",
        ["stramme nakkemuskler","ømme nakkemuskler","anspent nakke","muskelspenninger i nakken"],
    ),
    "spinning_vertigo": (
        "karusellsvimmelhet",
        "Føles det som om rommet eller du selv snurrer rundt?",
        ["karusellsvimmelhet","rommet snurrer","alt snurrer","rotasjonssvimmelhet","karusellfølelse"],
    ),
    "position_triggered_vertigo": (
        "svimmelhet ved bestemte hodebevegelser",
        "Utløses svimmelheten når du snur deg i sengen eller bøyer hodet?",
        ["svimmel når jeg snur meg","svimmel når jeg snur hodet","svimmel når jeg legger meg","stillingsutløst svimmelhet"],
    ),
    "brief_vertigo": (
        "svimmelhetsanfall som varer under ett minutt",
        "Varer de kraftigste svimmelhetsanfallene vanligvis under ett minutt?",
        ["svimmelheten varer noen sekunder","svimmel i noen sekunder","svimmelhetsanfall under ett minutt","svimmelheten varer under ett minutt"],
    ),
    "low_back_pain": (
        "korsryggsmerter",
        "Har du vondt nederst i ryggen eller i korsryggen?",
        ["vondt i korsryggen","korsryggsmerter","vondt nederst i ryggen","smerter i korsryggen"],
    ),
    "back_pain_movement": (
        "ryggsmerter som varierer med bevegelse",
        "Blir ryggsmertene tydelig påvirket av bevegelse, bøying eller løft?",
        ["ryggsmerter ved bevegelse","vondt i ryggen når jeg bøyer meg","vondt i ryggen ved løft","ryggen gjør vondt ved bevegelse"],
    ),
    "radiating_leg_pain": (
        "smerter fra ryggen eller setet ned i benet",
        "Stråler det smerter fra ryggen eller setet ned i ett ben?",
        ["smerter ned i benet","stråler ned i beinet","stråler ned i benet","utstråling til benet"],
    ),
    "leg_tingling": (
        "prikking eller nummenhet i benet",
        "Har du prikking eller nummenhet i ett ben?",
        ["prikking i benet","prikking i beinet","nummen i benet","nummenhet i benet","nummen i beinet"],
    ),
    "joint_pain": (
        "leddsmerter",
        "Har du smerter i ett eller flere ledd?",
        ["leddsmerter","vondt i leddene","vondt i ledd","smerter i leddene"],
    ),
    "joint_stiffness": (
        "ledd som er stive etter hvile",
        "Er leddene stive, særlig etter at du har sittet eller ligget i ro?",
        ["stive ledd","leddstivhet","stiv i leddene","stivhet etter hvile"],
    ),
    "activity_joint_pain": (
        "leddsmerter som øker ved belastning",
        "Blir leddsmertene verre når du bruker eller belaster leddet?",
        ["leddsmerter ved belastning","vondt i ledd ved bruk","leddsmerter verre ved aktivitet","leddsmerter ved aktivitet"],
    ),
    "ankle_pain": (
        "ankelsmerter",
        "Har du smerter i ankelen?",
        ["ankelsmerter","vondt i ankelen","smerter i ankelen","ankelen gjør vondt"],
    ),
    "ankle_swelling": (
        "hevelse rundt ankelen",
        "Er ankelen hoven?",
        ["hoven ankel","hevelse i ankelen","ankelen er hoven","hovent rundt ankelen"],
    ),
    "ankle_twist": (
        "nylig overtråkk eller vridning av ankelen",
        "Vred eller tråkket du over ankelen rett før plagene startet?",
        ["tråkket over","overtråkk","vrikket ankelen","vred ankelen"],
    ),
    "bruising": (
        "blåmerker",
        "Har du fått blåmerker ved det vonde området?",
        ["blåmerker","blåmerke","blåflekk"],
    ),
    "rash": (
        "utslett",
        "Har du utslett på huden?",
        ["utslett","røde prikker","rødt utslett","hudutslett"],
    ),
    "itchy_skin": (
        "kløe i huden",
        "Klør det i huden?",
        ["kløe","klør","kløende hud","hudkløe"],
    ),
    "dry_skin": (
        "tørr og sprukken hud",
        "Er huden tørr eller sprukken der du har plager?",
        ["tørr hud","sprukken hud","huden er tørr","huden sprekker"],
    ),
    "flexural_rash": (
        "utslett i albuebøyer eller knehaser",
        "Sitter utslettet særlig i albuebøyene eller bak knærne?",
        ["utslett i albuebøyen","utslett i knehasene","utslett bak knærne","utslett i albuebøyene"],
    ),
    "recurrent_skin_flares": (
        "tilbakevendende hudplager",
        "Har hudplagene kommet tilbake i perioder over lengre tid?",
        ["utslettet kommer tilbake","tilbakevendende utslett","hudplagene kommer og går"],
    ),
    "exposure_localized_rash": (
        "lokalt utslett etter hudkontakt",
        "Kom utslettet der huden hadde kontakt med for eksempel såpe, metall eller et nytt produkt?",
        ["utslett etter såpe","utslett etter hudkrem","utslett etter kontakt med metall","utslett under klokken","utslett etter nytt produkt"],
    ),
    "blisters": (
        "små væskefylte blemmer",
        "Har du små væskefylte blemmer i huden?",
        ["væskefylte blemmer","små blemmer","blemmer på huden"],
    ),
    "raised_wheals": (
        "opphevede vabler",
        "Har du opphevede vabler eller hevelser i huden?",
        ["vabler","opphevede vabler","opphevede hevelser i huden"],
    ),
    "changing_wheals": (
        "vabler som forsvinner og dukker opp andre steder",
        "Forsvinner enkeltvabler innen et døgn mens nye kan komme andre steder?",
        ["vabler som flytter seg","vablene flytter seg","vabler som forsvinner og kommer tilbake","vablene forsvinner innen et døgn"],
    ),
    "scaly_plaques": (
        "tykke avgrensede hudflekker med skjelling",
        "Har du tydelig avgrensede, tykke hudflekker med skjell?",
        ["skjellende hudflekker","tykke skjellende flekker","sølvhvite skjell","tykke hudplakk"],
    ),
    "extensor_plaques": (
        "skjellende flekker på albuer eller knær",
        "Sitter de skjellende flekkene på utsiden av albuene eller foran på knærne?",
        ["skjellende flekker på albuene","skjellende flekker på knærne","skjell på utsiden av albuene"],
    ),
    "scalp_scaling": (
        "skjellende flekker i hodebunnen",
        "Har du avgrensede områder med tykk skjelling i hodebunnen?",
        ["skjelling i hodebunnen","skjellende hodebunn","tykke skjell i hodebunnen"],
    ),
    "pimples": (
        "kviser",
        "Har du kviser, særlig i ansiktet, på brystet eller ryggen?",
        ["kviser","kvise","betente kviser","pustler i ansiktet"],
    ),
    "blackheads": (
        "hudormer",
        "Har du hudormer, som svarte eller hvite tette porer?",
        ["hudormer","sorte prikker i porene","svarte hudormer","hvite hudormer"],
    ),
    "night_itch": (
        "kløe om natten",
        "Klør det i huden om natten?",
        ["kløe om natten","klør om natten","kløen er verst om natten","nattlig kløe","klør mest om natten","kløe som er verst om natten"],
    ),
    "finger_web_rash": (
        "utslett mellom fingrene",
        "Har du små nupper eller utslett mellom fingrene?",
        ["utslett mellom fingrene","nupper mellom fingrene","prikker mellom fingrene"],
    ),
    "burrows": (
        "tynne ganger i huden",
        "Ser du tynne, buktende streker eller ganger i huden ved utslettet?",
        ["ganger i huden","tynne streker i huden","buktende streker i huden","skabbganger"],
    ),
    "itchy_contacts": (
        "kløe hos nærkontakter",
        "Har noen du bor med eller har nær hudkontakt med også fått kløe?",
        ["andre i huset klør","partneren klør","familien klør","flere hjemme klør","nærkontakter klør"],
    ),
}

SYMPTOM_LABELS = {key: value[0] for key, value in _SYMPTOMS.items()}
SYMPTOM_QUESTIONS = {key: value[1] for key, value in _SYMPTOMS.items()}
SYMPTOM_PATTERNS = {key: value[2] for key, value in _SYMPTOMS.items()}

NEGATIONS = ["ikke", "ingen", "intet", "uten", "aldri", "verken"]
