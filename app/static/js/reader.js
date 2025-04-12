// app/static/js/reader.js

$(document).ready(function() {
    // Константы и переменные для пагинации
    let currentPage = 1;
    let totalPages = 1;
    let paginatedContent = [];

    // Максимальное количество слов на страницу
    const MAX_WORDS_PER_PAGE = 300;

    // Инициализация пагинации
    function initializePagination() {
        const content = $('.reader-text').html();
        $('.reader-text').empty();

        // Если контент пустой, выходим
        if (!content || content.trim() === '') {
            console.error('Content is empty, nothing to paginate');
            return;
        }

        console.log('Initializing pagination for content...');

        // Принудительно разбиваем содержимое на страницы по словам
        // При большой книге обычные методы разбивки по высоте могут работать некорректно
        paginatedContent = [];

        // Разбиваем контент на абзацы и отдельные элементы
        const paragraphs = content.split('<br>');

        let currentPageContent = '';
        let wordCount = 0;

        // Перебираем все абзацы
        for (let i = 0; i < paragraphs.length; i++) {
            const paragraph = paragraphs[i];

            // Пропускаем пустые параграфы
            if (!paragraph.trim()) {
                continue;
            }

            // Разбиваем абзац на приблизительное количество слов
            // Используем регулярное выражение для примерного подсчета слов
            const paragraphWordCount = paragraph.split(/\s+/).length;

            // Если добавление этого абзаца превысит лимит и у нас уже есть содержимое,
            // создаем новую страницу
            if (wordCount + paragraphWordCount > MAX_WORDS_PER_PAGE && currentPageContent !== '') {
                paginatedContent.push(currentPageContent);
                currentPageContent = '';
                wordCount = 0;
            }

            // Добавляем абзац к текущей странице
            if (currentPageContent !== '') {
                currentPageContent += '<br>';
            }
            currentPageContent += paragraph;
            wordCount += paragraphWordCount;

            // Если этот абзац сам по себе большой, разбиваем его на несколько страниц
            if (paragraphWordCount > MAX_WORDS_PER_PAGE * 2) {
                console.log('Large paragraph detected, forcing pagination');
                // Разбиваем длинный абзац на предложения
                const sentences = paragraph.split(/(?<=[.!?])\s+/);
                let sentencePage = '';
                let sentenceWordCount = 0;

                for (let j = 0; j < sentences.length; j++) {
                    const sentence = sentences[j];
                    const sentenceWords = sentence.split(/\s+/).length;

                    if (sentenceWordCount + sentenceWords > MAX_WORDS_PER_PAGE && sentencePage !== '') {
                        if (currentPageContent !== '') {
                            paginatedContent.push(currentPageContent);
                        }
                        paginatedContent.push(sentencePage);
                        sentencePage = '';
                        sentenceWordCount = 0;
                        currentPageContent = '';
                        wordCount = 0;
                    }

                    if (sentencePage !== '') {
                        sentencePage += ' ';
                    }
                    sentencePage += sentence;
                    sentenceWordCount += sentenceWords;
                }

                if (sentencePage !== '') {
                    currentPageContent = sentencePage;
                    wordCount = sentenceWordCount;
                }
            }
        }

        // Добавляем последнюю страницу, если она не пуста
        if (currentPageContent !== '') {
            paginatedContent.push(currentPageContent);
        }

        // Если у нас нет страниц или всего одна небольшая страница,
        // принудительно разбиваем текст на фрагменты
        if (paginatedContent.length <= 1 && content.length > 1000) {
            console.log('Forcing content splitting');
            paginatedContent = [];

            // Разбиваем весь текст на примерно равные части
            const totalChars = content.length;
            const charsPerPage = 2000; // примерное количество символов на страницу

            for (let i = 0; i < totalChars; i += charsPerPage) {
                // При разбиении пытаемся не разрывать слова
                let endPos = Math.min(i + charsPerPage, totalChars);
                if (endPos < totalChars) {
                    // Ищем ближайший пробел или конец предложения
                    const nextSpace = content.indexOf(' ', endPos);
                    const nextPeriod = content.indexOf('. ', endPos);

                    if (nextPeriod > -1 && nextPeriod < nextSpace + 20) {
                        endPos = nextPeriod + 1;
                    } else if (nextSpace > -1 && nextSpace < endPos + 50) {
                        endPos = nextSpace;
                    }
                }

                const pageContent = content.substring(i, endPos);
                paginatedContent.push(pageContent);
            }
        }

        // Обновляем количество страниц
        totalPages = paginatedContent.length;

        console.log(`Content divided into ${totalPages} pages`);

        // Добавляем элементы управления пагинацией
        addPaginationControls();

        // Показываем первую страницу
        showPage(1);
    }

    // Показываем указанную страницу
    function showPage(pageNumber) {
        if (pageNumber < 1 || pageNumber > totalPages) return;

        currentPage = pageNumber;
        $('.reader-text').html(paginatedContent[pageNumber - 1]);

        // Обновляем отображение номера страницы
        $('.pagination-controls .page-info').text(`${currentPage} / ${totalPages}`);

        // Обновляем состояние кнопок
        $('.pagination-controls #prev-page').prop('disabled', currentPage === 1);
        $('.pagination-controls #next-page').prop('disabled', currentPage === totalPages);

        // Прокручиваем в начало контейнера
        $('.reader-container').scrollTop(0);

        // Привязываем обработчик событий к словам заново
        bindWordClickHandler();
    }

    // Добавляем элементы управления пагинацией
    function addPaginationControls() {
        // Проверяем, существуют ли элементы управления уже
        if ($('.pagination-controls').length === 0) {
            // Создаем контейнер для элементов управления пагинацией
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
        }

        // Привязываем обработчики событий
        $('#prev-page').off('click').on('click', function() {
            showPage(currentPage - 1);
        });

        $('#next-page').off('click').on('click', function() {
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

        // Добавляем навигацию с помощью жестов (свайпов) для мобильных устройств
        let touchStartX = 0;
        $('.reader-container').off('touchstart').on('touchstart', function(e) {
            touchStartX = e.originalEvent.touches[0].clientX;
        });

        $('.reader-container').off('touchend').on('touchend', function(e) {
            const touchEndX = e.originalEvent.changedTouches[0].clientX;
            const diff = touchStartX - touchEndX;

            if (Math.abs(diff) > 50) { // Минимальное расстояние для определения свайпа
                if (diff > 0) {
                    // Свайп влево (следующая страница)
                    showPage(currentPage + 1);
                } else {
                    // Свайп вправо (предыдущая страница)
                    showPage(currentPage - 1);
                }
            }
        });
    }

    // Привязываем обработчик событий к словам
    function bindWordClickHandler() {
        $('.word').off('click').on('click', function() {
            const word = $(this).data('word');
            currentWord = word;

            // Получаем окружающий контекст (примерно 10 слов до и после)
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

            // Получаем информацию о слове
            fetchWordInfo(word);
        });
    }

    // Обрабатываем изменение размера шрифта
    function handleFontSizeChange() {
        // Перезагружаем пагинацию при изменении размера шрифта
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

    // Обработчик для события прокрутки колесиком мыши (для навигации)
    $('.reader-container').on('wheel', function(e) {
        // Только обрабатываем большие прокрутки, чтобы избежать случайных переключений страниц
        if (Math.abs(e.originalEvent.deltaY) > 50) {
            if (e.originalEvent.deltaY > 0) {
                // Прокрутка вниз - следующая страница
                showPage(currentPage + 1);
            } else {
                // Прокрутка вверх - предыдущая страница
                showPage(currentPage - 1);
            }
            // Предотвращаем стандартную прокрутку страницы
            e.preventDefault();
        }
    });

    // Инициализируем пагинацию после загрузки страницы
    console.log("Initializing reader.js");
    initializePagination();

    // Также повторно инициализируем пагинацию при изменении размера окна
    $(window).on('resize', function() {
        // Небольшая задержка для уменьшения частоты вызовов
        clearTimeout(window.resizeTimeout);
        window.resizeTimeout = setTimeout(function() {
            initializePagination();
        }, 250);
    });
});