// app/static/js/reader.js

$(document).ready(function() {
    // Переменные для пагинации
    let currentPage = 1;
    let totalPages = 1;
    let paginatedContent = [];

    // Переменные для работы со словами
    let currentWord = null;
    let currentWordContext = null;

    // Константы для пагинации
    const MAX_LINES_PER_PAGE = 25;     // Максимальное количество строк на странице
    const AVG_CHARS_PER_LINE = 80;     // Среднее количество символов в строке
    const MAX_CHARS_PER_PAGE = MAX_LINES_PER_PAGE * AVG_CHARS_PER_LINE;

    // Функция инициализации пагинации
    function initializePagination() {
        console.log("Initializing pagination...");

        // Получаем исходный текст
        const originalContent = $('.reader-text').html();
        if (!originalContent || originalContent.trim() === '') {
            console.error('Content is empty, nothing to paginate');
            return;
        }

        // Очищаем текстовый контейнер
        $('.reader-text').empty();

        // Разбиваем текст на абзацы по <br> тегам
        const paragraphs = originalContent.split(/<br\s*\/?>/i).filter(p => p.trim() !== '');

        // Разбиваем на страницы с учетом заданного количества строк
        paginatedContent = [];
        let currentPageContent = '';
        let currentCharCount = 0;

        // Для каждого абзаца
        for (let i = 0; i < paragraphs.length; i++) {
            const paragraph = paragraphs[i];

            // Приблизительное количество символов в абзаце (учитываем HTML-теги)
            const textLength = paragraph.replace(/<[^>]*>/g, '').length;

            // Если абзац слишком большой для одной страницы, разбиваем его на предложения
            if (textLength > MAX_CHARS_PER_PAGE) {
                // Разбиваем абзац на предложения (учитываем русские и английские предложения)
                const sentences = paragraph.split(/(?<=[.!?])\s+/).filter(s => s.trim() !== '');
                let sentenceGroup = '';
                let sentenceGroupLength = 0;

                // Для каждого предложения в абзаце
                for (let j = 0; j < sentences.length; j++) {
                    const sentence = sentences[j];
                    const sentenceLength = sentence.replace(/<[^>]*>/g, '').length;

                    // Проверяем, поместится ли предложение на текущую страницу
                    if (currentCharCount + sentenceGroupLength + sentenceLength > MAX_CHARS_PER_PAGE) {
                        // Если текущая группа предложений не пуста, добавляем ее к текущей странице
                        if (sentenceGroup !== '') {
                            if (currentPageContent !== '') {
                                currentPageContent += '<br>';
                            }
                            currentPageContent += sentenceGroup;
                            currentCharCount += sentenceGroupLength;

                            // Если предложение не помещается, создаем новую страницу
                            if (currentCharCount + sentenceLength > MAX_CHARS_PER_PAGE) {
                                paginatedContent.push(currentPageContent);
                                currentPageContent = '';
                                currentCharCount = 0;
                            }
                        }

                        // Сбрасываем группу предложений и добавляем текущее предложение
                        sentenceGroup = sentence;
                        sentenceGroupLength = sentenceLength;
                    } else {
                        // Предложение помещается в текущую группу
                        if (sentenceGroup !== '') {
                            sentenceGroup += ' ';
                            sentenceGroupLength += 1;
                        }
                        sentenceGroup += sentence;
                        sentenceGroupLength += sentenceLength;
                    }
                }

                // Добавляем оставшиеся предложения
                if (sentenceGroup !== '') {
                    if (currentCharCount + sentenceGroupLength > MAX_CHARS_PER_PAGE) {
                        // Если текущая страница не пуста и группа предложений не помещается, создаем новую страницу
                        if (currentPageContent !== '') {
                            paginatedContent.push(currentPageContent);
                            currentPageContent = sentenceGroup;
                            currentCharCount = sentenceGroupLength;
                        } else {
                            // Текущая страница пуста, добавляем группу предложений
                            currentPageContent = sentenceGroup;
                            currentCharCount = sentenceGroupLength;
                        }
                    } else {
                        // Группа предложений помещается на текущую страницу
                        if (currentPageContent !== '') {
                            currentPageContent += '<br>';
                            currentCharCount += 1;
                        }
                        currentPageContent += sentenceGroup;
                        currentCharCount += sentenceGroupLength;
                    }
                }
            } else {
                // Абзац поместится на одну страницу, проверяем, поместится ли с текущим контентом
                if (currentCharCount + textLength + 1 > MAX_CHARS_PER_PAGE) {
                    // Не поместится, создаем новую страницу
                    paginatedContent.push(currentPageContent);
                    currentPageContent = paragraph;
                    currentCharCount = textLength;
                } else {
                    // Поместится на текущую страницу
                    if (currentPageContent !== '') {
                        currentPageContent += '<br>';
                        currentCharCount += 1;
                    }
                    currentPageContent += paragraph;
                    currentCharCount += textLength;
                }
            }

            // Если накопилось достаточно текста, создаем новую страницу
            if (currentCharCount >= MAX_CHARS_PER_PAGE && i < paragraphs.length - 1) {
                paginatedContent.push(currentPageContent);
                currentPageContent = '';
                currentCharCount = 0;
            }
        }

        // Добавляем последнюю страницу, если остался контент
        if (currentPageContent) {
            paginatedContent.push(currentPageContent);
        }

        // Если получилось слишком мало страниц или текст слишком мал
        if (paginatedContent.length === 0) {
            paginatedContent = [originalContent];
        }

        // Обновляем общее количество страниц
        totalPages = paginatedContent.length;
        console.log(`Content divided into ${totalPages} pages`);

        // Добавляем элементы управления пагинацией
        addPaginationControls();

        // Показываем первую страницу
        showPage(1);
    }

    // Показать указанную страницу
    function showPage(pageNumber) {
        if (pageNumber < 1 || pageNumber > totalPages) return;

        currentPage = pageNumber;
        $('.reader-text').html(paginatedContent[pageNumber - 1]);

        // Обновляем отображение номера страницы
        $('.pagination-controls .page-info').text(`${currentPage} / ${totalPages}`);

        // Обновляем состояние кнопок навигации
        $('.pagination-controls #prev-page').prop('disabled', currentPage === 1);
        $('.pagination-controls #next-page').prop('disabled', currentPage === totalPages);

        // Прокручиваем в начало контейнера
        $('.reader-container').scrollTop(0);

        // Привязываем обработчик событий к словам заново
        bindWordClickHandler();
    }

    // Добавляем элементы управления пагинацией
    function addPaginationControls() {
        // Удаляем существующие элементы управления, чтобы избежать дублирования
        $('.pagination-controls').remove();

        // Создаем и добавляем новые элементы управления
        const paginationControls = `
            <div class="pagination-controls text-center mb-3">
                <button id="prev-page" class="btn btn-outline-secondary me-2" ${currentPage === 1 ? 'disabled' : ''}>
                    <i class="fas fa-chevron-left"></i>
                </button>
                <span class="page-info mx-2">
                    ${currentPage} / ${totalPages}
                </span>
                <button id="next-page" class="btn btn-outline-secondary ms-2" ${currentPage === totalPages ? 'disabled' : ''}>
                    <i class="fas fa-chevron-right"></i>
                </button>
            </div>
        `;

        $('.reader-container').prepend(paginationControls);

        // Привязываем обработчики событий к кнопкам
        $('#prev-page').on('click', function() {
            showPage(currentPage - 1);
        });

        $('#next-page').on('click', function() {
            showPage(currentPage + 1);
        });

        // Добавляем навигацию с помощью клавиш стрелок
        $(document).off('keydown.pagination').on('keydown.pagination', function(e) {
            if (e.key === 'ArrowLeft') {
                showPage(currentPage - 1);
            } else if (e.key === 'ArrowRight') {
                showPage(currentPage + 1);
            }
        });

        // Добавляем жесты свайпа для мобильных устройств
        let touchStartX = 0;
        $('.reader-container').off('touchstart').on('touchstart', function(e) {
            touchStartX = e.originalEvent.touches[0].clientX;
        });

        $('.reader-container').off('touchend').on('touchend', function(e) {
            const touchEndX = e.originalEvent.changedTouches[0].clientX;
            const diff = touchStartX - touchEndX;

            if (Math.abs(diff) > 50) { // Минимальное расстояние для определения свайпа
                if (diff > 0) {
                    // Свайп влево - следующая страница
                    showPage(currentPage + 1);
                } else {
                    // Свайп вправо - предыдущая страница
                    showPage(currentPage - 1);
                }
            }
        });
    }

    // Привязываем обработчик нажатия к словам
    function bindWordClickHandler() {
        $('.word').off('click').on('click', function() {
            const word = $(this).data('word');
            currentWord = word;

            // Получаем окружающий контекст
            const wordElements = $('.word');
            const currentIndex = wordElements.index(this);
            const startIndex = Math.max(0, currentIndex - 10);
            const endIndex = Math.min(wordElements.length - 1, currentIndex + 10);

            let contextWords = [];
            for (let i = startIndex; i <= endIndex; i++) {
                const element = wordElements[i];
                if (i === currentIndex) {
                    contextWords.push('<strong>' + $(element).text() + '</strong>');
                } else {
                    contextWords.push($(element).text());
                }
            }

            currentWordContext = contextWords.join(' ');

            // Обновляем модальное окно и показываем его
            $('#wordTitle').text(word);
            $('#wordLoading').removeClass('d-none');
            $('#wordContent').addClass('d-none');
            $('#wordError').addClass('d-none');

            const modal = new bootstrap.Modal(document.getElementById('wordInfoModal'));
            modal.show();

            // Включаем кнопку перевода в чате
            $('#translateWord').prop('disabled', false);

            // Получаем информацию о слове через API
            fetchWordInfo(word);
        });
    }

    // Обрабатываем изменения размера шрифта
    function handleFontSizeChange() {
        // Если размер шрифта меняется, нужно пересчитать количество строк и символов
        let fontSize = parseInt($('body').css('--reader-font-size')) || 18;
        // Корректировка параметров на основе размера шрифта
        if (fontSize <= 16) {
            // Маленький шрифт, больше строк
            MAX_LINES_PER_PAGE = 30;
        } else if (fontSize >= 22) {
            // Большой шрифт, меньше строк
            MAX_LINES_PER_PAGE = 20;
        } else {
            // Стандартный размер
            MAX_LINES_PER_PAGE = 25;
        }

        // Перезагружаем пагинацию
        initializePagination();
    }

    // Добавляем обработчики для кнопок изменения размера шрифта
    $('#decreaseFontSize, #increaseFontSize, #fontSizeRange').on('click change', function() {
        // Небольшая задержка для применения нового размера шрифта
        setTimeout(handleFontSizeChange, 100);
    });

    // Обрабатываем изменение темы
    $('#themeLight, #themeSepia, #themeDark, input[name="theme"]').on('click change', function() {
        // Небольшая задержка для применения новой темы
        setTimeout(handleFontSizeChange, 100);
    });

    // Обработчик для прокрутки колесиком мыши
    $('.reader-container').on('wheel', function(e) {
        // Только обрабатываем большие прокрутки
        if (Math.abs(e.originalEvent.deltaY) > 50) {
            if (e.originalEvent.deltaY > 0) {
                // Прокрутка вниз - следующая страница
                showPage(currentPage + 1);
            } else {
                // Прокрутка вверх - предыдущая страница
                showPage(currentPage - 1);
            }
            // Предотвращаем стандартную прокрутку
            e.preventDefault();
        }
    });

    // Инициализируем пагинацию после загрузки страницы
    console.log("Reader.js loaded, initializing pagination");
    initializePagination();

    // Перезагружаем пагинацию при изменении размера окна
    $(window).on('resize', function() {
        // Задержка для уменьшения частоты вызовов
        clearTimeout(window.resizeTimeout);
        window.resizeTimeout = setTimeout(function() {
            initializePagination();
        }, 250);
    });
});