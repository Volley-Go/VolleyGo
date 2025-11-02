/**
 * UI组件库
 * 可复用的UI组件
 */

/**
 * 创建评分卡片组件
 */
function createScoreCard(score, label, color = 'blue') {
    return `
        <div class="bg-white rounded-xl p-4 border border-gray-200 hover-lift transition-all">
            <div class="text-sm text-gray-500 mb-1">${label}</div>
            <div class="text-3xl font-bold text-gray-800 mb-2">${score.toFixed(1)}</div>
            <div class="w-full h-2 bg-gray-200 rounded-full">
                <div class="h-2 bg-${color}-500 rounded-full transition-all duration-500" 
                     style="width: ${score}%"></div>
            </div>
        </div>
    `;
}

/**
 * 创建进度条组件
 */
function createProgressBar(current, total, showText = true) {
    const percentage = (current / total * 100).toFixed(0);
    
    return `
        <div class="w-full">
            ${showText ? `
                <div class="flex justify-between text-xs text-gray-600 mb-2">
                    <span>${current} / ${total}</span>
                    <span>${percentage}%</span>
                </div>
            ` : ''}
            <div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                <div class="h-2 bg-gradient-to-r from-volleyball-orange to-volleyball-dark-orange rounded-full transition-all duration-500" 
                     style="width: ${percentage}%"></div>
            </div>
        </div>
    `;
}

/**
 * 创建徽章组件
 */
function createBadge(text, variant = 'default') {
    const styles = {
        'default': 'bg-gray-100 text-gray-800 border-gray-300',
        'primary': 'bg-volleyball-orange text-white border-volleyball-orange',
        'success': 'bg-green-100 text-green-800 border-green-300',
        'warning': 'bg-yellow-100 text-yellow-800 border-yellow-300',
        'danger': 'bg-red-100 text-red-800 border-red-300',
        'info': 'bg-blue-100 text-blue-800 border-blue-300'
    };
    
    return `
        <span class="inline-flex items-center px-3 py-1 border rounded-lg text-xs font-medium ${styles[variant] || styles.default}">
            ${text}
        </span>
    `;
}

/**
 * 创建卡片组件
 */
function createCard(content, className = '') {
    return `
        <div class="bg-white rounded-2xl p-6 border border-gray-200 hover-lift transition-all ${className}">
            ${content}
        </div>
    `;
}

/**
 * 创建按钮组件
 */
function createButton(text, options = {}) {
    const {
        variant = 'primary',
        size = 'md',
        icon = '',
        onClick = '',
        disabled = false,
        className = ''
    } = options;
    
    const variants = {
        'primary': 'bg-gradient-to-r from-volleyball-orange to-volleyball-dark-orange text-white hover:shadow-xl',
        'secondary': 'bg-gray-100 text-gray-800 hover:bg-gray-200',
        'outline': 'border-2 border-volleyball-orange text-volleyball-orange hover:bg-volleyball-orange hover:text-white'
    };
    
    const sizes = {
        'sm': 'px-4 py-2 text-sm',
        'md': 'px-6 py-3 text-base',
        'lg': 'px-8 py-4 text-lg'
    };
    
    return `
        <button 
            ${onClick ? `onclick="${onClick}"` : ''}
            ${disabled ? 'disabled' : ''}
            class="rounded-xl font-semibold transition-all ${variants[variant]} ${sizes[size]} ${className} ${disabled ? 'opacity-50 cursor-not-allowed' : ''}">
            ${icon ? `<span class="mr-2">${icon}</span>` : ''}
            ${text}
        </button>
    `;
}

/**
 * 创建Toast通知
 */
function showToast(message, type = 'info', duration = 3000) {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const colors = {
        'success': 'bg-green-500',
        'error': 'bg-red-500',
        'warning': 'bg-yellow-500',
        'info': 'bg-blue-500'
    };
    
    const icons = {
        'success': '✓',
        'error': '✕',
        'warning': '⚠',
        'info': 'ℹ'
    };
    
    const toast = document.createElement('div');
    toast.className = `${colors[type]} text-white px-6 py-3 rounded-xl shadow-lg mb-3 flex items-center gap-3 animate-slide-in`;
    toast.innerHTML = `
        <span class="text-xl">${icons[type]}</span>
        <span>${message}</span>
    `;
    
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('animate-slide-out');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/**
 * 创建Toast容器
 */
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'fixed top-4 right-4 z-50';
    document.body.appendChild(container);
    return container;
}

/**
 * 创建加载骨架屏
 */
function createSkeleton(type = 'card') {
    if (type === 'card') {
        return `
            <div class="bg-white rounded-2xl p-6 border border-gray-200 animate-pulse">
                <div class="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                <div class="h-3 bg-gray-200 rounded w-full mb-2"></div>
                <div class="h-3 bg-gray-200 rounded w-5/6"></div>
            </div>
        `;
    }
    return '';
}

/**
 * 格式化时间
 */
function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

/**
 * 格式化日期
 */
function formatDate(date) {
    const now = new Date();
    const diff = now - date;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) return `${days}天前`;
    if (hours > 0) return `${hours}小时前`;
    if (minutes > 0) return `${minutes}分钟前`;
    return '刚刚';
}

/**
 * 动画工具函数
 */
const AnimationUtils = {
    // 淡入
    fadeIn(element, duration = 300) {
        element.style.opacity = 0;
        element.style.transition = `opacity ${duration}ms`;
        setTimeout(() => element.style.opacity = 1, 10);
    },
    
    // 淡出
    fadeOut(element, duration = 300) {
        element.style.opacity = 1;
        element.style.transition = `opacity ${duration}ms`;
        element.style.opacity = 0;
        return new Promise(resolve => setTimeout(resolve, duration));
    },
    
    // 滑入
    slideIn(element, direction = 'bottom', duration = 300) {
        const transforms = {
            'top': 'translateY(-100%)',
            'bottom': 'translateY(100%)',
            'left': 'translateX(-100%)',
            'right': 'translateX(100%)'
        };
        
        element.style.transform = transforms[direction];
        element.style.transition = `transform ${duration}ms`;
        setTimeout(() => element.style.transform = 'translate(0, 0)', 10);
    }
};

/**
 * 本地存储工具
 */
const Storage = {
    get(key, defaultValue = null) {
        try {
            const value = localStorage.getItem(key);
            return value ? JSON.parse(value) : defaultValue;
        } catch {
            return defaultValue;
        }
    },
    
    set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch {
            return false;
        }
    },
    
    remove(key) {
        localStorage.removeItem(key);
    },
    
    clear() {
        localStorage.clear();
    }
};

