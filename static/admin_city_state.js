// Показывает поле State в форме City только для стран с has_states=True (например США) —
// для всех остальных стран строка State полностью скрыта, форма выглядит как раньше.
// Также подставляет в <select id="id_state"> только штаты выбранной страны.
//
// Данные читаются из двух JSON-мэппингов, которые рендерит
// templates/admin/locations/city/change_form.html:
//   #country-has-states-data  → {country_id: true}       (страны с has_states=True)
//   #states-by-country-data   → {country_id: [{id, name}, ...]}
//
// Важно: поле Country использует select2 (autocomplete_fields), а select2 триггерит
// "change" только через jQuery-событийную систему, а не как нативное DOM-событие —
// обычный addEventListener("change", ...) на скрытом <select> его не ловит. Поэтому,
// как и в admin_country_flag.js, слушаем через django.jQuery.
(function () {
    function getJSON(dataId) {
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

        var $country = $("#id_country");
        var $state = $("#id_state");
        if ($country.length === 0 || $state.length === 0) return;

        var stateSelect = $state[0];
        var hasStatesMap = getJSON("country-has-states-data");
        var statesByCountry = getJSON("states-by-country-data");
        var $stateRow = $state.closest(".form-row");

        // изначально выбранный штат (при открытии формы редактирования существующего города) —
        // сохраняем, чтобы восстановить выбор после пересборки списка опций
        var initialStateId = stateSelect.value;
        var firstRun = true;

        function rebuildOptions(countryId, selectedId) {
            var options = statesByCountry[countryId] || [];
            stateSelect.innerHTML = "";

            var blank = document.createElement("option");
            blank.value = "";
            blank.textContent = "---------";
            stateSelect.appendChild(blank);

            options.forEach(function (state) {
                var opt = document.createElement("option");
                opt.value = state.id;
                opt.textContent = state.name;
                if (String(state.id) === String(selectedId)) opt.selected = true;
                stateSelect.appendChild(opt);
            });
        }

        function sync() {
            var countryId = $country.val();
            var hasStates = !!hasStatesMap[countryId];

            if (!hasStates) {
                stateSelect.value = "";
                $stateRow.hide();
                return;
            }

            rebuildOptions(countryId, firstRun ? initialStateId : "");
            $stateRow.show();
        }

        sync();
        firstRun = false;

        // select2 триггерит нативный change на скрытом <select>, поэтому обычного
        // .on("change") достаточно (см. тот же комментарий в admin_country_flag.js)
        $country.on("change", sync);
    });
})();
