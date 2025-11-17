/**
 * 主应用逻辑
 * 管理页面状态和路由
 */

// 应用状态管理
const AppState = {
    // 用户信息
    user: {
        username: 'guest',
        level: 1,
        xp: 0,
        rank: '青铜',
        stars: 0,
        mainPosition: '自由人'
    },
    
    // 当前页面
    currentPage: 'home',
    
    // 新手引导状态
    onboardingStep: 0,
    showOnboarding: true,
    
    // 当前选中的位置
    selectedPosition: 'libero',
    
    // 分析结果
    analysisResult: null,
    
    // 战术测试
    tacticsTest: {
        started: false,
        currentQuestion: 0,
        answers: [],
        questions: [],
        currentModule: null
    },

    // 解锁的战术学习模块
    unlockedTactics: ['基础轮转规则'],
    
    // AI教练对话历史
    aiCoachChat: []
};

/**
 * 初始化应用
 */
async function initApp() {
    // 检查后端API健康状态
    const health = await api.healthCheck();
    console.log('API状态:', health);
    
    // 加载战术题库
    const tacticsData = await api.getTacticsQuestions();
    if (!tacticsData.error) {
        AppState.tacticsTest.allQuestions = tacticsData.questions || [];
    }
    
    // 检查是否已经完成新手引导
    const hasCompletedOnboarding = localStorage.getItem('onboarding_completed');
    if (hasCompletedOnboarding) {
        AppState.showOnboarding = false;
        renderMainPage();
    } else {
        // 首次进入显示全屏欢迎界面
        renderWelcomeScreen();
    }
}

/**
 * 渲染全屏欢迎界面
 */
function renderWelcomeScreen() {
    const container = document.getElementById('page-content');
    
    container.innerHTML = `
        <div class="fixed inset-0 gradient-bg flex items-center justify-center z-50 overflow-hidden">
            <!-- 背景装饰 -->
            <div class="absolute inset-0 overflow-hidden">
                <div class="absolute top-0 right-0 w-96 h-96 bg-volleyball-orange opacity-10 rounded-full blur-3xl transform translate-x-32 -translate-y-32"></div>
                <div class="absolute bottom-0 left-0 w-96 h-96 bg-volleyball-blue opacity-10 rounded-full blur-3xl transform -translate-x-32 translate-y-32"></div>
            </div>
            
            <!-- 主要内容 -->
            <div class="relative z-10 max-w-4xl w-full px-6 py-12 text-center animate-fade-in">
                <!-- Logo/图标 -->
                <div class="mb-8 animate-bounce-slow">
                    <div class="w-32 h-32 mx-auto bg-gradient-to-br from-volleyball-orange to-volleyball-dark-orange rounded-full flex items-center justify-center shadow-2xl">
                        <span class="text-7xl">🏐</span>
                    </div>
                </div>
                
                <!-- 标题 -->
                <h1 class="text-6xl md:text-7xl font-bold text-gray-800 mb-4 animate-slide-down">
                    排球冒险
                </h1>
                <p class="text-2xl md:text-3xl text-gray-600 mb-12 animate-slide-up">
                    AI 助力你的排球训练之旅
                </p>
                
                <!-- 特色功能卡片 -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12 animate-fade-in-delay">
                    <div class="bg-white bg-opacity-90 rounded-2xl p-6 shadow-xl hover-lift transition-all border-2 border-orange-100">
                        <div class="text-5xl mb-4">📹</div>
                        <h3 class="text-xl font-semibold mb-2 text-gray-800">AI动作识别</h3>
                        <p class="text-gray-600 text-sm">实时分析训练视频，专业反馈指导</p>
                    </div>
                    <div class="bg-white bg-opacity-90 rounded-2xl p-6 shadow-xl hover-lift transition-all border-2 border-blue-100">
                        <div class="text-5xl mb-4">🎯</div>
                        <h3 class="text-xl font-semibold mb-2 text-gray-800">技能树系统</h3>
                        <p class="text-gray-600 text-sm">系统化学习，从基础到高级</p>
                    </div>
                    <div class="bg-white bg-opacity-90 rounded-2xl p-6 shadow-xl hover-lift transition-all border-2 border-purple-100">
                        <div class="text-5xl mb-4">🏆</div>
                        <h3 class="text-xl font-semibold mb-2 text-gray-800">成长激励</h3>
                        <p class="text-gray-600 text-sm">星级评分、段位晋升、排行榜</p>
                    </div>
                </div>
                
                <!-- 开始按钮 -->
                <button onclick="startOnboarding()" 
                        class="px-12 py-4 bg-gradient-to-r from-volleyball-orange to-volleyball-dark-orange text-white text-xl font-bold rounded-full shadow-2xl hover:shadow-3xl transition-all transform hover:scale-105 animate-pulse-slow">
                    🚀 开始冒险
                </button>
                
                <!-- 底部提示 -->
                <p class="mt-8 text-gray-500 text-sm animate-fade-in-delay-2">
                    💡 首次使用将为您进行简单引导
                </p>
            </div>
        </div>
    `;
}

/**
 * 开始引导流程
 */
function startOnboarding() {
    AppState.onboardingStep = 0;
    renderOnboarding();
}

/**
 * 渲染新手引导
 */
function renderOnboarding() {
    const container = document.getElementById('page-content');
    const step = AppState.onboardingStep;
    
    const steps = [
        {
            emoji: '🏐',
            title: '欢迎来到排球冒险！',
            description: '通过AI动作识别和战术学习，成为排球大师',
            content: `
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="bg-white bg-opacity-80 border border-orange-100 rounded-2xl p-6 hover-lift transition-all">
                        <div class="text-5xl mb-4">📹</div>
                        <h3 class="text-xl font-semibold mb-2 text-gray-800">AI动作识别</h3>
                        <p class="text-gray-600 text-sm">上传训练视频，AI实时分析你的动作，给出专业反馈</p>
                    </div>
                    <div class="bg-white bg-opacity-80 border border-orange-100 rounded-2xl p-6 hover-lift transition-all">
                        <div class="text-5xl mb-4">🎯</div>
                        <h3 class="text-xl font-semibold mb-2 text-gray-800">技能树系统</h3>
                        <p class="text-gray-600 text-sm">从基础到高级，系统化学习排球技术</p>
                    </div>
                    <div class="bg-white bg-opacity-80 border border-orange-100 rounded-2xl p-6 hover-lift transition-all">
                        <div class="text-5xl mb-4">🏆</div>
                        <h3 class="text-xl font-semibold mb-2 text-gray-800">成长激励</h3>
                        <p class="text-gray-600 text-sm">获得星级评分、段位晋升、排行榜竞争</p>
                    </div>
                </div>
            `
        },
        {
            emoji: '✨',
            title: '核心功能',
            description: '我们为你准备了完整的成长体系',
            content: `
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="bg-white bg-opacity-80 border-2 border-green-200 rounded-2xl p-6">
                        <div class="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center mb-4">
                            <span class="text-2xl">📚</span>
                        </div>
                        <h3 class="text-lg font-semibold mb-3 text-gray-800">基础阶段</h3>
                        <p class="text-sm text-gray-600 mb-3">所有位置通用的基础技能</p>
                        <ul class="text-sm text-gray-600 space-y-2">
                            <li>• 基本姿势与移动</li>
                            <li>• 发球、垫球、传球</li>
                            <li>• 扣球、拦网、防守</li>
                            <li>• 场上意识与沟通</li>
                        </ul>
                    </div>
                    
                    <div class="bg-white bg-opacity-80 border-2 border-blue-200 rounded-2xl p-6">
                        <div class="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-4">
                            <span class="text-2xl">🎯</span>
                        </div>
                        <h3 class="text-lg font-semibold mb-3 text-gray-800">专门技能</h3>
                        <p class="text-sm text-gray-600 mb-3">根据位置定制的专属技能</p>
                        <ul class="text-sm text-gray-600 space-y-2">
                            <li>• 主攻：四步助跑、后排进攻</li>
                            <li>• 接应：右侧强攻、反击扣球</li>
                            <li>• 副攻：快攻战术、拦网技术</li>
                            <li>• 二传：传球手型、战术组织</li>
                            <li>• 自由人：防守挖球、鱼跃救球</li>
                        </ul>
                    </div>
                    
                    <div class="bg-white bg-opacity-80 border-2 border-purple-200 rounded-2xl p-6">
                        <div class="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mb-4">
                            <span class="text-2xl">🏅</span>
                        </div>
                        <h3 class="text-lg font-semibold mb-3 text-gray-800">激励系统</h3>
                        <p class="text-sm text-gray-600 mb-3">游戏化元素让学习更有趣</p>
                        <ul class="text-sm text-gray-600 space-y-2">
                            <li>• 星级评价（1-3星）</li>
                            <li>• 段位系统（青铜到王者）</li>
                            <li>• 多邻国风格完成动效</li>
                            <li>• 排行榜竞争</li>
                        </ul>
                    </div>
                </div>
            `
        },
        {
            emoji: '🎯',
            title: '选择你的位置',
            description: '每个位置都有独特的技能树和成长路线',
            content: renderPositionSelection()
        },
        {
            emoji: '🗺️',
            title: '你的进阶之路',
            description: '查看你选择的位置的成长路线',
            content: renderProgressionPath()
        }
    ];
    
    const currentStep = steps[step];
    
    container.innerHTML = `
        <!-- 新手引导容器 -->
        <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-40 p-4">
            <div class="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                <!-- 顶部标题 -->
                <div class="sticky top-0 bg-white border-b border-gray-200 p-6 z-10">
                    <div class="flex justify-between items-start mb-2">
                        <div>
                            <h2 class="text-2xl font-bold text-gray-800 mb-1">
                                新手引导 - ${currentStep.title}
                            </h2>
                            <p class="text-sm text-gray-500">${currentStep.description}</p>
                        </div>
                        <button onclick="skipOnboarding()" 
                                class="text-gray-400 hover:text-gray-600 opacity-70">
                            ✕
                        </button>
                    </div>
                </div>
                
                <!-- 进度条 -->
                <div class="px-6 pt-4">
                    <div class="flex justify-between items-center mb-2">
                        <span class="text-sm text-gray-600">第 ${step + 1} 步，共 4 步</span>
                        <span class="text-sm text-gray-600">${Math.round((step + 1) / 4 * 100)}%</span>
                    </div>
                    <div class="w-full h-2 bg-gray-200 rounded-full">
                        <div class="h-2 bg-gradient-to-r from-volleyball-orange to-volleyball-dark-orange rounded-full transition-all duration-500" 
                             style="width: ${(step + 1) / 4 * 100}%"></div>
                    </div>
                </div>
                
                <!-- 内容区域 -->
                <div class="p-6" id="onboarding-content">
                    <div class="text-6xl text-center mb-6">${currentStep.emoji}</div>
                    ${currentStep.content}
                </div>
                
                <!-- 底部按钮 -->
                <div class="sticky bottom-0 bg-white border-t border-gray-200 p-6 flex justify-between items-center">
                    <button onclick="skipOnboarding()" 
                            class="px-6 py-2 text-gray-600 hover:text-gray-800 transition-all">
                        跳过引导
                    </button>
                    
                    <div class="flex gap-3">
                        ${step > 0 ? `
                            <button onclick="prevOnboardingStep()" 
                                    class="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-all">
                                上一步
                            </button>
                        ` : ''}
                        
                        <button onclick="${step < 3 ? 'nextOnboardingStep()' : 'completeOnboarding()'}" 
                                class="px-8 py-2 bg-gradient-to-r from-volleyball-orange to-volleyball-dark-orange text-white rounded-lg hover:shadow-lg transition-all ${step === 2 && !AppState.selectedPosition ? 'opacity-50 cursor-not-allowed' : ''}"
                                ${step === 2 && !AppState.selectedPosition ? 'disabled' : ''}>
                            ${step < 3 ? '下一步' : '开始冒险'}
                            ${step < 3 ? '→' : '🚀'}
                        </button>
                    </div>
                </div>
                
                <!-- 步骤指示器 -->
                <div class="flex justify-center gap-2 pb-6">
                    ${[0, 1, 2, 3].map(i => `
                        <div class="w-2 h-2 rounded-full ${i <= step ? 'bg-volleyball-orange' : 'bg-gray-300'}"></div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
    
    // 头像现在直接在HTML中使用src属性，不需要额外的setTimeout设置
}

/**
 * 位置选择渲染
 */
function renderPositionSelection() {
    console.log('开始渲染位置选择');
    const positions = [
        {
            id: 'outside',
            name: '主攻',
            difficulty: '中等',
            icon: '🏐',
            avatar: 'https://api.dicebear.com/7.x/avataaars-neutral/svg?seed=hitter&backgroundColor=0ea5e9',
            features: ['全面发展', '攻防兼备', '核心得分手']
        },
        {
            id: 'middle',
            name: '副攻',
            difficulty: '中等',
            icon: '⚡',
            avatar: 'https://api.dicebear.com/7.x/avataaars-neutral/svg?seed=middle&backgroundColor=10b981',
            features: ['防线支柱', '快攻先锋', '拦网专家']
        },
        {
            id: 'setter',
            name: '二传',
            difficulty: '较难',
            icon: '🎯',
            avatar: 'https://api.dicebear.com/7.x/avataaars-neutral/svg?seed=setter&backgroundColor=ffa500',
            features: ['球队大脑', '战术指挥', '节奏控制']
        },
        {
            id: 'opposite',
            name: '接应',
            difficulty: '较难',
            icon: '💪',
            avatar: 'https://api.dicebear.com/7.x/avataaars-neutral/svg?seed=opposite&backgroundColor=f59e0b',
            features: ['终结者', '强力进攻', '单拦核心']
        },
        {
            id: 'libero',
            name: '自由人',
            difficulty: '中等',
            icon: '🛡️',
            avatar: 'https://api.dicebear.com/7.x/avataaars-neutral/svg?seed=libero&backgroundColor=3b82f6',
            features: ['防守专家', '接发球核心', '防线指挥']
        },
        {
            id: 'defensive',
            name: '防守队员',
            difficulty: '较易',
            icon: '🎨',
            avatar: 'https://api.dicebear.com/7.x/avataaars-neutral/svg?seed=defender&backgroundColor=14b8a6',
            features: ['后排防守', '接发球', '团队支援']
        }
    ];
    
    // 调试：输出第一个位置的avatar URL
    if (positions.length > 0) {
        console.log('第一个位置头像URL:', positions[0].avatar);
    }
    
    const htmlString = `
        <div class="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6" id="position-selection-grid">
            ${positions.map((pos, index) => `
                <div onclick="selectPosition('${pos.id}')" 
                     class="bg-white border-2 rounded-2xl p-6 cursor-pointer hover-lift transition-all ${AppState.selectedPosition === pos.id ? 'border-volleyball-orange' : 'border-gray-200'}">
                    <div class="w-16 h-16 mb-3 mx-auto rounded-full overflow-hidden border-2 border-gray-200" style="background-color: #f3f4f6; min-width: 64px; min-height: 64px;">
                        <img src="${pos.avatar}" alt="${pos.name}" style="width: 100%; height: 100%; object-fit: cover; display: block;" />
                    </div>
                    <h3 class="text-lg font-semibold mb-2">${pos.name}</h3>
                    <div class="flex items-center gap-2 mb-3">
                        <span class="text-3xl">📊</span>
                        <span class="px-3 py-1 border border-gray-300 rounded-lg text-xs">${pos.difficulty}</span>
                    </div>
                    <div class="space-y-2">
                        ${pos.features.map(feature => `
                            <div class="flex items-center gap-2 text-sm text-gray-600">
                                <span class="text-green-500">✓</span>
                                <span>${feature}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `).join('')}
        </div>
        
        ${!AppState.selectedPosition ? `
            <div class="bg-yellow-50 border border-yellow-200 rounded-2xl p-4 flex items-start gap-3">
                <span class="text-2xl">💡</span>
                <p class="text-sm text-gray-700">请选择一个位置继续。不用担心，你可以随时尝试其他位置！</p>
            </div>
        ` : ''}
    `;
    
    // 调试：检查生成的HTML中是否包含头像URL
    if (htmlString.includes('api.dicebear.com')) {
        console.log('✅ HTML中包含DiceBear URL');
    } else {
        console.error('❌ HTML中未找到DiceBear URL');
    }
    
    return htmlString;
}

/**
 * 进阶路线渲染
 */
function renderProgressionPath() {
    if (!AppState.selectedPosition) {
        return `<div class="text-center text-gray-500">请先选择一个位置</div>`;
    }
    
    const positionNames = {
        'outside': '主攻手',
        'middle': '副攻手',
        'setter': '二传手',
        'opposite': '接应二传',
        'libero': '自由人',
        'defensive': '防守队员'
    };
    
    return `
        <div class="space-y-6">
            <div class="bg-white rounded-xl p-6 flex items-center gap-4">
                <div class="text-5xl">💎</div>
                <div>
                    <div class="text-sm text-gray-500">你选择了</div>
                    <div class="text-2xl font-bold text-gray-800">${positionNames[AppState.selectedPosition]}</div>
                </div>
            </div>
            
            <div class="bg-gradient-to-br from-green-50 to-green-100 border border-green-200 rounded-2xl p-6">
                <div class="flex items-start gap-3 mb-4">
                    <span class="text-2xl">🎯</span>
                    <h3 class="text-xl font-semibold text-gray-800">战术角色</h3>
                </div>
                <p class="text-gray-700 mb-4">球队"防线支柱 + 快攻先锋"，在前排承担拦网中枢与快攻突袭点</p>
                
                <div class="space-y-2">
                    <div class="flex items-start gap-2">
                        <span class="text-green-600">✓</span>
                        <span class="text-sm text-gray-700">进攻：执行快攻战术、吸引拦网</span>
                    </div>
                    <div class="flex items-start gap-2">
                        <span class="text-green-600">✓</span>
                        <span class="text-sm text-gray-700">防守：前排拦网核心，判断对方二传意图</span>
                    </div>
                    <div class="flex items-start gap-2">
                        <span class="text-green-600">✓</span>
                        <span class="text-sm text-gray-700">协作：与二传紧密沟通节奏；掩护主攻或接应</span>
                    </div>
                </div>
            </div>
            
            <div class="grid grid-cols-2 gap-4">
                <div class="bg-gradient-to-br from-green-50 to-green-100 border-2 border-green-300 rounded-2xl p-6">
                    <div class="flex items-center justify-between mb-3">
                        <div class="flex items-center gap-2">
                            <span class="text-2xl">📚</span>
                            <h4 class="font-semibold">基础阶段</h4>
                        </div>
                        <span class="text-2xl font-bold text-green-600">0%</span>
                    </div>
                    <p class="text-sm text-gray-600">8 个技能分类</p>
                    <div class="mt-2 flex flex-wrap gap-2">
                        ${['基本姿势与移动', '发球技术', '垫球技术', '传球技术'].map(skill => `
                            <span class="inline-flex items-center gap-1 px-2 py-1 bg-white rounded-lg text-xs">
                                <span class="w-1.5 h-1.5 bg-green-500 rounded-full"></span>
                                ${skill}
                            </span>
                        `).join('')}
                        <span class="text-xs text-gray-500">...还有 4 个分类</span>
                    </div>
                </div>
                
                <div class="bg-gradient-to-br from-blue-50 to-blue-100 border-2 border-blue-300 rounded-2xl p-6">
                    <div class="flex items-center justify-between mb-3">
                        <div class="flex items-center gap-2">
                            <span class="text-2xl">🎯</span>
                            <h4 class="font-semibold">专属技能</h4>
                        </div>
                        <span class="text-2xl font-bold text-blue-600">0%</span>
                    </div>
                    <p class="text-sm text-gray-600">3 个技能分类</p>
                    <div class="mt-2 flex flex-wrap gap-2">
                        ${['快攻技术', '拦网技术', '战术配合'].map(skill => `
                            <span class="inline-flex items-center gap-1 px-2 py-1 bg-white rounded-lg text-xs">
                                <span class="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
                                ${skill}
                            </span>
                        `).join('')}
                    </div>
                </div>
            </div>
            
            <div class="bg-yellow-50 border border-yellow-200 rounded-2xl p-5">
                <div class="flex items-start gap-3">
                    <span class="text-2xl">💡</span>
                    <div>
                        <h4 class="font-semibold text-yellow-900 mb-2">准备好了吗？</h4>
                        <p class="text-sm text-yellow-800">点击"开始冒险"，立即开始你的排球成长之旅！完成挑战获得星星，解锁更多技能。</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

/**
 * 选择位置
 */
function selectPosition(positionId) {
    AppState.selectedPosition = positionId;
    AppState.user.mainPosition = positionId;

    if (AppState.showOnboarding) {
        renderOnboarding();
    } else {
        renderMainPage();
    }
}

/**
 * 下一步引导
 */
function nextOnboardingStep() {
    if (AppState.onboardingStep < 3) {
        AppState.onboardingStep++;
        renderOnboarding();
    }
}

/**
 * 上一步引导
 */
function prevOnboardingStep() {
    if (AppState.onboardingStep > 0) {
        AppState.onboardingStep--;
        renderOnboarding();
    }
}

/**
 * 跳过新手引导
 */
function skipOnboarding() {
    if (confirm('确定要跳过新手引导吗？')) {
        completeOnboarding();
    }
}

/**
 * 完成新手引导
 */
function completeOnboarding() {
    localStorage.setItem('onboarding_completed', 'true');
    AppState.showOnboarding = false;
    renderMainPage();
}

/**
 * 渲染主页面
 */
function renderMainPage() {
    const container = document.getElementById('page-content');
    
    container.innerHTML = `
        <!-- 顶部用户信息栏 -->
        ${renderHeader()}
        
        <!-- 主内容区域 -->
        <div class="p-4 space-y-6">
            <!-- 排球场位置模块 -->
            ${renderVolleyballCourt()}
            
            <!-- 功能标签页 -->
            ${renderMainTabs()}
        </div>
        
        <!-- 底部导航栏 -->
        ${renderBottomNav()}
    `;
    
    // 默认选中战术学习标签
    showTab('tactics');
}

/**
 * 渲染顶部信息栏
 */
function renderHeader() {
    return `
        <div class="gradient-orange text-white p-4 rounded-b-2xl shadow-lg">
            <div class="flex justify-between items-start mb-3">
                <div class="flex items-center gap-4">
                    <div>
                        <h1 class="text-2xl font-bold">排球冒险</h1>
                        <p class="text-sm text-white text-opacity-90">游客模式</p>
                    </div>
                    <div class="w-12 h-12 bg-white bg-opacity-20 rounded-full border-2 border-white shadow-lg flex items-center justify-center overflow-hidden">
                        <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=volleyball" alt="用户头像" class="w-full h-full object-cover" />
                    </div>
                </div>
            </div>
            
            <div class="flex flex-wrap gap-2 mb-3">
                <div class="flex gap-2">
                    <span class="px-3 py-1 bg-white bg-opacity-20 border border-white border-opacity-30 rounded-lg text-xs flex items-center gap-1">
                        <span>🥉</span> ${AppState.user.rank}
                    </span>
                    <span class="px-3 py-1 bg-white bg-opacity-20 border border-white border-opacity-30 rounded-lg text-xs">
                        ${AppState.user.stars}
                    </span>
                </div>
                <div class="flex gap-2">
                    <span class="px-3 py-1 bg-white bg-opacity-20 border border-white border-opacity-30 rounded-lg text-xs flex items-center gap-1">
                        <span>⬆️</span> Lv.${AppState.user.level}
                    </span>
                    <span class="px-3 py-1 bg-white bg-opacity-20 border border-white border-opacity-30 rounded-lg text-xs">
                        💫 ${AppState.user.xp} XP
                    </span>
                </div>
            </div>
            
            <!-- 等级进度条 -->
            <div class="bg-yellow-900 bg-opacity-30 border border-yellow-700 rounded-xl p-3">
                <div class="flex justify-between text-xs text-white text-opacity-90 mb-2">
                    <span>等级 ${AppState.user.level} 进度</span>
                    <span>还需 100 XP</span>
                </div>
                <div class="w-full h-2 bg-white bg-opacity-20 rounded-full">
                    <div class="h-2 bg-gradient-to-r from-volleyball-orange to-volleyball-dark-orange rounded-full" 
                         style="width: ${AppState.user.xp % 100}%"></div>
                </div>
            </div>
        </div>
    `;
}

/**
 * 渲染排球场位置
 */
function renderVolleyballCourt() {
    const positionIdMap = {
        outside: '主攻',
        middle: '副攻',
        setter: '二传',
        opposite: '接应',
        libero: '自由人',
        defensive: '防守队员'
    };

    const currentSelection = AppState.selectedPosition ||
        Object.keys(positionIdMap).find(key => positionIdMap[key] === AppState.user.mainPosition) ||
        'libero';

    const positions = [
        { id: 'outside', name: '主攻', stars: 10, level: 2, avatar: 'https://api.dicebear.com/7.x/avataaars-neutral/svg?seed=hitter&backgroundColor=0ea5e9' },
        { id: 'middle', name: '副攻', stars: 45, level: 4, avatar: 'https://api.dicebear.com/7.x/avataaars-neutral/svg?seed=middle&backgroundColor=10b981' },
        { id: 'setter', name: '二传', stars: 25, level: 3, avatar: 'https://api.dicebear.com/7.x/avataaars-neutral/svg?seed=setter&backgroundColor=ffa500' },
        { id: 'opposite', name: '接应', stars: 70, level: 5, avatar: 'https://api.dicebear.com/7.x/avataaars-neutral/svg?seed=opposite&backgroundColor=f59e0b' },
        { id: 'libero', name: '自由人', xp: '1800/2000 XP', avatar: 'https://api.dicebear.com/7.x/avataaars-neutral/svg?seed=libero&backgroundColor=3b82f6' },
        { id: 'defensive', name: '防守队员', stars: 100, level: 6, avatar: 'https://api.dicebear.com/7.x/avataaars-neutral/svg?seed=defender&backgroundColor=14b8a6' }
    ];

    return `
        <div class="bg-white bg-opacity-80 border-2 border-white rounded-3xl p-6 shadow-2xl">
            <div class="flex justify-between items-center mb-4">
                <h2 class="text-xl font-semibold flex items-center gap-2">
                    <span>🏐</span>
                    排球场位置
                </h2>
                <span class="px-3 py-1 border border-orange-300 rounded-lg text-xs text-orange-600">
                    点击位置开始训练
                </span>
            </div>
            
            <!-- 排球场图示 -->
            <div class="volleyball-court-bg rounded-2xl p-8 relative" style="min-height: 400px;">
                <div class="grid grid-cols-3 gap-4">
                    ${positions.map(pos => {
                        const isSelected = currentSelection === pos.id;
                        return `
                            <div class="bg-gray-100 bg-opacity-75 border-2 ${isSelected ? 'border-white bg-white shadow-xl ring-2 ring-volleyball-orange' : 'border-gray-300'} rounded-2xl p-4 hover-lift cursor-pointer transition-all" onclick="selectPosition('${pos.id}')">
                                <div class="text-center mb-2">
                                    <h3 class="font-semibold ${isSelected ? 'text-gray-800' : 'text-gray-600'}">${pos.name}</h3>
                                </div>
                                <div class="flex justify-center gap-2 text-xs text-gray-600 mb-3">
                                    ${pos.xp ? `
                                        <div class="w-full">
                                            <div class="h-1.5 bg-gray-200 rounded-full mb-1">
                                                <div class="h-1.5 bg-gradient-to-r from-volleyball-orange to-volleyball-dark-orange rounded-full" style="width: 90%"></div>
                                            </div>
                                            <p class="text-xs text-center">${pos.xp}</p>
                                        </div>
                                    ` : `
                                        <span>⭐ ${pos.stars}★</span>
                                        <span>⬆️ Lv.${pos.level}</span>
                                    `}
                                </div>
                                <div class="flex justify-center">
                                    <div class="relative w-16 h-16">
                                        <div class="w-16 h-16 bg-white border-3 border-white rounded-full shadow-lg overflow-hidden">
                                            <img src="${pos.avatar}" alt="${pos.name}" style="width: 100%; height: 100%; object-fit: cover;" />
                                        </div>
                                        ${isSelected ? `
                                            <div class="absolute -bottom-1 -right-1 w-7 h-7 bg-blue-500 border-2 border-white rounded-full shadow-lg flex items-center justify-center">
                                                <span class="text-white text-xs font-bold">6</span>
                                            </div>
                                            <span class="absolute -top-2 -right-2 px-2 py-1 bg-gradient-to-r from-yellow-400 to-yellow-500 text-white text-xs rounded-lg shadow-md">
                                                ★ 主打
                                            </span>
                                        ` : ''}
                                    </div>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        </div>
    `;
}

/**
 * 渲染主功能标签页
 */
function renderMainTabs() {
    return `
        <div class="space-y-4">
            <!-- 标签切换按钮 -->
            <div class="bg-white bg-opacity-80 rounded-2xl p-1 flex">
                <button onclick="showTab('tactics')" 
                        id="tab-tactics"
                        class="flex-1 py-3 px-6 rounded-xl font-medium transition-all flex items-center justify-center gap-2">
                    <span>📚</span>
                    战术学习
                </button>
                <button onclick="showTab('ai-coach')" 
                        id="tab-ai-coach"
                        class="flex-1 py-3 px-6 rounded-xl font-medium transition-all flex items-center justify-center gap-2">
                    <span>🤖</span>
                    AI 教练
                </button>
            </div>
            
            <!-- 标签内容 -->
            <div id="tab-content"></div>
        </div>
    `;
}

/**
 * 显示标签页
 */
function showTab(tabName) {
    // 更新标签按钮样式
    document.querySelectorAll('[id^="tab-"]').forEach(btn => {
        btn.classList.remove('bg-volleyball-orange', 'text-white', 'shadow-md');
        btn.classList.add('text-gray-600');
    });
    
    const activeTab = document.getElementById(`tab-${tabName}`);
    activeTab.classList.add('bg-volleyball-orange', 'text-white', 'shadow-md');
    activeTab.classList.remove('text-gray-600');
    
    // 渲染对应内容
    const contentDiv = document.getElementById('tab-content');
    
    if (tabName === 'tactics') {
        contentDiv.innerHTML = renderTacticsTab();
    } else if (tabName === 'ai-coach') {
        contentDiv.innerHTML = renderAICoachTab();
    }
}

/**
 * 渲染战术学习标签页
 */
function renderTacticsTab() {
    const unlockedSet = new Set(AppState.unlockedTactics || []);
    const baseTactics = [
        {
            emoji: '🔄',
            title: '基础轮转规则',
            level: '初级',
            description: '排球比赛中的轮转是最基本也是最重要的规则之一。每当己方获得发球权时，全队需要顺时针轮转一个位置。...',
            stars: 2,
            xp: 50
        },
        {
            emoji: '🏐',
            title: '位置与职责',
            level: '初级',
            description: '排球场上有6个位置，每个位置都有特定的职责。了解各位置的作用是掌握排球战术的基础。...',
            stars: 2,
            xp: 50,
            requiredStars: 2,
            requiredLevel: 1
        },
        {
            emoji: '📐',
            title: '接发球站位',
            level: '初级',
            description: '接发球（一传）是进攻的起点。合理的站位能够确保更好地接起对方的发球。...',
            requiredStars: 5,
            requiredLevel: 2
        },
        {
            emoji: '⚡',
            title: '进攻战术组合',
            level: '中级',
            description: '通过多点进攻和快速配合，可以撕开对方的防线。常见的进攻战术包括快攻、强攻、后排攻等。...',
            requiredStars: 15,
            requiredLevel: 3
        },
        {
            emoji: '🛡️',
            title: '拦网体系',
            level: '中级',
            description: '有效的拦网不仅能直接得分，还能降低后排防守压力。团队拦网需要良好的协同配合。...',
            requiredStars: 25,
            requiredLevel: 4
        },
        {
            emoji: '🎯',
            title: '防守阵型',
            level: '高级',
            description: '后排防守阵型决定了球队的防守覆盖范围。不同的阵型适用于不同的比赛情况。...',
            requiredStars: 50,
            requiredLevel: 5
        }
    ];

    const tactics = baseTactics.map(tactic => ({
        ...tactic,
        locked: !unlockedSet.has(tactic.title)
    }));
    
    return `
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            ${tactics.map(tactic => `
                <div class="bg-white ${tactic.locked ? 'opacity-75' : ''} border ${tactic.locked ? 'border-gray-200' : 'border-orange-200'} rounded-2xl p-5 ${!tactic.locked ? 'hover-lift cursor-pointer' : ''} transition-all"
                     ${!tactic.locked ? `onclick="startTacticsLearn('${tactic.title}')"` : ''}>
                    <div class="flex items-start gap-4">
                        <div class="text-4xl ${tactic.locked ? 'opacity-50' : ''}">${tactic.emoji}</div>
                        <div class="flex-1">
                            <div class="flex items-start justify-between mb-2">
                                <h3 class="text-lg font-semibold text-gray-800">${tactic.title}</h3>
                                <span class="px-2 py-1 ${
                                    tactic.level === '初级' ? 'bg-green-100 border-green-200' :
                                    tactic.level === '中级' ? 'bg-volleyball-orange text-white' :
                                    'bg-red-500 text-white'
                                } border rounded-lg text-xs">
                                    ${tactic.level}
                                </span>
                            </div>
                            <p class="text-sm text-gray-600 mb-3">${tactic.description}</p>
                            
                            ${tactic.locked ? `
                                <div class="flex gap-2 text-xs">
                                    <span class="flex items-center gap-1 text-gray-500">
                                        <span>⭐</span> 需要 ${tactic.requiredStars}★
                                    </span>
                                    <span class="flex items-center gap-1 text-gray-500">
                                        <span>⬆️</span> 需要 Lv.${tactic.requiredLevel}
                                    </span>
                                </div>
                            ` : `
                                <div class="flex gap-2">
                                    <span class="px-3 py-1 bg-yellow-100 border border-yellow-200 rounded-lg text-xs">
                                        <span>⭐</span> ${tactic.stars}
                                    </span>
                                    <span class="px-3 py-1 bg-blue-500 text-white rounded-lg text-xs">
                                        💫 ${tactic.xp} XP
                                    </span>
                                </div>
                            `}
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

/**
 * 渲染AI教练标签页
 */
function renderAICoachTab() {
    return `
        <div class="bg-gradient-to-br from-purple-100 to-blue-100 border-2 border-purple-200 rounded-2xl p-8">
            <div class="max-w-3xl mx-auto">
                <div class="w-20 h-20 bg-gradient-to-r from-volleyball-purple to-volleyball-blue rounded-full flex items-center justify-center mx-auto mb-6">
                    <span class="text-4xl">🤖</span>
                </div>
                
                <h2 class="text-2xl font-bold text-center text-gray-800 mb-3">AI 排球教练</h2>
                <p class="text-center text-gray-700 mb-8">
                    您的专属 AI 教练，提供智能问答和视频分析服务。
                    无论是技术问题、战术疑惑，还是训练视频分析，AI 教练都能为您提供专业指导。
                </p>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                    <div class="bg-white bg-opacity-80 rounded-2xl p-6">
                        <div class="flex items-start gap-4">
                            <div class="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
                                <span class="text-2xl">💬</span>
                            </div>
                            <div>
                                <h4 class="font-semibold text-gray-800 mb-2">智能问答</h4>
                                <p class="text-sm text-gray-600">随时提问排球相关问题，获取专业解答和训练建议</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="bg-white bg-opacity-80 rounded-2xl p-6">
                        <div class="flex items-start gap-4">
                            <div class="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                                <span class="text-2xl">🎥</span>
                            </div>
                            <div>
                                <h4 class="font-semibold text-gray-800 mb-2">视频分析</h4>
                                <p class="text-sm text-gray-600">上传训练视频，AI 识别动作并提供详细反馈和改进建议</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <button onclick="openAICoachDialog()" 
                        class="w-full bg-gradient-to-r from-volleyball-purple to-volleyball-blue text-white py-4 rounded-xl font-semibold hover:shadow-xl transition-all flex items-center justify-center gap-2">
                    <span>🚀</span>
                    开始咨询 AI 教练
                </button>
            </div>
        </div>
    `;
}

/**
 * 打开AI教练对话框
 */
function openAICoachDialog() {
    showDialog('ai-coach');
}

/**
 * 开始战术学习
 */
function startTacticsLearn(tacticTitle) {
    AppState.tacticsTest.currentModule = tacticTitle;
    showDialog('tactics-learn', { title: tacticTitle });
}

/**
 * 显示通用对话框
 */
function showDialog(dialogType, data = {}) {
    const dialogContainer = document.createElement('div');
    dialogContainer.id = 'dialog-overlay';
    dialogContainer.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4';
    
    let dialogContent = '';
    
    if (dialogType === 'ai-coach') {
        dialogContent = renderAICoachDialog();
    } else if (dialogType === 'tactics-learn') {
        dialogContent = renderTacticsLearnDialog(data.title);
    }
    
    dialogContainer.innerHTML = `
        <div class="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div class="sticky top-0 bg-white border-b border-gray-200 p-6 flex justify-between items-center z-10">
                <h2 class="text-2xl font-bold text-gray-800">${dialogType === 'ai-coach' ? 'AI 教练' : '战术学习'}</h2>
                <button onclick="closeDialog()" class="text-gray-400 hover:text-gray-600 text-2xl">✕</button>
            </div>
            <div class="p-6">
                ${dialogContent}
            </div>
        </div>
    `;
    
    document.body.appendChild(dialogContainer);
}

/**
 * 关闭对话框
 */
function closeDialog() {
    const dialog = document.getElementById('dialog-overlay');
    if (dialog) {
        dialog.remove();
    }
}

/**
 * 渲染AI教练对话框内容
 */
function renderAICoachDialog() {
    return `
        <!-- 功能选择标签 -->
        <div class="mb-6">
            <div class="bg-gray-100 rounded-xl p-1 flex">
                <button onclick="showAITab('qa')" 
                        id="ai-tab-qa"
                        class="flex-1 py-3 px-4 rounded-lg font-medium transition-all bg-white shadow-sm text-volleyball-orange">
                    <span class="mr-2">💬</span>
                    智能问答
                </button>
                <button onclick="showAITab('analyze')" 
                        id="ai-tab-analyze"
                        class="flex-1 py-3 px-4 rounded-lg font-medium transition-all text-gray-600">
                    <span class="mr-2">🎥</span>
                    视频分析
                </button>
                <button onclick="showAITab('visualize')" 
                        id="ai-tab-visualize"
                        class="flex-1 py-3 px-4 rounded-lg font-medium transition-all text-gray-600">
                    <span class="mr-2">🎬</span>
                    视频生成
                </button>
            </div>
        </div>
        
        <!-- 标签内容 -->
        <div id="ai-tab-content">
            ${renderQATab()}
        </div>
    `;
}

/**
 * 显示AI标签页
 */
function showAITab(tabName) {
    // 更新按钮样式
    document.querySelectorAll('[id^="ai-tab-"]').forEach(btn => {
        btn.classList.remove('bg-white', 'shadow-sm', 'text-volleyball-orange');
        btn.classList.add('text-gray-600');
    });
    
    const activeTab = document.getElementById(`ai-tab-${tabName}`);
    activeTab.classList.add('bg-white', 'shadow-sm', 'text-volleyball-orange');
    activeTab.classList.remove('text-gray-600');
    
    // 渲染内容
    const contentDiv = document.getElementById('ai-tab-content');
    if (tabName === 'qa') {
        contentDiv.innerHTML = renderQATab();
    } else if (tabName === 'analyze') {
        contentDiv.innerHTML = renderAnalyzeTab();
    } else if (tabName === 'visualize') {
        contentDiv.innerHTML = renderVisualizeTab();
    }
}

/**
 * 渲染智能问答标签页
 */
function renderQATab() {
    // 初始化对话历史（如果不存在）
    if (!AppState.aiCoachChat) {
        AppState.aiCoachChat = [];
    }
    
    // 渲染对话历史
    const chatHistory = AppState.aiCoachChat.map(msg => {
        if (msg.role === 'user') {
            return `
                <div class="flex justify-end mb-4">
                    <div class="max-w-[80%] bg-gradient-to-r from-volleyball-orange to-volleyball-dark-orange text-white rounded-2xl rounded-tr-none p-4 shadow-lg">
                        <p class="text-sm font-medium">${msg.content}</p>
                    </div>
                </div>
            `;
        } else {
            return `
                <div class="flex justify-start mb-4">
                    <div class="max-w-[80%] bg-white border-2 border-gray-200 rounded-2xl rounded-tl-none p-4 shadow-lg">
                        <div class="flex items-start gap-3 mb-2">
                            <div class="w-8 h-8 bg-gradient-to-r from-volleyball-purple to-volleyball-blue rounded-full flex items-center justify-center flex-shrink-0">
                                <span class="text-sm">🤖</span>
                            </div>
                            <div class="flex-1">
                                <p class="text-xs text-gray-500 mb-1">AI教练</p>
                                <div class="text-sm text-gray-700 whitespace-pre-wrap">${msg.content}</div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
    }).join('');
    
    return `
        <!-- 智能问答界面 -->
        <div class="flex flex-col h-[600px]">
            <!-- 欢迎提示 -->
            ${AppState.aiCoachChat.length === 0 ? `
                <div class="bg-gradient-to-br from-purple-50 to-blue-50 border-2 border-purple-200 rounded-2xl p-6 mb-4 text-center">
                    <div class="w-16 h-16 bg-gradient-to-r from-volleyball-purple to-volleyball-blue rounded-full flex items-center justify-center mx-auto mb-4">
                        <span class="text-3xl">🤖</span>
                    </div>
                    <h3 class="text-xl font-semibold text-gray-800 mb-2">欢迎咨询AI教练</h3>
                    <p class="text-sm text-gray-600 mb-4">我可以回答您关于排球技术、战术、训练方法等任何问题</p>
                    
                    <!-- 快捷问题 -->
                    <div class="grid grid-cols-2 gap-2 mt-4">
                        <button onclick="askQuickQuestion('如何提高扣球力量？')" class="px-4 py-2 bg-white border border-purple-200 rounded-lg text-sm text-gray-700 hover:bg-purple-50 transition-all text-left">
                            💪 如何提高扣球力量？
                        </button>
                        <button onclick="askQuickQuestion('拦网的技巧有哪些？')" class="px-4 py-2 bg-white border border-purple-200 rounded-lg text-sm text-gray-700 hover:bg-purple-50 transition-all text-left">
                            🛡️ 拦网的技巧有哪些？
                        </button>
                        <button onclick="askQuickQuestion('什么是快攻战术？')" class="px-4 py-2 bg-white border border-purple-200 rounded-lg text-sm text-gray-700 hover:bg-purple-50 transition-all text-left">
                            ⚡ 什么是快攻战术？
                        </button>
                        <button onclick="askQuickQuestion('如何练习一传？')" class="px-4 py-2 bg-white border border-purple-200 rounded-lg text-sm text-gray-700 hover:bg-purple-50 transition-all text-left">
                            📥 如何练习一传？
                        </button>
                    </div>
                </div>
            ` : ''}
            
            <!-- 对话历史区域 -->
            <div id="qa-chat-history" class="flex-1 overflow-y-auto mb-4 p-4 bg-gray-50 rounded-xl scrollbar-hide">
                ${chatHistory || '<div class="text-center text-gray-400 text-sm mt-8">还没有对话记录，开始提问吧！</div>'}
            </div>
            
            <!-- 输入区域 -->
            <div class="border-t border-gray-200 pt-4">
                <div class="flex gap-3">
                    <input type="text" 
                           id="qa-input" 
                           placeholder="输入您的问题...（例如：如何提高扣球准确性？）" 
                           class="flex-1 px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-volleyball-orange focus:border-transparent"
                           onkeypress="if(event.key === 'Enter') submitQAQuestion()">
                    <button onclick="submitQAQuestion()" 
                            id="qa-submit-btn"
                            class="px-6 py-3 bg-gradient-to-r from-volleyball-orange to-volleyball-dark-orange text-white rounded-xl font-semibold hover:shadow-xl transition-all flex items-center justify-center gap-2">
                        <span>🚀</span>
                        发送
                    </button>
                </div>
                <p class="text-xs text-gray-500 mt-2 text-center">
                    💡 可以询问任何排球相关问题，AI教练会为您提供专业解答
                </p>
            </div>
        </div>
    `;
}

/**
 * 快捷提问
 */
function askQuickQuestion(question) {
    document.getElementById('qa-input').value = question;
    submitQAQuestion();
}

/**
 * 提交问答问题
 */
async function submitQAQuestion() {
    const input = document.getElementById('qa-input');
    const question = input.value.trim();
    
    if (!question) {
        showToast('请输入问题', 'warning');
        return;
    }
    
    // 禁用输入和按钮
    input.disabled = true;
    const submitBtn = document.getElementById('qa-submit-btn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="animate-spin">⏳</span> 思考中...';
    
    // 添加用户消息到历史
    if (!AppState.aiCoachChat) {
        AppState.aiCoachChat = [];
    }
    AppState.aiCoachChat.push({
        role: 'user',
        content: question
    });
    
    // 重新渲染对话界面（显示用户消息）
    const contentDiv = document.getElementById('ai-tab-content');
    contentDiv.innerHTML = renderQATab();
    
    // 滚动到底部
    setTimeout(() => {
        const chatHistory = document.getElementById('qa-chat-history');
        if (chatHistory) {
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }
    }, 100);
    
    try {
        // 调用AI API
        const result = await api.askAICoach(question);
        
        if (result.success) {
            // 添加AI回答到历史
            AppState.aiCoachChat.push({
                role: 'assistant',
                content: result.answer
            });
            
            // 重新渲染对话界面（显示AI回答）
            contentDiv.innerHTML = renderQATab();
            
            // 滚动到底部
            setTimeout(() => {
                const chatHistory = document.getElementById('qa-chat-history');
                if (chatHistory) {
                    chatHistory.scrollTop = chatHistory.scrollHeight;
                }
            }, 100);
            
            showToast('AI回答完成！', 'success');
        } else {
            // 添加错误消息
            AppState.aiCoachChat.push({
                role: 'assistant',
                content: `抱歉，暂时无法回答您的问题：${result.error}`
            });
            
            contentDiv.innerHTML = renderQATab();
            showToast(`问答失败: ${result.error}`, 'error');
        }
    } catch (error) {
        // 添加错误消息
        AppState.aiCoachChat.push({
            role: 'assistant',
            content: `抱歉，发生错误：${error.message}`
        });
        
        const contentDiv = document.getElementById('ai-tab-content');
        contentDiv.innerHTML = renderQATab();
        showToast(`问答过程出错: ${error.message}`, 'error');
    } finally {
        // 恢复输入和按钮
        const newInput = document.getElementById('qa-input');
        const newSubmitBtn = document.getElementById('qa-submit-btn');
        if (newInput) {
            newInput.disabled = false;
            newInput.value = '';
            newInput.focus();
        }
        if (newSubmitBtn) {
            newSubmitBtn.disabled = false;
            newSubmitBtn.innerHTML = '<span>🚀</span> 发送';
        }
    }
}

/**
 * 渲染分析标签页
 */
function renderAnalyzeTab() {
    return `
        <!-- 视频上传区域 -->
        <div class="mb-8">
            <h3 class="text-xl font-semibold mb-4 flex items-center gap-2">
                <span>🎥</span>
                上传训练视频
            </h3>
            
            <div class="border-2 border-dashed border-gray-300 rounded-2xl p-8 text-center hover:border-volleyball-orange transition-all">
                <input type="file" 
                       id="video-upload" 
                       accept="video/*" 
                       class="hidden" 
                       onchange="handleVideoUpload(event)">
                
                <label for="video-upload" class="cursor-pointer">
                    <div class="text-6xl mb-4">📹</div>
                    <p class="text-lg font-semibold text-gray-700 mb-2">点击或拖拽上传视频</p>
                    <p class="text-sm text-gray-500">支持 MP4, AVI, MOV 格式，最大50MB</p>
                </label>
            </div>
            
            <div id="upload-preview" class="mt-4 hidden">
                <video id="preview-video" controls class="w-full rounded-xl"></video>
                
                <!-- 分析选项 -->
                <div class="mt-4 space-y-3">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">分析模式</label>
                        <select id="analysis-mode" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-volleyball-orange focus:border-transparent">
                            <option value="single">单帧快速分析（推荐）</option>
                            <option value="sequence">连续帧深度分析</option>
                        </select>
                    </div>
                    
                    <button onclick="startAnalysis()" 
                            class="w-full bg-gradient-to-r from-volleyball-orange to-volleyball-dark-orange text-white py-4 rounded-xl font-semibold hover:shadow-xl transition-all flex items-center justify-center gap-2">
                        <span>🚀</span>
                        开始AI分析
                    </button>
                </div>
            </div>
        </div>
        
        <!-- 分析结果区域 -->
        <div id="analysis-results" class="hidden">
            <h3 class="text-xl font-semibold mb-4 flex items-center gap-2">
                <span>📊</span>
                分析结果
            </h3>
            <div id="results-content"></div>
        </div>
    `;
}

/**
 * 渲染视频可视化标签页
 */
function renderVisualizeTab() {
    return `
        <!-- 视频上传区域 -->
        <div class="mb-8">
            <h3 class="text-xl font-semibold mb-4 flex items-center gap-2">
                <span>🎬</span>
                生成可视化视频
            </h3>
            
            <div class="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-4">
                <p class="text-sm text-blue-800 flex items-start gap-2">
                    <span class="text-lg">💡</span>
                    <span>将你的训练视频转换为专业的分析视频，支持4种可视化效果</span>
                </p>
            </div>
            
            <div class="border-2 border-dashed border-gray-300 rounded-2xl p-8 text-center hover:border-volleyball-blue transition-all">
                <input type="file" 
                       id="video-upload-vis" 
                       accept="video/*" 
                       class="hidden" 
                       onchange="handleVideoUploadForVis(event)">
                
                <label for="video-upload-vis" class="cursor-pointer">
                    <div class="text-6xl mb-4">🎥</div>
                    <p class="text-lg font-semibold text-gray-700 mb-2">点击上传视频</p>
                    <p class="text-sm text-gray-500">支持 MP4, AVI, MOV 格式，最大50MB</p>
                </label>
            </div>
            
            <div id="upload-preview-vis" class="mt-4 hidden">
                <video id="preview-video-vis" controls class="w-full rounded-xl mb-4"></video>
                
                <!-- 可视化类型选择 -->
                <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700 mb-3">选择可视化类型</label>
                    <div class="grid grid-cols-2 gap-3">
                        <label class="relative cursor-pointer">
                            <input type="radio" name="vis-type" value="overlay" checked class="sr-only peer">
                            <div class="border-2 border-gray-200 rounded-xl p-4 peer-checked:border-volleyball-blue peer-checked:bg-blue-50 transition-all">
                                <div class="text-3xl mb-2">🎨</div>
                                <h4 class="font-semibold text-sm mb-1">骨架叠加</h4>
                                <p class="text-xs text-gray-600">在原视频上叠加骨架动画</p>
                            </div>
                        </label>
                        
                        <label class="relative cursor-pointer">
                            <input type="radio" name="vis-type" value="skeleton" class="sr-only peer">
                            <div class="border-2 border-gray-200 rounded-xl p-4 peer-checked:border-volleyball-blue peer-checked:bg-blue-50 transition-all">
                                <div class="text-3xl mb-2">🦴</div>
                                <h4 class="font-semibold text-sm mb-1">纯骨架动画</h4>
                                <p class="text-xs text-gray-600">仅显示骨架，白色背景</p>
                            </div>
                        </label>
                        
                        <label class="relative cursor-pointer">
                            <input type="radio" name="vis-type" value="comparison" class="sr-only peer">
                            <div class="border-2 border-gray-200 rounded-xl p-4 peer-checked:border-volleyball-blue peer-checked:bg-blue-50 transition-all">
                                <div class="text-3xl mb-2">📊</div>
                                <h4 class="font-semibold text-sm mb-1">对比视频</h4>
                                <p class="text-xs text-gray-600">原视频与骨架并排对比</p>
                            </div>
                        </label>
                        
                        <label class="relative cursor-pointer">
                            <input type="radio" name="vis-type" value="trajectory" class="sr-only peer">
                            <div class="border-2 border-gray-200 rounded-xl p-4 peer-checked:border-volleyball-blue peer-checked:bg-blue-50 transition-all">
                                <div class="text-3xl mb-2">📈</div>
                                <h4 class="font-semibold text-sm mb-1">轨迹追踪</h4>
                                <p class="text-xs text-gray-600">显示关键点运动轨迹</p>
                            </div>
                        </label>
                    </div>
                </div>
                
                <button onclick="startVisualization()" 
                        class="w-full bg-gradient-to-r from-volleyball-blue to-volleyball-purple text-white py-4 rounded-xl font-semibold hover:shadow-xl transition-all flex items-center justify-center gap-2">
                    <span>🎬</span>
                    生成可视化视频
                </button>
            </div>
        </div>
        
        <!-- 可视化结果区域 -->
        <div id="visualization-results" class="hidden">
            <h3 class="text-xl font-semibold mb-4 flex items-center gap-2">
                <span>✅</span>
                生成成功
            </h3>
            <div id="visualization-content"></div>
        </div>
    `;
}

/**
 * 处理视频上传（分析用）
 */
function handleVideoUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // 验证文件
    const maxSize = 50 * 1024 * 1024; // 50MB
    if (file.size > maxSize) {
        showToast('文件太大！请上传小于50MB的视频。', 'error');
        return;
    }
    
    const allowedTypes = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-matroska'];
    if (!allowedTypes.includes(file.type)) {
        showToast('不支持的文件格式！请上传MP4、AVI或MOV格式的视频。', 'error');
        return;
    }
    
    // 显示预览
    const preview = document.getElementById('upload-preview');
    const video = document.getElementById('preview-video');
    
    const url = URL.createObjectURL(file);
    video.src = url;
    preview.classList.remove('hidden');
    
    // 保存文件到全局变量
    window.uploadedVideoFile = file;
}

/**
 * 处理视频上传（可视化用）
 */
function handleVideoUploadForVis(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // 验证文件
    const maxSize = 50 * 1024 * 1024; // 50MB
    if (file.size > maxSize) {
        showToast('文件太大！请上传小于50MB的视频。', 'error');
        return;
    }
    
    const allowedTypes = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-matroska'];
    if (!allowedTypes.includes(file.type)) {
        showToast('不支持的文件格式！请上传MP4、AVI或MOV格式的视频。', 'error');
        return;
    }
    
    // 显示预览
    const preview = document.getElementById('upload-preview-vis');
    const video = document.getElementById('preview-video-vis');
    
    const url = URL.createObjectURL(file);
    video.src = url;
    preview.classList.remove('hidden');
    
    // 保存文件到全局变量
    window.uploadedVideoFileForVis = file;
}

/**
 * 开始AI分析
 */
async function startAnalysis() {
    if (!window.uploadedVideoFile) {
        showToast('请先上传视频！', 'warning');
        return;
    }
    
    // 获取分析模式
    const mode = document.getElementById('analysis-mode').value;
    
    // 显示加载状态
    showLoading(true);
    
    try {
        // 调用API分析视频
        const result = await api.analyzeVideo(window.uploadedVideoFile, mode);
        
        // 隐藏加载状态
        showLoading(false);
        
        if (result.success) {
            // 显示分析结果
            displayAnalysisResults(result);
            showToast('分析完成！', 'success');
        } else {
            showToast(`分析失败: ${result.error}`, 'error');
        }
    } catch (error) {
        showLoading(false);
        showToast(`分析过程出错: ${error.message}`, 'error');
    }
}

/**
 * 开始视频可视化生成
 */
async function startVisualization() {
    if (!window.uploadedVideoFileForVis) {
        showToast('请先上传视频！', 'warning');
        return;
    }
    
    // 获取选中的可视化类型
    const visTypeRadio = document.querySelector('input[name="vis-type"]:checked');
    const visType = visTypeRadio ? visTypeRadio.value : 'overlay';
    
    // 获取类型名称
    const visTypeNames = {
        'overlay': '骨架叠加',
        'skeleton': '纯骨架动画',
        'comparison': '对比视频',
        'trajectory': '轨迹追踪'
    };
    
    // 显示加载状态
    showLoading(true);
    const loadingDiv = document.getElementById('loading');
    loadingDiv.innerHTML = `
        <div class="bg-white rounded-2xl p-8 text-center max-w-md">
            <div class="animate-spin rounded-full h-16 w-16 border-b-4 border-volleyball-blue mx-auto mb-4"></div>
            <p class="text-lg font-semibold text-gray-700">正在生成${visTypeNames[visType]}视频...</p>
            <p class="text-sm text-gray-500 mt-2">这可能需要30秒到2分钟，请耐心等待</p>
        </div>
    `;
    
    try {
        // 调用API生成可视化视频
        const result = await api.visualizeVideo(window.uploadedVideoFileForVis, visType);
        
        // 恢复加载状态
        loadingDiv.innerHTML = `
            <div class="bg-white rounded-2xl p-8 text-center">
                <div class="animate-spin rounded-full h-16 w-16 border-b-4 border-volleyball-orange mx-auto mb-4"></div>
                <p class="text-lg font-semibold text-gray-700">AI正在分析中...</p>
            </div>
        `;
        showLoading(false);
        
        if (result.success) {
            // 显示可视化结果
            displayVisualizationResults(result);
            showToast('视频生成成功！', 'success');
        } else {
            showToast(`生成失败: ${result.error}`, 'error');
        }
    } catch (error) {
        showLoading(false);
        showToast(`生成过程出错: ${error.message}`, 'error');
    }
}

/**
 * 显示可视化结果
 */
function displayVisualizationResults(result) {
    const resultsDiv = document.getElementById('visualization-results');
    const resultsContent = document.getElementById('visualization-content');
    
    const visTypeNames = {
        'overlay': '骨架叠加',
        'skeleton': '纯骨架动画',
        'comparison': '对比视频',
        'trajectory': '轨迹追踪'
    };
    
    const visTypeDescriptions = {
        'overlay': '在原视频上叠加了姿态骨架，可以清楚看到动作的关键点和连接线。',
        'skeleton': '纯骨架动画，去除了背景，专注于动作本身的分析。',
        'comparison': '左侧是原始视频，右侧是骨架动画，方便对比学习。',
        'trajectory': '显示关键点的运动轨迹，可以看到动作的路径和方向。'
    };
    
    resultsContent.innerHTML = `
        <div class="space-y-6">
            <!-- 类型说明 -->
            <div class="bg-gradient-to-br from-blue-50 to-purple-50 border border-blue-200 rounded-xl p-5">
                <h4 class="font-semibold text-gray-800 mb-2 flex items-center gap-2">
                    <span>${result.vis_type === 'overlay' ? '🎨' : result.vis_type === 'skeleton' ? '🦴' : result.vis_type === 'comparison' ? '📊' : '📈'}</span>
                    ${visTypeNames[result.vis_type]}
                </h4>
                <p class="text-sm text-gray-700">${visTypeDescriptions[result.vis_type]}</p>
            </div>
            
            <!-- 视频播放器 -->
            <div class="bg-black rounded-xl overflow-hidden">
                <video id="result-video" controls autoplay class="w-full">
                    <source src="${result.video_url}" type="video/mp4">
                    您的浏览器不支持视频播放。
                </video>
            </div>
            
            <!-- 操作按钮 -->
            <div class="grid grid-cols-2 gap-3">
                <a href="${result.video_url}" 
                   download="${result.filename}"
                   class="px-6 py-3 bg-green-500 text-white rounded-xl text-center font-semibold hover:shadow-lg transition-all flex items-center justify-center gap-2">
                    <span>⬇️</span>
                    下载视频
                </a>
                <button onclick="resetVisualization()" 
                        class="px-6 py-3 border-2 border-gray-300 rounded-xl hover:bg-gray-50 transition-all font-semibold">
                    重新生成
                </button>
            </div>
            
            <!-- 提示 -->
            <div class="bg-yellow-50 border border-yellow-200 rounded-xl p-4">
                <p class="text-sm text-yellow-800 flex items-start gap-2">
                    <span class="text-lg">💡</span>
                    <span>视频已保存到服务器的output目录，你可以下载保存或分享给朋友！</span>
                </p>
            </div>
        </div>
    `;
    
    resultsDiv.classList.remove('hidden');
}

/**
 * 重置可视化
 */
function resetVisualization() {
    document.getElementById('visualization-results').classList.add('hidden');
    document.getElementById('upload-preview-vis').classList.add('hidden');
    document.getElementById('video-upload-vis').value = '';
    window.uploadedVideoFileForVis = null;
}

/**
 * 显示分析结果
 */
function displayAnalysisResults(result) {
    const resultsDiv = document.getElementById('analysis-results');
    const resultsContent = document.getElementById('results-content');
    
    const score = result.score || {};
    const totalScore = score.total_score || 0;
    
    // 获取等级评价
    let level = '初级';
    let levelColor = 'yellow';
    let levelEmoji = '📚';
    
    if (totalScore >= 85) {
        level = '高级';
        levelColor = 'green';
        levelEmoji = '🏆';
    } else if (totalScore >= 70) {
        level = '中级';
        levelColor = 'blue';
        levelEmoji = '🌟';
    }
    
    resultsContent.innerHTML = `
        <!-- 总体评分卡片 -->
        <div class="bg-gradient-to-br from-${levelColor}-50 to-${levelColor}-100 border-2 border-${levelColor}-300 rounded-2xl p-6 mb-6">
            <div class="flex items-center justify-between mb-4">
                <div class="flex items-center gap-3">
                    <span class="text-5xl">${levelEmoji}</span>
                    <div>
                        <h4 class="text-2xl font-bold text-gray-800">${totalScore.toFixed(1)} 分</h4>
                        <p class="text-sm text-gray-600">${level} 水平</p>
                    </div>
                </div>
                <div class="text-6xl font-bold text-${levelColor}-600 opacity-20">${totalScore.toFixed(0)}</div>
            </div>
        </div>
        
        <!-- 分项得分 -->
        <div class="grid grid-cols-2 gap-4 mb-6">
            <div class="bg-white rounded-xl p-4 border border-gray-200">
                <div class="text-sm text-gray-500 mb-1">手臂动作</div>
                <div class="text-2xl font-bold text-gray-800">${(score.arm_score || 0).toFixed(1)}</div>
                <div class="w-full h-2 bg-gray-200 rounded-full mt-2">
                    <div class="h-2 bg-blue-500 rounded-full" style="width: ${score.arm_score || 0}%"></div>
                </div>
            </div>
            
            <div class="bg-white rounded-xl p-4 border border-gray-200">
                <div class="text-sm text-gray-500 mb-1">身体姿态</div>
                <div class="text-2xl font-bold text-gray-800">${(score.body_score || 0).toFixed(1)}</div>
                <div class="w-full h-2 bg-gray-200 rounded-full mt-2">
                    <div class="h-2 bg-green-500 rounded-full" style="width: ${score.body_score || 0}%"></div>
                </div>
            </div>
            
            <div class="bg-white rounded-xl p-4 border border-gray-200">
                <div class="text-sm text-gray-500 mb-1">位置准确</div>
                <div class="text-2xl font-bold text-gray-800">${(score.position_score || 0).toFixed(1)}</div>
                <div class="w-full h-2 bg-gray-200 rounded-full mt-2">
                    <div class="h-2 bg-purple-500 rounded-full" style="width: ${score.position_score || 0}%"></div>
                </div>
            </div>
            
            <div class="bg-white rounded-xl p-4 border border-gray-200">
                <div class="text-sm text-gray-500 mb-1">稳定性</div>
                <div class="text-2xl font-bold text-gray-800">${(score.stability_score || 0).toFixed(1)}</div>
                <div class="w-full h-2 bg-gray-200 rounded-full mt-2">
                    <div class="h-2 bg-orange-500 rounded-full" style="width: ${score.stability_score || 0}%"></div>
                </div>
            </div>
        </div>
        
        <!-- 姿态图像 -->
        ${result.pose_image_base64 ? `
            <div class="mb-6">
                <h4 class="text-lg font-semibold mb-3 flex items-center gap-2">
                    <span>🎨</span>
                    姿态检测结果
                </h4>
                <img src="data:image/jpeg;base64,${result.pose_image_base64}" 
                     class="w-full rounded-xl border-2 border-gray-200"
                     alt="姿态检测">
            </div>
        ` : ''}
        
        <!-- 轨迹分析（序列模式） -->
        ${result.trajectory_plot_base64 ? `
            <div class="mb-6">
                <h4 class="text-lg font-semibold mb-3 flex items-center gap-2">
                    <span>📈</span>
                    运动轨迹分析
                </h4>
                <img src="data:image/jpeg;base64,${result.trajectory_plot_base64}" 
                     class="w-full rounded-xl border-2 border-gray-200"
                     alt="轨迹分析">
            </div>
        ` : ''}
        
        <!-- 反馈建议 -->
        ${score.feedback && score.feedback.length > 0 ? `
            <div class="bg-blue-50 border border-blue-200 rounded-xl p-5">
                <h4 class="font-semibold text-blue-900 mb-3 flex items-center gap-2">
                    <span>💡</span>
                    改进建议
                </h4>
                <ul class="space-y-2">
                    ${score.feedback.map(fb => `
                        <li class="flex items-start gap-2 text-sm text-blue-800">
                            <span class="text-blue-500 mt-0.5">▸</span>
                            <span>${fb}</span>
                        </li>
                    `).join('')}
                </ul>
            </div>
        ` : ''}
        
        <!-- 操作按钮 -->
        <div class="flex gap-3 mt-6">
            <button onclick="closeDialog()" 
                    class="flex-1 px-6 py-3 border border-gray-300 rounded-xl hover:bg-gray-50 transition-all">
                关闭
            </button>
            <button onclick="handleVideoUpload(event)" 
                    class="flex-1 px-6 py-3 bg-volleyball-orange text-white rounded-xl hover:shadow-lg transition-all">
                再次分析
            </button>
        </div>
    `;
    
    resultsDiv.classList.remove('hidden');
}

/**
 * 渲染战术学习对话框
 */
function renderTacticsLearnDialog(title) {
    const { intro, keyPoints, badge } = getTacticsLearnContent(title);

    return `
        <div class="space-y-6">
            <div class="bg-gradient-to-br from-orange-50 to-yellow-50 border border-orange-200 rounded-2xl p-6">
                <div class="flex items-start gap-4 mb-4">
                    <div class="text-4xl">🔄</div>
                    <div class="flex-1">
                        <div class="flex items-center gap-2 mb-2">
                            <h3 class="text-xl font-semibold text-gray-800">知识点介绍</h3>
                            ${badge ? `<span class="px-2 py-1 bg-white border border-orange-200 rounded-lg text-xs text-orange-700">${badge}</span>` : ''}
                        </div>
                        <p class="text-gray-700">
                            ${intro}
                        </p>
                    </div>
                </div>
            </div>

            <div>
                <h3 class="text-lg font-semibold mb-4 flex items-center gap-2">
                    <span>📝</span>
                    关键要点
                </h3>
                <div class="space-y-3">
                    ${keyPoints.map((point, idx) => `
                        <div class="bg-white border border-gray-200 rounded-xl p-4 flex items-start gap-3">
                            <div class="w-6 h-6 bg-volleyball-orange text-white rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0">
                                ${idx + 1}
                            </div>
                            <p class="text-gray-700">${point}</p>
                        </div>
                    `).join('')}
                </div>
            </div>

            <div class="bg-gradient-to-br from-green-50 to-green-100 border-2 border-green-300 rounded-2xl p-5">
                <h4 class="font-semibold text-green-900 mb-3 flex items-center gap-2">
                    <span>🎁</span>
                    完成奖励
                </h4>
                <div class="flex gap-3">
                    <span class="px-4 py-2 bg-yellow-100 border border-yellow-200 rounded-lg text-sm font-medium">
                        <span>⭐</span> 最多 2 星
                    </span>
                    <span class="px-4 py-2 bg-blue-500 text-white rounded-lg text-sm font-medium">
                        💫 50 经验
                    </span>
                </div>
            </div>

            <div class="flex gap-3">
                <button onclick="closeDialog()"
                        class="flex-1 px-6 py-3 border border-gray-300 rounded-xl hover:bg-gray-50 transition-all">
                    稍后学习
                </button>
                <button onclick="startTacticsTest()"
                        class="flex-1 px-6 py-3 bg-gradient-to-r from-volleyball-orange to-volleyball-dark-orange text-white rounded-xl hover:shadow-xl transition-all flex items-center justify-center gap-2">
                    开始测试
                    <span>→</span>
                </button>
            </div>
        </div>
    `;
}

function getTacticsLearnContent(title) {
    const defaultContent = {
        intro: '排球比赛中的轮转是最基本也是最重要的规则之一。每当己方获得发球权时，全队需要顺时针轮转一个位置。',
        keyPoints: [
            '获得发球权时顺时针轮转',
            '前排3人、后排3人的位置关系必须保持',
            '发球时所有队员必须在本方场区内',
            '发球后可以自由移动到战术位置',
            '轮转顺序决定了每个队员的发球次序'
        ],
        badge: ''
    };

    if (title !== '位置与职责') {
        return defaultContent;
    }

    const positionId = getCurrentPositionId();

    const roleContent = {
        outside: {
            name: '主攻',
            intro: '主攻是侧翼的主要火力点，需要在稳固一传的同时完成高强度攻防转换，为球队持续得分并在关键分段承担突破任务。',
            keyPoints: [
                '侧翼拉开与高点强攻，终结长回合',
                '接发球和防守覆盖，保护二传出球',
                '根据拦网布置调整线路，降低失误',
                '后排 pipe/吊球变化，带动进攻节奏',
                '和二传沟通节奏，提前呼叫战术'
            ]
        },
        middle: {
            name: '副攻',
            intro: '副攻负责中路拦网与快攻突袭，是防守支柱也是牵制点，需要快速启动、精准起跳，在攻防两端抢占先机。',
            keyPoints: [
                '拦网优先：盯主攻或随球转移，封死主通道',
                '快攻跑位与起跳节奏，保持半步领先',
                '边路协防与补位，缩短横移距离',
                '与二传建立手势/眼神暗号，快球不掉速',
                '封拦后及时二次起跳或保护二传落点'
            ]
        },
        setter: {
            name: '二传',
            intro: '二传是球队大脑，负责分配进攻点与节奏控制，需要快速判断接一传质量，选择最优线路并隐藏传球意图。',
            keyPoints: [
                '接一传后快速到位，保持稳定传球姿态',
                '依据拦网布置选择快、平、拉开的优先级',
                '眼神与脚步伪装，减少被读网',
                '维持与每个攻手的配合高度与节奏差',
                '防守时保护短球与前场空档，撑起覆盖'
            ]
        },
        opposite: {
            name: '接应',
            intro: '接应是球队的终结者与补位发起点，需要在网口提供单人拦网支撑，并承担反击和不利球的稳定得分。',
            keyPoints: [
                '右侧强攻与调整攻，处理高球减少失误',
                '单人拦网守住二传对角与主攻直线',
                '参与一传/防守的后排支援，提升轮次稳定',
                '与二传沟通背快、后排快球的使用时机',
                '发球加强压迫，争取直接得分或破坏一传'
            ]
        },
        libero: {
            name: '自由人',
            intro: '自由人是防守与接发球的指挥中枢，需要阅读对手进攻线路，稳定第一传并组织队友的防守站位与轮转衔接。',
            keyPoints: [
                '接发球优先稳准，呼叫队友分区，降低失误',
                '阅读二传习惯与攻手落点，提前站位',
                '防守后快速传导到位，确保二传可用球',
                '指挥后排覆盖与自由接应，保持沟通',
                '发起快传/吊传协助反击，提高转换效率'
            ]
        },
        defensive: {
            name: '防守队员',
            intro: '防守队员侧重后排保护与防反连接，需要灵活移动、分担一传，并在转换中为二传或接应创造衔接角度。',
            keyPoints: [
                '后排分区明确，优先盯直线或短球空档',
                '接发球角度控制，保证高弧度可组织',
                '反击时传导给二传或直接吊传到安全区',
                '观察对手扣发节奏，调整站位与重心',
                '持续呼应队友，确保覆盖链不断档'
            ]
        }
    };

    const content = roleContent[positionId] || {
        name: '当前位置',
        intro: '围绕你选择的位置，理解职责与配合，确保攻防衔接流畅。',
        keyPoints: [
            '明确自己在轮次中的站位与责任',
            '与二传/自由人保持沟通，减少失误',
            '根据对手特点调整拦防策略',
            '转换球时迅速落位，保持节奏',
            '练习专项技能，补齐短板'
        ]
    };

    return {
        intro: content.intro,
        keyPoints: content.keyPoints,
        badge: `当前角色：${content.name}`
    };
}

function getCurrentPositionId() {
    if (AppState.selectedPosition) {
        return AppState.selectedPosition;
    }

    const nameToIdMap = {
        '主攻': 'outside',
        '主攻手': 'outside',
        '副攻': 'middle',
        '副攻手': 'middle',
        '二传': 'setter',
        '接应': 'opposite',
        '自由人': 'libero',
        '防守队员': 'defensive'
    };

    if (AppState.user.mainPosition && nameToIdMap[AppState.user.mainPosition]) {
        return nameToIdMap[AppState.user.mainPosition];
    }

    return 'libero';
}

/**
 * 开始战术测试
 * 注意：tactics.js 中已经定义了此函数的完整实现
 * 由于 tactics.js 在 app.js 之前加载，所以实际的实现在 tactics.js 中
 * 这里的定义会被 tactics.js 中的实现覆盖（如果后加载则不会）
 * 为了确保兼容性，这里调用全局版本
 */
async function startTacticsTest() {
    // 如果 tactics.js 已加载，直接调用它的实现
    // 否则调用备用版本
    if (typeof window.startTacticsTestModule === 'function') {
        await window.startTacticsTestModule();
    } else if (typeof startTacticsTestModule === 'function') {
        await startTacticsTestModule();
    } else {
        console.error('战术测试功能未正确加载');
        showToast('战术测试功能加载失败', 'error');
    }
}

/**
 * 渲染底部导航栏
 */
function renderBottomNav() {
    return `
        <div class="fixed bottom-0 left-0 right-0 bg-white bg-opacity-95 border-t border-gray-200 shadow-lg">
            <div class="max-w-screen-xl mx-auto px-4">
                <div class="flex justify-around py-2">
                    <button onclick="navigateTo('home')" 
                            class="flex flex-col items-center py-2 px-6 ${AppState.currentPage === 'home' ? 'text-volleyball-orange' : 'text-gray-500'}">
                        <div class="relative">
                            <span class="text-2xl">🏠</span>
                            ${AppState.currentPage === 'home' ? '<div class="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-1 h-1 bg-volleyball-orange rounded-full"></div>' : ''}
                        </div>
                        <span class="text-xs mt-1">主页</span>
                    </button>
                    
                    <button onclick="navigateTo('leaderboard')" 
                            class="flex flex-col items-center py-2 px-6 text-gray-500">
                        <span class="text-2xl">🏆</span>
                        <span class="text-xs mt-1">排行榜</span>
                    </button>
                    
                    <button onclick="navigateTo('profile')" 
                            class="flex flex-col items-center py-2 px-6 text-gray-500">
                        <span class="text-2xl">👤</span>
                        <span class="text-xs mt-1">我的</span>
                    </button>
                    
                    <button onclick="navigateTo('settings')" 
                            class="flex flex-col items-center py-2 px-6 text-gray-500">
                        <span class="text-2xl">⚙️</span>
                        <span class="text-xs mt-1">设置</span>
                    </button>
                </div>
            </div>
        </div>
    `;
}

/**
 * 页面导航
 */
function navigateTo(page) {
    AppState.currentPage = page;
    
    // 滚动到顶部
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    switch(page) {
        case 'home':
            renderMainPage();
            break;
        case 'leaderboard':
            renderLeaderboardPage();
            break;
        case 'profile':
            renderProfilePage();
            break;
        case 'settings':
            renderSettingsPage();
            break;
        default:
            renderMainPage();
    }
}

/**
 * 显示/隐藏加载状态
 */
function showLoading(show) {
    const loading = document.getElementById('loading');
    if (show) {
        loading.classList.remove('hidden');
    } else {
        loading.classList.add('hidden');
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

