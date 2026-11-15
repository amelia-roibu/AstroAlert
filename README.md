# AstroAlert
### Platformă cloud pentru monitorizarea evenimentelor astronomice

**Disciplina:** Cloud Computing cu Microsoft Azure  
**Repository:** [GitHub – AstroAlert](https://github.com/amelia-roibu/AstroAlert)  
**Domeniu:** Cloud Computing · Astronomie · Software Engineering

## 1. Descrierea proiectului

AstroAlert este o platformă software destinată monitorizării și afișării evenimentelor astronomice, utilizând date furnizate de surse publice, în special NASA.

Scopul proiectului este dezvoltarea unei aplicații care centralizează informații despre diferite fenomene astronomice și permite utilizatorilor să consulte evenimentele relevante prin intermediul unor endpoint-uri API și al unor filtre bazate pe caracteristicile acestora.

Proiectul urmărește dezvoltarea unei aplicații funcționale care să poată fi ulterior extinsă cu mecanisme de procesare asincronă și notificare a utilizatorilor.

## 2. Funcționalități

Platforma va integra următoarele categorii de evenimente astronomice:

- **Near-Earth Objects (NEO):** monitorizarea asteroizilor care se apropie de Pământ, cu informații despre distanță, viteză, dimensiune și potențialul periculos.
- **Eclipse solare și lunare:** afișarea evenimentelor din cataloagele NASA, cu informații despre tipul eclipsei, magnitudine, seria Saros, durată și regiunile de vizibilitate.
- **Ploi de meteoriți:** integrarea datelor despre principalele fenomene de tip meteor shower.
- **Explozii solare și ejecții coronale (CME):** monitorizarea fenomenelor solare utilizând surse publice de date astronomice.

Pentru fiecare categorie se urmărește dezvoltarea unor endpoint-uri API care permit consultarea și filtrarea evenimentelor după parametri relevanți.

## 3. Arhitectura și tehnologiile utilizate

Versiunea actuală utilizează o arhitectură modulară, organizată în jurul următoarelor componente:

- **Backend:** Python și FastAPI pentru expunerea endpoint-urilor REST.
- **Data processing:** servicii dedicate preluării, parsării și normalizării datelor astronomice.
- **Database:** SQLAlchemy pentru persistența și accesarea datelor; SQLite este utilizat în etapa locală de dezvoltare.
- **External data sources:** NASA NeoWs API și cataloagele NASA pentru eclipse.
- **Testing:** pytest pentru verificarea funcționalităților și a integrării componentelor.

### Arhitectura cloud planificată

Pentru îndeplinirea cerințelor disciplinei, aplicația va fi extinsă folosind servicii Microsoft Azure:

- **Azure App Service:** găzduirea aplicației backend.
- **Azure SQL Database:** stocarea persistentă a datelor astronomice.
- **Azure Virtual Network și Private Endpoint:** izolarea accesului la baza de date.
- **Azure Key Vault:** gestionarea securizată a secretelor și a conexiunilor.
- **Azure Storage Queue / Azure Service Bus:** transmiterea asincronă a solicitărilor de notificare.
- **Azure Functions:** procesarea mesajelor și trimiterea notificărilor.
- **Application Insights:** monitorizarea performanței și colectarea logurilor.
- **Azure CLI / Terraform:** automatizarea deployment-ului și gestionarea infrastructurii.

## 4. Obiectivul final

Rezultatul urmărit este o platformă cloud modulară, capabilă să centralizeze informații despre evenimente astronomice din surse publice și să ofere utilizatorilor posibilitatea de a consulta și filtra aceste evenimente.

Prin utilizarea serviciilor Microsoft Azure, AstroAlert va demonstra integrarea componentelor de compute, storage, networking, securitate, messaging, serverless și observabilitate într-o aplicație cu un domeniu de utilizare concret.

Proiectul reprezintă totodată o bază tehnică pentru dezvoltări ulterioare în domeniul software-ului astronomic și al aplicațiilor Space Tech.