//  API Helper Module
// Centralized FETCH request handling


class APIClient {
  constructor(baseURL = '/api') {
    this.baseURL = baseURL;
  }

  // ============ FETCH Helpers ============
  
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || `HTTP ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // ============ PAINTINGS ============
  
  async savePainting(paintingData) {
    return this.request('/paintings', {
      method: 'POST',
      body: JSON.stringify(paintingData)
    });
  }

  async getPaintings(filters = {}) {
    const params = new URLSearchParams(filters);
    return this.request(`/paintings?${params}`);
  }

  async getPainting(id) {
    return this.request(`/paintings/${id}`);
  }

  async deletePainting(id) {
    return this.request(`/paintings/${id}`, {
      method: 'DELETE'
    });
  }

  // ============ FLOWERS ============
  
  async uploadFlower(file, name) {
    const formData = new FormData();
    formData.append('flower_image', file);
    formData.append('name', name);

    const url = `${this.baseURL}/flowers`;
    const response = await fetch(url, {
      method: 'POST',
      body: formData  // Don't set Content-Type
    });
    
    return await response.json();
  }

  async getFlowers(limit = 50) {
    return this.request(`/flowers?limit=${limit}`);
  }

  // ============ CHARMS ============
  
  async uploadCharm(file, name, shape = 'circle') {
    const formData = new FormData();
    formData.append('charm_image', file);
    formData.append('name', name);
    formData.append('shape', shape);

    const url = `${this.baseURL}/charms`;
    const response = await fetch(url, {
      method: 'POST',
      body: formData
    });
    
    return await response.json();
  }

  async getCharms(limit = 50) {
    return this.request(`/charms?limit=${limit}`);
  }

  // ============ ARRANGEMENTS ============
  
  async saveArrangement(arrangementData) {
    return this.request('/arrangements', {
      method: 'POST',
      body: JSON.stringify(arrangementData)
    });
  }

  async getArrangements(limit = 20) {
    return this.request(`/arrangements?limit=${limit}`);
  }

  // ============ BRACELETS ============
  
  async saveBracelet(braceletData) {
    return this.request('/bracelets', {
      method: 'POST',
      body: JSON.stringify(braceletData)
    });
  }

  async getBracelets(limit = 20) {
    return this.request(`/bracelets?limit=${limit}`);
  }

  // ============ SOCIAL & STATS ============
  
  async getTrendingCreations(limit = 12) {
    return this.request(`/users/trending?limit=${limit}`);
  }

  async getCommunityStats() {
    return this.request('/users/stats');
  }

  async likeCreation(creationId, creationType) {
    return this.request(`/users/${creationId}/like`, {
      method: 'POST',
      body: JSON.stringify({ creation_type: creationType })
    });
  }
}

// Export API client instance
const api = new APIClient();