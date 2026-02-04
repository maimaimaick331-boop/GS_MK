/**
 * 三地库存与交割监控 - 实时驱动逻辑 (V1.5)
 */

document.addEventListener('DOMContentLoaded', () => {
    // 初始加载
    refreshData();
    
    // 启动秒级刷新 (1s)
    setInterval(updateTime, 1000);
    setInterval(refreshData, 2000); // 考虑到后端采集频率，数据每2秒拉取一次即可
});

function updateTime() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('zh-CN', { hour12: false });
    document.getElementById('sys-time').textContent = `系统时间: ${timeStr}`;
}

async function refreshData() {
    try {
        // 1. 获取价格数据
        const priceResp = await APIClient.getRealtimeData();
        if (priceResp.success) {
            updatePriceTicker(priceResp.data);
            calculatePremiums(priceResp.data);
        }

        // 2. 获取聚合库存数据
        const invResp = await APIClient.getAggregatedInventory();
        if (invResp.success) {
            updateInventoryDisplay(invResp.data);
            document.getElementById('last-update').textContent = `最后同步: ${new Date().toLocaleTimeString()}`;
            document.getElementById('api-status').innerHTML = '<span class="up">● 正常</span>';
        }
    } catch (error) {
        console.error('数据刷新失败:', error);
        document.getElementById('api-status').innerHTML = '<span class="down">● 连接断开</span>';
    }
}

function updatePriceTicker(data) {
    const ticker = document.getElementById('price-ticker');
    ticker.innerHTML = '';

    const markets = [
        { name: '伦敦金现', key: 'London', metal: 'gold' },
        { name: '伦敦银现', key: 'London', metal: 'silver' },
        { name: '伦敦铜', key: 'London', metal: 'copper' },
        { name: 'COMEX银', key: 'Comex', metal: 'silver' },
        { name: 'COMEX铜', key: 'Comex', metal: 'copper' },
        { name: 'SHFE银', key: 'Shanghai', metal: 'silver' },
        { name: 'SHFE铜', key: 'Shanghai', metal: 'copper' }
    ];

    markets.forEach(m => {
        const item = data[m.key] ? data[m.key][m.metal] : null;
        if (item) {
            const card = document.createElement('div');
            card.className = 'ticker-card';
            const updateTime = item.provider_as_of ? item.provider_as_of.split(' ')[1] || item.provider_as_of : '--:--';
            card.innerHTML = `
                <div class="symbol">
                    <span>${m.name}</span>
                    <span class="source-tag">${item.source || ''}</span>
                </div>
                <div class="price">${APIClient.formatNumber(item.price, m.metal === 'silver' ? 3 : 2)}</div>
                <div class="ticker-footer">
                    <span class="change">${item.market === 'Shanghai' ? 'CNY' : 'USD'}</span>
                    <span class="update-time">🕒 ${updateTime}</span>
                </div>
            `;
            ticker.appendChild(card);
        }
    });
}

function updateInventoryDisplay(data) {
    // 更新 COMEX
    renderSection('comex-section', data.comex, 'CME (百万盎司)');
    // 更新 LME
    renderSection('lme-section', data.lme, 'LME (吨)');
    // 更新 SHFE
    renderSection('shfe-section', data.shfe, 'SHFE (吨)');
}

function renderSection(sectionId, marketData, unitLabel) {
    const section = document.getElementById(sectionId);
    if (!section) return;
    const title = section.querySelector('h2').outerHTML;
    let html = title;

    // 概念解释映射
    const conceptMap = {
        'registered_oz': {
            label: '注册仓单 (Registered)',
            desc: '已签发标准仓单，可随时用于实物交割的库存。'
        },
        'eligible_oz': {
            label: '合格库存 (Eligible)',
            desc: '符合交易所质量标准，但尚未转化为仓单的库存。'
        },
        'on-warrant': {
            label: '注浆仓单 (On-Warrant)',
            desc: 'LME系统中尚未注销、可供交割的仓单库存。'
        },
        'cancelled-warrants': {
            label: '注销仓单 (Cancelled)',
            desc: '已申请提取实物、不再供交割的仓单。通常预示库存外流。'
        }
    };

    for (const [metal, info] of Object.entries(marketData)) {
        // 自动判定市场类型
        const isLME = info.source === 'LME';
        const regLabel = isLME ? conceptMap['on-warrant'].label : conceptMap['registered_oz'].label;
        const eliLabel = isLME ? '注销仓单 (Cancelled)' : conceptMap['eligible_oz'].label;

        html += `
            <div class="inventory-card">
                <h3>
                    <span>${metal.toUpperCase()}</span>
                    <span class="metal-tag">${info.source}</span>
                </h3>
                <div class="stat-item">
                    <span class="stat-label">总库存 (${info.unit || '盎司/吨'})</span>
                    <span class="stat-value">${APIClient.formatNumber(info.total_oz, 2)}</span>
                </div>
                <div class="stat-item" title="${isLME ? conceptMap['on-warrant'].desc : conceptMap['registered_oz'].desc}">
                    <span class="stat-label">${regLabel}</span>
                    <span class="stat-value">${APIClient.formatNumber(info.registered_oz, 2)}</span>
                </div>
                <div class="stat-item" title="${isLME ? conceptMap['cancelled-warrants'].desc : conceptMap['eligible_oz'].desc}">
                    <span class="stat-label">${eliLabel}</span>
                    <span class="stat-value">${APIClient.formatNumber(info.eligible_oz, 2)}</span>
                </div>
                <div class="audit-info">
                    <div class="audit-row"><strong>数据来源:</strong> <span>${info.source}</span></div>
                    <div class="audit-row"><strong>报告链接:</strong> <a href="${info.source_url}" target="_blank">点击查看原文</a></div>
                    <div class="audit-row"><strong>报告日期:</strong> <span>${info.report_date || 'N/A'}</span></div>
                    <div class="audit-row"><strong>采集时间:</strong> <span>${info.fetched_at || 'N/A'}</span></div>
                    <div class="audit-row"><strong>对应指标:</strong> <span>${info.field_used || 'N/A'}</span></div>
                    <div class="audit-row"><strong>报表单元:</strong> <span>${info.cell_ref || 'N/A'}</span></div>
                    <div class="audit-row"><strong>指纹(SHA256):</strong> <span class="hash-text">${info.file_hash ? info.file_hash.substring(0, 16) + '...' : 'N/A'}</span></div>
                    <div class="audit-row"><strong>数据质量:</strong> <span class="quality-tag ${info.quality === 'REALTIME' ? 'up' : 'down'}">${info.quality === 'REALTIME' ? '实时' : '模拟/延迟'}</span></div>
                </div>
            </div>
        `;
    }
    section.innerHTML = html;
}

function calculatePremiums(data) {
    try {
        const ldnSilver = data.London?.silver?.price;
        const shSilver = data.Shanghai?.silver?.price;
        const cmxSilver = data.Comex?.silver?.price;
        
        // 尝试获取实时汇率，如果失败则使用保底值 7.15
        // 上海黄金单位是 元/克，伦敦金单位是 美元/盎司
        // 1盎司 = 31.1035克
        const usdcny = (data.Shanghai?.gold?.price && data.London?.gold?.price) ? 
            (data.Shanghai.gold.price * 31.1035 / data.London.gold.price) : 7.15;

        if (ldnSilver && shSilver) {
            // SHFE 溢价 = ((SHFE / USDCNY) / 32.1507 - London) / London * 100
            // SHFE 银单位是元/kg, 1kg = 32.1507 盎司
            const shUsdPerOz = (shSilver / usdcny) / 32.1507;
            const prem = ((shUsdPerOz - ldnSilver) / ldnSilver) * 100;
            const el = document.getElementById('silver-premium');
            if (el) {
                el.textContent = `${prem > 0 ? '+' : ''}${prem.toFixed(2)}%`;
                el.className = `premium-value ${prem > 0 ? 'up' : 'down'}`;
            }
        }

        if (ldnSilver && cmxSilver) {
            const efp = cmxSilver - ldnSilver;
            const el = document.getElementById('silver-efp');
            if (el) {
                el.textContent = `${efp > 0 ? '+' : ''}$${efp.toFixed(3)}`;
                el.className = `premium-value ${efp > 0 ? 'up' : 'down'}`;
            }
        }

        // 铜溢价计算 (LME 铜 vs SHFE 铜)
        const ldnCopper = data.London?.copper?.price;
        const shCopper = data.Shanghai?.copper?.price;
        if (ldnCopper && shCopper) {
            // SHFE 铜是元/吨，LME 铜也是美元/吨
            const shUsd = shCopper / usdcny;
            const prem = ((shUsd - ldnCopper) / ldnCopper) * 100;
            const el = document.getElementById('copper-premium');
            if (el) {
                el.textContent = `${prem > 0 ? '+' : ''}${prem.toFixed(2)}%`;
                el.className = `premium-value ${prem > 0 ? 'up' : 'down'}`;
            }
        }
    } catch (e) {
        console.error('溢价计算失败:', e);
    }
}
