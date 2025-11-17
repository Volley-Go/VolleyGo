/**
 * 战术学习和测试模块
 */

/**
 * 开始战术测试（模块内部实现）
 */
async function startTacticsTestModule() {
    // 获取题库
    const tacticsData = await api.getTacticsQuestions();
    
    if (tacticsData.error) {
        showToast('获取题库失败，请稍后重试', 'error');
        return;
    }
    
    // 确定当前模块（默认基础轮转规则）
    const moduleName = AppState.tacticsTest.currentModule || '基础轮转规则';
    AppState.tacticsTest.currentModule = moduleName;

    // 随机选择5道题
    const allQuestions = tacticsData.questions || [];
    const selectedQuestions = selectRandomQuestions(allQuestions, 5);

    AppState.tacticsTest = {
        started: true,
        currentQuestion: 0,
        answers: [],
        questions: selectedQuestions,
        score: 0,
        currentModule: moduleName
    };
    
    closeDialog();
    renderTacticsTestDialog();
}

/**
 * 开始战术测试（全局函数）
 * 这是对外暴露的接口，供 app.js 调用
 */
async function startTacticsTest() {
    await startTacticsTestModule();
}

// 将函数暴露到全局作用域（作为备用）
if (typeof window !== 'undefined') {
    window.startTacticsTestModule = startTacticsTestModule;
}

/**
 * 随机选择题目
 */
function selectRandomQuestions(questions, count) {
    const shuffled = [...questions].sort(() => Math.random() - 0.5);
    return shuffled.slice(0, count);
}

/**
 * 渲染战术测试对话框
 */
function renderTacticsTestDialog() {
    const test = AppState.tacticsTest;
    const currentQ = test.questions[test.currentQuestion];
    const progress = ((test.currentQuestion) / test.questions.length * 100).toFixed(0);
    
    const dialogContainer = document.createElement('div');
    dialogContainer.id = 'dialog-overlay';
    dialogContainer.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4';
    
    dialogContainer.innerHTML = `
        <div class="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <!-- 头部 -->
            <div class="sticky top-0 bg-white border-b border-gray-200 p-6 z-10">
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-2xl font-bold text-gray-800">战术测试</h2>
                    <button onclick="closeDialog()" class="text-gray-400 hover:text-gray-600 text-2xl">✕</button>
                </div>
                
                <!-- 进度条 -->
                <div class="space-y-2">
                    <div class="flex justify-between text-sm text-gray-600">
                        <span>问题 ${test.currentQuestion + 1} / ${test.questions.length}</span>
                        <span>${progress}%</span>
                    </div>
                    <div class="w-full h-2 bg-gray-200 rounded-full">
                        <div class="h-2 bg-gradient-to-r from-volleyball-orange to-volleyball-dark-orange rounded-full transition-all duration-300" 
                             style="width: ${progress}%"></div>
                    </div>
                </div>
            </div>
            
            <!-- 题目内容 -->
            <div class="p-6">
                <!-- 题目 -->
                <div class="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-2xl p-6 mb-6">
                    <div class="flex items-start gap-3 mb-4">
                        <span class="px-3 py-1 bg-blue-500 text-white rounded-lg text-xs font-medium">
                            ${currentQ.difficulty}
                        </span>
                        <span class="px-3 py-1 bg-white bg-opacity-80 rounded-lg text-xs text-gray-700">
                            ${currentQ.category}
                        </span>
                    </div>
                    <h3 class="text-xl font-semibold text-gray-800">${currentQ.question}</h3>
                </div>
                
                <!-- 选项 -->
                <div class="space-y-3 mb-6">
                    ${currentQ.options.map((option, idx) => `
                        <button onclick="selectAnswer(${idx})" 
                                id="option-${idx}"
                                class="w-full text-left p-4 border-2 border-gray-200 rounded-xl hover:border-volleyball-orange transition-all flex items-center gap-3 answer-option">
                            <div class="w-6 h-6 border-2 border-gray-300 rounded-full flex-shrink-0"></div>
                            <span class="text-gray-700">${option}</span>
                        </button>
                    `).join('')}
                </div>
                
                <!-- 检查答案按钮 -->
                <button onclick="checkAnswer()" 
                        id="check-answer-btn"
                        class="w-full py-4 bg-volleyball-orange text-white rounded-xl font-semibold hover:shadow-lg transition-all opacity-50 cursor-not-allowed"
                        disabled>
                    检查答案
                </button>
                
                <!-- 答案解释（初始隐藏） -->
                <div id="answer-explanation" class="hidden mt-6">
                    <div class="bg-green-50 border border-green-200 rounded-xl p-5">
                        <h4 class="font-semibold text-green-900 mb-2 flex items-center gap-2">
                            <span>✓</span>
                            答案解析
                        </h4>
                        <p class="text-sm text-green-800" id="explanation-text"></p>
                    </div>
                    
                    <button onclick="nextQuestion()" 
                            class="w-full mt-4 py-4 bg-gradient-to-r from-volleyball-orange to-volleyball-dark-orange text-white rounded-xl font-semibold hover:shadow-lg transition-all">
                        ${test.currentQuestion < test.questions.length - 1 ? '下一题' : '查看结果'}
                        →
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(dialogContainer);
}

/**
 * 选择答案
 */
function selectAnswer(optionIndex) {
    // 清除之前的选中状态
    document.querySelectorAll('.answer-option').forEach(opt => {
        opt.classList.remove('border-volleyball-orange', 'bg-orange-50');
        opt.classList.add('border-gray-200');
        const circle = opt.querySelector('div');
        circle.classList.remove('bg-volleyball-orange', 'border-volleyball-orange');
        circle.classList.add('border-gray-300');
    });
    
    // 标记新选中的答案
    const selectedOption = document.getElementById(`option-${optionIndex}`);
    selectedOption.classList.add('border-volleyball-orange', 'bg-orange-50');
    selectedOption.classList.remove('border-gray-200');
    
    const circle = selectedOption.querySelector('div');
    circle.classList.add('bg-volleyball-orange', 'border-volleyball-orange');
    circle.classList.remove('border-gray-300');
    
    // 启用检查答案按钮
    const checkBtn = document.getElementById('check-answer-btn');
    checkBtn.classList.remove('opacity-50', 'cursor-not-allowed');
    checkBtn.disabled = false;
    
    // 保存选择
    AppState.tacticsTest.selectedAnswer = optionIndex;
}

/**
 * 检查答案
 */
function checkAnswer() {
    const test = AppState.tacticsTest;
    const currentQ = test.questions[test.currentQuestion];
    const selectedAnswer = test.selectedAnswer;
    
    if (selectedAnswer === undefined) return;
    
    const isCorrect = selectedAnswer === currentQ.correct_answer;
    
    // 记录答案
    test.answers.push({
        questionId: currentQ.id,
        selectedAnswer,
        isCorrect
    });
    
    if (isCorrect) {
        test.score++;
    }
    
    // 显示所有选项的正确/错误状态
    document.querySelectorAll('.answer-option').forEach((opt, idx) => {
        opt.classList.add('pointer-events-none');
        
        if (idx === currentQ.correct_answer) {
            opt.classList.add('border-green-500', 'bg-green-50');
            opt.classList.remove('border-gray-200', 'border-volleyball-orange');
            const circle = opt.querySelector('div');
            circle.innerHTML = '✓';
            circle.classList.add('bg-green-500', 'border-green-500', 'text-white');
        } else if (idx === selectedAnswer) {
            opt.classList.add('border-red-500', 'bg-red-50');
            opt.classList.remove('border-volleyball-orange', 'bg-orange-50');
            const circle = opt.querySelector('div');
            circle.innerHTML = '✕';
            circle.classList.add('bg-red-500', 'border-red-500', 'text-white');
        }
    });
    
    // 显示解释
    const explanationDiv = document.getElementById('answer-explanation');
    const explanationText = document.getElementById('explanation-text');
    explanationText.textContent = currentQ.explanation;
    explanationDiv.classList.remove('hidden');
    
    // 如果答对了，显示绿色边框
    if (isCorrect) {
        explanationDiv.classList.remove('bg-red-50', 'border-red-200');
        explanationDiv.classList.add('bg-green-50', 'border-green-200');
        explanationDiv.querySelector('h4').classList.remove('text-red-900');
        explanationDiv.querySelector('h4').classList.add('text-green-900');
        explanationDiv.querySelector('p').classList.remove('text-red-800');
        explanationDiv.querySelector('p').classList.add('text-green-800');
    } else {
        explanationDiv.classList.remove('bg-green-50', 'border-green-200');
        explanationDiv.classList.add('bg-red-50', 'border-red-200');
        explanationDiv.querySelector('h4').classList.remove('text-green-900');
        explanationDiv.querySelector('h4').classList.add('text-red-900');
        explanationDiv.querySelector('h4').querySelector('span').textContent = '✕';
        explanationDiv.querySelector('p').classList.remove('text-green-800');
        explanationDiv.querySelector('p').classList.add('text-red-800');
    }
    
    // 禁用检查按钮
    const checkBtn = document.getElementById('check-answer-btn');
    checkBtn.classList.add('hidden');
}

/**
 * 下一题
 */
function nextQuestion() {
    const test = AppState.tacticsTest;
    
    if (test.currentQuestion < test.questions.length - 1) {
        test.currentQuestion++;
        delete test.selectedAnswer;
        closeDialog();
        renderTacticsTestDialog();
    } else {
        // 显示测试结果
        showTestResults();
    }
}

/**
 * 显示测试结果
 */
function showTestResults() {
    const test = AppState.tacticsTest;
    const totalQuestions = test.questions.length;
    const correctAnswers = test.score;
    const percentage = (correctAnswers / totalQuestions * 100).toFixed(0);
    
    let level = '初级';
    let emoji = '📚';
    let message = '继续加油！';
    let stars = 1;
    let xp = 25;
    
    if (percentage >= 80) {
        level = '优秀';
        emoji = '🏆';
        message = '太棒了！你已经掌握了这个战术！';
        stars = 3;
        xp = 50;
    } else if (percentage >= 60) {
        level = '良好';
        emoji = '🌟';
        message = '不错！再复习一下会更好！';
        stars = 2;
        xp = 35;
    }
    
    // 更新用户XP和星星
    AppState.user.xp += xp;
    AppState.user.stars += stars;

    // 根据完成的模块解锁后续内容
    unlockTacticsModule(test.currentModule);
    
    closeDialog();
    
    const dialogContainer = document.createElement('div');
    dialogContainer.id = 'dialog-overlay';
    dialogContainer.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4';
    
    dialogContainer.innerHTML = `
        <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 text-center">
            <div class="text-8xl mb-6 animate-bounce">${emoji}</div>
            <h2 class="text-3xl font-bold text-gray-800 mb-2">测试完成！</h2>
            <p class="text-lg text-gray-600 mb-6">${message}</p>
            
            <!-- 得分 -->
            <div class="bg-gradient-to-br from-orange-50 to-yellow-50 rounded-2xl p-6 mb-6">
                <div class="text-5xl font-bold text-volleyball-orange mb-2">
                    ${correctAnswers}/${totalQuestions}
                </div>
                <p class="text-gray-600">正确率: ${percentage}%</p>
            </div>
            
            <!-- 奖励 -->
            <div class="bg-green-50 border border-green-200 rounded-xl p-4 mb-6">
                <h4 class="font-semibold text-green-900 mb-3">获得奖励</h4>
                <div class="flex justify-center gap-3">
                    <span class="px-4 py-2 bg-yellow-100 border border-yellow-200 rounded-lg font-medium">
                        ⭐ ${stars} 星
                    </span>
                    <span class="px-4 py-2 bg-blue-500 text-white rounded-lg font-medium">
                        💫 ${xp} XP
                    </span>
                </div>
            </div>
            
            <!-- 按钮 -->
            <div class="space-y-3">
                <button onclick="reviewAnswers()" 
                        class="w-full py-3 border-2 border-volleyball-orange text-volleyball-orange rounded-xl font-semibold hover:bg-volleyball-orange hover:text-white transition-all">
                    查看答案解析
                </button>
                <button onclick="finishTest()" 
                        class="w-full py-3 bg-gradient-to-r from-volleyball-orange to-volleyball-dark-orange text-white rounded-xl font-semibold hover:shadow-lg transition-all">
                    完成
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(dialogContainer);
    
    // 播放完成音效（如果有）
    playSuccessSound();
}

/**
 * 查看答案解析
 */
function reviewAnswers() {
    const test = AppState.tacticsTest;
    
    closeDialog();
    
    const dialogContainer = document.createElement('div');
    dialogContainer.id = 'dialog-overlay';
    dialogContainer.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4';
    
    dialogContainer.innerHTML = `
        <div class="bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div class="sticky top-0 bg-white border-b border-gray-200 p-6 flex justify-between items-center z-10">
                <h2 class="text-2xl font-bold text-gray-800">答案解析</h2>
                <button onclick="finishTest()" class="text-gray-400 hover:text-gray-600 text-2xl">✕</button>
            </div>
            
            <div class="p-6 space-y-4">
                ${test.questions.map((q, qIdx) => {
                    const userAnswer = test.answers[qIdx];
                    const isCorrect = userAnswer.isCorrect;
                    
                    return `
                        <div class="border-2 ${isCorrect ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'} rounded-xl p-5">
                            <div class="flex items-start justify-between mb-3">
                                <h4 class="font-semibold text-gray-800">问题 ${qIdx + 1}</h4>
                                <span class="text-2xl">${isCorrect ? '✓' : '✕'}</span>
                            </div>
                            <p class="text-gray-700 mb-3">${q.question}</p>
                            
                            <div class="space-y-2 mb-3">
                                <div class="flex items-center gap-2">
                                    <span class="text-sm text-gray-600">你的答案:</span>
                                    <span class="px-3 py-1 ${isCorrect ? 'bg-green-100' : 'bg-red-100'} rounded-lg text-sm">
                                        ${q.options[userAnswer.selectedAnswer]}
                                    </span>
                                </div>
                                ${!isCorrect ? `
                                    <div class="flex items-center gap-2">
                                        <span class="text-sm text-gray-600">正确答案:</span>
                                        <span class="px-3 py-1 bg-green-100 rounded-lg text-sm">
                                            ${q.options[q.correct_answer]}
                                        </span>
                                    </div>
                                ` : ''}
                            </div>
                            
                            <div class="bg-white bg-opacity-50 rounded-lg p-3">
                                <p class="text-sm text-gray-700">${q.explanation}</p>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
            
            <div class="sticky bottom-0 bg-white border-t border-gray-200 p-6">
                <button onclick="finishTest()" 
                        class="w-full py-3 bg-volleyball-orange text-white rounded-xl font-semibold hover:shadow-lg transition-all">
                    返回主页
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(dialogContainer);
}

/**
 * 完成测试
 */
function finishTest() {
    const completedModule = AppState.tacticsTest.currentModule;

    unlockTacticsModule(completedModule);

    // 重置测试状态
    AppState.tacticsTest = {
        started: false,
        currentQuestion: 0,
        answers: [],
        questions: [],
        score: 0,
        currentModule: null
    };
    
    closeDialog();
    
    // 显示完成提示
    showToast('恭喜完成战术测试！', 'success');
    
    // 刷新主页面以显示新的XP和星星
    renderMainPage();
}

/**
 * 根据已完成的模块解锁后续内容
 */
function unlockTacticsModule(completedModule) {
    if (completedModule === '基础轮转规则' && !AppState.unlockedTactics.includes('位置与职责')) {
        AppState.unlockedTactics.push('位置与职责');
    }
}

/**
 * 播放成功音效
 */
function playSuccessSound() {
    // 这里可以添加音效播放逻辑
    // const audio = new Audio('/assets/sounds/success.mp3');
    // audio.play();
}

