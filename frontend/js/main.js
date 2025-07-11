class FilaDBApp {
    constructor() {
        this.currentUser = null;
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.checkAuth();
    }

    setupEventListeners() {
        document.getElementById('login-form').addEventListener('submit', this.handleLogin.bind(this));
        document.getElementById('logout-btn').addEventListener('click', this.handleLogout.bind(this));
        
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', this.handleNavigation.bind(this));
        });

        document.querySelectorAll('.close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.target.closest('.modal').style.display = 'none';
            });
        });
    }

    async checkAuth() {
        if (!api.token) {
            this.showLogin();
            return;
        }

        try {
            this.currentUser = await api.getCurrentUser();
            this.showMainApp();
        } catch (error) {
            this.showLogin();
        }
    }

    async handleLogin(e) {
        e.preventDefault();
        const formData = new FormData(e.target);

        try {
            await api.login(formData.get('email'), formData.get('password'));
            this.currentUser = await api.getCurrentUser();
            this.showMainApp();
        } catch (error) {
            this.showError('login-error', error.message);
        }
    }

    handleLogout() {
        api.clearToken();
        this.currentUser = null;
        this.showLogin();
    }

    showLogin() {
        document.getElementById('login-container').style.display = 'flex';
        document.getElementById('main-content').style.display = 'none';
    }

    showMainApp() {
        document.getElementById('login-container').style.display = 'none';
        document.getElementById('main-content').style.display = 'block';
        document.getElementById('user-email').textContent = this.currentUser.email;
        
        if (this.currentUser.role === 'admin') {
            document.getElementById('admin-link').style.display = 'block';
        }
    }

    handleNavigation(e) {
        e.preventDefault();
        const page = e.target.dataset.page;
        
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        e.target.classList.add('active');

        document.querySelectorAll('.page').forEach(p => {
            p.style.display = 'none';
        });
        document.getElementById(`${page}-page`).style.display = 'block';
    }

    showError(elementId, message) {
        const errorElement = document.getElementById(elementId);
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new FilaDBApp();
});
