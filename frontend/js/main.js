// ============================================================================
// CONFIGURATION & ÉTAT GLOBAL
// ============================================================================

const API_BASE_URL = 'http://localhost:8000';

// État global de l'application
const appState = {
    currentTab: 'tp1',
    datasets: {},
    cleaners: {},
    models: {},
    loading: false
};

// ============================================================================
// UTILITAIRES
// ============================================================================

function showLoading() {
    document.getElementById('loading-overlay').classList.add('show');
    appState.loading = true;
}

function hideLoading() {
    document.getElementById('loading-overlay').classList.remove('show');
    appState.loading = false;
}

function showToast(title, message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="toast-title">${title}</div>
        <div class="toast-message">${message}</div>
    `;
    
    document.getElementById('toast-container').appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function formatJSON(data) {
    return JSON.stringify(data, null, 2);
}

function showResult(containerId, content) {
    const container = document.getElementById(containerId);
    container.innerHTML = content;
    container.classList.add('show');
}

async function apiCall(endpoint, options = {}) {
    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Erreur API');
        }
        
        return data;
    } catch (error) {
        showToast('Erreur', error.message, 'error');
        throw error;
    } finally {
        hideLoading();
    }
}

// ============================================================================
// GESTION DES ONGLETS
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialiser les onglets
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.dataset.tab;
            switchTab(tabId);
        });
    });
    
    // Vérifier l'API au démarrage
    checkApiStatus();
});

function switchTab(tabId) {
    // Désactiver tous les onglets
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Masquer tous les panneaux
    document.querySelectorAll('.panel').forEach(panel => {
        panel.classList.remove('active');
    });
    
    // Activer l'onglet et le panneau sélectionnés
    document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
    document.getElementById(`panel-${tabId}`).classList.add('active');
    
    appState.currentTab = tabId;
}

async function checkApiStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            document.getElementById('api-status').textContent = 'En ligne';
            showToast('Connexion établie', 'L\'API est accessible', 'success');
        }
    } catch (error) {
        document.getElementById('api-status').textContent = 'Hors ligne';
        document.querySelector('.status-dot').style.background = 'var(--error)';
        showToast('Erreur de connexion', 'Impossible de joindre l\'API. Vérifiez qu\'elle est lancée.', 'error');
    }
}

// ============================================================================
// TP1 - CLEAN
// ============================================================================

async function generateDataset(phase) {
    const seed = parseInt(document.getElementById(`${phase === 'clean' ? 'tp1' : phase === 'eda' ? 'tp2' : phase === 'mv' ? 'tp3' : phase === 'ml' ? 'tp4' : 'tp5'}-seed`).value);
    const n = parseInt(document.getElementById(`${phase === 'clean' ? 'tp1' : phase === 'eda' ? 'tp2' : phase === 'mv' ? 'tp3' : phase === 'ml' ? 'tp4' : 'tp5'}-n`).value);
    
    const data = await apiCall('/dataset/generate', {
        method: 'POST',
        body: JSON.stringify({ phase, seed, n })
    });
    
    const dataset_id = data.meta.dataset_id;
    appState.datasets[phase] = dataset_id;
    
    const resultHtml = `
        <div class="result-header">✅ Dataset généré avec succès</div>
        <div class="result-content">
            <p><strong>Dataset ID:</strong> <code>${dataset_id}</code></p>
            <p><strong>Lignes:</strong> ${data.result.n_rows}</p>
            <p><strong>Colonnes:</strong> ${data.result.columns.join(', ')}</p>
        </div>
        <div class="metric-grid">
            <div class="metric-item">
                <div class="metric-value">${data.result.n_rows}</div>
                <div class="metric-label">Lignes</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">${data.result.n_cols}</div>
                <div class="metric-label">Colonnes</div>
            </div>
        </div>
    `;
    
    showResult(`${phase === 'clean' ? 'tp1' : phase === 'eda' ? 'tp2' : phase === 'mv' ? 'tp3' : phase === 'ml' ? 'tp4' : 'tp5'}-dataset-result`, resultHtml);
    showToast('Dataset créé', `${n} lignes générées avec succès`, 'success');
}

async function getCleanReport() {
    const dataset_id = appState.datasets['clean'];
    if (!dataset_id) {
        showToast('Erreur', 'Générez d\'abord un dataset', 'error');
        return;
    }
    
    const data = await apiCall(`/clean/report/${dataset_id}`);
    const report = data.report;
    
    let resultHtml = `
        <div class="result-header">📊 Rapport Qualité</div>
        <div class="metric-grid">
            <div class="metric-item">
                <div class="metric-value">${report.n_rows}</div>
                <div class="metric-label">Lignes totales</div>
            </div>
            <div class="metric-item">
                <div class="metric-value" style="color: var(--error)">${report.duplicates}</div>
                <div class="metric-label">Doublons</div>
            </div>
        </div>
        <h4 style="margin-top: 1rem; color: var(--primary)">Valeurs Manquantes</h4>
        <table class="result-table">
            <thead>
                <tr>
                    <th>Colonne</th>
                    <th>Nombre</th>
                    <th>Taux</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    for (const [col, stats] of Object.entries(report.missing_values)) {
        resultHtml += `
            <tr>
                <td><code>${col}</code></td>
                <td>${stats.count}</td>
                <td>${(stats.rate * 100).toFixed(1)}%</td>
            </tr>
        `;
    }
    
    resultHtml += `
            </tbody>
        </table>
        <h4 style="margin-top: 1rem; color: var(--primary)">Outliers Détectés</h4>
        <table class="result-table">
            <thead>
                <tr>
                    <th>Colonne</th>
                    <th>Nombre</th>
                    <th>Taux</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    for (const [col, stats] of Object.entries(report.outliers)) {
        if (stats.count > 0) {
            resultHtml += `
                <tr>
                    <td><code>${col}</code></td>
                    <td>${stats.count}</td>
                    <td>${(stats.rate * 100).toFixed(1)}%</td>
                </tr>
            `;
        }
    }
    
    resultHtml += '</tbody></table>';
    
    showResult('tp1-report-result', resultHtml);
    showToast('Analyse terminée', 'Rapport de qualité généré', 'success');
}

async function fitCleaner() {
    const dataset_id = appState.datasets['clean'];
    if (!dataset_id) {
        showToast('Erreur', 'Générez d\'abord un dataset', 'error');
        return;
    }
    
    const params = {
        impute_strategy: document.getElementById('tp1-impute').value,
        outlier_strategy: document.getElementById('tp1-outlier').value,
        categorical_strategy: document.getElementById('tp1-categorical').value
    };
    
    const data = await apiCall('/clean/fit', {
        method: 'POST',
        body: JSON.stringify({
            meta: { dataset_id },
            params
        })
    });
    
    const cleaner_id = data.result.cleaner_id;
    appState.cleaners['clean'] = cleaner_id;
    
    const resultHtml = `
        <div class="result-header">🎓 Pipeline appris avec succès</div>
        <div class="result-content">
            <p><strong>Cleaner ID:</strong> <code>${cleaner_id}</code></p>
            <p><strong>Paramètres:</strong></p>
            <ul style="margin-left: 1rem; color: var(--text-secondary)">
                <li>Imputation: <strong>${params.impute_strategy}</strong></li>
                <li>Outliers: <strong>${params.outlier_strategy}</strong></li>
                <li>Catégorielles: <strong>${params.categorical_strategy}</strong></li>
            </ul>
        </div>
        <div class="metric-grid">
            <div class="metric-item">
                <div class="metric-value">${data.report.rules_learned.impute_values_count}</div>
                <div class="metric-label">Règles imputation</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">${data.report.rules_learned.outlier_bounds_count}</div>
                <div class="metric-label">Règles outliers</div>
            </div>
        </div>
    `;
    
    showResult('tp1-clean-result', resultHtml);
    document.getElementById('tp1-transform-btn').disabled = false;
    showToast('Pipeline créé', 'Prêt à appliquer le nettoyage', 'success');
}

async function transformData() {
    const dataset_id = appState.datasets['clean'];
    const cleaner_id = appState.cleaners['clean'];
    
    if (!dataset_id || !cleaner_id) {
        showToast('Erreur', 'Fittez d\'abord le pipeline', 'error');
        return;
    }
    
    const data = await apiCall('/clean/transform', {
        method: 'POST',
        body: JSON.stringify({
            meta: { dataset_id },
            params: { cleaner_id }
        })
    });
    
    const counters = data.report.counters;
    
    let resultHtml = `
        <div class="result-header">✨ Nettoyage appliqué avec succès</div>
        <div class="result-content">
            <p><strong>Dataset nettoyé:</strong> <code>${data.result.processed_dataset_id}</code></p>
        </div>
        <div class="metric-grid">
            <div class="metric-item">
                <div class="metric-value">${counters.rows_before}</div>
                <div class="metric-label">Lignes avant</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">${counters.rows_after}</div>
                <div class="metric-label">Lignes après</div>
            </div>
            <div class="metric-item">
                <div class="metric-value" style="color: var(--success)">${counters.duplicates_removed}</div>
                <div class="metric-label">Doublons supprimés</div>
            </div>
        </div>
        <h4 style="margin-top: 1rem; color: var(--primary)">Valeurs Imputées</h4>
        <table class="result-table">
            <thead>
                <tr>
                    <th>Colonne</th>
                    <th>Nombre</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    for (const [col, count] of Object.entries(counters.missing_imputed)) {
        resultHtml += `
            <tr>
                <td><code>${col}</code></td>
                <td>${count}</td>
            </tr>
        `;
    }
    
    resultHtml += '</tbody></table>';
    
    showResult('tp1-clean-result', resultHtml);
    showToast('Nettoyage terminé', `${counters.duplicates_removed} doublons supprimés`, 'success');
}

// ============================================================================
// TP2 - EDA
// ============================================================================

async function getEdaSummary() {
    const dataset_id = appState.datasets['eda'];
    if (!dataset_id) {
        showToast('Erreur', 'Générez d\'abord un dataset', 'error');
        return;
    }
    
    const data = await apiCall('/eda/summary', {
        method: 'POST',
        body: JSON.stringify({
            meta: { dataset_id }
        })
    });
    
    const vars = data.result.variables;
    
    let resultHtml = `
        <div class="result-header">📊 Statistiques Descriptives</div>
        <table class="result-table">
            <thead>
                <tr>
                    <th>Variable</th>
                    <th>Type</th>
                    <th>Count</th>
                    <th>Mean</th>
                    <th>Std</th>
                    <th>Min</th>
                    <th>Max</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    for (const [varName, stats] of Object.entries(vars)) {
        resultHtml += `
            <tr>
                <td><code>${varName}</code></td>
                <td>${stats.type}</td>
                <td>${stats.count}</td>
                <td>${stats.mean ? stats.mean.toFixed(2) : 'N/A'}</td>
                <td>${stats.std ? stats.std.toFixed(2) : 'N/A'}</td>
                <td>${stats.min ? stats.min.toFixed(2) : 'N/A'}</td>
                <td>${stats.max ? stats.max.toFixed(2) : 'N/A'}</td>
            </tr>
        `;
    }
    
    resultHtml += '</tbody></table>';
    
    showResult('tp2-summary-result', resultHtml);
    showToast('Analyse terminée', 'Statistiques calculées', 'success');
}

async function getEdaCorrelation() {
    const dataset_id = appState.datasets['eda'];
    if (!dataset_id) {
        showToast('Erreur', 'Générez d\'abord un dataset', 'error');
        return;
    }
    
    const data = await apiCall('/eda/correlation', {
        method: 'POST',
        body: JSON.stringify({
            meta: { dataset_id }
        })
    });
    
    const topCorr = data.result.top_correlations;
    
    let resultHtml = `
        <div class="result-header">🔗 Top Corrélations</div>
        <table class="result-table">
            <thead>
                <tr>
                    <th>Variable 1</th>
                    <th>Variable 2</th>
                    <th>Corrélation</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    topCorr.slice(0, 10).forEach(item => {
        const color = Math.abs(item.correlation) > 0.7 ? 'var(--error)' : 
                      Math.abs(item.correlation) > 0.5 ? 'var(--warning)' : 
                      'var(--text-secondary)';
        resultHtml += `
            <tr>
                <td><code>${item.var1}</code></td>
                <td><code>${item.var2}</code></td>
                <td style="color: ${color}; font-weight: 600">${item.correlation.toFixed(3)}</td>
            </tr>
        `;
    });
    
    resultHtml += '</tbody></table>';
    
    showResult('tp2-corr-result', resultHtml);
    showToast('Analyse terminée', 'Corrélations calculées', 'success');
}

async function getEdaPlots() {
    const dataset_id = appState.datasets['eda'];
    if (!dataset_id) {
        showToast('Erreur', 'Générez d\'abord un dataset', 'error');
        return;
    }
    
    const data = await apiCall('/eda/plots', {
        method: 'POST',
        body: JSON.stringify({
            meta: { dataset_id }
        })
    });
    
    const artifacts = data.artifacts;
    
    let resultHtml = '<div class="result-header">📈 Visualisations Interactives</div>';
    
    let plotIndex = 0;
    for (const [plotName, plotJson] of Object.entries(artifacts)) {
        const plotId = `plot-${plotName}-${plotIndex++}`;
        resultHtml += `
            <h4 style="margin-top: 1rem; color: var(--primary); text-transform: capitalize">${plotName.replace(/_/g, ' ')}</h4>
            <div id="${plotId}" class="chart-container"></div>
        `;
    }
    
    showResult('tp2-plots-result', resultHtml);
    
    // Render Plotly charts
    plotIndex = 0;
    for (const [plotName, plotJson] of Object.entries(artifacts)) {
        const plotId = `plot-${plotName}-${plotIndex++}`;
        const plotData = JSON.parse(plotJson);
        Plotly.newPlot(plotId, plotData.data, plotData.layout || {}, {responsive: true});
    }
    
    showToast('Visualisations créées', `${Object.keys(artifacts).length} graphiques générés`, 'success');
}

// ============================================================================
// TP3 - MULTIVARIÉ
// ============================================================================

async function runPCA() {
    const dataset_id = appState.datasets['mv'];
    if (!dataset_id) {
        showToast('Erreur', 'Générez d\'abord un dataset', 'error');
        return;
    }
    
    const n_components = parseInt(document.getElementById('tp3-pca-n').value);
    const scale = document.getElementById('tp3-pca-scale').value === 'true';
    
    const data = await apiCall('/mv/pca/fit_transform', {
        method: 'POST',
        body: JSON.stringify({
            meta: { dataset_id },
            params: { n_components, scale }
        })
    });
    
    const result = data.result;
    
    let resultHtml = `
        <div class="result-header">🎯 Résultats PCA</div>
        <div class="metric-grid">
            <div class="metric-item">
                <div class="metric-value">${n_components}</div>
                <div class="metric-label">Composantes</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">${(result.cumulative_variance[n_components-1] * 100).toFixed(1)}%</div>
                <div class="metric-label">Variance expliquée</div>
            </div>
        </div>
        <h4 style="margin-top: 1rem; color: var(--primary)">Variance par Composante</h4>
        <table class="result-table">
            <thead>
                <tr>
                    <th>Composante</th>
                    <th>Variance</th>
                    <th>Cumulative</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    result.explained_variance_ratio.forEach((var_ratio, i) => {
        resultHtml += `
            <tr>
                <td><code>PC${i+1}</code></td>
                <td>${(var_ratio * 100).toFixed(2)}%</td>
                <td>${(result.cumulative_variance[i] * 100).toFixed(2)}%</td>
            </tr>
        `;
    });
    
    resultHtml += `
            </tbody>
        </table>
        <h4 style="margin-top: 1rem; color: var(--primary)">Top Contributors PC1</h4>
        <ul style="margin-left: 1rem; color: var(--text-secondary)">
    `;
    
    result.top_loadings['PC1'].top_variables.forEach(varName => {
        resultHtml += `<li><code>${varName}</code></li>`;
    });
    
    resultHtml += '</ul>';
    
    showResult('tp3-pca-result', resultHtml);
    showToast('PCA terminée', `${(result.cumulative_variance[n_components-1] * 100).toFixed(1)}% de variance expliquée`, 'success');
}

async function runKMeans() {
    const dataset_id = appState.datasets['mv'];
    if (!dataset_id) {
        showToast('Erreur', 'Générez d\'abord un dataset', 'error');
        return;
    }
    
    const k = parseInt(document.getElementById('tp3-k').value);
    const scale = document.getElementById('tp3-kmeans-scale').value === 'true';
    
    const data = await apiCall('/mv/cluster/kmeans', {
        method: 'POST',
        body: JSON.stringify({
            meta: { dataset_id },
            params: { k, scale }
        })
    });
    
    const result = data.result;
    const interpretation = data.report.interpretation;
    
    let resultHtml = `
        <div class="result-header">🎨 Résultats K-Means</div>
        <div class="metric-grid">
            <div class="metric-item">
                <div class="metric-value">${k}</div>
                <div class="metric-label">Clusters</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">${result.silhouette_score ? result.silhouette_score.toFixed(3) : 'N/A'}</div>
                <div class="metric-label">Silhouette Score</div>
            </div>
            <div class="metric-item">
                <div class="metric-value" style="text-transform: capitalize">${interpretation.quality}</div>
                <div class="metric-label">Qualité</div>
            </div>
        </div>
        <h4 style="margin-top: 1rem; color: var(--primary)">Tailles des Clusters</h4>
        <table class="result-table">
            <thead>
                <tr>
                    <th>Cluster</th>
                    <th>Taille</th>
                    <th>%</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    const totalSize = Object.values(result.cluster_sizes).reduce((a, b) => a + b, 0);
    for (const [cluster, size] of Object.entries(result.cluster_sizes)) {
        resultHtml += `
            <tr>
                <td><code>${cluster}</code></td>
                <td>${size}</td>
                <td>${((size / totalSize) * 100).toFixed(1)}%</td>
            </tr>
        `;
    }
    
    resultHtml += '</tbody></table>';
    
    showResult('tp3-kmeans-result', resultHtml);
    showToast('Clustering terminé', `${k} clusters créés (qualité: ${interpretation.quality})`, 'success');
}

// ============================================================================
// TP4 - ML
// ============================================================================

async function trainModel() {
    const dataset_id = appState.datasets['ml'];
    if (!dataset_id) {
        showToast('Erreur', 'Générez d\'abord un dataset', 'error');
        return;
    }
    
    const model_type = document.getElementById('tp4-model-type').value;
    
    const data = await apiCall('/ml/train', {
        method: 'POST',
        body: JSON.stringify({
            meta: { dataset_id },
            params: { model_type }
        })
    });
    
    const model_id = data.result.model_id;
    appState.models['ml'] = model_id;
    
    const metrics_train = data.report.metrics_train;
    const metrics_test = data.report.metrics_test;
    
    let resultHtml = `
        <div class="result-header">🤖 Modèle entraîné avec succès</div>
        <div class="result-content">
            <p><strong>Model ID:</strong> <code>${model_id}</code></p>
            <p><strong>Type:</strong> ${model_type === 'logreg' ? 'Logistic Regression' : 'Random Forest'}</p>
            <p><strong>Features:</strong> ${data.result.n_features}</p>
        </div>
        
        <h4 style="margin-top: 1rem; color: var(--primary)">Métriques Train</h4>
        <div class="metric-grid">
            <div class="metric-item">
                <div class="metric-value">${(metrics_train.accuracy * 100).toFixed(1)}%</div>
                <div class="metric-label">Accuracy</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">${(metrics_train.precision * 100).toFixed(1)}%</div>
                <div class="metric-label">Precision</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">${(metrics_train.recall * 100).toFixed(1)}%</div>
                <div class="metric-label">Recall</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">${(metrics_train.f1_score * 100).toFixed(1)}%</div>
                <div class="metric-label">F1-Score</div>
            </div>
        </div>
        
        <h4 style="margin-top: 1rem; color: var(--primary)">Métriques Test</h4>
        <div class="metric-grid">
            <div class="metric-item">
                <div class="metric-value">${(metrics_test.accuracy * 100).toFixed(1)}%</div>
                <div class="metric-label">Accuracy</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">${(metrics_test.precision * 100).toFixed(1)}%</div>
                <div class="metric-label">Precision</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">${(metrics_test.recall * 100).toFixed(1)}%</div>
                <div class="metric-label">Recall</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">${(metrics_test.f1_score * 100).toFixed(1)}%</div>
                <div class="metric-label">F1-Score</div>
            </div>
        </div>
    `;
    
    showResult('tp4-train-result', resultHtml);
    document.getElementById('tp4-predict-btn').disabled = false;
    showToast('Entraînement terminé', `Accuracy test: ${(metrics_test.accuracy * 100).toFixed(1)}%`, 'success');
}

async function makePrediction() {
    const model_id = appState.models['ml'];
    if (!model_id) {
        showToast('Erreur', 'Entraînez d\'abord un modèle', 'error');
        return;
    }
    
    const dataset_id = appState.datasets['ml'];
    const dataText = document.getElementById('tp4-predict-data').value;
    
    let predictData;
    try {
        predictData = JSON.parse(dataText);
    } catch (e) {
        showToast('Erreur', 'Format JSON invalide', 'error');
        return;
    }
    
    const data = await apiCall('/ml/predict', {
        method: 'POST',
        body: JSON.stringify({
            meta: { dataset_id },
            data: predictData,
            params: { model_id }
        })
    });
    
    const predictions = data.result.predictions;
    const probabilities = data.result.probabilities;
    
    let resultHtml = `
        <div class="result-header">🎯 Prédictions</div>
        <table class="result-table">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Prédiction</th>
                    <th>Probabilité</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    predictions.forEach((pred, i) => {
        const prob = probabilities ? probabilities[i] : null;
        resultHtml += `
            <tr>
                <td>${i + 1}</td>
                <td><strong>${pred}</strong></td>
                <td>${prob ? (prob * 100).toFixed(1) + '%' : 'N/A'}</td>
            </tr>
        `;
    });
    
    resultHtml += '</tbody></table>';
    
    showResult('tp4-predict-result', resultHtml);
    showToast('Prédictions réalisées', `${predictions.length} prédiction(s)`, 'success');
}

// ============================================================================
// TP5 - ML AVANCÉ
// ============================================================================

async function tuneModel() {
    const dataset_id = appState.datasets['ml2'] || appState.datasets['ml'];
    if (!dataset_id) {
        showToast('Erreur', 'Générez d\'abord un dataset', 'error');
        return;
    }
    
    const model_type = document.getElementById('tp5-model-type').value;
    const search = document.getElementById('tp5-search-type').value;
    const cv = parseInt(document.getElementById('tp5-cv').value);
    
    const data = await apiCall('/ml2/tune', {
        method: 'POST',
        body: JSON.stringify({
            meta: { dataset_id },
            params: { model_type, search, cv }
        })
    });
    
    const best_model_id = data.result.best_model_id;
    appState.models['ml2'] = best_model_id;
    
    let resultHtml = `
        <div class="result-header">⚡ Optimisation terminée</div>
        <div class="result-content">
            <p><strong>Best Model ID:</strong> <code>${best_model_id}</code></p>
            <p><strong>Type:</strong> ${model_type === 'logreg' ? 'Logistic Regression' : 'Random Forest'}</p>
            <p><strong>Recherche:</strong> ${search === 'grid' ? 'Grid Search' : 'Random Search'}</p>
        </div>
        <div class="metric-grid">
            <div class="metric-item">
                <div class="metric-value">${(data.result.best_score * 100).toFixed(1)}%</div>
                <div class="metric-label">Meilleur Score CV</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">${cv}</div>
                <div class="metric-label">Folds</div>
            </div>
        </div>
        <h4 style="margin-top: 1rem; color: var(--primary)">Meilleurs Paramètres</h4>
        <pre style="background: var(--bg-dark); padding: 1rem; border-radius: 8px; overflow-x: auto; font-family: var(--font-mono); font-size: 0.875rem;">${JSON.stringify(data.result.best_params, null, 2)}</pre>
    `;
    
    showResult('tp5-tune-result', resultHtml);
    document.getElementById('tp5-importance-btn').disabled = false;
    showToast('Tuning terminé', `Score CV: ${(data.result.best_score * 100).toFixed(1)}%`, 'success');
}

async function getFeatureImportance() {
    const model_id = appState.models['ml2'];
    if (!model_id) {
        showToast('Erreur', 'Lancez d\'abord le tuning', 'error');
        return;
    }
    
    const data = await apiCall(`/ml2/feature-importance/${model_id}`);
    
    const topFeatures = data.result.top_features;
    
    let resultHtml = `
        <div class="result-header">📊 Feature Importance</div>
        <table class="result-table">
            <thead>
                <tr>
                    <th>Rang</th>
                    <th>Feature</th>
                    <th>Importance</th>
                    <th>Barre</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    const maxImportance = Math.max(...Object.values(topFeatures));
    let rank = 1;
    for (const [feature, importance] of Object.entries(topFeatures)) {
        const barWidth = (importance / maxImportance) * 100;
        resultHtml += `
            <tr>
                <td>${rank++}</td>
                <td><code>${feature}</code></td>
                <td>${importance.toFixed(4)}</td>
                <td>
                    <div style="background: var(--border); border-radius: 4px; height: 8px;">
                        <div style="background: var(--primary); width: ${barWidth}%; height: 100%; border-radius: 4px;"></div>
                    </div>
                </td>
            </tr>
        `;
    }
    
    resultHtml += '</tbody></table>';
    
    showResult('tp5-importance-result', resultHtml);
    showToast('Importance calculée', `${Object.keys(topFeatures).length} features analysées`, 'success');
}
