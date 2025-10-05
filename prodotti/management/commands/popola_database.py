from django.core.management.base import BaseCommand
from django.utils.text import slugify
from prodotti.models import Categoria, Prodotto, ImmagineProdotto
from clienti.models import Cliente, Appuntamento
from preventivi.models import Preventivo, VocePreventivo
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Popola il database con dati di esempio per il negozio cucine'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🚀 Inizio popolamento database...'))
        
        # Pulisci database (opzionale)
        if input('Vuoi cancellare i dati esistenti? (s/n): ').lower() == 's':
            self.stdout.write('🗑️  Cancellazione dati esistenti...')
            VocePreventivo.objects.all().delete()
            Preventivo.objects.all().delete()
            Appuntamento.objects.all().delete()
            Cliente.objects.all().delete()
            ImmagineProdotto.objects.all().delete()
            Prodotto.objects.all().delete()
            Categoria.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Dati cancellati'))
        
        # 1. Crea Categorie
        self.stdout.write('📦 Creazione categorie...')
        categorie_data = [
            {'nome': 'Cucine Moderne', 'descrizione': 'Design contemporaneo e minimalista', 'ordine': 1},
            {'nome': 'Cucine Classiche', 'descrizione': 'Stile tradizionale ed elegante', 'ordine': 2},
            {'nome': 'Cucine Componibili', 'descrizione': 'Modulari e personalizzabili', 'ordine': 3},
            {'nome': 'Elettrodomestici', 'descrizione': 'Forni, frigoriferi e lavastoviglie', 'ordine': 4},
            {'nome': 'Accessori', 'descrizione': 'Complementi e accessori per cucine', 'ordine': 5},
        ]
        
        categorie = {}
        for cat_data in categorie_data:
            categoria, created = Categoria.objects.get_or_create(
                nome=cat_data['nome'],
                defaults={
                    'slug': slugify(cat_data['nome']),
                    'descrizione': cat_data['descrizione'],
                    'ordine': cat_data['ordine']
                }
            )
            categorie[cat_data['nome']] = categoria
            status = '✓ Creata' if created else '→ Esistente'
            self.stdout.write(f'  {status}: {categoria.nome}')
        
        # 2. Crea Prodotti
        self.stdout.write('\n🍳 Creazione prodotti...')
        prodotti_data = [
            # Cucine Moderne
            {
                'categoria': 'Cucine Moderne',
                'nome': 'Cucina Linear Minimal',
                'descrizione': 'Cucina moderna con ante laccate lucide, design essenziale e funzionale. Include elettrodomestici di classe A+++.',
                'specifiche': 'Dimensioni: 360cm x 60cm x 220cm\nMateriali: Laccato lucido, acciaio inox\nColori disponibili: Bianco, Grigio Antracite, Nero',
                'prezzo': 8500.00,
                'in_evidenza': True,
            },
            {
                'categoria': 'Cucine Moderne',
                'nome': 'Cucina Urban Style',
                'descrizione': 'Design contemporaneo con isola centrale, piano in quarzo e illuminazione LED integrata.',
                'specifiche': 'Dimensioni: 420cm x 90cm x 230cm\nMateriali: Laminato opaco, quarzo\nIsola: 180cm x 90cm',
                'prezzo': 12500.00,
                'in_evidenza': True,
            },
            {
                'categoria': 'Cucine Moderne',
                'nome': 'Cucina Tech Innovation',
                'descrizione': 'Cucina smart con comandi touch, elettrodomestici connessi e sistema di aspirazione integrato.',
                'specifiche': 'Dimensioni: 390cm x 65cm x 240cm\nSistema smart home integrato\nElettrodomestici Wi-Fi',
                'prezzo': 15800.00,
                'in_evidenza': True,
            },
            
            # Cucine Classiche
            {
                'categoria': 'Cucine Classiche',
                'nome': 'Cucina Rustica Toscana',
                'descrizione': 'Cucina in legno massello con finitura anticata, maniglie in ottone e top in marmo.',
                'specifiche': 'Dimensioni: 350cm x 60cm x 210cm\nLegno: Rovere massello\nTop: Marmo Carrara',
                'prezzo': 9800.00,
                'in_evidenza': True,
            },
            {
                'categoria': 'Cucine Classiche',
                'nome': 'Cucina Elegance Classic',
                'descrizione': 'Stile classico raffinato con ante a telaio, colonna dispensa e cappa decorativa.',
                'specifiche': 'Dimensioni: 380cm x 60cm x 230cm\nFinitura: Laccato avorio\nDettagli: Fregi decorativi',
                'prezzo': 11200.00,
                'in_evidenza': False,
            },
            
            # Cucine Componibili
            {
                'categoria': 'Cucine Componibili',
                'nome': 'Sistema Modular Flex',
                'descrizione': 'Sistema componibile totalmente personalizzabile, con oltre 50 moduli disponibili.',
                'specifiche': 'Moduli disponibili: Basi, pensili, colonne\nDimensioni personalizzabili\nOltre 20 finiture',
                'prezzo': 6500.00,
                'in_evidenza': True,
            },
            {
                'categoria': 'Cucine Componibili',
                'nome': 'Cucina Custom Design',
                'descrizione': 'Progettazione su misura con rendering 3D incluso, adattabile a ogni spazio.',
                'specifiche': 'Progetto personalizzato\nRendering 3D fotorealistico\nSopralluogo incluso',
                'prezzo': 8900.00,
                'in_evidenza': False,
            },
            
            # Elettrodomestici
            {
                'categoria': 'Elettrodomestici',
                'nome': 'Forno Multifunzione Premium',
                'descrizione': 'Forno da incasso con 12 programmi di cottura, display touch e pulizia pirolitica.',
                'specifiche': 'Capacità: 75L\nClasse energetica: A+++\nFunzioni: 12 programmi + grill',
                'prezzo': 1200.00,
                'in_evidenza': False,
            },
            {
                'categoria': 'Elettrodomestici',
                'nome': 'Frigorifero Side-by-Side',
                'descrizione': 'Frigorifero americano con dispenser acqua e ghiaccio, no frost e zone fresche.',
                'specifiche': 'Capacità: 550L\nClasse A++\nDispenser acqua/ghiaccio\nDisplay digitale',
                'prezzo': 2100.00,
                'in_evidenza': False,
            },
            {
                'categoria': 'Elettrodomestici',
                'nome': 'Piano Cottura Induzione',
                'descrizione': 'Piano cottura a induzione con 4 zone flessibili, comandi touch slider e timer.',
                'specifiche': 'Dimensioni: 60cm\n4 zone induzione\nBooster integrato\nSicurezza bambini',
                'prezzo': 850.00,
                'in_evidenza': False,
            },
            
            # Accessori
            {
                'categoria': 'Accessori',
                'nome': 'Lavello Undermount Inox',
                'descrizione': 'Lavello sottotop in acciaio inox, vasca singola con scolapiatti integrato.',
                'specifiche': 'Dimensioni: 76x44cm\nAcciaio inox 18/10\nSpessore: 1mm',
                'prezzo': 320.00,
                'in_evidenza': False,
            },
            {
                'categoria': 'Accessori',
                'nome': 'Cappa Aspirante Design',
                'descrizione': 'Cappa a scomparsa con illuminazione LED, 3 velocità e filtri antigrasso.',
                'specifiche': 'Larghezza: 90cm\nPortata: 800 m³/h\nLuminosità LED regolabile',
                'prezzo': 650.00,
                'in_evidenza': False,
            },
        ]
        
        prodotti = []
        for prod_data in prodotti_data:
            prodotto, created = Prodotto.objects.get_or_create(
                nome=prod_data['nome'],
                defaults={
                    'categoria': categorie[prod_data['categoria']],
                    'slug': slugify(prod_data['nome']),
                    'descrizione': prod_data['descrizione'],
                    'specifiche_tecniche': prod_data['specifiche'],
                    'prezzo_base': prod_data['prezzo'],
                    'disponibile': True,
                    'in_evidenza': prod_data['in_evidenza'],
                }
            )
            prodotti.append(prodotto)
            status = '✓ Creato' if created else '→ Esistente'
            evidenza = '⭐' if prodotto.in_evidenza else ''
            self.stdout.write(f'  {status}: {prodotto.nome} - €{prodotto.prezzo_base} {evidenza}')
        
        # 3. Crea Clienti
        self.stdout.write('\n👥 Creazione clienti...')
        clienti_data = [
            {'nome': 'Mario', 'cognome': 'Rossi', 'email': 'mario.rossi@email.it', 'telefono': '+39 333 1234567', 'citta': 'Roma'},
            {'nome': 'Laura', 'cognome': 'Bianchi', 'email': 'laura.bianchi@email.it', 'telefono': '+39 348 9876543', 'citta': 'Milano'},
            {'nome': 'Giuseppe', 'cognome': 'Verdi', 'email': 'giuseppe.verdi@email.it', 'telefono': '+39 338 5554444', 'citta': 'Firenze'},
            {'nome': 'Anna', 'cognome': 'Neri', 'email': 'anna.neri@email.it', 'telefono': '+39 320 7778888', 'citta': 'Torino'},
            {'nome': 'Marco', 'cognome': 'Esposito', 'email': 'marco.esposito@email.it', 'telefono': '+39 345 3332222', 'citta': 'Napoli'},
        ]
        
        clienti = []
        for cli_data in clienti_data:
            cliente, created = Cliente.objects.get_or_create(
                email=cli_data['email'],
                defaults={
                    'nome': cli_data['nome'],
                    'cognome': cli_data['cognome'],
                    'telefono': cli_data['telefono'],
                    'citta': cli_data['citta'],
                    'indirizzo': f'Via Example {random.randint(1, 100)}',
                    'cap': f'{random.randint(10000, 99999)}',
                }
            )
            clienti.append(cliente)
            status = '✓ Creato' if created else '→ Esistente'
            self.stdout.write(f'  {status}: {cliente.get_nome_completo()} ({cliente.email})')
        
        # 4. Crea Appuntamenti
        self.stdout.write('\n📅 Creazione appuntamenti...')
        tipi_consulenza = ['CONSULENZA', 'RILIEVO', 'PREVENTIVO']
        stati = ['RICHIESTO', 'CONFERMATO', 'COMPLETATO']
        
        for i, cliente in enumerate(clienti[:4]):  # Primi 4 clienti
            giorni_futuri = random.randint(1, 14)
            data_ora = datetime.now() + timedelta(days=giorni_futuri, hours=random.randint(9, 17))
            
            appuntamento, created = Appuntamento.objects.get_or_create(
                cliente=cliente,
                data_ora=data_ora,
                defaults={
                    'tipo_consulenza': random.choice(tipi_consulenza),
                    'stato': random.choice(stati),
                    'note': f'Interessato a cucine moderne per ristrutturazione completa.',
                }
            )
            status = '✓ Creato' if created else '→ Esistente'
            self.stdout.write(f'  {status}: {cliente.cognome} - {appuntamento.data_ora.strftime("%d/%m/%Y %H:%M")} [{appuntamento.stato}]')
        
        # 5. Crea Preventivi
        self.stdout.write('\n📄 Creazione preventivi...')
        
        for i, cliente in enumerate(clienti[:3]):  # Primi 3 clienti
            preventivo, created = Preventivo.objects.get_or_create(
                cliente=cliente,
                defaults={
                    'stato': ['BOZZA', 'INVIATO', 'ACCETTATO'][i % 3],
                    'sconto_percentuale': random.choice([0, 5, 10]),
                    'validita_giorni': 30,
                    'note': 'Installazione e trasporto inclusi nel prezzo.',
                }
            )
            
            if created:
                # Aggiungi 2-4 prodotti casuali al preventivo
                num_prodotti = random.randint(2, 4)
                prodotti_scelti = random.sample(prodotti, num_prodotti)
                
                for j, prodotto in enumerate(prodotti_scelti):
                    VocePreventivo.objects.create(
                        preventivo=preventivo,
                        prodotto=prodotto,
                        quantita=random.randint(1, 3) if prodotto.categoria.nome == 'Accessori' else 1,
                        prezzo_unitario_finale=prodotto.prezzo_base * random.uniform(0.9, 1.0),  # Piccolo sconto
                        ordine=j,
                    )
                
                preventivo.aggiorna_totale()
            
            status = '✓ Creato' if created else '→ Esistente'
            self.stdout.write(f'  {status}: {preventivo.numero_preventivo} - {cliente.cognome} - €{preventivo.totale_stimato} [{preventivo.stato}]')
        
        # Statistiche finali
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✅ DATABASE POPOLATO CON SUCCESSO!'))
        self.stdout.write('='*60)
        self.stdout.write(f'📦 Categorie create: {Categoria.objects.count()}')
        self.stdout.write(f'🍳 Prodotti creati: {Prodotto.objects.count()}')
        self.stdout.write(f'   ⭐ In evidenza: {Prodotto.objects.filter(in_evidenza=True).count()}')
        self.stdout.write(f'👥 Clienti creati: {Cliente.objects.count()}')
        self.stdout.write(f'📅 Appuntamenti creati: {Appuntamento.objects.count()}')
        self.stdout.write(f'📄 Preventivi creati: {Preventivo.objects.count()}')
        self.stdout.write(f'   📝 Voci preventivo: {VocePreventivo.objects.count()}')
        self.stdout.write('\n💡 Accedi all\'admin per vedere i dati: http://127.0.0.1:8000/admin/')
        self.stdout.write('='*60)
