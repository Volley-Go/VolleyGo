/**
 * 辅助页面渲染模块
 * 包含排行榜、个人资料、设置等页面
 */

/**
 * 渲染排行榜页面
 */
function renderLeaderboardPage() {
    const container = document.getElementById('page-content');
    
    // 模拟排行榜数据
    const leaderboard = [
        { rank: 1, name: '李明', badge: '👑 王者', stars: 856, days: 15, avatar: '🥇' },
        { rank: 2, name: '王芳', badge: '⚡ 大师', stars: 742, days: 22, avatar: '🥈' },
        { rank: 3, name: '张伟', badge: '⚡ 大师', stars: 658, days: 8, avatar: '🥉' },
        { rank: 4, name: '刘洋', badge: '💠 钻石', stars: 523, days: 12, avatar: '👤' },
        { rank: 5, name: '陈静', badge: '💠 钻石', stars: 445, days: 5, avatar: '👤' },
        { rank: 6, name: '你', badge: '💎 铂金', stars: 320, days: 7, avatar: '⭐', highlight: true }
    ];
    
    container.innerHTML = `
        ${renderHeader()}
        
        <div class="p-4 pb-24">
            <!-- 你的进度卡片 -->
            <div class="gradient-orange text-white rounded-2xl p-6 mb-6 shadow-lg">
                <div class="flex justify-between items-start mb-4">
                    <div class="flex-1">
                        <p class="text-sm opacity-90 mb-1">你的进度</p>
                        <div class="flex items-center gap-3 mb-2">
                            <span class="text-4xl">💎</span>
                            <div>
                                <p class="text-2xl font-bold">铂金</p>
                                <p class="text-sm opacity-75">还需 29 ⭐ 升级</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="text-right">
                        <p class="text-sm opacity-75 mb-1">当前排名</p>
                        <div class="flex items-center gap-2">
                            <span class="text-3xl">🏆</span>
                            <span class="text-4xl font-bold">#6</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 排行榜列表 -->
            <div class="space-y-3">
                ${leaderboard.map(user => `
                    <div class="${user.highlight ? 'bg-blue-50 border-blue-300' : 'bg-yellow-50 border-yellow-200'} border-2 rounded-2xl p-5 shadow-sm ${user.highlight ? 'ring-2 ring-blue-400' : ''}">
                        <div class="flex items-center gap-4">
                            <!-- 排名 -->
                            <div class="text-3xl font-bold ${user.rank <= 3 ? 'text-yellow-500' : 'text-gray-600'}">
                                ${user.rank <= 3 ? user.avatar : `#${user.rank}`}
                            </div>
                            
                            <!-- 用户信息 -->
                            <div class="flex-1">
                                <div class="flex items-center gap-3 mb-2">
                                    <h3 class="text-lg font-semibold text-gray-800">
                                        ${user.name}
                                        ${user.highlight ? '<span class="ml-2 px-2 py-1 bg-blue-500 text-white text-xs rounded-lg">你</span>' : ''}
                                    </h3>
                                </div>
                                <div class="flex items-center gap-3 text-sm">
                                    <span class="px-3 py-1 ${
                                        user.badge.includes('王者') ? 'bg-gradient-to-r from-red-500 to-orange-500' :
                                        user.badge.includes('大师') ? 'bg-gradient-to-r from-purple-500 to-pink-500' :
                                        user.badge.includes('钻石') ? 'bg-gradient-to-r from-blue-400 to-purple-500' :
                                        'bg-gradient-to-r from-cyan-400 to-blue-400'
                                    } text-white rounded-lg font-medium">
                                        ${user.badge}
                                    </span>
                                    <span class="text-gray-600 flex items-center gap-1">
                                        <span>⏱️</span> ${user.days}天
                                    </span>
                                </div>
                            </div>
                            
                            <!-- 星星数 -->
                            <div class="text-right">
                                <div class="flex items-center gap-2">
                                    <span class="text-2xl">⭐</span>
                                    <span class="text-2xl font-bold text-yellow-500">${user.stars}</span>
                                </div>
                            </div>
                            
                            <!-- 头像 -->
                            <div class="w-12 h-12 bg-white rounded-full shadow-md flex items-center justify-center">
                                ${user.rank <= 3 ? user.avatar : '👤'}
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
        
        ${renderBottomNav()}
    `;
}

/**
 * 渲染个人资料页面
 */
function renderProfilePage() {
    const container = document.getElementById('page-content');
    
    container.innerHTML = `
        ${renderHeader()}
        
        <div class="p-4 pb-24">
            <!-- 个人信息卡片 -->
            <div class="gradient-orange text-white rounded-2xl p-8 mb-6 shadow-lg relative overflow-hidden">
                <!-- 背景装饰 -->
                <div class="absolute inset-0 opacity-10">
                    <div class="absolute top-0 right-0 w-64 h-64 bg-white rounded-full -translate-y-32 translate-x-32"></div>
                </div>
                
                <div class="relative">
                    <div class="flex items-start gap-6 mb-6">
                        <div class="w-20 h-20 bg-white bg-opacity-20 rounded-full border-4 border-white shadow-xl"></div>
                        <div class="flex-1">
                            <h2 class="text-3xl font-bold mb-1">${AppState.user.username}</h2>
                            <p class="text-white text-opacity-90 mb-3">guest</p>
                            <span class="inline-block px-4 py-1.5 bg-gradient-to-r from-yellow-700 to-yellow-900 rounded-lg text-sm font-medium">
                                🥉 ${AppState.user.rank}
                            </span>
                        </div>
                    </div>
                    
                    <!-- 段位进度 -->
                    <div class="bg-white bg-opacity-20 border border-white border-opacity-30 rounded-xl p-4">
                        <div class="flex justify-between text-sm mb-2">
                            <span>段位进度</span>
                            <span>${AppState.user.stars} / 49 ⭐</span>
                        </div>
                        <div class="flex justify-between text-xs mb-2">
                            <span>青铜</span>
                            <span>→</span>
                            <span>白银 🥈</span>
                        </div>
                        <div class="w-full h-2 bg-white bg-opacity-20 rounded-full">
                            <div class="h-2 bg-gradient-to-r from-volleyball-orange to-volleyball-dark-orange rounded-full" 
                                 style="width: ${(AppState.user.stars / 49 * 100).toFixed(0)}%"></div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 功能标签 -->
            <div class="bg-gray-100 bg-opacity-50 border border-gray-200 rounded-2xl p-1 flex mb-6">
                <button onclick="showProfileTab('rank')" 
                        id="profile-tab-rank"
                        class="flex-1 py-3 rounded-xl font-medium transition-all bg-white text-volleyball-orange shadow-sm">
                    <span class="mr-2">🏆</span>
                    段位进阶
                </button>
                <button onclick="showProfileTab('stats')" 
                        id="profile-tab-stats"
                        class="flex-1 py-3 rounded-xl font-medium transition-all text-gray-600">
                    <span class="mr-2">📊</span>
                    统计
                </button>
                <button onclick="showProfileTab('achievements')" 
                        id="profile-tab-achievements"
                        class="flex-1 py-3 rounded-xl font-medium transition-all text-gray-600">
                    <span class="mr-2">🏅</span>
                    成就
                </button>
            </div>
            
            <!-- 标签内容 -->
            <div id="profile-tab-content"></div>
        </div>
        
        ${renderBottomNav()}
    `;
    
    // 默认显示段位进阶
    showProfileTab('rank');
}

/**
 * 显示个人资料标签
 */
function showProfileTab(tabName) {
    // 更新标签按钮样式
    document.querySelectorAll('[id^="profile-tab-"]').forEach(btn => {
        btn.classList.remove('bg-white', 'text-volleyball-orange', 'shadow-sm');
        btn.classList.add('text-gray-600');
    });
    
    const activeTab = document.getElementById(`profile-tab-${tabName}`);
    activeTab.classList.add('bg-white', 'text-volleyball-orange', 'shadow-sm');
    activeTab.classList.remove('text-gray-600');
    
    // 渲染对应内容
    const contentDiv = document.getElementById('profile-tab-content');
    
    if (tabName === 'rank') {
        contentDiv.innerHTML = renderRankProgression();
    } else if (tabName === 'stats') {
        contentDiv.innerHTML = renderStats();
    } else if (tabName === 'achievements') {
        contentDiv.innerHTML = renderAchievements();
    }
}

/**
 * 渲染段位进阶
 */
function renderRankProgression() {
    const ranks = [
        { name: '青铜', emoji: '🥉', stars: '0 - 49', color: 'yellow', current: true },
        { name: '白银', emoji: '🥈', stars: '50 - 99', color: 'gray' },
        { name: '黄金', emoji: '🥇', stars: '100 - 199', color: 'yellow' },
        { name: '铂金', emoji: '💎', stars: '200 - 349', color: 'cyan' },
        { name: '钻石', emoji: '💠', stars: '350 - 549', color: 'blue' },
        { name: '大师', emoji: '⚡', stars: '550 - 799', color: 'purple' },
        { name: '王者', emoji: '👑', stars: '800+', color: 'red' }
    ];
    
    return `
        <div class="space-y-4">
            ${ranks.map((rank, idx) => `
                <div class="${rank.current ? 'bg-gradient-to-r from-yellow-50 to-orange-50 border-2 border-orange-300 shadow-lg' : 'bg-gray-50 border border-gray-200'} rounded-2xl p-5">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-4">
                            <div class="w-16 h-16 bg-gradient-to-br ${
                                rank.color === 'yellow' ? 'from-yellow-400 to-yellow-600' :
                                rank.color === 'gray' ? 'from-gray-300 to-gray-500' :
                                rank.color === 'cyan' ? 'from-cyan-400 to-cyan-600' :
                                rank.color === 'blue' ? 'from-blue-400 to-blue-600' :
                                rank.color === 'purple' ? 'from-purple-400 to-purple-600' :
                                'from-red-400 to-red-600'
                            } rounded-full flex items-center justify-center shadow-lg ${!rank.current ? 'opacity-50' : ''}">
                                <span class="text-3xl">${rank.emoji}</span>
                            </div>
                            <div>
                                <div class="flex items-center gap-2">
                                    <h3 class="text-xl font-semibold ${rank.current ? 'text-gray-800' : 'text-gray-500'}">
                                        ${rank.name}
                                    </h3>
                                    ${rank.current ? '<span class="px-3 py-1 bg-volleyball-orange text-white rounded-lg text-xs font-medium">进行中</span>' : ''}
                                </div>
                                <p class="text-sm text-gray-600 flex items-center gap-1 mt-1">
                                    <span>⭐</span> ${rank.stars} 星
                                </p>
                                ${rank.current ? `
                                    <div class="mt-2">
                                        <div class="w-64 h-2 bg-white bg-opacity-20 rounded-full">
                                            <div class="h-2 bg-gradient-to-r from-volleyball-orange to-volleyball-dark-orange rounded-full" 
                                                 style="width: ${(AppState.user.stars / 49 * 100).toFixed(0)}%"></div>
                                        </div>
                                        <p class="text-xs mt-1 opacity-75">${AppState.user.stars} / 49 ⭐ (还需 ${49 - AppState.user.stars} 星)</p>
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                        
                        ${!rank.current ? `
                            <div class="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center opacity-40">
                                <span class="text-2xl">${rank.emoji}</span>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `).join('')}
            
            <!-- 奖励说明 -->
            <div class="bg-gradient-to-br from-orange-50 to-yellow-50 border border-orange-200 rounded-2xl p-6 mt-8">
                <div class="text-center">
                    <div class="text-5xl mb-3">🏆</div>
                    <h3 class="text-xl font-bold text-gray-800 mb-2">排球传奇之路</h3>
                    <p class="text-sm text-gray-600">持续训练，成为王者！</p>
                </div>
            </div>
        </div>
    `;
}

/**
 * 渲染统计数据
 */
function renderStats() {
    return `
        <div class="grid grid-cols-2 gap-4 mb-6">
            <div class="bg-white border border-gray-200 rounded-2xl p-6">
                <div class="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center mb-3">
                    <span class="text-2xl">⏱️</span>
                </div>
                <div class="text-3xl font-bold text-gray-800 mb-1">12.5 小时</div>
                <p class="text-sm text-gray-600">总训练时长</p>
            </div>
            
            <div class="bg-white border border-gray-200 rounded-2xl p-6">
                <div class="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-3">
                    <span class="text-2xl">✅</span>
                </div>
                <div class="text-3xl font-bold text-gray-800 mb-1">32 个</div>
                <p class="text-sm text-gray-600">完成挑战</p>
            </div>
            
            <div class="bg-white border border-gray-200 rounded-2xl p-6">
                <div class="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center mb-3">
                    <span class="text-2xl">🔥</span>
                </div>
                <div class="text-3xl font-bold text-gray-800 mb-1">7 天</div>
                <p class="text-sm text-gray-600">连续打卡</p>
            </div>
            
            <div class="bg-white border border-gray-200 rounded-2xl p-6">
                <div class="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mb-3">
                    <span class="text-2xl">💯</span>
                </div>
                <div class="text-3xl font-bold text-gray-800 mb-1">85 分</div>
                <p class="text-sm text-gray-600">平均评分</p>
            </div>
        </div>
        
        <!-- 最近活动 -->
        <div class="mt-6">
            <h3 class="text-lg font-semibold mb-4 flex items-center gap-2">
                <span>📅</span>
                最近活动
            </h3>
            
            <div class="space-y-3">
                ${[
                    { activity: '完成传球基础训练', time: '今天', icon: '✓' },
                    { activity: '完成扣球技巧训练', time: '今天', icon: '✓' },
                    { activity: '完成发球练习', time: '昨天', icon: '✓' },
                    { activity: '完成防守站位训练', time: '昨天', icon: '✓' }
                ].map(item => `
                    <div class="bg-gray-50 border border-gray-200 rounded-xl p-4 flex items-center justify-between">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 bg-yellow-400 rounded-full flex items-center justify-center">
                                <span class="text-white font-bold">${item.icon}</span>
                            </div>
                            <div>
                                <p class="text-gray-800 font-medium">${item.activity}</p>
                                <p class="text-xs text-gray-500">${item.time}</p>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

/**
 * 渲染成就系统
 */
function renderAchievements() {
    const achievements = [
        { name: '初出茅庐', description: '完成第一个挑战', icon: '🎯', unlocked: true, progress: null },
        { name: '星光璀璨', description: '获得10颗星星', icon: '⭐', unlocked: true, progress: null },
        { name: '完美主义者', description: '获得一次满分（3星）', icon: '💯', unlocked: true, progress: null },
        { name: '坚持不懈', description: '连续训练7天', icon: '🔥', unlocked: false, progress: '3 / 7' },
        { name: '全能选手', description: '解锁所有位置', icon: '🏐', unlocked: false, progress: '4 / 6' },
        { name: '训练狂人', description: '完成100个挑战', icon: '💪', unlocked: false, progress: '32 / 100' }
    ];
    
    return `
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            ${achievements.map(ach => `
                <div class="${ach.unlocked ? 'bg-gradient-to-br from-yellow-50 to-orange-50 border-orange-200' : 'bg-gray-50 border-gray-200'} border-2 rounded-2xl p-5">
                    <div class="flex items-start gap-4">
                        <div class="${ach.unlocked ? '' : 'opacity-50'}">
                            <div class="w-14 h-14 bg-gradient-to-br from-orange-400 to-orange-600 rounded-full flex items-center justify-center shadow-lg">
                                <span class="text-3xl">${ach.icon}</span>
                            </div>
                        </div>
                        <div class="flex-1">
                            <div class="flex items-center gap-2 mb-1">
                                <h4 class="text-lg font-semibold ${ach.unlocked ? 'text-gray-800' : 'text-gray-500'}">
                                    ${ach.name}
                                </h4>
                                ${ach.unlocked ? '<span class="px-2 py-1 bg-green-100 border border-green-200 rounded-lg text-xs text-green-700">已解锁</span>' : ''}
                            </div>
                            <p class="text-sm ${ach.unlocked ? 'text-gray-700' : 'text-gray-500'} mb-2">
                                ${ach.description}
                            </p>
                            
                            ${ach.progress ? `
                                <div>
                                    <div class="w-full h-2 bg-gray-200 rounded-full mb-1">
                                        <div class="h-2 bg-gradient-to-r from-volleyball-orange to-volleyball-dark-orange rounded-full" 
                                             style="width: ${parseInt(ach.progress.split('/')[0]) / parseInt(ach.progress.split('/')[1]) * 100}%"></div>
                                    </div>
                                    <p class="text-xs text-gray-500">${ach.progress}</p>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

/**
 * 渲染设置页面
 */
function renderSettingsPage() {
    const container = document.getElementById('page-content');
    
    container.innerHTML = `
        ${renderHeader()}
        
        <div class="p-4 pb-24">
            <div class="bg-gradient-to-r from-volleyball-blue to-volleyball-purple text-white rounded-2xl p-6 mb-6 shadow-lg">
                <div class="flex items-center gap-4">
                    <div class="w-16 h-16 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                        <span class="text-3xl">⚙️</span>
                    </div>
                    <div>
                        <h2 class="text-2xl font-bold">设置</h2>
                        <p class="text-sm opacity-90">管理你的应用偏好设置</p>
                    </div>
                </div>
            </div>
            
            <!-- 通用设置 -->
            <div class="mb-6">
                <h3 class="text-lg font-semibold mb-3 flex items-center gap-2">
                    <span>🔧</span>
                    通用设置
                </h3>
                
                <div class="bg-white border border-gray-200 rounded-2xl divide-y divide-gray-200">
                    <div class="p-4 flex items-center justify-between">
                        <div class="flex items-center gap-3">
                            <span class="text-2xl">🔔</span>
                            <div>
                                <p class="font-medium text-gray-800">推送通知</p>
                                <p class="text-xs text-gray-500">接收训练提醒和成就通知</p>
                            </div>
                        </div>
                        <label class="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" class="sr-only peer" checked>
                            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-volleyball-orange"></div>
                        </label>
                    </div>
                    
                    <div class="p-4 flex items-center justify-between">
                        <div class="flex items-center gap-3">
                            <span class="text-2xl">🔊</span>
                            <div>
                                <p class="font-medium text-gray-800">音效</p>
                                <p class="text-xs text-gray-500">播放操作音效和背景音乐</p>
                            </div>
                        </div>
                        <label class="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" class="sr-only peer" checked>
                            <div class="w-11 h-6 bg-gray-200 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-volleyball-orange"></div>
                        </label>
                    </div>
                    
                    <div class="p-4 flex items-center justify-between">
                        <div class="flex items-center gap-3">
                            <span class="text-2xl">🌙</span>
                            <div>
                                <p class="font-medium text-gray-800">深色模式</p>
                                <p class="text-xs text-gray-500">切换到深色主题</p>
                            </div>
                        </div>
                        <label class="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" class="sr-only peer">
                            <div class="w-11 h-6 bg-gray-300 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-gray-700"></div>
                        </label>
                    </div>
                </div>
            </div>
            
            <!-- 视频设置 -->
            <div class="mb-6">
                <h3 class="text-lg font-semibold mb-3 flex items-center gap-2">
                    <span>🎥</span>
                    视频设置
                </h3>
                
                <div class="bg-white border border-gray-200 rounded-2xl p-4">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-3">
                            <span class="text-xl">▶️</span>
                            <div>
                                <p class="font-medium text-gray-800">自动播放演示</p>
                                <p class="text-xs text-gray-500">查看挑战时自动播放动作演示</p>
                            </div>
                        </div>
                        <label class="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" class="sr-only peer" checked>
                            <div class="w-11 h-6 bg-gray-200 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-volleyball-orange"></div>
                        </label>
                    </div>
                </div>
            </div>
            
            <!-- 语言与地区 -->
            <div class="mb-6">
                <h3 class="text-lg font-semibold mb-3 flex items-center gap-2">
                    <span>🌍</span>
                    语言与地区
                </h3>
                
                <div class="bg-white border border-gray-200 rounded-2xl p-4">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-3">
                            <span class="text-2xl">🈯</span>
                            <div>
                                <p class="font-medium text-gray-800">语言</p>
                                <p class="text-xs text-gray-500">简体中文</p>
                            </div>
                        </div>
                        <span class="text-gray-400">→</span>
                    </div>
                </div>
            </div>
            
            <!-- 隐私与安全 -->
            <div class="mb-6">
                <h3 class="text-lg font-semibold mb-3 flex items-center gap-2">
                    <span>🔒</span>
                    隐私与安全
                </h3>
                
                <div class="bg-white border border-gray-200 rounded-2xl divide-y divide-gray-200">
                    <button class="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-all">
                        <div class="flex items-center gap-3">
                            <span class="text-2xl">📄</span>
                            <p class="font-medium text-gray-800">隐私政策</p>
                        </div>
                        <span class="text-gray-400">→</span>
                    </button>
                    
                    <button class="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-all">
                        <div class="flex items-center gap-3">
                            <span class="text-2xl">📋</span>
                            <div>
                                <p class="font-medium text-gray-800">用户协议</p>
                            </div>
                        </div>
                        <span class="text-gray-400">→</span>
                    </button>
                </div>
            </div>
            
            <!-- 帮助与支持 -->
            <div class="mb-6">
                <h3 class="text-lg font-semibold mb-3 flex items-center gap-2">
                    <span>❓</span>
                    帮助与支持
                </h3>
                
                <div class="bg-white border border-gray-200 rounded-2xl divide-y divide-gray-200">
                    <button class="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-all">
                        <div class="flex items-center gap-3">
                            <span class="text-2xl">📖</span>
                            <p class="font-medium text-gray-800">帮助中心</p>
                        </div>
                        <span class="text-gray-400">→</span>
                    </button>
                    
                    <button class="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-all">
                        <div class="flex items-center gap-3">
                            <span class="text-2xl">ℹ️</span>
                            <div>
                                <p class="font-medium text-gray-800">关于</p>
                                <p class="text-xs text-gray-500">版本 1.0.0</p>
                            </div>
                        </div>
                        <span class="text-gray-400">→</span>
                    </button>
                </div>
            </div>
            
            <!-- 退出登录 -->
            <div class="border-t border-gray-200 pt-6">
                <button onclick="logout()" 
                        class="w-full py-3 border-2 border-red-200 text-red-600 rounded-xl font-semibold hover:bg-red-50 transition-all flex items-center justify-center gap-2">
                    <span>🚪</span>
                    退出登录
                </button>
            </div>
        </div>
    `;
}

/**
 * 退出登录
 */
function logout() {
    if (confirm('确定要退出登录吗？')) {
        // 清除本地存储
        Storage.clear();
        
        // 重置应用状态
        AppState.onboardingStep = 0;
        AppState.showOnboarding = true;
        
        showToast('已退出登录', 'info');
        
        // 返回新手引导
        setTimeout(() => {
            initApp();
        }, 1000);
    }
}

