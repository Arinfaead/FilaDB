class ApiService {
    constructor() {
        this.baseURL = '/api/v1';
        this.token = localStorage.getItem('token');
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('token', token);
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem('token');
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

        if (this.token) {
            config.headers.Authorization = `Bearer ${this.token}`;
        }

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: 'Request failed' }));
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Auth endpoints
    async login(email, password) {
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);

        const response = await this.request('/auth/token', {
            method: 'POST',
            headers: {},
            body: formData,
        });

        this.setToken(response.access_token);
        return response;
    }

    async getCurrentUser() {
        return this.request('/auth/me');
    }

    async getUsers() {
        return this.request('/auth/users');
    }

    // Files endpoints
    async getFiles(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/files?${query}`);
    }

    async uploadFile(formData) {
        return this.request('/files', {
            method: 'POST',
            headers: {},
            body: formData,
        });
    }

    async getFile(id) {
        return this.request(`/files/${id}`);
    }

    async updateFile(id, data) {
        return this.request(`/files/${id}`, {
            method: 'PATCH',
            body: JSON.stringify(data),
        });
    }

    async deleteFile(id) {
        return this.request(`/files/${id}`, {
            method: 'DELETE',
        });
    }

    // Inventory endpoints
    async getFilaments(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/inventory/filaments?${query}`);
    }

    async createFilament(data) {
        return this.request('/inventory/filaments', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async getSpools(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/inventory/spools?${query}`);
    }

    async createSpool(data) {
        return this.request('/inventory/spools', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async updateSpool(id, data) {
        return this.request(`/inventory/spools/${id}`, {
            method: 'PATCH',
            body: JSON.stringify(data),
        });
    }

    async deleteSpool(id) {
        return this.request(`/inventory/spools/${id}`, {
            method: 'DELETE',
        });
    }

    // Admin endpoints
    async syncSpoolmanDB() {
        return this.request('/admin/sync/spoolmandb', {
            method: 'POST',
        });
    }

    async getBambuParts() {
        return this.request('/admin/bambu-parts');
    }

    async createBambuPart(data) {
        return this.request('/admin/bambu-parts', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }
}

// Create global instance
window.api = new ApiService();
