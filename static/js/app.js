/**
 * ZETEVNIA - AI Araç Kutusu
 * Canvas Drawing & API Integration
 */

class DrawingCanvas {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.error(`Canvas with id "${canvasId}" not found`);
            return;
        }

        this.ctx = this.canvas.getContext('2d', { willReadFrequently: true });
        this.isDrawing = false;
        this.lastX = 0;
        this.lastY = 0;
        this.hasDrawn = false;
        
        // Undo sistemi için geçmiş
        this.history = [];
        this.maxHistory = 20;

        this.setupCanvas();
        this.bindEvents();
    }

    setupCanvas() {
        this.canvas.width = 400;
        this.canvas.height = 400;

        this.ctx.strokeStyle = '#1E293B';
        this.ctx.lineWidth = 16;
        this.ctx.lineCap = 'round';
        this.ctx.lineJoin = 'round';

        this.clear(false);
    }
    
    saveState() {
        const imageData = this.canvas.toDataURL();
        this.history.push(imageData);
        if (this.history.length > this.maxHistory) {
            this.history.shift();
        }
        this.updateUndoButton();
    }
    
    undo() {
        if (this.history.length === 0) return false;
        
        const previousState = this.history.pop();
        const img = new Image();
        img.onload = () => {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
            this.ctx.drawImage(img, 0, 0);
        };
        img.src = previousState;
        
        this.updateUndoButton();
        
        if (this.history.length === 0) {
            this.hasDrawn = false;
        }
        
        return true;
    }
    
    updateUndoButton() {
        const undoBtn = document.getElementById('undoBtn');
        if (undoBtn) {
            undoBtn.disabled = this.history.length === 0;
        }
    }
    
    canUndo() {
        return this.history.length > 0;
    }
    
    download(filename = 'cizim.png') {
        const link = document.createElement('a');
        link.download = filename;
        link.href = this.canvas.toDataURL('image/png');
        link.click();
    }

    bindEvents() {
        this.canvas.addEventListener('mousedown', (e) => this.startDrawing(e));
        this.canvas.addEventListener('mousemove', (e) => this.draw(e));
        this.canvas.addEventListener('mouseup', () => this.stopDrawing());
        this.canvas.addEventListener('mouseout', () => this.stopDrawing());

        this.canvas.addEventListener('touchstart', (e) => this.handleTouch(e, 'start'));
        this.canvas.addEventListener('touchmove', (e) => this.handleTouch(e, 'move'));
        this.canvas.addEventListener('touchend', () => this.stopDrawing());
    }

    getCoordinates(e) {
        const rect = this.canvas.getBoundingClientRect();
        const scaleX = this.canvas.width / rect.width;
        const scaleY = this.canvas.height / rect.height;
        return {
            x: (e.clientX - rect.left) * scaleX,
            y: (e.clientY - rect.top) * scaleY
        };
    }

    getTouchCoordinates(e) {
        const rect = this.canvas.getBoundingClientRect();
        const touch = e.touches[0];
        const scaleX = this.canvas.width / rect.width;
        const scaleY = this.canvas.height / rect.height;
        return {
            x: (touch.clientX - rect.left) * scaleX,
            y: (touch.clientY - rect.top) * scaleY
        };
    }

    startDrawing(e) {
        // Çizim başlamadan önce mevcut durumu kaydet (undo için)
        this.saveState();
        
        this.isDrawing = true;
        this.hasDrawn = true;
        const coords = this.getCoordinates(e);
        this.lastX = coords.x;
        this.lastY = coords.y;
        this.canvas.classList.add('drawing');
    }

    draw(e) {
        if (!this.isDrawing) return;

        const coords = this.getCoordinates(e);

        this.ctx.beginPath();
        this.ctx.moveTo(this.lastX, this.lastY);
        this.ctx.lineTo(coords.x, coords.y);
        this.ctx.stroke();

        this.lastX = coords.x;
        this.lastY = coords.y;
    }

    handleTouch(e, type) {
        e.preventDefault();

        if (type === 'start') {
            this.saveState();
            this.isDrawing = true;
            this.hasDrawn = true;
            const coords = this.getTouchCoordinates(e);
            this.lastX = coords.x;
            this.lastY = coords.y;
            this.canvas.classList.add('drawing');
        } else if (type === 'move' && this.isDrawing) {
            const coords = this.getTouchCoordinates(e);
            this.ctx.beginPath();
            this.ctx.moveTo(this.lastX, this.lastY);
            this.ctx.lineTo(coords.x, coords.y);
            this.ctx.stroke();
            this.lastX = coords.x;
            this.lastY = coords.y;
        }
    }

    stopDrawing() {
        this.isDrawing = false;
        this.canvas.classList.remove('drawing');
    }

    clear(resetHistory = true) {
        this.ctx.fillStyle = '#FFFFFF';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        this.hasDrawn = false;
        
        if (resetHistory) {
            this.history = [];
            this.updateUndoButton();
        }
    }

    isEmpty() {
        return !this.hasDrawn;
    }

    toBase64() {
        return this.canvas.toDataURL('image/png');
    }
}

class NumberRecognitionApp {
    constructor() {
        this.canvas = null;
        this.apiEndpoint = '/api/rakam/tahmin-et';
        this.isProcessing = false;

        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.initSidebar();
            
            if (document.getElementById('drawingCanvas')) {
                this.canvas = new DrawingCanvas('drawingCanvas');
                this.bindButtons();
            }
        });
    }

    bindButtons() {
        const clearBtn = document.getElementById('clearBtn');
        const predictBtn = document.getElementById('predictBtn');
        const undoBtn = document.getElementById('undoBtn');
        const downloadBtn = document.getElementById('downloadBtn');

        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.handleClear());
        }

        if (predictBtn) {
            predictBtn.addEventListener('click', () => this.handlePredict());
        }
        
        if (undoBtn) {
            undoBtn.addEventListener('click', () => this.handleUndo());
        }
        
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => this.handleDownload());
        }

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Delete' || e.key === 'Backspace') {
                if (document.activeElement.tagName !== 'INPUT') {
                    this.handleClear();
                }
            }
            if (e.key === 'Enter') {
                if (document.activeElement.tagName !== 'INPUT') {
                    this.handlePredict();
                }
            }
            // Ctrl+Z ile Undo
            if (e.ctrlKey && e.key === 'z') {
                e.preventDefault();
                this.handleUndo();
            }
            // Ctrl+S ile İndir
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                this.handleDownload();
            }
        });
    }

    initSidebar() {
        const sidebarToggle = document.querySelector('.sidebar-toggle');
        const sidebar = document.querySelector('.sidebar');

        if (sidebarToggle && sidebar) {
            sidebarToggle.addEventListener('click', () => {
                sidebar.classList.toggle('open');
            });

            document.addEventListener('click', (e) => {
                if (window.innerWidth <= 768) {
                    if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                        sidebar.classList.remove('open');
                    }
                }
            });
        }
    }

    handleClear() {
        if (this.canvas) {
            this.canvas.clear();
            this.updateResult(null, 0);
            this.showToast('Tuval temizlendi', 'success');
        }
    }
    
    handleUndo() {
        if (this.canvas && this.canvas.canUndo()) {
            this.canvas.undo();
            this.showToast('Geri alındı', 'success');
        } else {
            this.showToast('Geri alınacak işlem yok', 'error');
        }
    }
    
    handleDownload() {
        if (this.canvas && !this.canvas.isEmpty()) {
            const timestamp = new Date().toISOString().slice(0, 19).replace(/[:-]/g, '');
            this.canvas.download(`zetevnia-cizim-${timestamp}.png`);
            this.showToast('Çizim indirildi', 'success');
        } else {
            this.showToast('İndirilecek çizim yok', 'error');
        }
    }

    async handlePredict() {
        if (this.isProcessing) return;

        if (!this.canvas || this.canvas.isEmpty()) {
            this.showToast('Lütfen önce bir sayı çizin', 'error');
            return;
        }

        this.isProcessing = true;
        this.setButtonLoading(true);

        try {
            const base64Image = this.canvas.toBase64();

            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image_data: base64Image
                })
            });

            const data = await response.json();
            
            if (!response.ok) {
                console.error('Server error:', data);
                throw new Error(data.detail || `HTTP error! status: ${response.status}`);
            }

            if (data.basari) {
                this.updateResult(data.tahmin, data.guven, true);
                this.showToast('Tahmin başarılı!', 'success');
                
                // Geçmişe kaydet
                predictionHistory.add(data.tahmin, data.guven, base64Image);
            } else {
                this.updateResult(null, 0);
                this.showToast('Tahmin yapılamadı', 'error');
            }

        } catch (error) {
            console.error('Prediction error:', error);
            this.updateResult(null, 0);
            this.showToast(error.message || 'Sunucu ile bağlantı kurulamadı', 'error');
        } finally {
            this.isProcessing = false;
            this.setButtonLoading(false);
        }
    }

    updateResult(value, confidence = 0, success = false) {
        const resultValue = document.getElementById('resultValue');
        const resultStatus = document.getElementById('resultStatus');
        const confidenceContainer = document.getElementById('confidenceContainer');
        const confidenceBar = document.getElementById('confidenceBar');
        const confidenceText = document.getElementById('confidenceText');

        if (!resultValue) return;

        if (value !== null && value !== undefined) {
            resultValue.textContent = value;
            resultValue.classList.remove('placeholder');

            if (confidenceContainer && confidenceBar && confidenceText) {
                confidenceContainer.style.display = 'block';
                confidenceBar.style.width = `${confidence}%`;
                
                confidenceBar.classList.remove('low', 'medium', 'high');
                if (confidence < 50) {
                    confidenceBar.classList.add('low');
                } else if (confidence < 80) {
                    confidenceBar.classList.add('medium');
                } else {
                    confidenceBar.classList.add('high');
                }
                
                confidenceText.textContent = `%${confidence.toFixed(1)} Güven`;
            }

            if (resultStatus) {
                resultStatus.innerHTML = `
                    <span class="result-status success">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                            <polyline points="22 4 12 14.01 9 11.01"></polyline>
                        </svg>
                        Başarıyla tanındı
                    </span>
                `;
            }
        } else {
            resultValue.textContent = '?';
            resultValue.classList.add('placeholder');

            if (confidenceContainer) {
                confidenceContainer.style.display = 'none';
            }

            if (resultStatus) {
                resultStatus.innerHTML = `
                    <span class="result-status">
                        Bir sayı çizin ve tahmin edin
                    </span>
                `;
            }
        }
    }

    setButtonLoading(loading) {
        const predictBtn = document.getElementById('predictBtn');
        if (!predictBtn) return;

        if (loading) {
            predictBtn.disabled = true;
            predictBtn.innerHTML = `
                <div class="loading-spinner"></div>
                İşleniyor...
            `;
        } else {
            predictBtn.disabled = false;
            predictBtn.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                    <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
                Tahmin Et
            `;
        }
    }

    showToast(message, type = 'success') {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div class="toast-icon">
                ${type === 'success' 
                    ? '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>'
                    : '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>'
                }
            </div>
            <span class="toast-message">${message}</span>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            </button>
        `;

        container.appendChild(toast);

        requestAnimationFrame(() => {
            toast.classList.add('show');
        });

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

const app = new NumberRecognitionApp();
window.app = app;

/**
 * Theme Manager - Karanlık/Aydınlık mod yönetimi
 */
class ThemeManager {
    constructor() {
        this.storageKey = 'zetevnia-theme';
        this.initialized = false;
    }

    init() {
        if (this.initialized) return;
        this.initialized = true;
        
        const savedTheme = localStorage.getItem(this.storageKey);
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (savedTheme) {
            this.setTheme(savedTheme, false);
        } else if (prefersDark) {
            this.setTheme('dark', false);
        }

        this.bindToggle();

        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem(this.storageKey)) {
                this.setTheme(e.matches ? 'dark' : 'light', false);
            }
        });
    }

    bindToggle() {
        const toggleBtn = document.getElementById('themeToggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggle());
        }
    }

    getTheme() {
        return document.documentElement.getAttribute('data-theme') || 'light';
    }

    setTheme(theme, save = true) {
        document.documentElement.setAttribute('data-theme', theme);
        if (save) {
            localStorage.setItem(this.storageKey, theme);
        }
        this.updateCanvasColors(theme);
    }

    toggle() {
        const currentTheme = this.getTheme();
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
    }

    updateCanvasColors(theme) {
        const canvas = document.getElementById('drawingCanvas');
        if (canvas) {
            const ctx = canvas.getContext('2d');
            ctx.strokeStyle = '#1E293B';
        }
    }
}

const themeManager = new ThemeManager();

// DOM hazır olduğunda tema yöneticisini başlat
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => themeManager.init());
} else {
    themeManager.init();
}

/**
 * Prediction History Manager - Tahmin geçmişi yönetimi
 */
class PredictionHistory {
    constructor() {
        this.storageKey = 'zetevnia-prediction-history';
        this.maxItems = 20;
        this.history = this.load();
    }

    load() {
        try {
            const data = localStorage.getItem(this.storageKey);
            return data ? JSON.parse(data) : [];
        } catch {
            return [];
        }
    }

    save() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.history));
        } catch (e) {
            console.error('Failed to save prediction history:', e);
        }
    }

    add(prediction, confidence, imageData) {
        const item = {
            id: Date.now(),
            prediction,
            confidence,
            imageData,
            timestamp: new Date().toISOString()
        };

        this.history.unshift(item);

        if (this.history.length > this.maxItems) {
            this.history = this.history.slice(0, this.maxItems);
        }

        this.save();
        this.render();
        
        return item;
    }

    remove(id) {
        this.history = this.history.filter(item => item.id !== id);
        this.save();
        this.render();
    }

    clear() {
        this.history = [];
        this.save();
        this.render();
    }

    getAll() {
        return this.history;
    }

    render() {
        const container = document.getElementById('historyList');
        if (!container) return;

        if (this.history.length === 0) {
            container.innerHTML = `
                <div class="history-empty">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <circle cx="12" cy="12" r="10"></circle>
                        <path d="M12 6v6l4 2"></path>
                    </svg>
                    <p data-i18n="history.empty">Henüz tahmin yapılmadı</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.history.map(item => `
            <div class="history-item" data-id="${item.id}">
                <div class="history-item-preview">
                    <img src="${item.imageData}" alt="Çizim">
                </div>
                <div class="history-item-info">
                    <div class="history-item-prediction">${item.prediction}</div>
                    <div class="history-item-confidence">%${item.confidence.toFixed(1)}</div>
                    <div class="history-item-time">${this.formatTime(item.timestamp)}</div>
                </div>
                <div class="history-item-actions">
                    <button class="history-load-btn" title="Yükle" onclick="predictionHistory.loadToCanvas(${item.id})">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                            <polyline points="17 8 12 3 7 8"></polyline>
                            <line x1="12" y1="3" x2="12" y2="15"></line>
                        </svg>
                    </button>
                    <button class="history-delete-btn" title="Sil" onclick="predictionHistory.remove(${item.id})">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M3 6h18"></path>
                            <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
                        </svg>
                    </button>
                </div>
            </div>
        `).join('');
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;

        if (diff < 60000) return 'Az önce';
        if (diff < 3600000) return `${Math.floor(diff / 60000)} dk önce`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)} saat önce`;
        return date.toLocaleDateString('tr-TR');
    }

    loadToCanvas(id) {
        const item = this.history.find(h => h.id === id);
        if (!item || !window.app || !window.app.canvas) return;

        const img = new Image();
        img.onload = () => {
            const canvas = window.app.canvas;
            canvas.ctx.clearRect(0, 0, canvas.canvas.width, canvas.canvas.height);
            canvas.ctx.drawImage(img, 0, 0);
            canvas.hasDrawn = true;
            canvas.history = [];
            canvas.updateUndoButton();
        };
        img.src = item.imageData;
    }

    init() {
        this.render();
        this.bindClearButton();
    }

    bindClearButton() {
        const clearBtn = document.getElementById('clearHistoryBtn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                if (confirm('Tüm geçmişi silmek istediğinize emin misiniz?')) {
                    this.clear();
                }
            });
        }
    }
}

const predictionHistory = new PredictionHistory();

// DOM hazır olduğunda geçmiş yöneticisini başlat
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => predictionHistory.init());
} else {
    predictionHistory.init();
}

window.app = null;
