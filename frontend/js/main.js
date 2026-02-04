/**
 * Terminal#2-18 主控脚本
 */

let autoUpdateInterval = null;
let isUpdating = false;

/**
 * 初始化
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('Terminal#2-18 终端初始化...');
    startAutoUpdate();
    manualRefresh();
});

/**
 * 启动自动刷新 (1秒一次)
 */
function startAutoUpdate() {
    if (autoUpdateInterval) clearInterval(autoUpdateInterval);
    autoUpdateInterval = setInterval(updateAllData, 1000);
    console.log('已启动秒级自动刷新');
}

/**
 * 切换自动刷新
 */
function toggleAutoUpdate() {
    const btn = document.querySelector('.controls .btn:first-child');
    if (autoUpdateInterval) {
        clearInterval(autoUpdateInterval);
        autoUpdateInterval = null;
        btn.textContent = '启动自动刷新';
        btn.style.backgroundColor = 'var(--accent-green)';
    } else {
        startAutoUpdate();
        btn.textContent = '停止自动刷新';
        btn.style.backgroundColor = 'var(--accent-blue)';
    }
}

/**
 * 手动刷新
 */
function manualRefresh() {
    updateAllData();
}

/**
 * 更新所有数据
 */
async function updateAllData() {
    if (isUpdating) return;
    isUpdating = true;

    try {
        const [priceResp, invResp] = await Promise.all([
            APIClient.getRealtimeData(),
            APIClient.getInventoryData()
        ]);

        if (priceResp.success && priceResp.data) {
            updatePriceUI(priceResp.data);
        }

        if (invResp.success && invResp.data) {
            updateInventoryUI(invResp.data);
        }

        document.getElementById('last-update').textContent = `最后更新: ${new Date().toLocaleTimeString()}`;
    } catch (error) {
        console.error('更新数据失败:', error);
    } finally {
        isUpdating = false;
    }
}

/**
 * 更新价格 UI
 */
function updatePriceUI(data) {
    // 伦敦数据
    if (data.London) {
        if (data.London.silver) updateValue('london-silver', data.London.silver.spot_price, true, data.London.silver);
        if (data.London.gold) updateValue('london-gold', data.London.gold.spot_price, true, data.London.gold);
        if (data.London.copper) updateValue('london-copper', data.London.copper.spot_price, true, data.London.copper);
    }

    // 纽约数据
    if (data.Comex) {
        if (data.Comex.silver) updateValue('comex-silver', data.Comex.silver.futures_price, true, data.Comex.silver);
        if (data.Comex.gold) updateValue('comex-gold', data.Comex.gold.futures_price, true, data.Comex.gold);
        if (data.Comex.copper) updateValue('comex-copper', data.Comex.copper.futures_price, true, data.Comex.copper);
    }

    // 计算 EFP (纽约 - 伦敦)
    if (data.Comex && data.London) {
        // 如果数据质量异常，则跳过 EFP 计算 (P0-4)
        const silverValid = data.Comex.silver && !data.Comex.silver.is_error && data.London.silver && !data.London.silver.is_error;
        const goldValid = data.Comex.gold && !data.Comex.gold.is_error && data.London.gold && !data.London.gold.is_error;
        const copperValid = data.Comex.copper && !data.Comex.copper.is_error && data.London.copper && !data.London.copper.is_error;

        const silverEfpEl = document.getElementById('efp-silver');
        const goldEfpEl = document.getElementById('efp-gold');
        const copperEfpEl = document.getElementById('efp-copper');

        if (silverValid) {
            const comexPrice = data.Comex.silver?.futures_price || 0;
            const londonPrice = data.London.silver?.spot_price || 0;
            const silverEFP = comexPrice - londonPrice;
            
            // 回流监测逻辑: 如果计算结果极其离谱 (例如 > 50% 价格)，标黄警告
            const isSuspicious = Math.abs(silverEFP) / londonPrice > 0.5;
            
            silverEfpEl.textContent = `白银 EFP: ${silverEFP > 0 ? '+' : ''}${silverEFP.toFixed(3)}`;
            silverEfpEl.style.color = isSuspicious ? 'var(--accent-yellow)' : (silverEFP > 0 ? 'var(--accent-green)' : 'var(--accent-red)');
            if (isSuspicious) silverEfpEl.title = "检测到基差异常，请检查单位或合约月份";
        } else {
            const reason = !data.Comex?.silver ? "NY 缺失" : (!data.London?.silver ? "London 缺失" : "数据错误");
            silverEfpEl.textContent = `白银 EFP: ${reason}`;
            silverEfpEl.style.color = 'var(--text-secondary)';
        }
        
        if (goldValid) {
            const comexPrice = data.Comex.gold?.futures_price || 0;
            const londonPrice = data.London.gold?.spot_price || 0;
            const goldEFP = comexPrice - londonPrice;
            
            const isSuspicious = Math.abs(goldEFP) / londonPrice > 0.1; // 黄金基差通常更小
            
            goldEfpEl.textContent = `黄金 EFP: ${goldEFP > 0 ? '+' : ''}${goldEFP.toFixed(2)}`;
            goldEfpEl.style.color = isSuspicious ? 'var(--accent-yellow)' : (goldEFP > 0 ? 'var(--accent-green)' : 'var(--accent-red)');
        } else {
            const reason = !data.Comex?.gold ? "NY 缺失" : (!data.London?.gold ? "London 缺失" : "数据错误");
            goldEfpEl.textContent = `黄金 EFP: ${reason}`;
            goldEfpEl.style.color = 'var(--text-secondary)';
        }

        if (copperValid) {
            // 铜转换: COMEX(USD/lb) * 2204.62 - London(USD/ton)
            const comexCopperTon = (data.Comex.copper?.futures_price || 0) * 2204.62;
            const londonCopperTon = data.London.copper?.futures_price || data.London.copper?.spot_price || 0;
            const copperEFP = comexCopperTon - londonCopperTon;
            
            const isSuspicious = Math.abs(copperEFP) / londonCopperTon > 0.3;
            
            copperEfpEl.textContent = `期铜 EFP: ${copperEFP > 0 ? '+' : ''}${copperEFP.toFixed(2)}`;
            copperEfpEl.style.color = isSuspicious ? 'var(--accent-yellow)' : (copperEFP > 0 ? 'var(--accent-green)' : 'var(--accent-red)');
        } else {
            const reason = !data.Comex?.copper ? "NY 缺失" : (!data.London?.copper ? "London 缺失" : "数据错误");
            copperEfpEl.textContent = `期铜 EFP: ${reason}`;
            copperEfpEl.style.color = 'var(--text-secondary)';
        }
    }
}

/**
 * 更新库存 UI (审计增强版 P0)
 */
function updateInventoryUI(data) {
    // 1. 更新 COMEX 部分
    if (data.comex) {
        const comex = data.comex;
        if (comex.silver) updateInventoryCard('inv-si', 'audit-si', comex.silver, 'Moz');
        if (comex.gold) updateInventoryCard('inv-gc', 'audit-gc', comex.gold, 'Moz');
        if (comex.copper) updateInventoryCard('inv-hg', 'audit-hg', comex.copper, 'Ton');
        
        // 更新 asOf 日期 (取银的数据作为代表)
        if (comex.silver && comex.silver.report_date) {
            document.getElementById('comex-inv-date').textContent = `asOf: ${comex.silver.report_date}`;
        }
    }

    // 2. 更新 LME 部分
    if (data.lme) {
        const lme = data.lme;
        if (lme.silver) updateInventoryCard('inv-lme-si', 'audit-lme-si', lme.silver, 'Moz');
        if (lme.copper) updateInventoryCard('inv-lme-cu', 'audit-lme-cu', lme.copper, 'Ton');
        
        // 更新 asOf 日期
        if (lme.silver && lme.silver.report_date) {
            document.getElementById('lme-inv-date').textContent = `asOf: ${lme.silver.report_date}`;
        }
    }
}

/**
 * 更新单个库存卡片及其审计详情
 */
function updateInventoryCard(valueId, auditId, data, unit) {
    const valEl = document.getElementById(valueId);
    const auditEl = document.getElementById(auditId);
    const cardEl = valEl.parentElement;

    if (!valEl || !data) return;

    // 更新主数值
    valEl.textContent = `${data.total_oz.toFixed(2)} ${unit}`;

    // 更新审计详情 Tooltip
    if (auditEl) {
        const qualityClass = data.quality === 'REALTIME' ? 'status-realtime' : 
                            (data.quality === 'STALE' ? 'status-stale' : 'status-error');
        
        // 映射质量状态显示
        const qualityText = {
            'REALTIME': '实时',
            'STALE': '延迟',
            'ERROR_DIFF': '偏差过大',
            'UNKNOWN_SPEC': '规格未知'
        }[data.quality] || data.quality;

        auditEl.innerHTML = `
            <div class="audit-item">
                <span class="audit-label">数据来源</span>
                <span class="audit-value">${data.source} <span class="status-tag ${qualityClass}">${qualityText}</span></span>
            </div>
            <div class="audit-item">
                <span class="audit-label">原始报告</span>
                <a href="${data.source_url}" target="_blank" class="audit-link">查看详情</a>
            </div>
            <div class="audit-item">
                <span class="audit-label">报告日期</span>
                <span class="audit-value">${data.report_date}</span>
            </div>
            <div class="audit-item">
                <span class="audit-label">采集时间</span>
                <span class="audit-value">${new Date(data.fetched_at).toLocaleString()}</span>
            </div>
            <div class="audit-item">
                <span class="audit-label">采集字段</span>
                <span class="audit-value">${data.field_name}</span>
            </div>
            <div class="audit-item">
                <span class="audit-label">单元格参考</span>
                <span class="audit-value">${data.cell_ref}</span>
            </div>
            <div class="audit-item" style="border-bottom:none; margin-top:8px;">
                <span class="audit-label">文件指纹 (SHA256)</span>
            </div>
            <div style="font-size:0.6rem; color:var(--text-secondary); word-break:break-all; font-family:monospace;">
                ${data.file_hash}
            </div>
            ${data.mapping ? `
            <div class="audit-item" style="border-bottom:none; margin-top:8px;">
                <span class="audit-label">校验逻辑</span>
            </div>
            <div style="font-size:0.65rem; color:var(--accent-green);">
                ${data.mapping}
            </div>` : ''}
        `;
    }

    // 根据质量调整卡片样式
    if (data.quality === 'ERROR_DIFF' || data.quality === 'UNKNOWN_SPEC') {
        cardEl.style.borderColor = 'var(--accent-red)';
    } else if (data.quality === 'STALE') {
        cardEl.style.borderColor = 'var(--accent-yellow)';
    } else {
        cardEl.style.borderColor = 'transparent';
    }
}

/**
 * 通用值更新 (带颜色波动)
 */
function updateValue(id, value, isPrice = false, metadata = null) {
    const el = document.getElementById(id);
    if (!el) return;

    // 处理带单位的情况
    let displayValue = value;
    if (isPrice) {
        displayValue = APIClient.formatCurrency(parseFloat(value));
    }

    // 更新文本内容（保留单位节点）
    const unitEl = el.querySelector('.unit');
    const tooltipEl = el.querySelector('.debug-tooltip');
    
    // 保存旧值用于比较
    const oldText = el.textContent.replace(/[^\d.-]/g, '');
    const oldVal = parseFloat(oldText);
    const newVal = parseFloat(value);

    // 仅更新数值部分，不覆盖 unit 和 tooltip
    let valNode = el.firstChild;
    if (valNode && valNode.nodeType === Node.TEXT_NODE) {
        valNode.textContent = displayValue;
    } else {
        el.prepend(document.createTextNode(displayValue));
    }

    if (isPrice && !isNaN(oldVal) && !isNaN(newVal)) {
        el.classList.remove('up', 'down');
        void el.offsetWidth;
        if (newVal > oldVal) {
            el.classList.add('up');
        } else if (newVal < oldVal) {
            el.classList.add('down');
        }
    }

    // 更新元信息和异常状态 (P0-1 & P0-4)
    if (metadata) {
        if (tooltipEl) {
            const qualityText = metadata.is_error ? '异常' : '正常';
            tooltipEl.innerHTML = `
                <b>来源:</b> ${metadata.source || '未知'}<br>
                <b>时间:</b> ${metadata.provider_as_of || 'N/A'}<br>
                <b>字段:</b> ${metadata.field_used || 'N/A'}<br>
                <b>质量:</b> <span style="color: ${metadata.is_error ? 'var(--accent-red)' : 'var(--accent-green)'}">${qualityText}</span>
            `;
        }
        
        // 异常标红
        if (metadata.is_error) {
            el.classList.add('error');
        } else {
            el.classList.remove('error');
        }
        
        // 保存 metadata 到元素 dataset 以便调试弹窗使用
        el.dataset.metadata = JSON.stringify(metadata);
    }
}

/**
 * 调试弹窗逻辑 (P0-2)
 */
async function showDebug(key) {
    const modal = document.getElementById('debugModal');
    const title = document.getElementById('debug-title');
    const mappingPre = document.getElementById('debug-mapping');
    const payloadPre = document.getElementById('debug-payload');

    title.textContent = `Debug Data: ${key.toUpperCase()}`;
    mappingPre.textContent = 'Loading...';
    payloadPre.textContent = 'Loading...';
    modal.style.display = 'block';

    try {
        const response = await fetch(`http://localhost:5000/api/debug/raw?key=${key}`);
        const result = await response.json();
        
        if (result.success) {
            mappingPre.textContent = JSON.stringify(result.data.mapping, null, 2);
            payloadPre.textContent = JSON.stringify(result.data.raw_payload, null, 2);
        } else {
            mappingPre.textContent = 'Error: ' + result.message;
            payloadPre.textContent = '';
        }
    } catch (error) {
        mappingPre.textContent = 'Error fetching debug data: ' + error.message;
        payloadPre.textContent = '';
    }
}

function closeDebug() {
    document.getElementById('debugModal').style.display = 'none';
}

// 点击弹窗外部关闭
window.onclick = function(event) {
    const modal = document.getElementById('debugModal');
    if (event.target == modal) {
        modal.style.display = "none";
    }
}
