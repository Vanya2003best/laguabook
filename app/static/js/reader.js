// Код для добавления в app/static/js/reader.js или включения в блок script в app/templates/reader/view.html

$(document).ready(function() {
    // Константы и переменные для пагинации
    const pageHeight = 650; // Высота страницы в пикселях (можно адаптировать)
    let currentPage = 1;
    let totalPages = 1;
    let paginatedContent = [];

    // Инициализация пагинации
    function initializePagination() {
        const content = $('.reader-text').html();
        $('.reader-text').empty();

        // Создаем временный элемент для измерения высоты контента
        const tempElement = $('<div class="reader-text-temp"></div>').html(content);
        tempElement.css({
            'position': 'absolute',
            'visibility': 'hidden',
            'width': $('.reader-container').width() + 'px',
            'font-size': $('body').css('--reader-font-size'),
            'line-height': '1.6'
        });

        $('body').append(tempElement);
        const fullHeight = tempElement.height();

        // Разделяем содержимое на страницы
        const words = tempElement.find('.word, br').toArray();
        let pageContent = [];
        let currentHeight = 0;
        let pageContentDiv = $('<div></div>');

        words.forEach(function(word) {
            const clone = $(word).clone();
            pageContentDiv.append(clone);

            // Если это <br>, то сразу добавляем break
            if (word.tagName === 'BR') {
                pageContentDiv.append(' ');
            }

            // Проверяем высоту
            if (pageContentDiv.height() > pageHeight) {
                // Сохраняем содержимое страницы до превышения высоты
                paginatedContent.push(pageContent.join(' '));

                // Начинаем новую страницу с текущего слова
                pageContent = [clone.prop('outerHTML')];
                pageContentDiv = $('<div></div>');
                pageContentDiv.append(clone);
            } else {
                // Добавляем слово к текущей странице
                pageContent.push(clone.prop('outerHTML'));
            }
        });

        // Добавляем последнюю страницу, если она не пуста
        if (pageContent.length > 0) {
            paginatedContent.push(pageContent.join(' '));
        }

        totalPages = paginatedContent.length;
        tempElement.remove();

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
        $('#current-page').text(currentPage);
        $('#total-pages').text(totalPages);

        // Обновляем состояние кнопок
        $('#prev-page').prop('disabled', currentPage === 1);
        $('#next-page').prop('disabled', currentPage === totalPages);

        // Привязываем обработчик событий к словам заново
        bindWordClickHandler();

        // Прокручиваем в начало контейнера
        $('.reader-container').scrollTop(0);
    }

    // Добавляем элементы управления пагинацией
    function addPaginationControls() {
        // Создаем контейнер для элементов управления пагинацией
        const paginationControls = `
            <div class="pagination-controls text-center mb-3">
                <button id="prev-page" class="btn btn-outline-secondary me-2">
                    <i class="fas fa-chevron-left"></i>
                </button>
                <span class="mx-2">
                    <span id="current-page">1</span> / <span id="total-pages">${totalPages}</span>
                </span>
                <button id="next-page" class="btn btn-outline-secondary ms-2">
                    <i class="fas fa-chevron-right"></i>
                </button>
            </div>
        `;

        $('.reader-container').prepend(paginationControls);

        // Привязываем обработчики событий
        $('#prev-page').on('click', function() {
            showPage(currentPage - 1);
        });

        $('#next-page').on('click', function() {
            showPage(currentPage + 1);
        });

        // Добавляем навигацию с помощью клавиш стрелок
        $(document).on('keydown', function(e) {
            if (e.key === 'ArrowLeft') {
                showPage(currentPage - 1);
            } else if (e.key === 'ArrowRight') {
                showPage(currentPage + 1);
            }
        });

        // Добавляем навигацию с помощью жестов (свайпов) для мобильных устройств
        let touchStartX = 0;
        $('.reader-container').on('touchstart', function(e) {
            touchStartX = e.originalEvent.touches[0].clientX;
        });

        $('.reader-container').on('touchend', function(e) {
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

    // Повторно привязываем обработчик событий к словам после загрузки новой страницы
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
        const controls = $('.pagination-controls').detach();
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
        // Определяем направление прокрутки
        if (e.originalEvent.deltaY > 0) {
            // Прокрутка вниз - следующая страница
            showPage(currentPage + 1);
        } else {
            // Прокрутка вверх - предыдущая страница
            showPage(currentPage - 1);
        }

        // Предотвращаем стандартную прокрутку страницы
        e.preventDefault();
    });

    // Инициализируем пагинацию после загрузки страницы
    initializePagination();

    // Также повторно инициализируем пагинацию при изменении размера окна
    $(window).on('resize', function() {
        // Небольшая задержка для уменьшения частоты вызовов
        clearTimeout(window.resizeTimeout);
        window.resizeTimeout = setTimeout(function() {
            const controls = $('.pagination-controls').detach();
            initializePagination();
        }, 250);
    });
});
