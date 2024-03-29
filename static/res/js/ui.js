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
function expandMobileNav() {
    var navBox = document.getElementById("mobile-nav");
    navBox.className += " expanded";
}
function hideMobileNav() {
    var navBox = document.getElementById("mobile-nav");
    navBox.classList.remove("expanded");
}
function toggleMobileNav() {
    var navBox = document.getElementById("mobile-nav");
    if (navBox.classList.contains("expanded")) {
        hideMobileNav();
    }
    else {
        expandMobileNav();
    }
}
function searchSubmitter(e, self) {
    if (!e) { var e = window.event; }
    e.preventDefault();
    
    // Enter key is pressed
    if (e.keyCode == 13) {
        search(self.value);
    }
}
function search(query) {
    url = "/search/" + encodeURI(query);
    location.href = url;
}