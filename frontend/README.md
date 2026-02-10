# 🎨 Frontend DataFlow - Interface Web Interactive

Interface web moderne et élégante pour interagir avec l'API FastAPI Data Science.

---

## ✨ Fonctionnalités

### Design Moderne
- 🎨 **Thème sombre** professionnel
- ⚡ **Animations fluides** et micro-interactions
- 📱 **Responsive** (mobile, tablet, desktop)
- 🌈 **Effets visuels** (gradients, grid overlay)
- 🎯 **UX optimisée** avec feedback visuel

### Interface Complète
- 📊 **5 Sections** (une par TP)
- 🔄 **Navigation par tabs** fluide
- 📈 **Graphiques interactifs** (Plotly)
- 📋 **Tableaux de données** stylisés
- 🔔 **Notifications toast** en temps réel
- ⏳ **Loading states** visuels

### Fonctionnalités par TP

#### TP1 - Clean
- Génération de dataset avec paramètres
- Rapport qualité interactif
- Configuration du pipeline de nettoyage
- Visualisation avant/après

#### TP2 - EDA
- Statistiques descriptives
- Corrélations
- 5 types de graphiques Plotly

#### TP3 - Multivarié
- PCA configurable
- K-Means clustering
- Métriques de qualité

#### TP4 - ML
- Entraînement de modèles
- Métriques train/test
- Interface de prédiction

#### TP5 - ML Avancé
- Hyperparameter tuning
- Feature importance
- Visualisations comparatives

---

## 🚀 Utilisation

### Option 1 : Docker (Recommandé)

```bash
# Lancer tous les services (API + Frontend + Jupyter)
docker-compose up --build

# Frontend accessible sur http://localhost:4000
# API sur http://localhost:8000
# Jupyter sur http://localhost:8888
```

### Option 2 : Serveur local

```bash
# Avec Python
cd frontend
python -m http.server 4000

# Avec Node.js
npx serve . -p 4000
```

Puis ouvrir : **http://localhost:4000**

---

## 🎯 Guide d'Utilisation

### 1. Vérification API
Au démarrage, le frontend vérifie automatiquement que l'API est accessible.
- ✅ **En ligne** : statut vert
- ❌ **Hors ligne** : statut rouge + notification

### 2. Navigation
- Cliquez sur les **onglets numérotés** pour changer de TP
- Chaque TP est **indépendant**
- Les **paramètres** sont sauvegardés

### 3. Workflow Typique (TP1)

```
1. Générer Dataset
   ↓ Cliquez sur "Générer Dataset"
   ↓ Résultat affiché avec ID et statistiques

2. Analyser Qualité
   ↓ Cliquez sur "Analyser la Qualité"
   ↓ Rapport avec missing values, doublons, outliers

3. Configurer Nettoyage
   ↓ Choisissez stratégies (imputation, outliers, encoding)
   ↓ Cliquez sur "Apprendre le Pipeline"

4. Appliquer Nettoyage
   ↓ Cliquez sur "Appliquer le Nettoyage"
   ↓ Résultat avec compteurs avant/après
```

### 4. Notifications
- 🟢 **Succès** : opération réussie
- 🔴 **Erreur** : problème détecté
- 🟡 **Info** : information

---

## 📁 Structure

```
frontend/
├── index.html          # Page principale
├── css/
│   └── main.css       # Styles complets
└── js/
    └── main.js        # Logique JavaScript
```

---

## 🎨 Design System

### Couleurs
```css
--primary: #6366f1      /* Bleu indigo */
--secondary: #06b6d4    /* Cyan */
--success: #10b981      /* Vert */
--warning: #f59e0b      /* Orange */
--error: #ef4444        /* Rouge */
--bg-dark: #0f172a      /* Fond principal */
--bg-card: #1e293b      /* Cartes */
```

### Typographie
- **Titres** : Outfit (Google Fonts)
- **Code** : JetBrains Mono (Google Fonts)
- **Poids** : 300-700

### Espacements
```css
--spacing-xs: 0.5rem    /* 8px */
--spacing-sm: 1rem      /* 16px */
--spacing-md: 1.5rem    /* 24px */
--spacing-lg: 2rem      /* 32px */
--spacing-xl: 3rem      /* 48px */
```

---

## 🔧 Configuration

### URL de l'API
Par défaut : `http://localhost:8000`

Pour modifier, éditer `js/main.js` :
```javascript
const API_BASE_URL = 'http://localhost:8000'; // Changer ici
```

---

## ⚡ Optimisations

### Performance
- ✅ CSS optimisé (variables, transitions)
- ✅ JavaScript modulaire
- ✅ Chargement asynchrone
- ✅ Pas de frameworks lourds

### Accessibilité
- ✅ Contraste élevé (WCAG AA)
- ✅ Navigation clavier
- ✅ Labels sémantiques
- ✅ ARIA attributes

---

## 🎯 Fonctionnalités Avancées

### État Global
L'application maintient un état global :
```javascript
appState = {
    currentTab: 'tp1',
    datasets: {},     // Datasets générés par TP
    cleaners: {},     // Pipelines de nettoyage
    models: {}        // Modèles ML entraînés
}
```

### Gestion d'Erreurs
- Vérification des prérequis (dataset généré avant utilisation)
- Messages d'erreur explicites
- Retry automatique en cas d'échec réseau

### Graphiques Plotly
- Interactifs (zoom, pan, hover)
- Exportables (PNG, SVG)
- Responsive
- Thème sombre intégré

---

## 📱 Responsive

### Breakpoints
```css
@media (max-width: 768px) {
    /* Mobile : colonnes empilées */
}
```

### Optimisations Mobile
- Tabs en colonne sur petit écran
- Formulaires adaptés
- Graphiques redimensionnés
- Boutons pleine largeur

---

## 🐛 Dépannage

### L'API n'est pas accessible
```
Vérifiez que l'API tourne sur http://localhost:8000
→ docker-compose up api
→ Ou : uvicorn app.main:app --reload
```

### CORS Error
L'API doit autoriser les requêtes depuis le frontend.  
✅ Déjà configuré dans `app/main.py`

### Graphiques ne s'affichent pas
Vérifiez que Plotly est chargé :
```html
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
```

---

## 🎓 Technologies Utilisées

- **HTML5** : Structure sémantique
- **CSS3** : Variables, Grid, Flexbox, Animations
- **JavaScript (ES6+)** : Fetch API, Async/Await
- **Plotly.js** : Graphiques interactifs
- **Google Fonts** : Outfit, JetBrains Mono

**Aucun framework** : Vanilla JS pour la légèreté !

---

## 🚀 Prochaines Améliorations

- [ ] Mode clair/sombre switchable
- [ ] Export des résultats en PDF
- [ ] Sauvegarde des sessions
- [ ] Comparaison de modèles
- [ ] Historique des opérations

---

## 📝 Licence

Projet pédagogique - Skayne - 2026

---

**Interface créée avec ❤️ pour DataFlow**
