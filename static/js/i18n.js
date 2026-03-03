/**
 * Internationalization (i18n) Manager
 * Çoklu dil desteği
 */
class I18nManager {
    constructor() {
        this.storageKey = 'zetevnia-language';
        this.currentLang = 'tr';
        this.translations = {};
        this.supportedLanguages = ['tr', 'en'];
        this.initialized = false;
    }

    async init() {
        if (this.initialized) return;
        this.initialized = true;

        const savedLang = localStorage.getItem(this.storageKey);
        const browserLang = navigator.language.split('-')[0];

        if (savedLang && this.supportedLanguages.includes(savedLang)) {
            this.currentLang = savedLang;
        } else if (this.supportedLanguages.includes(browserLang)) {
            this.currentLang = browserLang;
        }

        await this.loadTranslations(this.currentLang);
        this.translatePage();
        this.bindLanguageSelector();
        this.updateLanguageSelector();
    }

    async loadTranslations(lang) {
        try {
            const cacheBuster = new Date().getTime();
            const response = await fetch(`/static/locales/${lang}.json?v=${cacheBuster}`);
            if (!response.ok) throw new Error('Translation file not found');
            this.translations = await response.json();
            this.currentLang = lang;
        } catch (error) {
            console.error(`Failed to load translations for ${lang}:`, error);
            if (lang !== 'tr') {
                await this.loadTranslations('tr');
            }
        }
    }

    t(key, fallback = '') {
        const keys = key.split('.');
        let value = this.translations;

        for (const k of keys) {
            if (value && typeof value === 'object' && k in value) {
                value = value[k];
            } else {
                return fallback || key;
            }
        }

        return value || fallback || key;
    }

    translatePage() {
        const elements = document.querySelectorAll('[data-i18n]');
        elements.forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translation = this.t(key);

            if (element.tagName === 'INPUT' && element.placeholder) {
                element.placeholder = translation;
            } else if (element.hasAttribute('title')) {
                element.title = translation;
            } else {
                element.textContent = translation;
            }
        });

        const attrElements = document.querySelectorAll('[data-i18n-title]');
        attrElements.forEach(element => {
            const key = element.getAttribute('data-i18n-title');
            element.title = this.t(key);
        });

        document.documentElement.lang = this.currentLang;
    }

    async setLanguage(lang) {
        if (!this.supportedLanguages.includes(lang)) return;

        await this.loadTranslations(lang);
        localStorage.setItem(this.storageKey, lang);
        this.translatePage();
        this.updateLanguageSelector();

        window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: lang } }));
    }

    bindLanguageSelector() {
        const selector = document.getElementById('languageSelector');
        if (selector) {
            selector.addEventListener('change', (e) => {
                this.setLanguage(e.target.value);
            });
        }

        const langButtons = document.querySelectorAll('[data-lang]');
        langButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.setLanguage(button.getAttribute('data-lang'));
            });
        });
    }

    updateLanguageSelector() {
        const selector = document.getElementById('languageSelector');
        if (selector) {
            selector.value = this.currentLang;
        }

        const langButtons = document.querySelectorAll('[data-lang]');
        langButtons.forEach(button => {
            const lang = button.getAttribute('data-lang');
            button.classList.toggle('active', lang === this.currentLang);
        });
    }

    getCurrentLanguage() {
        return this.currentLang;
    }
}

const i18n = new I18nManager();

window.t = (key, fallback) => i18n.t(key, fallback);

// DOM hazır olduğunda başlat
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => i18n.init());
} else {
    i18n.init();
}
