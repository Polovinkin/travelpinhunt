// Показывает эмодзи флага справа от поля Country на странице City и обновляет его
// при выборе другой страны в select2-виджете (autocomplete_fields = ["country"]).
(function () {
    function getFlagsMap() {
        var el = document.getElementById("country-flags-data");
        if (!el) return {};
        try {
            return JSON.parse(el.textContent);
        } catch (e) {
            return {};
        }
    }

    document.addEventListener("DOMContentLoaded", function () {
        var $ = window.django && window.django.jQuery;
        if (!$) return;

        var $select = $("#id_country");
        if ($select.length === 0) return;

        var flags = getFlagsMap();

        // ставим флаг сразу после виджета (после select2 и иконок карандаш/плюс/глаз)
        var $anchor = $select.closest(".related-widget-wrapper");
        if ($anchor.length === 0) $anchor = $select;

        var $flag = $('<span class="country-flag-preview"></span>');
        $anchor.after($flag);

        function updateFlag() {
            var id = $select.val();
            $flag.text(id && flags[id] ? flags[id] : "");
        }

        updateFlag();
        // select2 триггерит нативный change на скрытом <select>, поэтому обычного .on("change") достаточно
        $select.on("change", updateFlag);
    });
})();
