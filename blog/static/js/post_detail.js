document.addEventListener("DOMContentLoaded", function () {
    const commentForm = document.getElementById("comment-form");
    const commentsContainer = document.getElementById("comments-container");

    if (commentForm) {
        commentForm.addEventListener("submit", function (e) {
            e.preventDefault();
            const formData = new FormData(this);

            fetch(this.action, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
            })
                .then((response) => response.json())
                .then((data) => {
                    commentsContainer.insertAdjacentHTML(
                        "beforeend",
                        data.html
                    );
                    commentForm.reset();
                });
        });
    }

    commentsContainer.addEventListener("click", function (e) {
        if (e.target.classList.contains("delete-comment")) {
            e.preventDefault();
            if (confirm("Are you sure you want to delete this comment?")) {
                fetch(e.target.href, {
                    method: "POST",
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "X-CSRFToken": getCookie("csrftoken"),
                    },
                })
                    .then((response) => response.json())
                    .then((data) => {
                        if (data.success) {
                            e.target.closest(".comment").remove();
                        }
                    });
            }
        }
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === name + "=") {
                    cookieValue = decodeURIComponent(
                        cookie.substring(name.length + 1)
                    );
                    break;
                }
            }
        }
        return cookieValue;
    }
});
