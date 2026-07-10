// Показывает эмодзи флага страны справа от select2-виджета и обновляет его при выборе
// новой опции. Используется в двух местах:
//   - City admin:     #id_country + JSON в <script id="country-flags-data"> ({country_id: flag})
//   - Location admin: #id_city    + JSON в <script id="city-flags-data">    ({city_id: flag})
(function () {
    var CONFIGS = [
        { selectId: "id_country", dataId: "country-flags-data" },
        { selectId: "id_city", dataId: "city-flags-data" },
    ];

    function getFlagsMap(dataId) {
        var el = document.getElementById(dataId);
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

        CONFIGS.forEach(function (config) {
            var $select = $("#" + config.selectId);
            if ($select.length === 0) return;

            var flags = getFlagsMap(config.dataId);

            // добавляем флаг как прямого потомка ".form-row" (а не рядом с select внутри
            // вложенных div'ов) — так у City (одно поле в строке) и Location (Name+City
            // в одной строке) флаг оказывается на одном и том же уровне вложенности,
            // и CSS (display:flex; align-items:center на .form-row) центрирует и
            // прижимает его вправо одинаково в обоих случаях
            var $row = $select.closest(".form-row");
            var $anchor = $row.length ? $row : $select;

            var $flag = $('<span class="country-flag-preview"></span>');
            $anchor.append($flag);

            function updateFlag() {
                var id = $select.val();
                $flag.text(id && flags[id] ? flags[id] : "");
            }

            updateFlag();
            // select2 триггерит нативный change на скрытом <select>, поэтому обычного .on("change") достаточно
            $select.on("change", updateFlag);
        });
    });
})();
