document.addEventListener("DOMContentLoaded", function () {
    const logoutLink = document.getElementById("logout-link");
    const logoutForm = document.getElementById("logout-form");

    if (logoutLink && logoutForm) {
        logoutLink.addEventListener("click", function (e) {
            e.preventDefault();
            logoutForm.submit();
        });
    }
});

const messages = document.querySelectorAll(".message");
messages.forEach(function (message) {
    const closeButton = message.querySelector(".close-message");
    if (closeButton) {
        closeButton.addEventListener("click", function () {
            message.style.display = "none";
        });
    }

    // 5초 후 자동으로 메시지 숨기기
    setTimeout(function () {
        message.style.opacity = "0";
        setTimeout(function () {
            message.style.display = "none";
        }, 300);
    }, 5000);
});
