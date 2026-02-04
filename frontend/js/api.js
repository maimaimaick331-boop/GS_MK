/**
 * API交互模块 - 针对 Terminal#2-18 优化
 */

const API_BASE = 'http://127.0.0.1:5000/api';

class APIClient {
    /**
     * 获取最新实时价格数据 (伦敦 vs 纽约)
     */
    static async getRealtimeData() {
        return this._request(`${API_BASE}/price/latest`);
    }

    /**
     * 获取库存数据
     */
    static async getInventoryData() {
        return this._request(`${API_BASE}/comex/latest`);
    }

    /**
     * 获取聚合库存数据 (三地监控)
     */
    static async getAggregatedInventory() {
        return this._request(`${API_BASE}/inventory/aggregated`);
    }

    /**
     * 通用请求方法
     */
    static async _request(url, method = 'GET', data = null) {
        try {
            const options = {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                }
            };

            if (data && method !== 'GET') {
                options.body = JSON.stringify(data);
            }

            const response = await fetch(url, options);
            if (!response.ok) {
                throw new Error(`HTTP Error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API请求失败:', error);
            throw error;
        }
    }

    /**
     * 格式化数字
     */
    static formatNumber(num, decimals = 2) {
        if (num === null || num === undefined) return '--.--';
        return Number(num).toLocaleString('en-US', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    }

    /**
     * 格式化货币
     */
    static formatCurrency(num, currency = '$') {
        if (num === null || num === undefined) return '--.--';
        return currency + this.formatNumber(num, 2);
    }
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = APIClient;
}
