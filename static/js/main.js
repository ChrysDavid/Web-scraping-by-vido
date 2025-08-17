// Variables globales
let progressModal;
let currentTaskId = null;

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser la modale de progression
    progressModal = new bootstrap.Modal(document.getElementById('progressModal'), {
        backdrop: 'static',
        keyboard: false
    });
    
    // Gérer le bouton d'annulation
    document.getElementById('cancelTask')?.addEventListener('click', cancelCurrentTask);
    
    // Ajouter des animations d'entrée
    addFadeInAnimation();
    
    // Initialiser les tooltips
    initializeTooltips();
});

// Fonctions utilitaires
function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            <i class="fas fa-${getAlertIcon(type)}"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Insérer l'alerte au début du contenu principal
    const main = document.querySelector('main');
    main.insertBefore(alertContainer.firstElementChild, main.firstElementChild);
    
    // Auto-supprimer après 5 secondes
    setTimeout(() => {
        const alert = main.querySelector('.alert');
        if (alert) {
            bootstrap.Alert.getInstance(alert)?.close();
        }
    }, 5000);
}

function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle',
        'primary': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function showProgressModal() {
    const modal = document.getElementById('progressModal');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const progressStats = document.getElementById('progressStats');
    
    // Réinitialiser la modale
    progressBar.style.width = '0%';
    progressBar.setAttribute('aria-valuenow', '0');
    progressText.textContent = 'Initialisation...';
    progressStats.innerHTML = '';
    
    progressModal.show();
}

function hideProgressModal() {
    progressModal.hide();
    currentTaskId = null;
}

function updateProgress(status) {
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const progressStats = document.getElementById('progressStats');
    
    const progress = status.progress || 0;
    progressBar.style.width = `${progress}%`;
    progressBar.setAttribute('aria-valuenow', progress);
    
    // Mettre à jour le texte de progression
    switch (status.status) {
        case 'running':
            progressText.innerHTML = `
                <i class="fas fa-spinner fa-spin"></i> 
                Téléchargement en cours... (${progress}%)
            `;
            break;
        case 'completed':
            progressText.innerHTML = `
                <i class="fas fa-check-circle text-success"></i> 
                Téléchargement terminé !
            `;
            break;
        case 'error':
            progressText.innerHTML = `
                <i class="fas fa-exclamation-triangle text-danger"></i> 
                Erreur lors du téléchargement
            `;
            break;
        default:
            progressText.textContent = 'En attente...';
    }
    
    // Mettre à jour les statistiques
    if (status.files_count !== undefined) {
        progressStats.innerHTML = `
            <div class="row text-center">
                <div class="col-6">
                    <small class="text-muted">Fichiers téléchargés</small><br>
                    <strong>${status.files_count || 0}</strong>
                </div>
                <div class="col-6">
                    <small class="text-muted">Temps écoulé</small><br>
                    <strong>${calculateElapsedTime(status.started_at)}</strong>
                </div>
            </div>
        `;
    }
}

function showCompletionResults(taskId, status) {
    hideProgressModal();
    
    // Afficher le message de succès
    showAlert(`Téléchargement terminé ! ${status.files_count || 0} fichier(s) téléchargé(s).`, 'success');
    
    // Afficher les options de téléchargement
    const resultsHtml = `
        <div class="card mt-3">
            <div class="card-header bg-success text-white">
                <h5 class="mb-0">
                    <i class="fas fa-check-circle"></i> Téléchargement terminé
                </h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-8">
                        <h6>Résumé :</h6>
                        <ul class="list-unstyled">
                            <li><i class="fas fa-link text-primary"></i> URL: ${status.url || 'N/A'}</li>
                            <li><i class="fas fa-file text-info"></i> Fichiers: ${status.files_count || 0}</li>
                            <li><i class="fas fa-clock text-secondary"></i> Terminé: ${formatDate(status.completed_at)}</li>
                        </ul>
                    </div>
                    <div class="col-md-4 text-end">
                        <a href="/download/${taskId}" class="btn btn-success btn-lg">
                            <i class="fas fa-download"></i> Télécharger
                        </a>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Insérer les résultats dans la page
    const resultsSection = document.getElementById('resultsSection');
    if (resultsSection) {
        resultsSection.innerHTML = resultsHtml;
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Réactiver les boutons
    resetFormButtons();
}

function cancelCurrentTask() {
    if (currentTaskId) {
        fetch(`/cancel-task/${currentTaskId}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('Tâche annulée', 'warning');
            }
        })
        .catch(error => {
            console.error('Erreur lors de l\'annulation:', error);
        });
    }
    
    hideProgressModal();
    resetFormButtons();
}

function resetFormButtons() {
    // Réinitialiser le bouton de web scraping
    const webScrapingButton = document.getElementById('startScraping');
    if (webScrapingButton) {
        webScrapingButton.disabled = false;
        webScrapingButton.innerHTML = '<i class="fas fa-play"></i> Démarrer le Scraping';
    }
    
    // Réinitialiser le bouton YouTube
    const youtubeButton = document.getElementById('startDownload');
    if (youtubeButton) {
        youtubeButton.disabled = false;
        youtubeButton.innerHTML = '<i class="fas fa-download"></i> Télécharger';
    }
}

function calculateElapsedTime(startTime) {
    if (!startTime) return 'N/A';
    
    const start = new Date(startTime);
    const now = new Date();
    const diff = Math.floor((now - start) / 1000);
    
    if (diff < 60) {
        return `${diff}s`;
    } else if (diff < 3600) {
        return `${Math.floor(diff / 60)}m ${diff % 60}s`;
    } else {
        const hours = Math.floor(diff / 3600);
        const minutes = Math.floor((diff % 3600) / 60);
        return `${hours}h ${minutes}m`;
    }
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    return date.toLocaleString('fr-FR', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function addFadeInAnimation() {
    const elements = document.querySelectorAll('.card, .hero-section, .feature-item');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    elements.forEach(element => {
        observer.observe(element);
    });
}

function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Fonctions de validation
function validateUrl(url) {
    try {
        new URL(url);
        return { valid: true };
    } catch (e) {
        return { valid: false, error: 'URL invalide' };
    }
}

function validateYouTubeUrl(url) {
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+/;
    if (!youtubeRegex.test(url)) {
        return { valid: false, error: 'URL YouTube invalide' };
    }
    return { valid: true };
}

// Gestion des erreurs globales
window.addEventListener('error', function(e) {
    console.error('Erreur JavaScript:', e.error);
    showAlert('Une erreur inattendue s\'est produite', 'danger');
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Promise rejetée:', e.reason);
    showAlert('Erreur de connexion au serveur', 'danger');
});

// Fonctions utilitaires pour les formulaires
function serializeFormData(form) {
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        // Gérer les checkboxes
        if (form.querySelector(`[name="${key}"]`).type === 'checkbox') {
            data[key] = form.querySelector(`[name="${key}"]`).checked;
        } else {
            data[key] = value;
        }
    }
    
    return data;
}

function resetForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.reset();
        
        // Réinitialiser les états personnalisés
        const selects = form.querySelectorAll('select');
        selects.forEach(select => {
            select.selectedIndex = 0;
        });
        
        const checkboxes = form.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.checked = checkbox.hasAttribute('checked');
        });
    }
}

// Animation de chargement pour les boutons
function setButtonLoading(button, loading = true) {
    if (loading) {
        button.disabled = true;
        button.dataset.originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Chargement...';
        button.classList.add('loading');
    } else {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText || button.innerHTML;
        button.classList.remove('loading');
    }
}

// Gestion du mode sombre (optionnel)
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
}

// Initialiser le mode sombre si sauvegardé
if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
}

// Fonction pour copier du texte dans le presse-papiers
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showAlert('Copié dans le presse-papiers', 'success');
    } catch (err) {
        console.error('Erreur de copie:', err);
        showAlert('Impossible de copier', 'danger');
    }
}

// Gestionnaire de redimensionnement de fenêtre
window.addEventListener('resize', function() {
    // Réajuster les éléments si nécessaire
    const modals = document.querySelectorAll('.modal.show');
    modals.forEach(modal => {
        const modalInstance = bootstrap.Modal.getInstance(modal);
        if (modalInstance) {
            modalInstance.handleUpdate();
        }
    });
});

// Fonction pour détecter si l'utilisateur est sur mobile
function isMobile() {
    return window.innerWidth <= 768;
}

// Gestion des raccourcis clavier
document.addEventListener('keydown', function(e) {
    // Échap pour fermer les modales
    if (e.key === 'Escape') {
        const openModals = document.querySelectorAll('.modal.show');
        openModals.forEach(modal => {
            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) {
                modalInstance.hide();
            }
        });
    }
    
    // Ctrl+R pour actualiser sans confirmation si pas de tâche en cours
    if (e.ctrlKey && e.key === 'r' && !currentTaskId) {
        e.preventDefault();
        location.reload();
    }
});

// Export des fonctions principales pour utilisation dans d'autres scripts
window.WebScraperUtils = {
    showAlert,
    showProgressModal,
    hideProgressModal,
    updateProgress,
    showCompletionResults,
    validateUrl,
    validateYouTubeUrl,
    formatDate,
    formatFileSize,
    setButtonLoading,
    copyToClipboard,
    isMobile
};