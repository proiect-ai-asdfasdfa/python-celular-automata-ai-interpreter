# WEEK 1
VV Claude VV
```
Q: i'm working in a team and trying to make something more or less impressive. how would you suggest we do it? make a 10week plan and make it based on the contents of the document. we plan to make it using python, recommend tools. keep in mind we're just beginners in this field. also make "modules", distinct pieces of functionality each of us could work on

A: ## Core idea
Describe every automaton in one **internal spec** (grid size, cell types, neighborhood, rules, update mode). The parser produces it, the engine runs it, the analyzer queries it, and the GUI displays it. Agree on this spec in week 1, because everything else depends on it.

To stand out, aim for these:
- All 5 questions answered.
- 5+ automata: Rule 30, Game of Life, Brian's Brain, Langton's Ant, Sandpile.
- A real NN experiment, such as learning an automaton's rule from generations.
- A controlled natural-language parser with good error messages.

## Tools
- **Python 3.11+, NumPy**: grids and fast neighbor counting.
- **Lark**: grammar-based parser for the text descriptions. It's beginner-friendly and works well for controlled natural language. Don't use an LLM at runtime, since the assignment forbids it.
- **Pydantic**: validating the spec.
- **Streamlit**: the easiest GUI for beginners. Use PyQt or Pygame only if someone wants more.
- **Matplotlib / Pillow**: rendering grids, GIF export.
- **SQLite or `.npz` files**: storing generations.
- **scikit-learn first, then PyTorch**: for the NN experiment.
- **pytest, Git/GitHub**: tests and collaboration.
- Keep a `logs/` folder for **all agent conversations** from day one.

## Modules (one per person)
1. **Engine**: grid, cell types, rule application, update modes (synchronous, agent-based like Langton's Ant), seeded randomness for stochastic automata, state save/load.
2. **Language**: grammar, parser, validator, error messages, a library of example descriptions.
3. **Analysis**: the 5 questions (state after N, stable state, configuration occurs, cell counts, cycle detection). Hint: think about how to fingerprint a state.
4. **UI + ML**: Streamlit app, simulation parameters, viewing generations, then dataset generation and the NN experiment.

## 10-week plan
| Week | Goal |
|---|---|
| 1 | Pick the spec format, set up the repo, split the modules. Engine: Rule 30 and Life working in the terminal. Deliverable 1 discussion. |
| 2 | Engine: generic rule representation and 2D neighborhoods. Language: first grammar for elementary CA. Analysis: "state after N" and counts. UI: skeleton page showing a grid. |
| 3 | Add Brian's Brain and the cyclic CA. Parser handles 2D rules. Stability and cycle detection. UI runs a simulation and shows a generation slider. |
| 4 | **Deliverable 2 (world state, rules, parameters, storage/recovery).** Save/load works end to end. Initial world: set manually or generated randomly. |
| 5 | Add Langton's Ant and the sandpile. "Configuration occurs" search. Validation errors shown in the UI. |
| 6 | Integrate everything. Write tests on known results (Life blinker has period 2, sandpile stabilizes). Stochastic automata (forest fire). |
| 7 | **ML dataset:** generate many (state, next state) pairs and whole trajectories across automata. Parser: broader phrasing and synonyms. |
| 8 | **Deliverable 3: NN experiment.** Train a small model to predict the next generation, compare with a baseline, and report accuracy. Try Rule 30 as the hard case. |
| 9 | **Deliverable 4: parsing demo.** Polish the UI (GIF export, stats plots, cell count graphs). Bug fixes. |
| 10 | Freeze features. Write the docs, install guide, and agent-log documentation. Rehearse the presentation with a live demo. |

The lab schedule runs 14 weeks, so shift these rows to match the actual deliverable dates.

## Beginner advice
- Get one automaton working **end to end** (text, then parse, simulate, answer a question, display) before adding more.
- Write tests per automaton early, since they catch integration bugs.
- Don't touch the NN until the dataset generator works.

Want me to sketch the spec format or the first grammar? I'd rather give you hints than a full solution there.

```
VV Gemini VV
```
Q:
<mesajul_anterior>
prima jumatate e ce a spus claude. spune-mi cu ce am putea incepe, nu stim NIMIC 

A:
Respiră adânci și relaxați-vă! E absolut normal să vă simțiți copleșiți când vedeți o listă de 15 automate, rețele neuronale, parsere și zece unelte de care nu ați mai auzit.

Ce v-a dat Claude în prima jumătate este un plan de arhitectură excelent pentru nota 10+, dar pentru cineva care nu știe nimic încă, arată ca manualul de pilotaj al unui avion.

Secretul este următorul: Nu trebuie să faceți totul acum. De fapt, cerința oficială a cursului este împărțită în pași foarte clari (Deliverables).

Hai să lăsăm deoparte termenii complicați (Lark, Pydantic, PyTorch) pentru următoarele 2-3 săptămâni și să vedem ce este proiectul pe românește și ce aveți de făcut azi și săptămâna asta.

1. Ce este, de fapt, un Automat Celular? (Pe scurt)
Imaginați-vă o tablă de șah (în programare îi zicem matrice sau grid).

Fiecare pătrățel (celulă) are o stare: de exemplu, 0 (moartă/albă) sau 1 (vie/neagră).

Timpul trece în pași (generații: Pasul 0, Pasul 1, Pasul 2...).

La fiecare pas, fiecare pătrățel se uită la vecinii lui (cei 8 din jurul lui) și își schimbă starea după o regulă simplă.

Exemplu (Game of Life): Dacă o celulă moartă (0) are exact 3 vecini vii (1), la pasul următor învie (devine 1). Altfel, rămâne 0.

Asta e tot! Toată „simularea” înseamnă să iei tabla de la Pasul 0, să aplici regula pe fiecare pătrățel și să obții tabla de la Pasul 1.

2. Regula de Aur a proiectului (Atenție!)
În cerința profesorului scrie: „All interactions with the conversational agents must be saved.”
Chiar de la această conversație, creați un folder numit logs/ pe calculator și salvați (Copy-Paste în fișiere text sau Export din ChatGPT/Claude/Gemini) absolut toate discuțiile pe care le aveți cu AI-ul pentru proiect. Este obligatoriu la predare!

3. Cu ce începem CONCRET săptămâna asta? (Pas cu Pas)
Uitați de parserul de limbaj natural și de rețele neuronale momentan (alea sunt abia în săptămânile 11 și 13!). Acum ne pregătim pentru L3 (Deliverable 1 - idei și echipă) și L6 (Deliverable 2 - motorul de simulare).

Pasul 1: Organizarea (Azi - 30 de minute)
Împărțiți rolurile (dacă sunteți 4):

Omul 1 (Engine): Se ocupă de matrice și reguli (logica jocului).

Omul 2 (Analiză & Stocare): Se ocupă de salvarea stărilor în fișiere și răspunsul la cele 5 întrebări (ex: „câte celule vii sunt la pasul N?”).

Omul 3 (Interfață + ML mai târziu): Face interfața vizuală (cu Streamlit – e incredibil de ușor, faci un site web din 10 linii de Python fără să știi web development).

Omul 4 (Limbaj / Parser): Se va ocupa de transformarea textului în reguli (până în săptămâna 6-7 îl poate ajuta pe Omul 1 și 2).

Instalați Python și VS Code (sau PyCharm) și faceți un grup pe GitHub/Discord.

Pasul 2: Primul vostru cod (Mâine - 1 oră)
Nu folosiți nicio librărie complicată încă. Deschideți un fișier test_life.py și rugați AI-ul (sau scrieți voi) cel mai simplu „Conway's Game of Life” în consolă, folosind doar liste sau numpy.
Scopul vostru este să vedeți în terminal cum o matrice de 5x5 cu un „Blinker” (3 celule vii în linie) se transformă dintr-o linie orizontală într-una verticală și înapoi. Când vedeți asta rulând, ați înțeles 40% din proiect.

Pasul 3: „Contractul” dintre voi (Pentru L3 - Deliverable 1)
Claude a zis un lucru foarte deștept: „Agree on this spec in week 1”. Ce înseamnă asta?
Dacă Omul 4 traduce textul utilizatorului, iar Omul 1 îl simulează, ei trebuie să vorbească aceeași limbă. Acea „limbă” este un simplu Dicționar în Python (sau fișier JSON).

Pentru Deliverable 1 (Lab 3), tot ce trebuie să îi arătați profesorului este: „Suntem echipa X, folosim Python + Streamlit, și am decis ca orice automat celular să fie reprezentat intern sub forma acestui JSON:”

JSON
{
  "name": "Game of Life",
  "grid_size": [20, 20],
  "states": {
    "0": "DEAD",
    "1": "ALIVE"
  },
  "neighborhood": "Moore", 
  "rules": [
    {
      "current_state": 0,
      "new_state": 1,
      "condition": "count(1) == 3"
    },
    {
      "current_state": 1,
      "new_state": 1,
      "condition": "count(1) == 2 or count(1) == 3"
    }
  ],
  "default_state": 0
}
(Notă: Vecinătatea „Moore” este termenul științific pentru „cei 8 vecini din jurul unei pătrățele”. Vecinătatea „Von Neumann” înseamnă doar cei 4 vecini: sus, jos, stânga, dreapta. Dacă spuneți cuvintele astea la laboratorul 3, profesorul o să fie impresionat).

4. Ce automate să alegeți din lista de 15?
Nu trebuie să le faceți pe toate 15! Alegeți 4 sau 5 care sunt foarte ușor de băgat în același tipar (același JSON ca mai sus):

Game of Life (Clasic, 2 stări: Viu/Mort).

Brian's Brain (Foarte similar cu Game of Life, dar are 3 stări: Off, Firing, Dying).

Forest Fire (3 stări: Empty, Tree, Fire – aproape identic ca logică cu primele două).

Elementary Cellular Automaton - Rule 30 (Este menționat explicit în barem că aduce puncte în plus! E de fapt și mai simplu: e doar un rând 1D, iar fiecare generație nouă se pune pe rândul următor al matricei).

Cyclic Cellular Automaton sau Crystal Growth (Foarte simple, aceleași reguli de numărare a vecinilor).

(Sfat: Evitați momentan Predator-Prey, Traffic sau Artificial Ecosystem – acelea implică „agenți” care se mișcă, au energie, se reproduc, și sunt mult mai greu de programat decât simple pătrățele care își schimbă culoarea).

Cum continuăm chiar acum?
Nu încercați să învățați totul deodată. Spune-mi:

Câți sunteți în echipă și în ce săptămână de facultate sunteți acum (ați trecut de Lab 2 / Lab 3)?

Vrei să îți scriu 20 de linii de cod Python comentate pas cu pas ca să vezi cum funcționează Game of Life în terminal și să aveți de unde pleca?
```

```
Q: suntem lab 3, maine il avem; suntem 4 oameni in echipa
da-mi o "structura", cum putem incepe, game of life si automatele pot fi invatate destuld e ok, noi vrem ajutor cu partea de ai, aici am vrea un plan. din nou, nu am mai facut ai-uri, nu stim ce si cum

A: Pentru mâine la Lab 3 (Deliverable 1), nu vă trebuie cod scris. Profesorul vrea doar să vadă cine sunteți și că aveți un plan tehnic clar.

În proiectul vostru, „partea de AI” se împarte în două lucruri complet diferite care vin abia la final (Lab 11 și Lab 13), dar pe care trebuie să le menționați mâine ca arhitectură:

Machine Learning (Lab 11): O rețea neuronală care „ghicește” regulile jocului doar uitându-se la tablă.

NLP / Procesare de Limbaj (Lab 13): Transformarea textului scris de om în reguli de cod (fără ChatGPT/LLM, pentru că e interzis la rulare).

1. Cum funcționează Rețeaua Neuronală (Lab 11) — explicat de la zero
Nu trebuie să programați matematica din spate. Librării ca scikit-learn fac totul în 5 linii de cod. Tot ce trebuie să înțelegeți acum este cum pregătiți datele.

Gândiți-vă la o rețea neuronală ca la o funcție din JS căreia nu îi scrieți voi if-urile. Îi dați mii de exemple de (input, output), iar ea își reglează singură parametrii interni ca să ghicească output-ul.

Trucul pentru proiectul vostru:
Un automat celular nu depinde de toată tabla de 100x100, ci doar de o celulă și vecinii ei (o fereastră mică de 3x3 pătrățele).

Input (
X): O listă cu 9 numere (cele 9 celule dintr-un pătrat 3x3 la Pasul 
T). De exemplu: [0, 1, 0, 0, 1, 1, 0, 0, 0].

Output (
Y): Un singur număr — ce a devenit celula din mijloc la Pasul 
T+1 (de exemplu, 1).

Planul vostru în 3 pași pentru ML:

Colectarea (Dataset-ul): Lăsați Engine-ul vostru clasic să ruleze Game of Life 100 de generații. Decupați fiecare pătrățel 3x3 și salvați ce a devenit centrul lui. Veți obține instantaneu 50.000 de perechi (Input, Output).

Antrenarea: Băgați aceste perechi într-un MLPClassifier (Multi-Layer Perceptron) din librăria scikit-learn.

Experimentul: Îi dați rețelei o tablă nouă pe care nu a mai văzut-o și o lăsați pe ea să deseneze generația următoare, fără să mai folosiți regulile programate de voi. Apoi comparați: „Rețeaua a ghicit 99% din Game of Life, dar doar 60% când am adăugat reguli bazate pe probabilități (cum e la Forest Fire).” Asta e tot experimentul!

2. Cum funcționează „AI-ul” pentru Text / NLP (Lab 13)
Cerința interzice folosirea unui agent extern (OpenAI/Claude) în aplicația finală. Deci nu faceți AI conversațional, ci un Parser bazat pe șabloane (ca un compilator mic sau un sistem de comenzi).

În loc să lăsați utilizatorul să scrie poezii, îi impuneți un limbaj natural controlat (propoziții în engleză cu structură fixă):

"Grid is 20 by 20. States are DEAD, ALIVE. If cell is DEAD and has 3 ALIVE neighbors then it becomes ALIVE."

Pentru asta folosiți librăria Lark (sau chiar expresii regulate / Regex la început). Lark vă lasă să definiți un șablon (o gramatică), extrage cuvintele cheie (20, DEAD, 3, ALIVE) și le pune direct în JSON-ul pe care îl folosește colegul cu Engine-ul.

3. Structura proiectului (Ce arătați mâine la Lab 3)
Arătați-i profesorului această structură de foldere și împărțirea pe cei 4 membri:

Plaintext
cellab/
├── spec.json          # "Contractul" - cum arată un automat salvat
├── engine/            # [Omul 1] Logica matricelor și aplicarea regulilor
├── analysis/          # [Omul 2] Salvare/încărcare + răspunsul la cele 5 întrebări
├── ai_ml/             # [Omul 3] Generare dataset (ferestre 3x3) + antrenare model
├── nlp_parser/        # [Omul 4] Traducerea textului în spec.json (cu Lark)
├── app.py             # [Omul 3 + 4] Interfața vizuală în Streamlit
└── logs/              # OBLIGATORIU: Toate conversațiile cu AI-ul salvate aici
Ce spuneți concret mâine la prezentarea de 5 minute:
Tehnologii alese: Python, NumPy pentru matrice, Streamlit pentru interfață web rapidă.

Reprezentarea internă: Orice automat (fie că vine din interfață, fie din text) este tradus într-un obiect JSON standard (care conține dimensiunea, stările și regulile de tranziție).

Strategia pentru ML (Deliverable 3): Vom transforma generațiile simulate în perechi de antrenament de tipul (vecinătate locală 3x3 la pasul T -> starea celulei centrale la pasul T+1) și vom antrena o rețea neuronală (MLPClassifier din scikit-learn / PyTorch) să învețe regulile de tranziție.

Strategia pentru NLP (Deliverable 4): Vom defini o gramatică pentru limbaj natural controlat folosind librăria Lark, care va parsa textul utilizatorului și va genera JSON-ul de configurare, fără a apela LLM-uri externe.

Cum vi se pare împărțirea asta? Vreți să detaliem ceva anume pentru discuția cu profesorul de mâine?
```

```
Q:
deci:
la inceput, noi / un ai implementeaza unul sau mai multe automate de genul, apoi rulam cateva generatii si salvam state change-urile pt fiecare pixel / element din matrice. ii dam acele informatii la o retea neuronala, scikit, si apoi noi ii putem da o matrice noua si astfel facem un experiment pe rn, si vedem daca da bn. cum selecteaza / alege rn-ul, la inceput mai ales, ce automat sa ruleze? ii dam noi regulile si matricea noua, sau doar matricea si el trb sa deduca sau avem mai multe rn-uri pentru fiecare automat

A:
Ai prins exact logica.

Gândește-te la o rețea neuronală ca la o funcție din JS sau Rust: fn predict_next_state(input) -> output. Rețeaua nu primește codul vostru cu reguli, ea doar găsește asocieri matematice în datele de antrenament pe care i le oferiți.

Ai două rute arhitecturale. Cum crezi că s-ar comporta fiecare?

Un model separat pentru fiecare automat (Varianta recomandată). Antrenezi Rețeaua A exclusiv cu zeci de mii de ferestre 3x3 din Game of Life. Când îi dai o matrice nouă, Rețeaua A va aproxima doar mecanica din Game of Life. Pentru Rule 30, creezi și antrenezi o Rețea B, complet independentă.

Un singur model "universal". Dacă amesteci datele de la toate automatele și îi ceri unei singure rețele să ghicească, va da rateuri imense dacă primește doar cele 9 celule din matrice ca input. Ce altceva ar trebui să mai adaugi în array-ul de input pe lângă starea celulelor ca rețeaua să știe ce joc se joacă în momentul ăla?

Pentru discuția de mâine, prezentați varianta 1. Este cel mai curat mod de a face experimentul cerut: nu îi dați nicio regulă explicită, îi dați doar stările matricei, iar rețeaua trebuie să deducă singură comportamentul. Evaluarea experimentului va fi pur și simplu un procent: cât la sută din matricea prezisă de rețea se suprapune perfect cu matricea generată de engine-ul vostru clasic.
```
