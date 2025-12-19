// cstimer에서 스크램블을 찾고 솔루션 버튼을 추가하는 스크립트
console.log('Cross Solver Extension Loaded');

// 솔루션을 표시할 div를 만드는 함수
function createSolutionDiv() {
    const solutionDiv = document.createElement('div');
    solutionDiv.id = 'cross-solution-display';
    solutionDiv.style.cssText = `
        position: fixed;
        top: 10px;
        right: 10px;
        width: 400px;
        max-height: 500px;
        min-width: 300px;
        min-height: 200px;
        background: white;
        border: 2px solid #4CAF50;
        border-radius: 8px;
        z-index: 10000;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        font-family: Arial, sans-serif;
        display: none;
        overflow: hidden;
        resize: both;
        font-size: 14px;
    `;
    solutionDiv.setAttribute('data-zoom-level', '1');
    
    // 드래그 가능한 헤더 추가
    const header = document.createElement('div');
    header.style.cssText = `
        background: #4CAF50;
        color: white;
        padding: 8px 15px;
        cursor: move;
        user-select: none;
        font-weight: bold;
        display: flex;
        justify-content: space-between;
        align-items: center;
    `;
    header.innerHTML = `
        <span>🧩 Cross Solutions</span>
        <div style="display: flex; align-items: center; gap: 5px;">
            <button id="zoom-out-btn" style="background: rgba(255,255,255,0.2); border: none; color: white; cursor: pointer; padding: 2px 6px; border-radius: 3px; font-size: 12px;">−</button>
            <span id="zoom-level" style="font-size: 11px; min-width: 30px; text-align: center;">100%</span>
            <button id="zoom-in-btn" style="background: rgba(255,255,255,0.2); border: none; color: white; cursor: pointer; padding: 2px 6px; border-radius: 3px; font-size: 12px;">+</button>
            <button id="fullscreen-btn" style="background: rgba(255,255,255,0.2); border: none; color: white; cursor: pointer; padding: 2px 6px; border-radius: 3px; font-size: 10px; margin-left: 5px;">⛶</button>
            <span style="cursor: pointer; padding: 0 5px;" onclick="document.getElementById('cross-solution-display').style.display='none'">✕</span>
        </div>
    `;
    
    // 컨텐트 영역
    const content = document.createElement('div');
    content.id = 'solution-content';
    content.style.cssText = `
        padding: 15px;
        height: calc(100% - 40px);
        overflow-y: auto;
    `;
    
    solutionDiv.appendChild(header);
    solutionDiv.appendChild(content);
    document.body.appendChild(solutionDiv);
    
    // 드래그 기능 추가
    makeDraggable(solutionDiv, header);
    
    // 확대/축소 기능 추가
    setupZoomControls(solutionDiv);
    
    return solutionDiv;
}

// 확대/축소 컨트롤 설정
function setupZoomControls(solutionDiv) {
    const zoomInBtn = document.getElementById('zoom-in-btn');
    const zoomOutBtn = document.getElementById('zoom-out-btn');
    const fullscreenBtn = document.getElementById('fullscreen-btn');
    const zoomLevelDisplay = document.getElementById('zoom-level');
    
    let zoomLevel = 1;
    const zoomStep = 0.1;
    const minZoom = 0.5;
    const maxZoom = 2.0;
    
    function updateZoom() {
        const percentage = Math.round(zoomLevel * 100);
        zoomLevelDisplay.textContent = percentage + '%';
        solutionDiv.style.fontSize = (14 * zoomLevel) + 'px';
        solutionDiv.setAttribute('data-zoom-level', zoomLevel.toString());
        
        // 줌 레벨에 따라 창 크기도 조절
        const currentWidth = parseInt(solutionDiv.style.width) || 400;
        const currentHeight = parseInt(solutionDiv.style.maxHeight) || 500;
        
        if (zoomLevel > 1) {
            solutionDiv.style.width = Math.min(currentWidth * 1.1, window.innerWidth * 0.9) + 'px';
            solutionDiv.style.maxHeight = Math.min(currentHeight * 1.1, window.innerHeight * 0.9) + 'px';
        }
    }
    
    zoomInBtn.onclick = function(e) {
        e.stopPropagation();
        if (zoomLevel < maxZoom) {
            zoomLevel = Math.min(zoomLevel + zoomStep, maxZoom);
            updateZoom();
        }
    };
    
    zoomOutBtn.onclick = function(e) {
        e.stopPropagation();
        if (zoomLevel > minZoom) {
            zoomLevel = Math.max(zoomLevel - zoomStep, minZoom);
            updateZoom();
        }
    };
    
    fullscreenBtn.onclick = function(e) {
        e.stopPropagation();
        toggleFullscreen(solutionDiv);
    };
}

// 전체화면 토글 기능
function toggleFullscreen(solutionDiv) {
    const isFullscreen = solutionDiv.classList.contains('fullscreen-mode');
    
    if (isFullscreen) {
        // 전체화면 해제
        solutionDiv.classList.remove('fullscreen-mode');
        solutionDiv.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            width: 400px;
            max-height: 500px;
            min-width: 300px;
            min-height: 200px;
            background: white;
            border: 2px solid #4CAF50;
            border-radius: 8px;
            z-index: 10000;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            font-family: Arial, sans-serif;
            display: block;
            overflow: hidden;
            resize: both;
            font-size: ${14 * parseFloat(solutionDiv.getAttribute('data-zoom-level') || '1')}px;
        `;
        document.getElementById('fullscreen-btn').textContent = '⛶';
    } else {
        // 전체화면 모드
        solutionDiv.classList.add('fullscreen-mode');
        solutionDiv.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            max-height: none;
            min-width: none;
            min-height: none;
            background: white;
            border: none;
            border-radius: 0;
            z-index: 10001;
            box-shadow: none;
            font-family: Arial, sans-serif;
            display: block;
            overflow: hidden;
            resize: none;
            font-size: ${14 * parseFloat(solutionDiv.getAttribute('data-zoom-level') || '1')}px;
        `;
        document.getElementById('fullscreen-btn').textContent = '⛶';
    }
}

// 키보드 단축키 설정
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        const solutionDiv = document.getElementById('cross-solution-display');
        if (!solutionDiv || solutionDiv.style.display === 'none') return;
        
        // Ctrl + Plus: 확대
        if (e.ctrlKey && (e.key === '+' || e.key === '=')) {
            e.preventDefault();
            const zoomInBtn = document.getElementById('zoom-in-btn');
            if (zoomInBtn) zoomInBtn.click();
        }
        
        // Ctrl + Minus: 축소
        if (e.ctrlKey && e.key === '-') {
            e.preventDefault();
            const zoomOutBtn = document.getElementById('zoom-out-btn');
            if (zoomOutBtn) zoomOutBtn.click();
        }
        
        // F11 또는 Ctrl + Enter: 전체화면 토글
        if (e.key === 'F11' || (e.ctrlKey && e.key === 'Enter')) {
            e.preventDefault();
            const fullscreenBtn = document.getElementById('fullscreen-btn');
            if (fullscreenBtn) fullscreenBtn.click();
        }
        
        // ESC: 창 닫기 (전체화면일 때는 전체화면 해제)
        if (e.key === 'Escape') {
            if (solutionDiv.classList.contains('fullscreen-mode')) {
                e.preventDefault();
                const fullscreenBtn = document.getElementById('fullscreen-btn');
                if (fullscreenBtn) fullscreenBtn.click();
            } else {
                solutionDiv.style.display = 'none';
            }
        }
    });
}

// 드래그 기능 구현
function makeDraggable(element, handle) {
    let isDragging = false;
    let startX, startY, initialLeft, initialTop;
    
    handle.addEventListener('mousedown', function(e) {
        isDragging = true;
        startX = e.clientX;
        startY = e.clientY;
        
        const rect = element.getBoundingClientRect();
        initialLeft = rect.left;
        initialTop = rect.top;
        
        document.addEventListener('mousemove', drag);
        document.addEventListener('mouseup', stopDrag);
        e.preventDefault();
    });
    
    function drag(e) {
        if (!isDragging) return;
        
        const dx = e.clientX - startX;
        const dy = e.clientY - startY;
        
        element.style.left = (initialLeft + dx) + 'px';
        element.style.top = (initialTop + dy) + 'px';
        element.style.right = 'auto'; // 오른쪽 고정 해제
    }
    
    function stopDrag() {
        isDragging = false;
        document.removeEventListener('mousemove', drag);
        document.removeEventListener('mouseup', stopDrag);
    }
}

// 스크램블 찾기 함수
function findScramble() {
    // cstimer에서 스크램블을 찾는 여러 가지 방법
    const scrambleSelectors = [
        'div[style*="font-size: 0.95em"]',  // font-size가 0.95em으로 변경됨
        'div[style*="font-size: 1em"]',     // 기존 1em도 유지 (호환성을 위해)
        '#scrambleDiv',
        '.scramble',
        'div:contains("scramble")'
    ];
    
    for (const selector of scrambleSelectors) {
        const element = document.querySelector(selector);
        if (element && element.textContent.trim()) {
            const text = element.textContent.trim();
            // 루빅스 큐브 스크램블 패턴 확인 (U, R, F, D, L, B와 ', 2가 포함된)
            if (/[URFDLB]['2]?\s/.test(text)) {
                return text;
            }
        }
    }
    
    // 대안: 페이지의 모든 div에서 스크램블 패턴 찾기
    const allDivs = document.querySelectorAll('div');
    for (const div of allDivs) {
        const text = div.textContent.trim();
        if (text && /^[URFDLB]['2]?\s+[URFDLB]/.test(text) && text.length > 10 && text.length < 200) {
            return text;
        }
    }
    
    return null;
}

// 솔루션 요청 함수
async function getSolution(scramble) {
    try {
        const encodedScramble = encodeURIComponent(scramble);
        const response = await fetch(`http://localhost:5000/solve?scramble=${encodedScramble}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error getting solution:', error);
        return { error: error.message };
    }
}

// 자동 솔루션 업데이트 관련 변수들
let currentScramble = '';
let autoSolveEnabled = false;
let isProcessing = false;

// 자동으로 솔루션을 업데이트하는 함수
async function autoUpdateSolution() {
    if (isProcessing) return;
    
    const newScramble = findScramble();
    if (!newScramble || newScramble === currentScramble) {
        return; // 스크램블이 없거나 이전과 같으면 패스
    }
    
    currentScramble = newScramble;
    isProcessing = true;
    
    console.log('🔄 Auto-solving new scramble:', newScramble);
    
    let solutionDiv = document.getElementById('cross-solution-display');
    if (!solutionDiv) {
        solutionDiv = createSolutionDiv();
    }
    
    // 로딩 표시
    const contentDiv = document.getElementById('solution-content');
    if (contentDiv) {
        contentDiv.innerHTML = `
            <div style="text-align: center; padding: 20px;">
                <div style="font-size: 16px; margin-bottom: 10px;">🔄 Auto-solving...</div>
                <div style="font-size: 12px; color: #666;">${newScramble}</div>
            </div>
        `;
    }
    
    // 창 표시
    solutionDiv.style.display = 'block';
    
    try {
        const solution = await getSolution(newScramble);
        displaySolution(solution, solutionDiv);
    } catch (error) {
        if (contentDiv) {
            contentDiv.innerHTML = `
                <div style="color: red; text-align: center; padding: 20px;">
                    ❌ Auto-solve failed<br>
                    <small>${error.message}</small>
                </div>
            `;
        }
    } finally {
        isProcessing = false;
    }
}

// 솔루션 표시 함수
function displaySolution(solutionData, solutionDiv) {
    const contentDiv = document.getElementById('solution-content');
    if (!contentDiv) return;
    
    if (solutionData.error) {
        contentDiv.innerHTML = `
            <div style="color: red; font-weight: bold;">❌ Error</div>
            <div style="font-size: 12px; margin-top: 5px;">${solutionData.error}</div>
        `;
        return;
    }
    
    const totalSolutions = solutionData.total_solutions || solutionData.solutions.length;
    const bestLength = solutionData.best_length;
    
    // 헤더 부분
    let html = `
        <div style="font-weight: bold; color: #4CAF50; margin-bottom: 10px;">
            ✅ ${totalSolutions} Solutions Found!
        </div>
        <div style="margin-bottom: 15px; font-size: 12px; color: #666;">
            <strong>Best:</strong> ${bestLength} moves | <strong>Time:</strong> ${solutionData.search_time.toFixed(3)}s
        </div>
    `;
    
    // 솔루션들을 표시 (최대 10개)
    const solutionsToShow = solutionData.solutions.slice(0, 10);
    
    html += `<div style="max-height: 300px; overflow-y: auto;">`;
    
    solutionsToShow.forEach((solution, index) => {
        const isOptimal = solution.is_optimal || solution.move_count === bestLength;
        const backgroundColor = isOptimal ? '#e8f5e8' : '#f9f9f9';
        const borderColor = isOptimal ? '#4CAF50' : '#ddd';
        const optimalBadge = isOptimal ? '<span style="background: #4CAF50; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px; margin-left: 5px;">OPTIMAL</span>' : '';
        
        html += `
            <div style="border: 1px solid ${borderColor}; background: ${backgroundColor}; padding: 8px; margin-bottom: 8px; border-radius: 4px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                    <div style="font-weight: bold; font-size: 12px;">
                        #${index + 1} ${solution.face} (${solution.move_count} moves)${optimalBadge}
                    </div>
                </div>
                <div style="background: white; padding: 6px; border-radius: 3px; font-family: monospace; font-size: 11px; word-break: break-all;">
                    ${solution.solution_string}
                </div>
                <button onclick="navigator.clipboard.writeText('${solution.solution_string}'); this.textContent='Copied!'; setTimeout(() => this.textContent='Copy', 1500)" 
                        style="margin-top: 5px; padding: 3px 8px; background: #2196F3; color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 10px;">
                    Copy
                </button>
            </div>
        `;
    });
    
    html += `</div>`;
    
    // 하단 버튼들
    html += `
        <div style="margin-top: 10px; text-align: center;">
            <button onclick="navigator.clipboard.writeText('${solutionData.solutions[0].solution_string}'); this.textContent='Best Copied!'; setTimeout(() => this.textContent='Copy Best', 1500)" 
                    style="margin-right: 5px; padding: 5px 10px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px;">
                Copy Best
            </button>
        </div>
    `;
    
    contentDiv.innerHTML = html;
}

// 메인 함수
function addSolveButton() {
    // 이미 버튼이 있다면 제거
    const existingButton = document.getElementById('cross-solve-button');
    if (existingButton) {
        existingButton.remove();
    }
    
    // 솔루션 표시 div 생성
    let solutionDiv = document.getElementById('cross-solution-display');
    if (!solutionDiv) {
        solutionDiv = createSolutionDiv();
    }
    
    // 솔브 버튼 생성
    const solveButton = document.createElement('button');
    solveButton.id = 'cross-solve-button';
    updateButtonText(solveButton);
    solveButton.style.cssText = `
        position: fixed;
        top: 10px;
        left: 10px;
        z-index: 10000;
        background: #4CAF50;
        color: white;
        border: none;
        padding: 10px 15px;
        border-radius: 5px;
        font-weight: bold;
        cursor: pointer;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        min-width: 180px;
    `;
    
    solveButton.onclick = function() {
        if (autoSolveEnabled) {
            // 자동 모드 끄기
            autoSolveEnabled = false;
            currentScramble = '';
            updateButtonText(solveButton);
            console.log('🔴 Auto-solve disabled');
        } else {
            // 수동으로 한 번 실행하거나 자동 모드 켜기
            if (solveButton.textContent.includes('Enable Auto')) {
                autoSolveEnabled = true;
                updateButtonText(solveButton);
                console.log('🟢 Auto-solve enabled');
                autoUpdateSolution(); // 즉시 한 번 실행
            } else {
                // 수동 실행
                manualSolve();
            }
        }
    };
    
    document.body.appendChild(solveButton);
    
    // 자동 모드가 켜져있으면 즉시 실행
    if (autoSolveEnabled) {
        setTimeout(autoUpdateSolution, 1000);
    }
}

function updateButtonText(button) {
    if (autoSolveEnabled) {
        button.textContent = '🟢 Auto ON (Click to OFF)';
        button.style.background = '#FF9800';
    } else {
        button.textContent = '🧩 Enable Auto-Solve';
        button.style.background = '#4CAF50';
    }
}

async function manualSolve() {
    const solveButton = document.getElementById('cross-solve-button');
    const scramble = findScramble();
    
    if (!scramble) {
        alert('스크램블을 찾을 수 없습니다. cstimer 페이지에서 스크램블이 표시되어 있는지 확인하세요.');
        return;
    }
    
    console.log('Manual solve for scramble:', scramble);
    
    // 버튼 상태 변경
    solveButton.textContent = '🔄 Solving...';
    solveButton.disabled = true;
    
    let solutionDiv = document.getElementById('cross-solution-display');
    if (!solutionDiv) {
        solutionDiv = createSolutionDiv();
    }
    
    try {
        const solution = await getSolution(scramble);
        displaySolution(solution, solutionDiv);
        solutionDiv.style.display = 'block';
    } catch (error) {
        alert(`에러가 발생했습니다: ${error.message}`);
    } finally {
        // 버튼 상태 복구
        updateButtonText(solveButton);
        solveButton.disabled = false;
    }
}

// 페이지 로드 완료 후 버튼 추가
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        addSolveButton();
        setupKeyboardShortcuts();
    });
} else {
    addSolveButton();
    setupKeyboardShortcuts();
}

// 페이지 변경 감지 (SPA를 위해)
let lastUrl = location.href;
new MutationObserver(() => {
    const url = location.href;
    if (url !== lastUrl) {
        lastUrl = url;
        setTimeout(addSolveButton, 1000); // 페이지 변경 후 잠시 기다림
    }
}).observe(document, { subtree: true, childList: true });

// 스크램블 변경 감지를 위한 MutationObserver
const scrambleObserver = new MutationObserver((mutations) => {
    if (!autoSolveEnabled) return;
    
    let shouldCheck = false;
    mutations.forEach((mutation) => {
        if (mutation.type === 'childList' || mutation.type === 'characterData') {
            // 텍스트 변경이나 DOM 변경 감지
            shouldCheck = true;
        }
    });
    
    if (shouldCheck) {
        // 약간의 지연을 두고 체크 (너무 빈번한 호출 방지)
        setTimeout(autoUpdateSolution, 500);
    }
});

// 전체 document를 감시 (스크램블이 어디에 나타날지 모르므로)
setTimeout(() => {
    scrambleObserver.observe(document.body, { 
        childList: true, 
        subtree: true, 
        characterData: true 
    });
    console.log('🎯 Scramble auto-detection enabled');
}, 2000);