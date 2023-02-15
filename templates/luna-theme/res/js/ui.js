DOM = {};
UI = {
    search: {
        visible: false
    }
};

function initUI() {
    DOM.searchBox = document.getElementById("searchInputContainer");
    DOM.searchBoxInput = document.querySelector("#searchInputContainer input");
}
document.addEventListener("DOMContentLoaded", function(){initUI()});
function showSearchBox() {
    DOM.searchBox.classList.remove("hidden");
    UI.search.visible = true;
    DOM.searchBoxInput.focus();
}
function hideSearchBox() {
    if (!DOM.searchBox.classList.contains("hidden")) {
        DOM.searchBox.className += " hidden";
        UI.search.visible = false;
    }
}
function searchButtonClick() {
    if (!UI.search.visible) {
        showSearchBox();
    }
    else {
        hideSearchBox();
    }
}