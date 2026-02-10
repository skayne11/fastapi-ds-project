# 🎨 Guide Visuel de l'Interface DataFlow

Ce document présente visuellement l'interface web et son utilisation.

---

## 🌟 Vue d'Ensemble

L'interface DataFlow est conçue pour être **intuitive**, **moderne** et **professionnelle**.

### Design Characteristics
- ✨ **Thème sombre** professionnel (moins de fatigue visuelle)
- 🌈 **Gradients subtils** et effets de profondeur
- ⚡ **Animations fluides** sur tous les éléments interactifs
- 📊 **Visualisations interactives** avec Plotly
- 🎯 **Workflow guidé** étape par étape

---

## 📐 Structure de l'Interface

### 1. Navigation (Header)
```
┌─────────────────────────────────────────────────────────────┐
│ 🔷 DataFlow v1.0              API: ● En ligne              │
└─────────────────────────────────────────────────────────────┘
```
- **Logo** : Icône hexagonale animée
- **Status API** : Indicateur en temps réel (vert=OK, rouge=erreur)
- **Sticky** : Reste visible lors du scroll

### 2. Hero Section
```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│         Plateforme Data Science                             │
│         Complète & Interactive                              │
│                                                             │
│  Du nettoyage au ML avancé, 5 phases en quelques clics     │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │    22    │  │     5    │  │    ∞     │                 │
│  │ Endpoints│  │  Phases  │  │Possibilités                │
│  └──────────┘  └──────────┘  └──────────┘                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```
- Titre avec **gradient animé**
- 3 **statistiques clés** en cards interactives
- **Hover effects** : elevation et glow

### 3. Tabs de Navigation
```
┌──────────┬──────────┬──────────┬──────────┬──────────┐
│ ● 01     │   02     │   03     │   04     │   05     │
│  Clean   │   EDA    │Multivarié│ML Baseline│ML Avancé │
└──────────┴──────────┴──────────┴──────────┴──────────┘
```
- **5 onglets** pour 5 TPs
- Onglet **actif** : gradient bleu + shadow
- Onglets **inactifs** : gris + hover effect
- **Responsive** : colonnes sur mobile

### 4. Content Area (Cards)
Chaque TP contient plusieurs cards :

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Titre de la Carte                          [Badge]       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Formulaires avec inputs stylisés]                        │
│                                                             │
│  [Bouton d'action avec icône + ripple effect]              │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ✅ Résultat affiché dynamiquement                    │   │
│  │ Avec métriques, tableaux, et graphiques             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 Palette de Couleurs

### Primaires
```
Indigo (Primary)    : #6366f1 ■
Cyan (Secondary)    : #06b6d4 ■
Success (Vert)      : #10b981 ■
Warning (Orange)    : #f59e0b ■
Error (Rouge)       : #ef4444 ■
```

### Backgrounds
```
Dark (Fond)         : #0f172a ■
Card (Cartes)       : #1e293b ■
Hover               : #334155 ■
```

### Text
```
Primary (Blanc)     : #f1f5f9 ■
Secondary (Gris)    : #94a3b8 ■
Border              : #334155 ■
```

---

## 💫 Animations & Interactions

### Entrée de Page
```
1. Navbar : slide down (0.5s)
2. Hero : fade in + translate up (0.8s)
3. Cards : fade in avec stagger (délai progressif)
```

### Boutons
```
1. Hover : translateY(-2px) + shadow
2. Click : ripple effect circulaire
3. Disabled : opacity 0.5 + cursor not-allowed
```

### Cards
```
1. Hover : border color change + shadow glow
2. Transition : 250ms cubic-bezier
```

### Résultats
```
1. Apparition : slide up + fade in (0.4s)
2. Tableaux : zebra striping + hover rows
3. Métriques : numbers in monospace font
```

---

## 📊 Composants Visuels

### 1. Inputs & Selects
```
┌─────────────────────────────────────┐
│ Label avec hint                     │
├─────────────────────────────────────┤
│ [  Valeur monospace  ]              │
└─────────────────────────────────────┘
```
- **Background** : dark
- **Border** : 2px solid, bleu au focus
- **Font** : JetBrains Mono (monospace)
- **Shadow** : glow effect au focus

### 2. Boutons
```
┌─────────────────────────────────────┐
│  🎯 Texte du Bouton                 │
└─────────────────────────────────────┘
```
**Variantes** :
- **Primary** : Gradient indigo, white text
- **Secondary** : Outline indigo, indigo text → fill on hover
- **Success** : Gradient vert

### 3. Métriques
```
┌──────────────┐
│     100      │ ← Grande valeur (monospace)
│   Lignes     │ ← Label (petit, gris)
└──────────────┘
```
- **Grid layout** : auto-fit
- **Hover** : légère élévation
- **Values** : Couleur primaire

### 4. Tableaux
```
┌──────────┬──────────┬──────────┐
│ Header   │ Header   │ Header   │ ← Background card, color primary
├──────────┼──────────┼──────────┤
│ Value    │ Value    │ Value    │
│ Value    │ Value    │ Value    │ ← Hover : background hover
└──────────┴──────────┴──────────┘
```

### 5. Graphiques Plotly
```
┌─────────────────────────────────────┐
│  Titre du Graphique                 │
├─────────────────────────────────────┤
│                                     │
│    [Graphique Plotly interactif]   │
│    • Zoom                           │
│    • Pan                            │
│    • Hover tooltip                  │
│    • Export PNG/SVG                 │
│                                     │
└─────────────────────────────────────┘
```

---

## 🔔 Notifications (Toasts)

```
┌─────────────────────────────────────┐
│ ✅ Titre                             │
│ Message de notification             │ ← Slide in depuis la droite
└─────────────────────────────────────┘
```

**Positions** : Top right  
**Types** :
- ✅ Success : Border vert
- ❌ Error : Border rouge
- ⚠️ Warning : Border orange
- ℹ️ Info : Border bleu

**Animation** :
- Entrée : slide in right
- Sortie : slide out right (auto après 4s)

---

## ⏳ Loading States

### Overlay
```
┌─────────────────────────────────────┐
│                                     │
│           ⟳ Spinner                 │
│      Traitement en cours...         │
│                                     │
└─────────────────────────────────────┘
```
- **Background** : dark blur
- **Spinner** : rotation infinie
- **Text** : gris clair

---

## 📱 Responsive Design

### Desktop (> 768px)
```
[ Nav                                  ]
[ Hero                                 ]
[ Tab1 | Tab2 | Tab3 | Tab4 | Tab5   ]
[ Card Grid (2-3 colonnes)            ]
```

### Mobile (< 768px)
```
[ Nav        ]
[ Hero       ]
[ Tab1       ]
[ Tab2       ]
[ Tab3       ]
[ Tab4       ]
[ Tab5       ]
[ Card       ]
[ (empilées) ]
```

**Adaptations** :
- Tabs : colonnes → vertical stack
- Forms : grid → 1 colonne
- Buttons : pleine largeur
- Métriques : plus petites

---

## 🎯 Workflow Visuel Typique

### TP1 - Clean

```
Step 1: Génération
┌─────────────────┐
│ Seed: 42        │
│ Lignes: 1000    │
│ [Générer]       │ ← Click
└─────────────────┘
         ↓
┌─────────────────────────────┐
│ ✅ Dataset créé             │
│ ID: clean_42_1000          │
│ 1000 lignes, 5 colonnes    │
└─────────────────────────────┘

Step 2: Rapport
[Analyser Qualité] ← Click
         ↓
┌─────────────────────────────┐
│ 📊 Rapport Qualité          │
│ Doublons: 30                │
│ Missing x1: 150 (15%)       │
│ [Tableau détaillé]          │
└─────────────────────────────┘

Step 3: Config
┌─────────────────┐
│ Impute: mean    │
│ Outliers: clip  │
│ [Fit Pipeline]  │ ← Click
└─────────────────┘
         ↓
[✅ Pipeline appris]

Step 4: Transform
[Appliquer] ← Click
         ↓
┌─────────────────────────────┐
│ ✨ Nettoyage terminé         │
│ 1000 → 970 lignes          │
│ 30 doublons supprimés      │
│ [Détails par colonne]      │
└─────────────────────────────┘
```

---

## 🎓 Best Practices UX Implémentées

### Feedback Visuel
- ✅ Loading states pour chaque action async
- ✅ Toasts pour confirmer succès/erreur
- ✅ Boutons disabled quand prérequis manquants
- ✅ Résultats affichés dans la même zone

### Guidage Utilisateur
- ✅ Numérotation des étapes
- ✅ Badges "Requis" sur étapes obligatoires
- ✅ Hints dans les labels
- ✅ Messages d'erreur explicites

### Performance
- ✅ Transitions CSS (pas de JS)
- ✅ Lazy rendering des graphiques
- ✅ Debouncing des events (si applicable)
- ✅ Minimal reflows

### Accessibilité
- ✅ Contraste WCAG AA
- ✅ Labels sémantiques
- ✅ Navigation clavier
- ✅ Focus visible

---

## 🚀 Améliorations Futures

- [ ] Mode clair/sombre toggle
- [ ] Sauvegarde session (localStorage)
- [ ] Export résultats (PDF, CSV)
- [ ] Comparaison de modèles côte-à-côte
- [ ] Historique des opérations
- [ ] Drag & drop pour upload fichiers
- [ ] WebSockets pour updates temps réel
- [ ] PWA (installable)

---

**Design créé avec ❤️ et attention aux détails**
