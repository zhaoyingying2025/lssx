/* 离散数学智能教学体 - 全局JavaScript */

// ==================== 移动端兼容性工具函数 ====================
(function() {
    'use strict';

    // 检测移动端
    window.isMobile = function() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) 
            || window.innerWidth < 992;
    };

    // 检测是否为微信浏览器
    window.isWeChat = function() {
        return /MicroMessenger/i.test(navigator.userAgent);
    };

    // 检测是否为iOS设备
    window.isIOS = function() {
        return /iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
    };

    // 检测是否为Safari浏览器
    window.isSafari = function() {
        return /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
    };

    // ==================== FastClick 实现（解决点击延迟） ====================
    // 轻量级 FastClick 实现，解决移动端300ms点击延迟
    function FastClick(layer) {
        let touchStartX = 0;
        let touchStartY = 0;
        let touchStartTime = 0;
        let trackingClick = false;
        let trackingClickStartTarget = null;

        function onClick(e) {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') {
                return;
            }
            if (trackingClick && e.timeStamp - touchStartTime > 100) {
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
            trackingClick = false;
        }

        function onTouchStart(e) {
            const touch = e.touches[0];
            touchStartX = touch.clientX;
            touchStartY = touch.clientY;
            touchStartTime = e.timeStamp;
            trackingClick = true;
            trackingClickStartTarget = e.target;
        }

        function onTouchMove(e) {
            if (!trackingClick) return;
            const touch = e.touches[0];
            const dx = Math.abs(touch.clientX - touchStartX);
            const dy = Math.abs(touch.clientY - touchStartY);
            // 移动超过10px则取消点击
            if (dx > 10 || dy > 10) {
                trackingClick = false;
            }
        }

        function onTouchEnd(e) {
            if (!trackingClick) return;
            if (e.timeStamp - touchStartTime > 700) {
                trackingClick = false;
                return;
            }
            // 触发立即点击
            const target = e.target;
            const clickEvent = document.createEvent('MouseEvents');
            clickEvent.initMouseEvent('click', true, true, window, 1, 0, 0, touchStartX, touchStartY, false, false, false, false, 0, null);
            clickEvent.forwardedTouchEvent = true;
            
            // 阻止默认的延迟click事件
            e.preventDefault();
            
            trackingClick = false;
            target.dispatchEvent(clickEvent);
        }

        layer.addEventListener('click', onClick, true);
        layer.addEventListener('touchstart', onTouchStart, { passive: false });
        layer.addEventListener('touchmove', onTouchMove, { passive: false });
        layer.addEventListener('touchend', onTouchEnd, { passive: false });

        return {
            destroy: function() {
                layer.removeEventListener('click', onClick, true);
                layer.removeEventListener('touchstart', onTouchStart);
                layer.removeEventListener('touchmove', onTouchMove);
                layer.removeEventListener('touchend', onTouchEnd);
            }
        };
    }

    window.FastClick = FastClick;

    // ==================== 统一事件绑定工具 ====================
    // 兼容触摸和点击事件，解决点击穿透问题
    window.addTapEvent = function(element, handler, options) {
        options = options || {};
        const tapThreshold = options.threshold || 10; // 移动阈值
        const timeThreshold = options.time || 500; // 时间阈值

        let startX = 0, startY = 0, startTime = 0, isMoving = false;
        let touchHandled = false; // 标记是否已通过touch事件触发

        // 检测是否真正支持触摸事件（不仅仅是userAgent判断）
        const supportsTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

        function onTouchStart(e) {
            const touch = e.touches[0];
            startX = touch.clientX;
            startY = touch.clientY;
            startTime = Date.now();
            isMoving = false;
            touchHandled = false;
        }

        function onTouchMove(e) {
            const touch = e.touches[0];
            const dx = Math.abs(touch.clientX - startX);
            const dy = Math.abs(touch.clientY - startY);
            if (dx > tapThreshold || dy > tapThreshold) {
                isMoving = true;
            }
        }

        function onTouchEnd(e) {
            if (isMoving) return;
            if (Date.now() - startTime > timeThreshold) return;

            // 标记已通过touch处理
            touchHandled = true;

            // 阻止后续的click事件（防止穿透）
            e.preventDefault();

            const touch = e.changedTouches[0];
            const clickEvent = new MouseEvent('tap', {
                bubbles: true,
                cancelable: true,
                view: window,
                clientX: touch.clientX,
                clientY: touch.clientY
            });
            e.target.dispatchEvent(clickEvent);

            // 直接调用handler
            handler.call(e.target, {
                type: 'tap',
                target: e.target,
                clientX: touch.clientX,
                clientY: touch.clientY,
                preventDefault: function() { e.preventDefault(); },
                stopPropagation: function() { e.stopPropagation(); }
            });
        }

        function onClick(e) {
            // 如果已经通过touch事件处理，则忽略click事件
            if (touchHandled) {
                touchHandled = false; // 重置标记
                return;
            }
            // 直接调用handler（无论桌面端还是移动端，只要没有touch事件触发就处理click）
            // 这样可以解决userAgent是移动端但实际不支持touch的环境
            if (!supportsTouch || !window.isMobile()) {
                handler.call(e.target, e);
            }
        }

        // 触摸事件（仅当设备支持触摸时才绑定）
        if (supportsTouch) {
            element.addEventListener('touchstart', onTouchStart, { passive: true });
            element.addEventListener('touchmove', onTouchMove, { passive: true });
            element.addEventListener('touchend', onTouchEnd, { passive: false });
        }

        // 点击事件（总是绑定，桌面端和移动端都需要）
        element.addEventListener('click', onClick, false);

        return {
            destroy: function() {
                if (supportsTouch) {
                    element.removeEventListener('touchstart', onTouchStart);
                    element.removeEventListener('touchmove', onTouchMove);
                    element.removeEventListener('touchend', onTouchEnd);
                }
                element.removeEventListener('click', onClick);
            }
        };
    };

    // ==================== 防止点击穿透 ====================
    window.preventClickThrough = function() {
        document.addEventListener('touchend', function(e) {
            // 记录触摸结束位置
            const touch = e.changedTouches[0];
            window._lastTouchEnd = {
                x: touch.clientX,
                y: touch.clientY,
                time: Date.now(),
                target: e.target
            };
        }, { passive: true });

        // 拦截touchend后300ms内的click事件
        document.addEventListener('click', function(e) {
            if (window._lastTouchEnd) {
                const dx = Math.abs(e.clientX - window._lastTouchEnd.x);
                const dy = Math.abs(e.clientY - window._lastTouchEnd.y);
                const dt = Date.now() - window._lastTouchEnd.time;
                
                // 如果点击位置和触摸结束位置接近，且时间间隔小于300ms，认为是穿透
                if (dx < 10 && dy < 10 && dt < 300) {
                    if (e.target !== window._lastTouchEnd.target) {
                        e.preventDefault();
                        e.stopPropagation();
                        return false;
                    }
                }
            }
        }, true);
    };

    // ==================== 滑动手势支持 ====================
    window.addSwipeEvent = function(element, options) {
        options = options || {};
        const threshold = options.threshold || 50; // 滑动距离阈值
        const restraint = options.restraint || 100; // 垂直方向最大偏移
        const allowedTime = options.time || 500; // 最大滑动时间
        
        let startX = 0, startY = 0, startTime = 0;

        function onTouchStart(e) {
            const touch = e.changedTouches[0];
            startX = touch.clientX;
            startY = touch.clientY;
            startTime = Date.now();
        }

        function onTouchEnd(e) {
            const touch = e.changedTouches[0];
            const distX = touch.clientX - startX;
            const distY = touch.clientY - startY;
            const elapsedTime = Date.now() - startTime;
            
            if (elapsedTime <= allowedTime) {
                if (Math.abs(distX) >= threshold && Math.abs(distY) <= restraint) {
                    // 水平滑动
                    const direction = distX < 0 ? 'left' : 'right';
                    const event = new CustomEvent('swipe', {
                        detail: { direction: direction, distance: Math.abs(distX) },
                        bubbles: true
                    });
                    element.dispatchEvent(event);
                    
                    if (direction === 'left' && options.onSwipeLeft) options.onSwipeLeft();
                    if (direction === 'right' && options.onSwipeRight) options.onSwipeRight();
                } else if (Math.abs(distY) >= threshold && Math.abs(distX) <= restraint) {
                    // 垂直滑动
                    const direction = distY < 0 ? 'up' : 'down';
                    const event = new CustomEvent('swipe', {
                        detail: { direction: direction, distance: Math.abs(distY) },
                        bubbles: true
                    });
                    element.dispatchEvent(event);
                    
                    if (direction === 'up' && options.onSwipeUp) options.onSwipeUp();
                    if (direction === 'down' && options.onSwipeDown) options.onSwipeDown();
                }
            }
        }

        element.addEventListener('touchstart', onTouchStart, { passive: true });
        element.addEventListener('touchend', onTouchEnd, { passive: true });

        return {
            destroy: function() {
                element.removeEventListener('touchstart', onTouchStart);
                element.removeEventListener('touchend', onTouchEnd);
            }
        };
    };
})();

// ==================== 页面加载动画 ====================
(function() {
    function hideLoader() {
        const loader = document.querySelector('.page-loader');
        if (loader) {
            // 使用 requestAnimationFrame 确保平滑过渡
            requestAnimationFrame(function() {
                setTimeout(function() {
                    loader.classList.add('hidden');
                    // 确保loader完全移除，不再拦截点击
                    setTimeout(function() {
                        loader.style.display = 'none';
                        loader.style.pointerEvents = 'none';
                    }, 600);
                }, 300);
            });
        }
    }

    // 多种触发方式确保loader一定能隐藏
    if (document.readyState === 'complete') {
        hideLoader();
    } else {
        // DOMContentLoaded 触发
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(hideLoader, 200);
        });
        // window load 触发（后备）
        window.addEventListener('load', function() {
            hideLoader();
        });
        // 最大超时保护：3秒后强制隐藏
        setTimeout(function() {
            const loader = document.querySelector('.page-loader');
            if (loader && !loader.classList.contains('hidden')) {
                loader.classList.add('hidden');
                loader.style.display = 'none';
                loader.style.pointerEvents = 'none';
            }
        }, 3000);
    }
})();

// ==================== 滚动指示器 ====================
(function() {
    const scrollIndicator = document.createElement('div');
    scrollIndicator.className = 'scroll-indicator';
    scrollIndicator.innerHTML = '<i class="bi bi-arrow-up"></i>';
    scrollIndicator.title = '返回顶部';
    document.body.appendChild(scrollIndicator);

    // 使用防抖优化滚动事件
    let scrollTimer = null;
    function handleScroll() {
        if (scrollTimer) return;
        scrollTimer = requestAnimationFrame(function() {
            if (window.scrollY > 300) {
                scrollIndicator.classList.add('show');
            } else {
                scrollIndicator.classList.remove('show');
            }
            scrollTimer = null;
        });
    }

    // 兼容iOS的滚动事件
    window.addEventListener('scroll', handleScroll, { passive: true });
    
    // 使用统一事件绑定
    if (window.addTapEvent) {
        window.addTapEvent(scrollIndicator, function() {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    } else {
        scrollIndicator.addEventListener('click', function() {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
})();

// ==================== 自定义Toast通知 ====================
window.showCustomToast = function(message, type) {
    const toast = document.createElement('div');
    toast.className = 'toast-custom ' + (type || 'success');
    toast.textContent = message;
    // 使用 will-change 优化动画性能
    toast.style.willChange = 'transform, opacity';
    document.body.appendChild(toast);

    setTimeout(function() {
        toast.style.animation = 'toastFadeOut 0.4s ease forwards';
        setTimeout(function() {
            if (toast.parentNode) toast.parentNode.removeChild(toast);
        }, 400);
    }, 3000);
};

// ==================== 数字递增动画 ====================
window.animateCounter = function(element, target, duration) {
    const start = 0;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const current = Math.floor(start + (target - start) * easeOut);
        
        element.textContent = current;

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
};

// ==================== 主初始化 ====================
document.addEventListener('DOMContentLoaded', function() {
    // 初始化点击穿透防护（仅在真正支持触摸的设备上）
    const supportsTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    if (supportsTouch && window.isMobile && window.isMobile()) {
        if (typeof window.preventClickThrough === 'function') {
            window.preventClickThrough();
        }
    }

    // 自动关闭alert提示
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            try {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } catch (e) {
                alert.style.display = 'none';
            }
        }, 5000);
    });

    // 工具提示初始化（移动端禁用，避免触发问题）
    if (!window.isMobile()) {
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltipTriggerList.forEach(function(el) {
            try {
                new bootstrap.Tooltip(el);
            } catch (e) {}
        });
    }

    // ==================== 侧边栏交互 ====================
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const body = document.body;

    // 检测是否为移动端
    function isMobile() {
        return window.innerWidth < 992;
    }

    // 侧边栏收缩/展开
    function toggleSidebar() {
        if (isMobile()) {
            sidebar.classList.toggle('show');
            sidebarOverlay.classList.toggle('show');
            // 防止背景滚动
            if (sidebar.classList.contains('show')) {
                body.style.overflow = 'hidden';
                body.classList.add('sidebar-open');
            } else {
                body.style.overflow = '';
                body.classList.remove('sidebar-open');
            }
        } else {
            sidebar.classList.toggle('collapsed');
            body.classList.toggle('sidebar-collapsed');
            const isCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem('sidebarCollapsed', isCollapsed);
        }
    }

    // 关闭移动端侧边栏
    function closeMobileSidebar() {
        if (sidebar && sidebar.classList.contains('show')) {
            sidebar.classList.remove('show');
            sidebarOverlay.classList.remove('show');
            body.style.overflow = '';
            body.classList.remove('sidebar-open');
        }
    }

    // 使用统一事件绑定（兼容触摸和点击）
    if (sidebarToggle) {
        if (window.addTapEvent) {
            window.addTapEvent(sidebarToggle, function(e) {
                e.preventDefault && e.preventDefault();
                toggleSidebar();
            });
        } else {
            sidebarToggle.addEventListener('click', function(e) {
                e.preventDefault();
                toggleSidebar();
            });
        }
    }

    if (mobileMenuBtn) {
        if (window.addTapEvent) {
            window.addTapEvent(mobileMenuBtn, function(e) {
                e.preventDefault && e.preventDefault();
                sidebar.classList.add('show');
                sidebarOverlay.classList.add('show');
                body.style.overflow = 'hidden';
                body.classList.add('sidebar-open');
            });
        } else {
            mobileMenuBtn.addEventListener('click', function(e) {
                e.preventDefault();
                sidebar.classList.add('show');
                sidebarOverlay.classList.add('show');
                body.style.overflow = 'hidden';
                body.classList.add('sidebar-open');
            });
        }
    }

    // 点击遮罩层关闭侧边栏
    if (sidebarOverlay) {
        if (window.addTapEvent) {
            window.addTapEvent(sidebarOverlay, function() {
                closeMobileSidebar();
            });
        } else {
            sidebarOverlay.addEventListener('click', function() {
                closeMobileSidebar();
            });
        }
    }

    // 页面加载时恢复侧边栏状态
    if (!isMobile()) {
        const savedState = localStorage.getItem('sidebarCollapsed');
        if (savedState === 'true') {
            sidebar.classList.add('collapsed');
            body.classList.add('sidebar-collapsed');
        }
    }

    // 窗口大小变化时处理（使用防抖）
    let resizeTimer = null;
    window.addEventListener('resize', function() {
        if (resizeTimer) clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            if (isMobile()) {
                sidebar.classList.remove('collapsed');
                body.classList.remove('sidebar-collapsed');
            } else {
                closeMobileSidebar();
            }
            // 更新视口高度变量
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', vh + 'px');
        }, 150);
    });

    // 初始化视口高度变量（解决iOS Safari 100vh问题）
    function setViewportHeight() {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', vh + 'px');
    }
    setViewportHeight();
    window.addEventListener('orientationchange', function() {
        setTimeout(setViewportHeight, 200);
    });

    // 点击侧边栏外部关闭移动端菜单
    document.addEventListener('click', function(e) {
        if (isMobile() && sidebar.classList.contains('show')) {
            const isClickInside = sidebar.contains(e.target) || (mobileMenuBtn && mobileMenuBtn.contains(e.target));
            if (!isClickInside) {
                closeMobileSidebar();
            }
        }
    });

    // ESC键关闭侧边栏
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && isMobile() && sidebar.classList.contains('show')) {
            closeMobileSidebar();
        }
    });

    // ==================== 移动端侧边栏滑动手势（仅真正支持触摸的设备） ====================
    const supportsTouchForSwipe = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    if (supportsTouchForSwipe && window.isMobile && window.isMobile() && sidebar) {
        window.addSwipeEvent(document.body, {
            threshold: 80,
            restraint: 120,
            onSwipeRight: function() {
                // 向右滑动打开侧边栏（仅当侧边栏关闭时）
                if (!sidebar.classList.contains('show') && !sidebar.classList.contains('collapsed')) {
                    const touch = arguments[0];
                    // 只在屏幕左侧20%区域开始滑动时触发
                    // 简化处理：直接打开
                }
            },
            onSwipeLeft: function() {
                // 向左滑动关闭侧边栏
                if (sidebar.classList.contains('show')) {
                    closeMobileSidebar();
                }
            }
        });
    }

    // ==================== 表单输入优化（iOS） ====================
    // 解决iOS输入框获焦放大问题
    if (window.isIOS && window.isIOS()) {
        const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], input[type="number"], textarea, select');
        inputs.forEach(function(input) {
            if (!input.style.fontSize) {
                input.style.fontSize = '16px';
            }
        });
    }

    // ==================== 图片懒加载 ====================
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.classList.add('loaded');
                        observer.unobserve(img);
                    }
                }
            });
        }, {
            rootMargin: '50px',
            threshold: 0.01
        });

        document.querySelectorAll('img[data-src]').forEach(function(img) {
            imageObserver.observe(img);
        });
    } else {
        // 降级处理：直接加载所有图片
        document.querySelectorAll('img[data-src]').forEach(function(img) {
            if (img.dataset.src) img.src = img.dataset.src;
        });
    }

    // ==================== 视口高度修复（移动端） ====================
    function setViewportHeight() {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', vh + 'px');
    }
    setViewportHeight();
    window.addEventListener('resize', setViewportHeight);
    window.addEventListener('orientationchange', function() {
        setTimeout(setViewportHeight, 200);
    });

    // ==================== 修复iOS Safari 100vh问题 ====================
    if (window.isIOS && window.isIOS()) {
        function fixIOSHeight() {
            document.documentElement.style.setProperty('--ios-height', window.innerHeight + 'px');
        }
        fixIOSHeight();
        window.addEventListener('resize', fixIOSHeight);
        window.addEventListener('orientationchange', function() {
            setTimeout(fixIOSHeight, 300);
        });
    }
});
